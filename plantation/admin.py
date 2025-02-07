from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from import_export.admin import ImportExportMixin
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .resources import UserResource, PlantationResource
from .models import Corporate, Employee, Plantation, Timeline, Comment, VisitRequest



# Unregister the default UserAdmin before defining your custom admin
admin.site.unregister(User)

# Extend the default UserAdmin with ImportExportMixin
class CustomUserAdmin(ImportExportMixin, DefaultUserAdmin):
    resource_class = UserResource
    list_display = ('username', 'email', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email')

# Register your custom UserAdmin
admin.site.register(User, CustomUserAdmin)

@admin.register(Corporate)
class CorporateAdmin(admin.ModelAdmin):
    list_display = ('name', 'admin_user', 'plantation_credits', 'employee_credits')
    search_fields = ('name', 'admin_user__username')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'corporate')
    search_fields = ('user__username', 'corporate__name')

# Custom form for PlantationAdmin to enforce validation
class PlantationAdminForm(ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        corporate = cleaned_data.get('corporate')

        if corporate:
            plantation_count = corporate.plantations.exclude(id=self.instance.id).count()
            if plantation_count >= corporate.plantation_credits:
                raise ValidationError(
                    f"Cannot add plantation '{cleaned_data.get('name')}'. Plantation limit exceeded for corporate account '{corporate.name}'."
                )
        return cleaned_data

@admin.register(Plantation)
class PlantationAdmin(ImportExportMixin, admin.ModelAdmin):
    form = PlantationAdminForm
    list_display = ('name', 'owner', 'corporate', 'created_at', 'updated_at')
    search_fields = ('name', 'owner__username', 'owner__email', 'corporate__name')
    resource_class = PlantationResource

@admin.register(Timeline)
class TimelineAdmin(admin.ModelAdmin):
    list_display = ('plantation', 'activity_date', 'description')
    list_filter = ('plantation', 'activity_date')
    search_fields = ('description',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('timeline', 'user', 'created_at', 'text')
    search_fields = ('text',)
    list_filter = ('timeline', 'user')


@admin.register(VisitRequest)
class VisitRequestAdmin(admin.ModelAdmin):
    list_display = ('owner', 'plantation', 'check_in_date', 'check_out_date', 'visitors', 'created_at')
    search_fields = ('owner__username', 'plantation__name', 'phone_number')
    list_filter = ('check_in_date', 'check_out_date')
