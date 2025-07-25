from django.db import models
LINEAS_INVESTIGACION = {
    "electronica": [
        "Análisis Técnica", "EduTech", "Experiencias ETIAE/MTIAE",
        "Productos – Prototipos – Tecnológicos", "Sistemas de Control", "Tecnologías Digitales"
    ],
    "diseno": [
        "Análisis Técnica", "Diseño de Prototipos", "Educación en y con tecnología",
        "Experiencias ETIAE/MTIAE", "Herramientas Digitales", "Monografías", "Propuesta Disciplinar"
    ],
    "tecnologia": [
        "Análisis Técnica", "Diseño de Prototipos", "Educación en y con tecnología",
        "Experiencias ETIAE/MTIAE", "Herramientas Digitales", "Monografías", "Propuesta Disciplinar"
    ]
}
class LineaInvestigacion(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Documento(models.Model):
    CATEGORIAS = [
        ('electronica', 'Electrónica'),
        ('diseno', 'Diseño Tecnológico'),
        ('tecnologia', 'Tecnología'),
    ]

    # Campos existentes...
    titulo = models.CharField(max_length=255, blank=True, null=True)
    autor = models.CharField(max_length=255, blank=True, null=True)
    director = models.CharField(max_length=255, blank=True, null=True)
    palabras_clave = models.CharField(max_length=255, blank=True, null=True)
    unidad_patrocinante = models.CharField(max_length=255, blank=True, null=True)
    publicacion = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    metodologia = models.TextField(blank=True, null=True)
    contenidos = models.TextField(blank=True, null=True)
    conclusiones = models.TextField(blank=True, null=True)
    fuentes = models.TextField(blank=True, null=True)
    enlace = models.URLField(blank=True, null=True)   
    archivo = models.FileField(upload_to='documentos/', max_length=255, blank=True, null=True)
    enlace_archivo = models.URLField("Enlace al PDF (Cloudinary)", blank=True, null=True)
    año = models.CharField(max_length=4, blank=True, null=True)
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default='electronica')

    # NUEVO: relación muchos a muchos
    lineas_investigacion = models.ManyToManyField(LineaInvestigacion, blank=True)

    def __str__(self):
        return self.titulo if self.titulo else "Documento sin título"



# Este modelo representa un trabajo de grado presentado por uno o varios estudiantes 
