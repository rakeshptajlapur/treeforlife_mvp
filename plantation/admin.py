from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from import_export.admin import ImportExportMixin
from .resources import UserResource, PlantationResource
from .models import Corporate, Employee, Plantation, Timeline, Comment

# Unregister the default UserAdmin before defining your custom admin
admin.site.unregister(User)

# Extend the default UserAdmin with ImportExportMixin
class CustomUserAdmin(ImportExportMixin, DefaultUserAdmin):
    resource_class = UserResource
    # You can customize the list display or search fields if needed
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

@admin.register(Plantation)
class PlantationAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'owner', 'corporate', 'created_at', 'updated_at')
    # Now you can search by plantation name, owner username/email, or corporate name
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
