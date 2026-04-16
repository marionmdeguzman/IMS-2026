from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', RedirectView.as_view(url='/admin-portal/login/', permanent=False)),
    path('django-admin/', admin.site.urls),

    # JWT API
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Auth (client-facing)
    path('', include('accounts.urls')),

    # Admin portal
    path('admin-portal/', include('dashboard.urls')),
    path('admin-portal/members/', include('members.urls')),
    path('admin-portal/bookings/', include('bookings.urls')),
    path('admin-portal/billing/', include('billing.urls')),
    path('admin-portal/notifications/', include('notifications.urls')),
    path('admin-portal/services/', include('services.urls')),

    # Public booking
    path('book/', include('bookings.public_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
