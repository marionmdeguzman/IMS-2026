from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('dashboard/', views.overview, name='overview'),
    path('reports/no-shows/', views.no_show_report, name='no_show_report'),
]
