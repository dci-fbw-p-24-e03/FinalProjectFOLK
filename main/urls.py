from django.urls import path
from .views import *

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", home_view, name="home_view"),
    path('contact/', contact_us, name='contact_us'),
    path('contact/success/', contact_success, name='contact_success'),

]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )