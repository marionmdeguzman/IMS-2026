from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/create/', views.payment_create, name='payment_create'),
    path('memberships/', views.membership_list, name='membership_list'),
    path('plans/', views.plan_list, name='plan_list'),
    path('plans/create/', views.plan_create, name='plan_create'),
    path('plans/<int:pk>/edit/', views.plan_edit, name='plan_edit'),
    path('revenue/', views.revenue_report, name='revenue_report'),
]
