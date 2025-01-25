from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from MiApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('MiApp.urls')),  # Asegúrate de que esto esté correctamente configurado
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
