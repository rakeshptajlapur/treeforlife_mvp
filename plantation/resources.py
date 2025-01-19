from import_export import resources
from django.contrib.auth.models import User
from plantation.models import Plantation
from django.utils.timezone import now



class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_staff', 'is_active', 'date_joined')  # Include date_joined for export
        export_order = ('id', 'username', 'email', 'is_staff', 'is_active', 'date_joined')

    def before_import_row(self, row, **kwargs):
        # Optionally handle date_joined during import
        if not row.get('date_joined'):
            from django.utils.timezone import now
            row['date_joined'] = now()  # Auto-fill with the current timestamp if missing



class PlantationResource(resources.ModelResource):
    owner_email = resources.Field()  # We will use email to identify the user

    class Meta:
        model = Plantation
        fields = ('id', 'name', 'owner_email', 'created_at', 'updated_at')  # owner_email instead of owner
        export_order = ('id', 'name', 'owner_email', 'created_at', 'updated_at')

    def before_import_row(self, row, **kwargs):
        # Get the email and assign the owner
        email = row.get('owner_email')
        user = None

        if email:
            # Try to find the user by email
            user, created = User.objects.get_or_create(email=email)
            if created:
                # If the user was created, set additional fields if needed
                user.is_active = True  # You can set default values like is_active
                user.save()

        row['owner'] = user  # Assign the user as owner (existing or newly created)
        return row


