from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from repositorio.views import (
    DocumentoCreateView, DocumentoEView, DocumentoDView, DocumentoTView,
    DocumentoDetailView, DocumentoEliminarView, login_view,
    busqueda_ajax, principal, DocumentoUpdateView, resultados_busqueda_view
)
from repositorio import views

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', principal, name='principal'),
    path('admin/', admin.site.urls),
    path('crear/', DocumentoCreateView.as_view(), name='documento_crear'),
    path('documentosE/', DocumentoEView.as_view(), name='lic_electronica'),
    path('documentosD/', DocumentoDView.as_view(), name='lic_diseno'),
    path('documentosT/', DocumentoTView.as_view(), name='lic_tecnologia'),
    path('documento/detalle/<int:pk>/', DocumentoDetailView.as_view(), name='documento_detalle'),
    # LOGIN
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='principal'), name='logout'),
    
    path('documento/<int:pk>/eliminar/', DocumentoEliminarView.as_view(), name='documento_confirmar_eliminar'),
    path('busqueda/', TemplateView.as_view(template_name="buscar_documentos.html"), name="buscar_documento"),
    path('busqueda/ajax/', busqueda_ajax, name='documento_busqueda_ajax'),
    path('busqueda-ajax/', views.busqueda_ajax, name='busqueda_ajax'),
    path('resultados/', resultados_busqueda_view, name='resultados_busqueda'),
    path('documento/<int:pk>/editar/', DocumentoUpdateView.as_view(), name='documento_editar'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""
urlpatterns = [
    path('admin/', admin.site.urls),  
    path('subir/', subir_trabajo, name='subir_trabajo'),    
    path('', lista_trabajos, name='lista_trabajos'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""



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