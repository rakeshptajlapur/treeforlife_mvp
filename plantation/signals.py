from django.urls import reverse
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from threading import Thread
from .models import VisitRequest, Timeline, Comment
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

def send_email_async(subject, message, recipient_list):
    Thread(
        target=send_mail,
        args=(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list),
        kwargs={"fail_silently": False}
    ).start()

@receiver(pre_save, sender=VisitRequest)
def handle_visit_status_change(sender, instance, **kwargs):
    try:
        old_instance = VisitRequest.objects.get(pk=instance.pk)
        
        # Check if either status or admin_comment has changed
        if old_instance.status != instance.status or old_instance.admin_comment != instance.admin_comment:
            status_action = "updated" if old_instance.status == instance.status else instance.status.lower()
            
            subject = f"Visit Request {status_action} - {instance.plantation.name}"
            
            # Customize message based on status
            status_message = {
                "Approved": "We're pleased to inform you that your visit request has been approved.",
                "Rejected": "We regret to inform you that your visit request could not be approved.",
                "Pending": "Your visit request status has been updated."
            }.get(instance.status, "Your visit request status has been updated.")
            
            message = f"""
Dear {instance.owner.username},

{status_message}

Visit Details:
- Plantation: {instance.plantation.name}
- Check-in: {instance.check_in_date.strftime('%B %d, %Y %I:%M %p')}
- Check-out: {instance.check_out_date.strftime('%B %d, %Y %I:%M %p')}
- Number of Visitors: {instance.visitors}

{f"Admin Message: {instance.admin_comment}" if instance.admin_comment else ""}

{'''Next Steps:
1. Please arrive on time
2. Carry valid identification
3. Follow plantation guidelines
4. Contact support for any queries''' if instance.status == "Approved" else ""}

Best Regards,
TreeForLife Team
            """
            
            if instance.owner.email:
                send_email_async(subject, message, [instance.owner.email])
                
    except VisitRequest.DoesNotExist:
        pass  # This is a new instance

# 1. Timeline Creation Notification
@receiver(post_save, sender=Timeline)
def notify_owner_new_timeline(sender, instance, created, **kwargs):
    if created:  # Only for new timelines
        plantation = instance.plantation
        if plantation.owner and plantation.owner.email:
            subject = f"New Timeline Update - {plantation.name}"
            message = f"""
Dear {plantation.owner.username},

A new timeline update has been added to your plantation:

Plantation Details:
- Name: {plantation.name}
- ID: {plantation.plantation_id()}

Timeline Update:
- Date: {instance.activity_date.strftime('%B %d, %Y')}
- Title: {instance.activity_title or 'No title'}
- Description: {instance.description}

Best Regards,
TreeForLife Team
            """
            send_email_async(subject, message, [plantation.owner.email])

# 2. Owner Comment Notification
@receiver(post_save, sender=Comment)
def notify_admin_owner_comment(sender, instance, created, **kwargs):
    if created and instance.user == instance.timeline.plantation.owner:
        timeline = instance.timeline
        subject = f"New Owner Comment - {timeline.plantation.name}"
        message = f"""
New comment from plantation owner:

Plantation: {timeline.plantation.name} (ID: {timeline.plantation.plantation_id()})
Owner: {instance.user.username}
Timeline Entry: {timeline.activity_title or 'No title'}
Comment: {instance.text}
Date: {instance.created_at.strftime('%B %d, %Y %I:%M %p')}

Best Regards,
TreeForLife Team
        """
        send_email_async(subject, message, [settings.ADMIN_EMAIL])

# 3. Admin Comment Notification
@receiver(post_save, sender=Comment)
def notify_owner_admin_comment(sender, instance, created, **kwargs):
    if created and instance.user.is_staff:
        plantation = instance.timeline.plantation
        if plantation.owner and plantation.owner.email:
            subject = f"Admin Response - {plantation.name} Timeline"
            message = f"""
Dear {plantation.owner.username},

An admin has responded to your plantation timeline:

Timeline Entry: {instance.timeline.activity_title or 'No title'}
Date: {instance.created_at.strftime('%B %d, %Y %I:%M %p')}
Admin Response: {instance.text}

Best Regards,
TreeForLife Team
            """
            send_email_async(subject, message, [plantation.owner.email])
            
