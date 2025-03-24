from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Corporate(models.Model):
    """
    Represents a corporate account that has its own credits
    and an admin user.
    """
    admin_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='corporate_account')
    name = models.CharField(max_length=255)
    plantation_credits = models.PositiveIntegerField(default=0)
    employee_credits = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Employee(models.Model):
    """
    Represents an employee user belonging to a specific Corporate.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    corporate = models.ForeignKey(Corporate, on_delete=models.CASCADE, related_name='employees')

    def __str__(self):
        return f"{self.user.username} ({self.corporate.name})"


class Plantation(models.Model):
    name = models.CharField(max_length=255)
    plantation_date = models.DateField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='plantation_images/')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    corporate = models.ForeignKey(
        Corporate, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='plantations'
    )  # New field

    # New fields
    latitude = models.FloatField(null=True, blank=True)  # Latitude
    longitude = models.FloatField(null=True, blank=True)  # Longitude
    STATE_CHOICES = [
        ('Andhra Pradesh', 'Andhra Pradesh'),
        ('Arunachal Pradesh', 'Arunachal Pradesh'),
        ('Assam', 'Assam'),
        ('Bihar', 'Bihar'),
        ('Chhattisgarh', 'Chhattisgarh'),
        ('Goa', 'Goa'),
        ('Gujarat', 'Gujarat'),
        ('Haryana', 'Haryana'),
        ('Himachal Pradesh', 'Himachal Pradesh'),
        ('Jharkhand', 'Jharkhand'),
        ('Karnataka', 'Karnataka'),
        ('Kerala', 'Kerala'),
        ('Madhya Pradesh', 'Madhya Pradesh'),
        ('Maharashtra', 'Maharashtra'),
        ('Manipur', 'Manipur'),
        ('Meghalaya', 'Meghalaya'),
        ('Mizoram', 'Mizoram'),
        ('Nagaland', 'Nagaland'),
        ('Odisha', 'Odisha'),
        ('Punjab', 'Punjab'),
        ('Rajasthan', 'Rajasthan'),
        ('Sikkim', 'Sikkim'),
        ('Tamil Nadu', 'Tamil Nadu'),
        ('Telangana', 'Telangana'),
        ('Tripura', 'Tripura'),
        ('Uttar Pradesh', 'Uttar Pradesh'),
        ('Uttarakhand', 'Uttarakhand'),
        ('West Bengal', 'West Bengal'),
        ('Delhi', 'Delhi'),
        ('Jammu and Kashmir', 'Jammu and Kashmir'),
        ('Ladakh', 'Ladakh'),
    ]
    state = models.CharField(max_length=50, choices=STATE_CHOICES, null=True, blank=True)  # State dropdown

    def plantation_id(self):
        """Generate plantation ID in the format PLT-DDMMYY-ID."""
        date_str = self.plantation_date.strftime('%d%m%y')
        return f"PLT-{date_str}-{self.id}"

    def __str__(self):
        return self.name

    def clean(self):
        """
        Custom validation to enforce plantation credits.
        """
        if self.corporate:
            plantation_count = self.corporate.plantations.exclude(id=self.id).count()
            if plantation_count >= self.corporate.plantation_credits:
                raise ValidationError(
                    f"Cannot add plantation '{self.name}'. Plantation limit exceeded for corporate account '{self.corporate.name}'."
                )

    def save(self, *args, **kwargs):
        # Call clean to enforce validation
        self.clean()
        super().save(*args, **kwargs)


class Timeline(models.Model):
    plantation = models.ForeignKey(Plantation, on_delete=models.CASCADE, related_name='timelines')
    activity_date = models.DateField()
    activity_title = models.CharField(max_length=255, null=True, blank=True)  # Allow NULL values
    description = models.TextField()  # This will be used as the activity description
    activity_image = models.ImageField(upload_to='timeline_images/', null=True, blank=True)  # New field for activity image
    video_url = models.URLField(max_length=200, null=True, blank=True)  # New field for video URL

    def __str__(self):
        return f"{self.activity_title} on {self.activity_date}"


class Comment(models.Model):
    timeline = models.ForeignKey(Timeline, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Who made the comment
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.timeline.activity_date}"

    class Meta:
        ordering = ['-created_at']


class VisitRequest(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]
    
    plantation = models.ForeignKey('Plantation', on_delete=models.CASCADE, related_name="visit_requests")
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    check_in_date = models.DateTimeField()
    check_out_date = models.DateTimeField()
    visitors = models.PositiveIntegerField()
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    
    # New fields
    admin_comment = models.TextField(blank=True, null=True, verbose_name="Admin Comment")
    status_updated_at = models.DateTimeField(auto_now=True)
    """status_updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='visit_status_updates'
    )"""

    def __str__(self):
        return f"Visit Request by {self.owner.username} for {self.plantation.name} ({self.status})"