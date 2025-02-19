from django.urls import path, include
from django.contrib import admin
from . import views
from django.contrib.auth import views as auth_views
from .views import book_visit


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

    # ---- BUlk IMP EXP Routes ----
    path('corporate/employees/export/', views.export_employees, name='export_employees'),
    path('corporate/employees/import/', views.import_employees, name='import_employees'),
    
    path('corporate/plantations/export/', views.export_plantations, name='export_plantations'),
    path('corporate/plantations/import/', views.import_plantations, name='import_plantations'),
    path('corporate/plantations/template/', views.download_import_template, name='download_import_template'),

    #---delete employee in manage employee table route---
    path('corporate/employees/delete/<int:employee_id>/', views.delete_employee, name='delete_employee'),
   
    #---certificates view--- 
    path('certificate/<int:plantation_id>/', views.view_certificate, name='view_certificate'),

    #---visit request form---
    path('plantation/<int:plantation_id>/visit/', views.book_visit, name='book_visit'),
    
    # Add this new URL pattern
    path('mapview/', views.plantation_map_view, name='plantation_map'),
    

    


]