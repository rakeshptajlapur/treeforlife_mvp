from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
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


# Custom User Creation Form with Email
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

# Unregister the default UserAdmin
admin.site.unregister(User)

# Custom User Admin
@admin.register(User)
class CustomUserAdmin(ImportExportMixin, BaseUserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)

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
    class Meta:
        model = Plantation
        fields = '__all__'

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
    list_display = ('plantation_id', 'name', 'owner', 'corporate', 'created_at', 'updated_at', 'latitude', 'longitude', 'state', 'gifted_by_name')
    search_fields = ('name', 'owner__username', 'owner__email', 'corporate__name', 'state', 'gifted_by_name')
    list_filter = ('state', 'corporate', 'created_at')
    ordering = ('-created_at',)
    resource_class = PlantationResource
    readonly_fields = ('plantation_id', 'created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('plantation_id', 'name', 'owner', 'corporate', 'plantation_date', 'description', 'gifted_by_name')
        }),
        ('Location Details', {
            'fields': ('latitude', 'longitude', 'state')
        }),
        ('Media', {
            'fields': ('image',)
        })
    )

    def plantation_id(self, obj):
        if obj and obj.pk:
            return obj.plantation_id()
        return "Will be generated after saving"
    plantation_id.short_description = 'Plantation ID'
    plantation_id.admin_order_field = 'id'

# Add after PlantationAdminForm
class TimelineAdminForm(ModelForm):
    class Meta:
        model = Timeline
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize plantation field label and choices
        if 'plantation' in self.fields:
            self.fields['plantation'].label = "Plantation (ID - Name)"
            plantations = Plantation.objects.all()
            self.fields['plantation'].choices = [
                (p.id, f"{p.plantation_id()} - {p.name}") 
                for p in plantations
            ]

@admin.register(Timeline)
class TimelineAdmin(admin.ModelAdmin):
    form = TimelineAdminForm
    list_display = ('get_plantation_id', 'plantation', 'activity_date', 'activity_title', 'description')
    list_filter = (PlantationIDFilter, 'activity_date')
    search_fields = ('activity_title', 'description', 'plantation__name')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # If editing existing timeline
            return ('plantation', 'display_plantation_id')
        return ()

    def get_fieldsets(self, request, obj=None):
        if obj:  # If editing existing timeline
            fieldsets = (
                ('Plantation Information', {
                    'fields': ('display_plantation_id', 'plantation'),
                    'description': 'Plantation information cannot be changed after creation.'
                }),
            )
        else:  # If creating new timeline
            fieldsets = (
                ('Plantation Information', {
                    'fields': ('plantation',),
                    'description': 'Select plantation by ID. Once created, plantation cannot be changed.'
                }),
            )
        
        fieldsets += (
            ('Timeline Details', {
                'fields': ('activity_date', 'activity_title', 'description')
            }),
            ('Media', {
                'fields': ('activity_image', 'video_url')
            }),
        )
        return fieldsets

    def display_plantation_id(self, obj):
        if obj and obj.plantation:
            return f"Plantation ID: {obj.plantation.plantation_id()}"
        return "-"
    display_plantation_id.short_description = "Plantation ID"

    def get_plantation_id(self, obj):
        if obj and obj.plantation:
            return obj.plantation.plantation_id()
        return "-"
    get_plantation_id.short_description = 'Plantation ID'
    get_plantation_id.admin_order_field = 'plantation__id'

class CommentAdminForm(ModelForm):
    class Meta:
        model = Comment
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'timeline' in self.fields:
            # Show both plantation ID and timeline title in dropdown
            timelines = Timeline.objects.select_related('plantation').all()
            self.fields['timeline'].choices = [
                (t.id, f"{t.plantation.plantation_id()} - {t.activity_title}") 
                for t in timelines
            ]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    form = CommentAdminForm
    list_display = ('get_plantation_id', 'timeline', 'user', 'created_at', 'text')
    search_fields = ('text', 'timeline__plantation__name')
    list_filter = (PlantationIDFilter, 'timeline', 'user')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing comment
            return ('display_plantation_id', 'timeline', 'user', 'created_at')
        return ('display_plantation_id', 'created_at')  # New comment

    def get_fieldsets(self, request, obj=None):
        if obj:  # Editing existing comment
            return (
                ('Plantation Information', {
                    'fields': ('display_plantation_id', 'timeline'),
                    'description': 'Timeline and plantation information cannot be changed after creation.'
                }),
                ('Comment Details', {
                    'fields': ('user', 'text', 'created_at')
                })
            )
        else:  # Adding new comment
            return (
                ('Plantation Information', {
                    'fields': ('timeline',),
                    'description': 'Select timeline by Plantation ID and Timeline title. Cannot be changed after creation.'
                }),
                ('Comment Details', {
                    'fields': ('user', 'text')
                })
            )

    def display_plantation_id(self, obj):
        if obj and obj.timeline and obj.timeline.plantation:
            return f"Plantation ID: {obj.timeline.plantation.plantation_id()}"
        return "-"
    display_plantation_id.short_description = "Plantation ID"

    def get_plantation_id(self, obj):
        return obj.timeline.plantation.plantation_id()
    get_plantation_id.short_description = 'Plantation ID'
    get_plantation_id.admin_order_field = 'timeline__plantation__id'

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new comment
            if not obj.user:  # If user not set
                obj.user = request.user  # Set current admin as user
        super().save_model(request, obj, form, change)

@admin.register(VisitRequest)
class VisitRequestAdmin(admin.ModelAdmin):
    list_display = ['get_plantation_id', 'plantation', 'owner', 'check_in_date', 'check_out_date', 'visitors', 'status']
    list_filter = [PlantationIDFilter, 'status', 'check_in_date']
    search_fields = ['plantation__name', 'owner__username']
    
    # Define base readonly fields
    readonly_fields = ['created_at', 'status_updated_at', 'plantation', 'owner', 
                      'phone_number', 'check_in_date', 'check_out_date', 'visitors',
                      'display_plantation_id']  # Add display_plantation_id
    
    def get_plantation_id(self, obj):
        return obj.plantation.plantation_id()
    get_plantation_id.short_description = 'Plantation ID'
    get_plantation_id.admin_order_field = 'plantation__id'
    
    def display_plantation_id(self, obj):
        if obj and obj.plantation:
            return f"Plantation ID: {obj.plantation.plantation_id()}"
        return "-"
    display_plantation_id.short_description = "Plantation ID"
    
    fieldsets = (
        ('Visit Details', {
            'fields': (
                'display_plantation_id',  # Add at the top
                'plantation', 
                'owner', 
                'phone_number',
                'check_in_date', 
                'check_out_date', 
                'visitors', 
                'message'
            )
        }),
        ('Status Management', {
            'fields': (
                'status', 
                'admin_comment', 
                'status_updated_at'
            ),
            'description': 'Update visit request status and add comments for the plantation owner.'
        })
    )

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ['created_at', 'status_updated_at']
        return self.readonly_fields