from django.urls import path
from . import public_views

app_name = 'bookings_public'

urlpatterns = [
    path('', public_views.public_booking, name='public_booking'),
    path('confirm/<str:token>/', public_views.booking_confirm, name='confirm'),
    path('slots/', public_views.public_slots, name='public_slots'),
]
