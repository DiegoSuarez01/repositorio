"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to rlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views

urlpatterns = [
    path('trabajos/', views.lista_trabajos, name='lista_trabajos'),
]


"""
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

Esta configuración añade rutas para que, en modo de desarrollo (DEBUG=True), los archivos en MEDIA_ROOT 
sean accesibles desde el navegador mediante MEDIA_URL.
Esto es especialmente útil para servir archivos durante el desarrollo sin necesidad de configurar u
n servidor web externo.
Uso: Permite que los usuarios accedan a los archivos subidos, como los trabajos de grado en formato PDF, 
    directamente desde el servidor de desarrollo.
"""