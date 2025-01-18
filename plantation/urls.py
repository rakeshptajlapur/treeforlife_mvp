from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('login/', views.login_view, name='login'),  # Use custom login view
    path('logout/', views.logout_view, name='logout'),
    path('owner-details/<str:username>/', views.owner_details, name='owner_details'),
    path('plantation-details/<int:id>/', views.plantation_details, name='plantation_details'),
    path('plantation/<int:plantation_id>/timeline/<int:timeline_id>/', views.timeline_detail, name='timeline_detail'),
    path('plantation/<int:plantation_id>/timeline/<int:timeline_id>/add_comment/', views.add_comment, name='add_comment'),
    path('plantation/<int:plantation_id>/timeline/<int:timeline_id>/ajax/', views.timeline_detail_ajax, name='timeline_detail_ajax'),


]