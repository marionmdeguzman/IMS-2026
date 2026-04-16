from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.appointment_list, name='appointment_list'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar-events/', views.calendar_events, name='calendar_events'),
    path('create/', views.appointment_create, name='appointment_create'),
    path('slots/', views.get_slots, name='get_slots'),
    path('<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('<int:pk>/status/', views.appointment_update_status, name='appointment_update_status'),
]
