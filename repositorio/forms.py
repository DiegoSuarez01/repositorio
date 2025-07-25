from django import forms
from .models import Documento, LineaInvestigacion

LINEAS_INVESTIGACION = {
    "electronica": [
        "Análisis Técnica", "EduTech", "Experiencias ETIAE/MTIAE",
        "Productos – Prototipos – Tecnológicos", "Sistemas de Control", "Tecnologías Digitales"
    ],
    "diseno": [
        "Análisis_Técnica", "Diseño de Prototipos", "Educación en y con tecnología",
        "Experiencias ETIAE/MTIAE", "Herramientas Digitales", "Monografías", "Propuesta Disciplinar"
    ],
    "tecnologia": [
        "Análisis Técnica", "Diseño de Prototipos", "Educación en y con tecnología",
        "Experiencias ETIAE/MTIAE", "Herramientas Digitales", "Monografías", "Propuesta Disciplinar"
    ],
}

class DocumentoForm(forms.ModelForm):
    lineas_investigacion = forms.ModelMultipleChoiceField(
        queryset=LineaInvestigacion.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    class Meta:
        model = Documento
        fields = ['archivo', 'enlace_archivo', 'titulo', 'autor','publicacion', 'unidad_patrocinante' ,'palabras_clave', 'metodologia', 
                  'descripcion', 'fuentes', 'conclusiones','contenidos', 'director', 'enlace', 'categoria','lineas_investigacion']
        
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título (opcional)'}),
            'autor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Autor (opcional)'}),
            'publicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Publicación (opcional)'}),
            'unidad_patrocinante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unidad patrocinante (opcional)'}),
            'palabras_clave': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Palabras clave (opcional)'}),
            'metodologia': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Metodología (opcional)'}),
            'contenidos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Contenidos (opcional)'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción (opcional)'}),
            'fuentes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Fuentes (opcional)'}),
            'conclusiones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Conclusiones (opcional)'}),
            'director': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Director (opcional)'}),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'enlace_archivo' : forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'enlace': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enlace (opcional)'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'lineas_investigacion': forms.CheckboxSelectMultiple(),   
        }
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer todos los campos opcionales excepto archivo
        for field in self.fields:
            if field != 'archivo':
                self.fields[field].required = False
    
        # Filtrar las líneas de investigación según la categoría
        categoria_inicial = self.data.get('categoria') or self.initial.get('categoria')
        if categoria_inicial in LINEAS_INVESTIGACION:
            lineas = LineaInvestigacion.objects.filter(nombre__in=LINEAS_INVESTIGACION[categoria_inicial])
            self.fields['lineas_investigacion'].queryset = lineas
        else:
            self.fields['lineas_investigacion'].queryset = LineaInvestigacion.objects.none()
