from django.urls import reverse
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from .models import VisitRequest, Timeline, Comment, Plantation, Corporate, Employee
from plantation.tasks import send_email_task

# 1. Visit Request Status Change Notification
@receiver(pre_save, sender=VisitRequest)
def handle_visit_status_change(sender, instance, **kwargs):
    try:
        old_instance = VisitRequest.objects.get(pk=instance.pk)
        if old_instance.status != instance.status or old_instance.admin_comment != instance.admin_comment:
            status_action = "updated" if old_instance.status == instance.status else instance.status.lower()
            subject = f"Visit Request {status_action} - {instance.plantation.name}"
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
                send_email_task.delay(subject, message, [instance.owner.email])
    except VisitRequest.DoesNotExist:
        pass  # This is a new instance

# 2. Timeline Creation Notification
@receiver(post_save, sender=Timeline)
def notify_owner_new_timeline(sender, instance, created, **kwargs):
    if created:
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
            send_email_task.delay(subject, message, [plantation.owner.email])

# 3. Owner Comment Notification
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
        send_email_task.delay(subject, message, [settings.ADMIN_EMAIL])

# 4. Admin Comment Notification
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
            send_email_task.delay(subject, message, [plantation.owner.email])

# 5. User Creation Notification
@receiver(post_save, sender=User)
def notify_new_user_creation(sender, instance, created, **kwargs):
    if created and instance.email:
        token = default_token_generator.make_token(instance)
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        reset_url = f"{settings.SITE_URL}/reset/{uid}/{token}/"
        subject = "Welcome to TreeForLife - Account Created"
        message = f"""
Dear {instance.username},

Welcome to TreeForLife! Your account has been created successfully.

Username: {instance.username}
Email: {instance.email}

Please set your password using this link:
{reset_url}

Best Regards,
TreeForLife Team
        """
        send_email_task.delay(subject, message, [instance.email])

# 6. Plantation Assignment Notification
@receiver(pre_save, sender=Plantation)
def notify_plantation_assignment(sender, instance, **kwargs):
    try:
        old_instance = Plantation.objects.get(pk=instance.pk)
        if old_instance.owner != instance.owner and instance.owner:
            subject = f"New Plantation Assigned - {instance.name}"
            message = f"""
Dear {instance.owner.username},

You have been assigned as the owner of:

Plantation Details:
- Name: {instance.name}
- ID: {instance.plantation_id()}
- Location: {instance.state}

You can view your plantation details at:
{settings.SITE_URL}/plantation-details/{instance.id}/

Best Regards,
TreeForLife Team
            """
            send_email_task.delay(subject, message, [instance.owner.email])
    except Plantation.DoesNotExist:
        pass

# 7. Employee Creation Notification
@receiver(post_save, sender=Employee)
def notify_new_employee(sender, instance, created, **kwargs):
    if created and instance.user.email:
        token = default_token_generator.make_token(instance.user)
        uid = urlsafe_base64_encode(force_bytes(instance.user.pk))
        reset_url = f"{settings.SITE_URL}/reset/{uid}/{token}/"
        subject = f"Welcome to {instance.corporate.name} - TreeForLife Employee Portal"
        message = f"""
Dear {instance.user.username},

Welcome to TreeForLife! You've been added as an employee of {instance.corporate.name}.

Your Account Details:
Username: {instance.user.username}
Email: {instance.user.email}

Set your password here:
{reset_url}

Corporate Details:
Company: {instance.corporate.name}
Admin: {instance.corporate.admin_user.get_full_name() or instance.corporate.admin_user.username}

Best Regards,
TreeForLife Team
        """
        send_email_task.delay(subject, message, [instance.user.email])

# 8. Corporate Account Creation
@receiver(post_save, sender=Corporate)
def notify_corporate_creation(sender, instance, created, **kwargs):
    if created and instance.admin_user.email:
        subject = "Corporate Account Created - TreeForLife"
        message = f"""
Dear {instance.admin_user.get_full_name() or instance.admin_user.username},

Your corporate account has been created successfully.

Corporate Details:
- Company Name: {instance.name}
- Plantation Credits: {instance.plantation_credits}
- Employee Credits: {instance.employee_credits}

Access your dashboard at:
{settings.SITE_URL}/corporate/dashboard/

Best Regards,
TreeForLife Team
        """
        send_email_task.delay(subject, message, [instance.admin_user.email])

# 9. Corporate Credits Update Notification
@receiver(pre_save, sender=Corporate)
def notify_corporate_credits_update(sender, instance, **kwargs):
    try:
        old_instance = Corporate.objects.get(pk=instance.pk)
        credits_changed = (
            old_instance.plantation_credits != instance.plantation_credits or 
            old_instance.employee_credits != instance.employee_credits
        )
        if credits_changed and instance.admin_user.email:
            subject = f"Credits Updated - {instance.name}"
            message = f"""
Dear {instance.admin_user.get_full_name() or instance.admin_user.username},

Your corporate account credits have been updated by TreeForLife Admin:

Previous Credits:
- Plantation Credits: {old_instance.plantation_credits}
- Employee Credits: {old_instance.employee_credits}

Updated Credits:
- Plantation Credits: {instance.plantation_credits}
- Employee Credits: {instance.employee_credits}

You can manage your resources at:
{settings.SITE_URL}/corporate/dashboard/

Best Regards,
TreeForLife Team
            """
            send_email_task.delay(subject, message, [instance.admin_user.email])
    except Corporate.DoesNotExist:
        pass  # Skip for new corporate creation as it's handled by other signal

