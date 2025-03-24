from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from threading import Thread
from .models import VisitRequest

def send_email_async(subject, message, recipient_list):
    Thread(
        target=send_mail,
        args=(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list),
        kwargs={"fail_silently": False}
    ).start()

@receiver(pre_save, sender=VisitRequest)
def handle_visit_status_change(sender, instance, **kwargs):
    try:
        # Get the old instance if it exists
        old_instance = VisitRequest.objects.get(pk=instance.pk)
        
        # Check if status has changed
        if old_instance.status != instance.status:
            subject = f"Visit Request {instance.status} - {instance.plantation.name}"
            
            message = f"""
Dear {instance.owner.username},

Your visit request for {instance.plantation.name} has been {instance.status.lower()}.

Visit Details:
- Check-in: {instance.check_in_date.strftime('%B %d, %Y %I:%M %p')}
- Check-out: {instance.check_out_date.strftime('%B %d, %Y %I:%M %p')}
- Number of Visitors: {instance.visitors}

{f"Admin Message: {instance.admin_comment}" if instance.admin_comment else ""}

{"Next steps and visit guidelines will be sent shortly." if instance.status == "Approved" else ""}

Best Regards,
TreeForLife Team
            """
            
            # Send email asynchronously
            if instance.owner.email:
                send_email_async(subject, message, [instance.owner.email])
                
    except VisitRequest.DoesNotExist:
        pass  # This is a new instance