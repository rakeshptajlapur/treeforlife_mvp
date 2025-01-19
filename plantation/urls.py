from django.urls import path, include
from django.contrib import admin
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
path('', views.homepage, name='homepage'),
    path('admin/', admin.site.urls),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # existing stuff...
    path('owner-details/<str:username>/', views.owner_details, name='owner_details'),
    path('plantation-details/<int:id>/', views.plantation_details, name='plantation_details'),
    path('plantation/<int:plantation_id>/timeline/<int:timeline_id>/', views.timeline_details, name='timeline_details'),
    path('plantation/<int:plantation_id>/timeline/<int:timeline_id>/add_comment/', views.add_comment, name='add_comment'),
    path('plantation/<int:plantation_id>/timeline/<int:timeline_id>/ajax/', views.timeline_details_ajax, name='timeline_details_ajax'),

    # ---- NEW CORPORATE ROUTES ----
    path('corporate/dashboard/', views.corporate_dashboard, name='corporate_dashboard'),
    path('corporate/employees/', views.manage_employees, name='manage_employees'),
    path('corporate/employees/add/', views.add_employee, name='add_employee'),
    path('corporate/plantations/', views.manage_plantations, name='manage_plantations'),  # <--- ADD THIS
    path('corporate/plantation/<int:plantation_id>/assign/', views.assign_plantation, name='assign_plantation'),
    # ... etc


]