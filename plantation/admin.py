from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from import_export.admin import ImportExportMixin
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.contrib.admin import SimpleListFilter
from .resources import UserResource, PlantationResource
from .models import Corporate, Employee, Plantation, Timeline, Comment, VisitRequest


# Add this custom filter class
class PlantationIDFilter(SimpleListFilter):
    title = 'Plantation ID'
    parameter_name = 'plantation_id_filter'

    def lookups(self, request, model_admin):
        plantations = Plantation.objects.all()
        return [(p.id, p.plantation_id()) for p in plantations]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(plantation_id=self.value())
        return queryset


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
    list_display = ('plantation_id', 'name', 'owner', 'corporate', 'created_at', 'updated_at', 'latitude', 'longitude', 'state')
    search_fields = ('name', 'owner__username', 'owner__email', 'corporate__name', 'state')
    list_filter = ('state', 'corporate', 'created_at')
    ordering = ('-created_at',)
    resource_class = PlantationResource

    def plantation_id(self, obj):
        return obj.plantation_id()
    plantation_id.short_description = 'Plantation ID'
    plantation_id.admin_order_field = 'id'  # Allows sorting by ID

@admin.register(Timeline)
class TimelineAdmin(admin.ModelAdmin):
    list_display = ('get_plantation_id', 'plantation', 'activity_date', 'activity_title', 'description')
    list_filter = (PlantationIDFilter, 'activity_date')  # Replace 'plantation' with PlantationIDFilter
    search_fields = ('activity_title', 'description', 'plantation__name')
    fields = ('plantation', 'activity_date', 'activity_title', 'description', 'activity_image', 'video_url')

    def get_plantation_id(self, obj):
        return obj.plantation.plantation_id()
    get_plantation_id.short_description = 'Plantation ID'
    get_plantation_id.admin_order_field = 'plantation__id'  # Enable sorting

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('get_plantation_id','timeline', 'user', 'created_at', 'text')
    search_fields = ('text','timeline__plantation__name')
    list_filter = (PlantationIDFilter, 'timeline', 'user')

    def get_plantation_id(self, obj):
        return obj.timeline.plantation.plantation_id()
    get_plantation_id.short_description = 'Plantation ID'
    get_plantation_id.admin_order_field = 'timeline__plantation__id'  # Enable sorting


@admin.register(VisitRequest)
class VisitRequestAdmin(admin.ModelAdmin):
    list_display = ['get_plantation_id', 'plantation', 'owner', 'check_in_date', 'check_out_date', 'visitors', 'status']
    list_filter = [PlantationIDFilter, 'status', 'check_in_date']  # Add PlantationIDFilter here
    search_fields = ['plantation__name', 'owner__username']
    
    # Define base readonly fields
    readonly_fields = ['created_at', 'status_updated_at', 'plantation', 'owner', 
                      'phone_number', 'check_in_date', 'check_out_date', 'visitors']
    
    def get_plantation_id(self, obj):
        return obj.plantation.plantation_id()
    get_plantation_id.short_description = 'Plantation ID'
    get_plantation_id.admin_order_field = 'plantation__id'  # Enable sorting
    
    fieldsets = (
        ('Visit Details', {
            'fields': (
                'plantation', 'owner', 'phone_number',
                'check_in_date', 'check_out_date', 'visitors', 'message'
            )
        }),
        ('Status Management', {
            'fields': (
                'status', 'admin_comment', 'status_updated_at'
            ),
            'description': 'Update visit request status and add comments for the plantation owner.'
        })
    )

    def get_readonly_fields(self, request, obj=None):
        # If creating new object, only basic fields are readonly
        if obj is None:
            return ['created_at', 'status_updated_at']
        # If editing existing object, all fields except status and admin_comment are readonly
        return self.readonly_fields