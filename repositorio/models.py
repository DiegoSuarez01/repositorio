from django.db import models

class EstudianteUPN (models.Model):
    nombre=models.CharField(max_length=100)
    apellido=models.CharField(max_length=100)
    correo=models.EmailField()
"""
 Este modelo representa a los estudiantes que han presentado trabajos de grado. Cada estudiante tiene:

nombre: Un campo de texto que almacena el nombre del estudiante.
apellido: Un campo de texto que almacena el apellido del estudiante.
correo: Un campo de tipo EmailField que almacena la dirección de correo electrónico del estudiante, 
        lo cual es útil para contactar o identificar al estudiante.
"""
class Trabajodegrado(models.Model):
    titulo = models.CharField(max_length=200)
    EstudianteUPN = models.ForeignKey(EstudianteUPN, on_delete=models.CASCADE)
    resumen=models.TextField()
    archivo = models.FileField(upload_to='trabajos/')
    fecha_publicacion = models.DateField()
    palabras_clave = models.CharField(max_length=200)
    tutor = models.CharField(max_length=100)
    def __str__(self):
        return self.titulo



"""
 Este modelo representa un trabajo de grado presentado por un estudiante y tiene los siguientes campos:

titulo: Un campo de texto que almacena el título del trabajo de grado.
estudiante: Un campo de tipo ForeignKey que establece una relación con el modelo EstudianteUPN, 
            indicando quién es el autor del trabajo. La opción on_delete=models.CASCADE asegura 
            que si se elimina un estudiante, también se eliminarán sus trabajos asociados.
resumen: Un campo de texto largo (TextField) que almacena el resumen del trabajo de grado.
archivo: Un campo de tipo FileField que permite la carga de archivos (por ejemplo, documentos PDF o Word) 
        asociados al trabajo de grado. El archivo se almacenará en la carpeta trabajos/ dentro del directorio 
        definido para archivos subidos.
fecha_publicacion: Un campo de tipo DateField que almacena la fecha en la que el trabajo fue publicado o presentado.
palabras_clave: Un campo de texto que permite incluir términos o palabras clave para facilitar la búsqueda y 
                categorización de los trabajos.
tutor: Un campo de texto que almacena el nombre del tutor o director del trabajo de grado.
"""

    
    
    

# Create your models here.
