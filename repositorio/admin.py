from django.contrib import admin
from .models import EstudianteUPN, Trabajodegrado

admin.site.register(EstudianteUPN)
admin.site.register(Trabajodegrado)
"""
Con este código, los modelos Estudiante y TrabajoGrado estarán disponibles en la interfaz de administración de Django, 
lo que permite a los administradores del sitio gestionar estos datos (crear, editar o eliminar trabajos y estudiantes).

Uso: Facilita la administración del contenido del repositorio digital directamente desde la interfaz web del administrador.
"""


# Register your models here.