from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.client_login, name='login'),
    path('register/', views.client_register, name='register'),
    path('profile/', views.client_profile, name='client_profile'),
    path('admin-portal/login/', views.staff_login, name='staff_login'),
    path('admin-portal/logout/', views.staff_logout, name='staff_logout'),
]
