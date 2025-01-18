from django.contrib import admin
#from .models import Plantation, Timeline
from plantation.models import Plantation
from plantation.models import Timeline
from plantation.models import Comment



#admin.site.register(Plantation)
@admin.register(Plantation)
class PlantationAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner')


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