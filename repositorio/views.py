from django.conf import settings
from django.shortcuts import render, redirect
import fitz  # PyMuPDF
from django.views.generic.edit import UpdateView
from django.views.generic import CreateView, ListView, DetailView, DeleteView, View
from .models import Documento
from .forms import DocumentoForm
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.db.models import Q
import re
from collections import Counter
from repositorio.models import LineaInvestigacion
from django.utils.safestring import mark_safe
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            return redirect('principal')  # Usa el nombre de tu URL
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


import unicodedata

def normalizar(texto):
    """
    Convierte el texto a minúsculas y elimina acentos (tildes).
    """
    if not texto:
        return ""
    texto = texto.lower()
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def principal(request):
    return render(request, 'principal.html')

def busqueda_ajax(request):
    query = request.GET.get('q', '')
    resultados = []

    if query:
        query_normalizado = normalizar(query)
        documentos = Documento.objects.all()

        for doc in documentos:
            if query_normalizado in normalizar(doc.titulo):
                resultados.append({
                    'id': doc.id,
                    'titulo': doc.titulo,
                    'autor' : doc.autor,
                    'director' : doc.director,
                    'metodologia' : doc.metodologia,
                })
            if len(resultados) >= 10:
                break

    return JsonResponse({'resultados': resultados})



def buscar_documentos(request):
    query = request.GET.get('q', '')
    resultados = []

    if query:
        query_normalizado = normalizar(query)
        documentos = Documento.objects.all()

        for doc in documentos:
            if (
                query_normalizado in normalizar(doc.titulo) or
                query_normalizado in normalizar(doc.autor or '') or
                query_normalizado in normalizar(doc.categoria or '')
            ):
                resultados.append(doc)

    return render(request, 'busqueda_documentos.html', {
        'resultados': resultados,
        'query': query
    })

def obtener_años_disponibles():
    publicaciones = Documento.objects.values_list('publicacion', flat=True)
    años = set()

    for pub in publicaciones:
        if pub:
            año = detectar_año(pub)
            if año:
                años.add(año)
    
    return sorted(años)

def resultados_busqueda_view(request):
    query = request.GET.get('q', '').strip()
    categoria_filtro = request.GET.get('categoria', '')
    linea_filtro = request.GET.get('linea', '')
    año_filtro = request.GET.get('año', '')

    # 🔹 Obtener todos los años disponibles (antes de filtrar)
    años = Documento.objects.exclude(año__isnull=True).values_list('año', flat=True).distinct().order_by('-año')

    # 🔹 Obtener todos los documentos (sin filtros aún)
    documentos = Documento.objects.all()

    if query:
        documentos = [doc for doc in documentos if normalizar(query) in normalizar(
            ' '.join([
                doc.titulo or '',
                doc.autor or '',
                doc.director or '',
                doc.metodologia or '',
                doc.categoria or '',
                ' '.join([li.nombre for li in doc.lineas_investigacion.all()])
            ])
        )]

    if categoria_filtro:
        documentos = [doc for doc in documentos if doc.categoria == categoria_filtro]
    
    if linea_filtro:
        documentos = [doc for doc in documentos if doc.lineas_investigacion.filter(nombre=linea_filtro).exists()]
    
    if año_filtro:
        documentos = [doc for doc in documentos if str(doc.año) == año_filtro]

    categorias = Documento.objects.values_list('categoria', flat=True).distinct()
    lineas = LineaInvestigacion.objects.values_list('nombre', flat=True).distinct()

    return render(request, 'resultados_busqueda.html', {
        'query': query,
        'resultados': documentos,
        'categorias': categorias,
        'lineas': lineas,
        'año_filtro': año_filtro,
        'años': años,  # <- Esta lista sí se va a mostrar al cargar la página
    })

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
def asegurar_lineas_investigacion():
    from .models import LineaInvestigacion
    for categoria, nombres in LINEAS_INVESTIGACION.items():
        for nombre in nombres:
            LineaInvestigacion.objects.get_or_create(nombre=nombre)

class DocumentoUpdateView(UpdateView):
    asegurar_lineas_investigacion()
    model = Documento
    form_class = DocumentoForm
    template_name = 'documento_editar.html'
    login_url = 'login'

    def get_success_url(self):
        return reverse_lazy('documento_detalle', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Generar lista con id y nombre para cada línea
        linea_data = {}
        for categoria, nombres in LINEAS_INVESTIGACION.items():
            lineas = LineaInvestigacion.objects.filter(nombre__in=nombres)
            linea_data[categoria] = [
                {"id": linea.id, "nombre": linea.nombre} for linea in lineas
            ]
        
        context["linea_data"] = {
            k: mark_safe(json.dumps(v)) for k, v in linea_data.items()
        }
    
        return context

class DocumentoEliminarView(DeleteView):
    login_url = 'login'
    model = Documento
    template_name = 'documento_confirmar_eliminar.html' 
    
    def get_success_url(self):
        documento = self.get_object()
        return reverse_lazy(f"lic_{documento.categoria.lower()}") if documento.categoria else reverse_lazy('principal')

import requests
import tempfile
class DocumentoCreateView(CreateView):
    login_url = 'login'
    model = Documento
    form_class = DocumentoForm
    template_name = 'documento_form.html'

    def get_success_url(self):
        if self.object:
            if self.object.categoria == "electronica":
                return reverse_lazy('lic_electronica')
            elif self.object.categoria == "diseno":
                return reverse_lazy('lic_diseno')
            elif self.object.categoria == "tecnologia":
                return reverse_lazy('lic_tecnologia')
        return reverse_lazy('principal')
    
    def get_context_data(self, **kwargs):
        asegurar_lineas_investigacion()
        context = super().get_context_data(**kwargs)
        
        # Generar lista con id y nombre para cada línea
        linea_data = {}
        for categoria, nombres in LINEAS_INVESTIGACION.items():
            lineas = LineaInvestigacion.objects.filter(nombre__in=nombres)
            linea_data[categoria] = [
                {"id": linea.id, "nombre": linea.nombre} for linea in lineas
            ]
        
        context["linea_data"] = {
            k: mark_safe(json.dumps(v)) for k, v in linea_data.items()
        }
    
        return context

    def form_valid(self, form):
        documento = form.save(commit=False)
    
        archivo_pdf = None  # Ruta del PDF final (local o descargado)
    
        # 🧩 Si hay archivo subido localmente
        if documento.archivo:
            archivo_pdf = documento.archivo.path
    
        # 🌐 Si no hay archivo subido pero sí hay enlace
        elif documento.enlace:
            try:
                response = requests.get(documento.enlace)
                if response.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(response.content)
                        archivo_pdf = tmp_file.name
                else:
                    print("❌ Error descargando el PDF desde el enlace.")
            except Exception as e:
                print("❌ Error en la descarga:", e)
    
        # 🔍 Si se obtuvo un archivo PDF de alguna forma
        if archivo_pdf:
            texto, num_paginas, ruta_pdf = extraer_texto(archivo_pdf)
            info_extraida = procesar_documento(archivo_pdf)
            if info_extraida is None:
                info_extraida = {}
    
            info_general = info_extraida.get("Información General", {})
            documento.año = detectar_año(texto)
            documento.titulo = info_general.get("TÍTULO", "No disponible")
            documento.autor = info_general.get("AUTOR(ES)", "No disponible")
            documento.director = info_general.get("DIRECTOR", "No registrado")
            documento.palabras_clave = info_general.get("PALABRAS CLAVE", "No disponibles")
            documento.unidad_patrocinante = info_general.get("UNIDAD PATROCINANTE", "No disponible")
            documento.publicacion = info_general.get("PUBLICACIÓN", "No disponible")
            documento.descripcion = info_extraida.get("Descripción", "No disponible")
            documento.metodologia = info_extraida.get("Metodología", "No disponible")
            documento.contenidos = info_extraida.get("Contenidos", "No disponible")
            documento.conclusiones = info_extraida.get("Conclusiones", "No disponible")
    
            fuentes = info_extraida.get("Fuentes", "No disponible")
            documento.fuentes = "\n".join(fuentes) if isinstance(fuentes, list) else fuentes
    
        # 🎯 Guardar categoría y líneas
        lineas_ids = self.request.POST.getlist("lineas_investigacion")
        documento.categoria = form.cleaned_data['categoria']
        documento.save()
        documento.lineas_investigacion.set(lineas_ids)
    
        return redirect(self.get_success_url())
    
# Vistas de las licenciaturas
class DocumentoEView(ListView):
    model = Documento
    template_name = 'lic_electronica.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        return Documento.objects.filter(categoria__iexact='electronica')

class DocumentoDView(ListView):
    model = Documento
    template_name = 'lic_diseno.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        return Documento.objects.filter(categoria__iexact='diseno')

class DocumentoTView(ListView):
    model = Documento
    template_name = 'lic_tecnologia.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        return Documento.objects.filter(categoria__iexact='tecnologia')

class DocumentoDetailView(DetailView):
    model = Documento
    template_name = 'documento_detalle.html'

# ----------- EXTRACCIÓN DE INFORMACIÓN -----------

def extraer_texto(pdf_path):
    # Abrir el archivo PDF
    doc = fitz.open(pdf_path)
    num_paginas = len(doc)

    # Extraer el texto de cada página
    texto = ""
    for pagina in doc:
        texto += pagina.get_text()

    # Devolver el texto y el número de páginas
    return texto, num_paginas, pdf_path

def eliminar_tabla_contenido(doc):
    """
    Elimina páginas desde que se detecta 'Tabla de contenido' o similar,
    y continúa eliminando mientras más del 30% de las líneas contengan números o numeración tipo índice.
    """
    texto_total = ""
    eliminar = False
    saltando = False

    for i, pagina in enumerate(doc):
        texto_pagina = pagina.get_text()
        lineas = texto_pagina.splitlines()

        # 🔹 Paso 1: detectar inicio del índice
        if not eliminar:
            if re.search(r"(?i)(TABLA\s+DE\s+CONTENIDO|Índice\s+de\s+contenido|Contenido|Tabla\s+de\s+contenidos)", texto_pagina):
                eliminar = True
                saltando = True
                print(f"📌 Tabla de contenido detectada en página {i+1}, analizando siguientes páginas...")
                continue

        # 🔹 Paso 2: si estamos eliminando, revisar si esta página es índice (basado en numeraciones)
        if eliminar and saltando:
            total = len(lineas)
            if total == 0:
                continue

            numeradas = sum(
                1 for linea in lineas
                if re.match(r"\s*\d+(\.\d+)*\s+.+", linea)  # Ej: "1. Introducción", "3.4 Marco teórico"
            )

            porcentaje = numeradas / total
            if porcentaje >= 0.3:
                print(f"🧹 Página {i+1} eliminada (índice con {porcentaje:.0%} de líneas numeradas)")
                continue  # Saltamos esta página
            else:
                saltando = False  # Ya no estamos en tabla de contenido

        # 🔹 Paso 3: conservar el resto de las páginas
        texto_total += texto_pagina

    return texto_total

# Esta función intenta extraer el título de un texto (por ejemplo, el de un PDF convertido)
# Ignora encabezados típicos y se detiene si encuentra el nombre del autor
def obtener_titulo(texto, nombre_autor=None):
    """
    Extrae el título tomando máximo 10 líneas desde el primer contenido útil
    e ignorando encabezados institucionales. Detiene la extracción si encuentra el nombre del autor.
    """
    # Divide el texto completo en líneas
    lineas = texto.splitlines() 
    # Lista donde se irán guardando las líneas del posible título
    titulo_lineas = []
    # Contador para detectar si hay dos líneas vacías seguidas (lo cual indica posible final del título)
    lineas_vacias_seguidas = 0
    # Bandera para saber cuándo empezar a considerar líneas como parte del título
    ha_empezado = False
    # Límite máximo de líneas a considerar como título
    max_lineas = 10    # Si se proporcionó el nombre del autor, se normaliza para compararlo fácilmente
    autor_normalizado = normalizar(nombre_autor) if nombre_autor else None
    # Recorremos todas las líneas del texto
    for linea in lineas:
        # Quitamos espacios al inicio y al final
        limpia = linea.strip()
        # Si la línea tiene palabras institucionales comunes, la ignoramos
        if any(pal in limpia.upper() for pal in [
            "UNIVERSIDAD PEDAGÓGICA NACIONAL", "FACULTAD", "DEPARTAMENTO", "LICENCIATURA", "PÁGINA"
        ]):
            continue
        # Si aún no hemos empezado y la línea está vacía o solo tiene un número o dice "página", la ignoramos
        if not ha_empezado and (not limpia or limpia.isdigit() or re.search(r'\|\s*P\s*a\s*g\s*e', limpia, re.IGNORECASE)):
            continue
        # Marcamos que ya empezamos a encontrar contenido útil
        ha_empezado = True
        # Si encontramos el nombre del autor, detenemos la extracción
        if autor_normalizado and autor_normalizado in normalizar(limpia):
            break
        # Si la línea está vacía, aumentamos el contador de vacías seguidas
        if not limpia:
            lineas_vacias_seguidas += 1
            # Si hay 2 vacías seguidas, probablemente se acabó el bloque del título
            if lineas_vacias_seguidas >= 2:
                break
            continue
        else:
            # Si no está vacía, reiniciamos el contador
            lineas_vacias_seguidas = 0
        # Si la línea tiene solo un número o es una marca de página, la ignoramos
        if limpia.isdigit() or re.search(r'\|\s*P\s*a\s*g\s*e', limpia, re.IGNORECASE):
            continue
        # Agregamos esta línea como parte del posible título
        titulo_lineas.append(limpia)
        # Si ya tenemos suficientes líneas (10), paramos
        if len(titulo_lineas) >= max_lineas:
            break
    # Unimos todas las líneas del título en una sola cadena
    titulo = ' '.join(titulo_lineas)  
    # Eliminamos espacios múltiples entre palabras
    titulo = re.sub(r'\s{2,}', ' ', titulo).strip()
    # Si se encontró un título, lo devolvemos; si no, devolvemos None
    return titulo if titulo else None

#lista de apellidos 
APELLIDOS_COMUNES = [
    "Abella", "Acevedo", "Aldana", "Ardila", "Ariza", "Arias", "Acosta", "Barahona", "Barrera", "Beltrán", "Benítez", "Bohórquez","Bossa", "Bustamante","Buitrago",
    "Cano", "Cárdenas", "Cely", "Casallas", "Castillo", "Castro", "Chacón", "Cifuentes", "Cordero", "Cortés","Cocunubo", "Corredor", "Díaz", "Duarte", "Estupiñán", 
    "Escobar", "Fayad", "Florez","García", "Garcia", "Gómez", "González", "Guataquí", "Guerrero", "Gutiérrez", "Hernández", "Jiménez", "Leiva", "Lopera", "López",
    "Lozano", "Mahecha", "Maldonado", "Malagón", "Marroquín", "Marín", "Martin", "Martínez", "Medina", "Merchan", "Merchán", "Montero", "Monsalve", "More", "Moreno", 
    "Murillo", "Ordoñez","Oviedo", "Otálora", "Patiño", "Peña", "Perdomo", "Perez", "Pereira", "Pilar", "Pinzón", "Poveda", "Prieto", "Quintero", "Ramírez", "Reyes", 
    "Rivera", "Roberto", "Rodríguez", "Rojas","Romero", "Rua", "Rincón", "Rueda", "Salazar", "Sánchez","Sandoval", "Sarmiento","Sanabria", "Suarez", "Suárez", "Torres",
    "Téllez", "Terreros", "Urueña", "Valero", "Vargas", "Vega", "Velandia", "Velásquez","Valencia","Zamora"
]


def detectar_nombres_por_apellidos(texto, apellidos_comunes):
    etiquetas = [
        "autor(es):", "autor:", "presentado por:", "asesor:", "asesora:",
        "asesor", "asesora", "director:", "tutor:", "elaborado por:",
        "docente:", "nombre:","directora:", "dirigido por:", "profesor:"
    ]
    palabras_prohibidas = [
        "cedid", "institucion", "institución", "institución educativa", "colegio",
        "tecnología en"
    ]
    nombres_detectados = []
    linea_anterior = ""

    for linea in texto.splitlines():
        linea_original = linea.strip()

        # Si la línea anterior contiene palabras prohibidas, no procesar esta
        if any(p in linea_anterior.lower() for p in palabras_prohibidas):
            linea_anterior = linea  # actualizar igual
            continue
        # Si esta línea contiene palabras prohibidas, también se descarta
        if any(p in linea_original.lower() for p in palabras_prohibidas):
            linea_anterior = linea  # actualizar
            continue
        # Ahora sí: limpiar y procesar
        linea_limpia = linea_original.lower()
        for etiqueta in etiquetas:
            linea_limpia = linea_limpia.replace(etiqueta, "")
        # Separar si hay múltiples nombres
        posibles_nombres = re.split(r"/|,| y ", linea_limpia)
        for nombre in posibles_nombres:
            nombre_candidato = " ".join(p.capitalize() for p in nombre.strip().split())
            if (
                any(ap.lower() in nombre_candidato.lower() for ap in apellidos_comunes)
                and len(nombre_candidato.split()) <= 5
                and not re.search(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", nombre_candidato)
            ):
                if nombre_candidato not in nombres_detectados:
                    nombres_detectados.append(nombre_candidato)
        linea_anterior = linea  # actualizar para la próxima vuelta

    return nombres_detectados

def es_nombre_valido(texto):
    texto = texto.lower()
    palabras_prohibidas = [
        "gracias", "agradezco", "agradecimiento", "felicito", "mira", "dedico",  
        "abuelo", "abuela", "mamá", "maestro", "maestra",                        
        "padres", "madre", "padre", "cuidados", "esposa", "esposo",              
        "profesor", "familia", "cedid", "institucion", "institución", 
        "institución educativa", "colegio"                                                    
    ]
    return not any(p in texto for p in palabras_prohibidas)

def detectar_año(texto):
    """
    Busca un año que comience con '20' (ej: 2015, 2020, 2023) en el texto.
    Retorna el primer año encontrado o None si no hay coincidencias.
    """
    coincidencias = re.findall(r"\b(20\d{2})\b", texto)
    return coincidencias[0] if coincidencias else None

def extraer_info_sin_formato_rae(texto, num_paginas, ruta_pdf):
    """Extrae información clave si el documento no tiene formato RAE."""
    #Primeras paginas
    doc = fitz.open(ruta_pdf)
    primeras_paginas = ""
    paginas_leidas = 0
    i = 0

    while paginas_leidas < 2 and i < len(doc):
        contenido = doc[i].get_text().strip()
        if contenido:  # Si no está vacía
            primeras_paginas += contenido + "\n"
            paginas_leidas += 1
        i += 1

    info = {
        "TÍTULO": "No encontrado",
        "AUTOR(ES)": "No encontrado",
        "DIRECTOR": "No encontrado",
        "PALABRAS CLAVE": "No disponibles",
        "UNIDAD PATROCINANTE": "Universidad Pedagógica Nacional",
        "PUBLICACIÓN": "No disponible",
        
    }
    # Si no se encontró título, usar el nombre del archivo como fallback
    info["TÍTULO"] = obtener_titulo(texto)
    # Buscar AUTOR
    if info["AUTOR(ES)"] == "No encontrado":
        posibles_nombres = detectar_nombres_por_apellidos(primeras_paginas, APELLIDOS_COMUNES)
    
        vistos = set()
        nombres_unicos = []
    
        for nombre in posibles_nombres:
            if nombre not in vistos and es_nombre_valido(nombre):  # <- asumes que ya tienes esta función
                vistos.add(nombre)
                nombres_unicos.append(nombre)
            if len(nombres_unicos) == 3:
                break
    
        if nombres_unicos:
            if len(nombres_unicos) == 1:
                info["AUTOR(ES)"] = nombres_unicos[0]
            elif len(nombres_unicos) == 2:
                info["AUTOR(ES)"] = nombres_unicos[0]
                info["DIRECTOR"] = nombres_unicos[1]
            elif len(nombres_unicos) == 3:
                info["AUTOR(ES)"] = f"{nombres_unicos[0]} /\n {nombres_unicos[1]}"
                info["DIRECTOR"] = nombres_unicos[2]

    nombre_para_titulo = nombres_unicos[0] if nombres_unicos else None
    info["TÍTULO"] = obtener_titulo(texto, nombre_para_titulo)
    # Buscar FECHA
    año = detectar_año(primeras_paginas)
    if año:
        info["PUBLICACIÓN"] = f"Bogotá. Universidad Pedagógica Nacional, {año}. {num_paginas}p."
    else:
        info["PUBLICACIÓN"] = f"Bogotá. Universidad Pedagógica Nacional. {num_paginas}p."

    return info

def extraer_descripcion(texto, cierres):
    contenido_dec = ""
    for cierre in cierres:
        matches = list(re.finditer(
            rf"\s*(\d+\s*\.\s*)?(Introducci[oó]n|INTRODUCCI[OÓ]N|Introducci[oó]n\s*y\s*aspectos\s0*generales|CAP[IÌ]TULO I|Resumen|RESUMEN|Resumen\.|Resumen\s*Ejecutivo)\s*\n([\s\S]*?){cierre}",
            texto,  
            re.MULTILINE | re.DOTALL
        ))

        for match in matches:
            posible_contenido = match.group(3).strip()
            lineas = posible_contenido.splitlines()

            if lineas and (
                re.match(r"^\s*\d+\s*$", lineas[0]) and int(lineas[0]) >= 2
                or lineas[0].lower().startswith("xvii")
            ):
                continue

            lineas_numeradas = sum(
                1 for l in lineas if re.match(r"^\s*(\d+\.){1,3}\s*", l)
            )
            if lineas_numeradas / max(1, len(lineas)) > 0.4:
                continue

            if sum(1 for c in posible_contenido if c == '.') / max(1, len(posible_contenido)) > 0.2:
                continue

            contenido_dec = posible_contenido
            break

    if contenido_dec:
        parrafos = re.split(r'\n+\s*\n+', contenido_dec)
        parrafos_largos = [
            re.sub(r'\s+', ' ', p).strip()
            for p in parrafos
            if len(p.split()) > 50
        ]

        if len(parrafos_largos) >= 2:
            return '\n\n'.join(parrafos_largos[:2])
        elif parrafos_largos:
            return parrafos_largos[0]
        else:
            return re.sub(r'\s+', ' ', contenido_dec).strip()

    return "No encontrado"

def extraer_fuentes(texto):
    matches_f = re.finditer(
        r"\s*(\d+[\.\s]*)?"
        r"(Referencias|REFERENCIAS|Bibliograf[ií]a|BIBLIOGRAFÍA|Bibliogr[aáÁ]ficos|Referencias\s*bibliográficas|Referencias\s*Bibliográficas|Referencias\s*Bibliográficas\s*:|REFERENCIAS\s*BIBLIOGRÁFICAS|BIBLIOGRÁFICOS)"
        r"\s*\n+(?!\s*\d\.\d)"
        r"([\s\S]*?)(?=(Anexo|Anexos|ANEXOS|INDICE|Listas|Ap[eéÉ]ndice\sA|Tabla\s*de\s*Imágenes|Plan\s*de\s*trabajo\s*semanal|Contenido|\Z)\s*$)",
        texto,
        re.MULTILINE | re.DOTALL
    )

    fuente_final = ""

    for match in matches_f:
        posible_fuente = match.group(3).strip()

        # Verifica si contiene al menos una cita con año (ej. (2020))
        if not re.search(r'\(\d{4}', posible_fuente):
            continue

        # Limpieza línea por línea, conservando contenido útil
        lineas_fuente = [
            re.sub(r'\s+', ' ', linea).strip()
            for linea in posible_fuente.splitlines()
            if len(linea.strip()) > 10
        ]

        if lineas_fuente:
            texto_fuente = '\n'.join(lineas_fuente).strip()

            # Limitar a 1000 palabras
            palabras = texto_fuente.split()
            if len(palabras) > 1000:
                palabras = palabras[:1000]
            fuente_final = ' '.join(palabras)
            return fuente_final

    return ""


# Función para extraer las palabras más frecuentes ignorando conectores
def extraer_palabras_clave(titulo, descripcion, metodologia, cantidad=7):
    # Unificar todo el contenido en un solo bloque de texto
    texto = f"{titulo} {descripcion} {metodologia}".lower()

    #  Diccionario de palabras que queremos excluir
    stopwords = {
        'la', 'el', 'los', 'las', 'de', 'del', 'en', 'y', 'a', 'que', 'un', 'una',
        'es', 'se', 'por', 'para', 'con', 'como', 'su', 'al', 'lo', 'sus', 'le',
        'o', 'más', 'pero', 'no', 'ni', 'porque', 'cuando', 'donde', 'sobre', 'ya',
        'cual', 'cuál', 'qué', 'puede', 'mismo', 'cada', 'otros', 'otras', 'parte',
        'tiene', 'ser', 'estar', 'siendo', 'desde', 'trabajo', 'estudio', 'investigación',
        'proceso', 'desarrollo', 'proyecto', 'educación', 'educativa', 'tema', 'aspectos',
        'forma', 'caso', 'nuevo', 'nueva', 'análisis', 'información', 'grado',
        'estrategia', 'tecnologías', 'comunicación', 'tic', 'nueva', 'décimo',
        'undécimo', 'primero', 'segundo', 'tercero', 'cuarto', 'quinto', 'sexto',
        'séptimo', 'octavo', 'noveno', 'once', 'doce', 'básico', 'media', 'mayor',
        'menor', 'actual', 'primaria', 'secundaria', 'niveles', 'atención',
        'colegio', 'escolar', 'universidad', 'institución', 'estancia', 'educativo',
        'académico', 'sede', 'docente', 'docentes', 'estudiante', 'estudiantes',
        'profesor', 'profesores', 'ltda', 's.a.', 'cia', 'compañía', 'sociedad',
        'empresa', 'ejemplo', 'uso', 'realización', 'finalidad', 'propósito',
        'objetivo', 'contexto', 'modo', 'manera', 'medio', 'nivel', 'ámbito',
        'campo', 'forma', 'mediada', 'moderar', 'función', 'propuesta', 'presente',
        'nace', 'pedagógica', 'fin', 'nacional', 'cargas', 'estresoras', 'producen',
        'elementos', 'considerar', 'informe', 'club', 'social', 'proyección',
        'informativa', 'consolidar', 'escenario', 'teniendo', 'práctico', 'formación'
        'está', 'proyectado', 'actividades', 'desarrollen', 'habilidades' ,'ejemplos',
        'algunas','etapa','personas','leal','esta','personas','grupo','siguiente',
        'brindar','necesidad','coherencia','través','cuales','implican','permiten',
        'utilizado','combinación','área','este', 'diferentes','asignatura','dinámica',
        'basado', 'básica','respuestas','fundamentación', 'título','estructuración',
        'formación','productivo','vereda','actividad','encontrado','hemos','muchas',
        'fase','documento','busca','buscar','unidad','analogías','figura','partir',
        'recorrido','ello','realizó','tipo','plantear','licenciatura','cabo','encuentran',
        'descritas','abordamos','específico','taller','aplicadas','revisión','muestra',
        'roles','participación','está','genere'
    }

    #  Extraer solo palabras de 3 o más letras
    palabras = re.findall(r'\b[a-záéíóúñ]{4,}\b', texto)
    # Filtrar por palabras no incluidas en stopwords
    palabras_filtradas = [p for p in palabras if p not in stopwords]
    # Contar frecuencia
    contador = Counter(palabras_filtradas)

    # Obtener las más comunes
    palabras_clave = [palabra for palabra, _ in contador.most_common(cantidad)]

    return ', '.join(palabras_clave) if palabras_clave else "No disponibles"

def extraer_contenidos(texto):
    """
    Extrae la sección de Contenidos a partir de un encabezado común (índice, tabla de contenido, etc.)
    y devuelve una lista numerada limpia.
    """
    import re
    # Buscar encabezado entre múltiples variantes
    encabezado_patron = re.compile(
        r'\b(Tabla\s*de\s*contenido|Índice\s*de\s*contenido|Tabla\s+de\s+Contenidos|Contenido|ÍNDICE|TABLA\s*DE\s*CONTENIDO)\b',
        re.IGNORECASE
    )
    match = encabezado_patron.search(texto)
    if not match:
        return "No encontrado (no se encontró encabezado de contenido)"

    # Obtener texto desde el final del encabezado
    inicio = match.end()
    texto_restante = texto[inicio:]

    # Separar en líneas no vacías
    lineas = texto_restante.splitlines()
    lineas_utiles = [l.strip() for l in lineas if l.strip()]

    # Tomar las primeras 40 líneas útiles
    posibles_contenidos = lineas_utiles[:40]

    # Limpiar y filtrar líneas
    elementos = []
    for linea in posibles_contenidos:
        linea = re.sub(r'[\.·•…\-_]{3,}', '', linea)  # quitar puntos suspensivos y similares
        linea = re.sub(r'\s+', ' ', linea)  # normalizar espacios
        linea = re.sub(r'^\d+(\.\d+)*\s*', '', linea)  # quitar numeraciones tipo 1.1
        linea = linea.strip()
        if len(linea) > 2:
            elementos.append(linea)

    # Quitar duplicados manteniendo el orden
    vistos = set()
    final = []
    for e in elementos:
        clave = e.lower()
        if clave not in vistos:
            vistos.add(clave)
            final.append(e)

    if not final:
        return "No encontrado (contenido vacío tras el encabezado)"

    return "\n".join(f"{i+1}. {elem}" for i, elem in enumerate(final))

def extraer_metodologia(texto, cierres):
    candidatos = []
    for cierre in cierres:
        pattern = re.finditer(
            rf"""
            \s*
            (\d+\s*\.\s*)?[\s\n]*
            (
                Metodolog[íi]a\.? |
                METODOLOG[IÍ]A |
                Diseño\s[Mm]etodol[oó]gico|
                Marco\smetodol[oóÓ]gico|
                Marco\sMetodol[oóÓ]gico|
                MARCO\s*METODOL[OÓ]GICO|
                Aspectos\s+Metodol[oóÓ]gicos |
                ASPECTOS\sMETODOL[OÓ]GICOS |
                Marco\s+procedimental |
                Metodolog[íiÍI]a\s+de\s+la\s+sesi[oóÓ]n |
                ejercicios\spropuestos |
                Design\sThinking |
                Diseño\s*de\s*investigación|
                Plan\sDe\sTrabajo |
                PLAN\sDE\sTRABAJO |
                Capítulo\sI\:\sContextualizaci[oó]n |
                Guías\sy\sTalleres\sSTEM |
                Metodología\spara\srecolección\sde\sdatos\sde\spérdidas |
                Enfoque\s*y\s*Metodología\s*investigación\. |
                METODOLOGÍA\s*DE\s*DISEÑO|
                Metodología\s*de\s*Desarrollo\s*de\s*software\s*RUP
            )

             \s*\n([\s\S]*?){cierre}""",
            texto,
            re.MULTILINE | re.DOTALL | re.VERBOSE
        )

        for match in pattern:
            posible_contenido = match.group(3).strip()
            lineas = posible_contenido.splitlines()

            if lineas:
                primera = lineas[0].strip()
                if re.fullmatch(r"\d+(\.\d+)*", primera):
                    continue
                if re.match(r"^\d+(\.\d+)*\s+[A-ZÁÉÍÓÚÑa-záéíóúñ]{1,10}$", primera):
                    continue

            if 10 < len(posible_contenido.split()) < 1000:
                candidatos.append(posible_contenido)

    if candidatos:
        mejor = max(candidatos, key=len)
        parrafos = re.split(r'\n\s*\n', mejor)
        parrafos_largos = [
            re.sub(r'\s+', ' ', p).strip()
            for p in parrafos
            if len(p.split()) > 40
        ]

        if len(parrafos_largos) >= 2:
            return '\n\n'.join(parrafos_largos[:2])
        elif parrafos_largos:
            return parrafos_largos[0]
        else:
            return re.sub(r'\s+', ' ', mejor).strip()

    return "No encontrado"

def extraer_conclusiones(texto, cierres):
    candidatos = []

    for cierre in cierres:
        pattern_conc = re.finditer(
            r"\s*(\d+\s*\.\s*\d*\s*)?"
            r"(Conclusiones|Conclusi[oó]n|CONCLUSIONES|CONCLUSIONES\.|CONCLUSI[OÓ]N|Conclusiones\s*y\s*recomendaciones)"
            rf"\s*[\n\.]*([\s\S]*?){cierre}",
            texto,
            re.MULTILINE | re.DOTALL
        )

        for match in pattern_conc:
            posible_contenido = match.group(3).strip()
            lineas = posible_contenido.splitlines()

            if lineas:
                primera = lineas[0].strip()
                if re.fullmatch(r"\d+(\.\d+)*", primera):
                    continue
                if re.match(r"^\d+(\.\d+)*\s+[A-ZÁÉÍÓÚÑa-záéíóúñ]{1,10}$", primera):
                    continue

            palabras = posible_contenido.split()
            indice_punto = next((i for i, p in enumerate(palabras) if '.' in p), None)
            if indice_punto is not None and indice_punto < 5:
                continue

            if 10 < len(palabras) < 1000:
                if any(
                    palabra in posible_contenido.lower().split('\n')[0]
                    for palabra in ["bibliografía", "referencias", 'recomendaciones']
                ):
                    continue
                if sum(1 for c in posible_contenido if c in ".·•") / max(1, len(posible_contenido)) > 0.3:
                    continue

                candidatos.append(posible_contenido)

    if candidatos:
        mejor = max(candidatos, key=len)
        parrafos = re.split(r'\n\s*\n', mejor)
        parrafos_largos = [
            re.sub(r'\s+', ' ', p).strip()
            for p in parrafos
            if len(p.split()) > 10
        ]

        if len(parrafos_largos) >= 2:
            return '\n\n'.join(parrafos_largos[:2])
        elif parrafos_largos:
            return parrafos_largos[0]
        else:
            return re.sub(r'\s+', ' ', mejor).strip()

    return "No encontrado"

def extraer_secciones_sin_formato_rae(texto, num_paginas, ruta_pdf):
    # Abrimos el documento
    doc = fitz.open(ruta_pdf)

    # 1. Extraer CONTENIDOS antes de eliminar la tabla
    contenidos = extraer_contenidos(texto)

    # 2. Eliminar tabla de contenido directamente desde el documento
    texto = eliminar_tabla_contenido(doc)

    # 3. Limpiar numeraciones sueltas (después de eliminar tabla)
    texto = re.sub(r'\n\s*\d+\s*\n', '', texto)

    cierres = [
        r"(?=\n\s*\n)",         # Coincidencia por doble salto de línea
        r"(?=\.\s*\n)"          # Coincidencia por punto seguido de salto de línea
    ]

    # 4. Extraer otras secciones con el texto limpio
    secciones = {
        "Información General": extraer_info_sin_formato_rae(texto, num_paginas, ruta_pdf),
        "Descripción": extraer_descripcion(texto, cierres),
        "Fuentes": extraer_fuentes(texto) or "No encontrado",
        "Contenidos": contenidos,
        "Metodología": extraer_metodologia(texto, cierres),
        "Conclusiones": extraer_conclusiones(texto, cierres)
    }

    # 5. Palabras clave inferidas con base en otras secciones
    info_general = secciones.get("Información General", {})
    titulo = info_general.get("TÍTULO", "")
    descripcion = secciones["Descripción"]
    metodologia = secciones["Metodología"]
    info_general["PALABRAS CLAVE"] = extraer_palabras_clave(titulo, descripcion, metodologia)

    return secciones


    
def extraer_palabras_c(texto):
    patron = re.compile(
        r"(?i)Palabras(?:\s+Claves?)?\s*:?\s*\n*([\s\S]{0,400})"
    )
    coincidencia = patron.search(texto)
    if not coincidencia:
        return None

    seccion = coincidencia.group(1)
    lineas = seccion.strip().splitlines()
    palabras_clave = []

    for linea in lineas:
        linea = linea.strip()
        if not linea:
            continue

        # Detenerse si hay un número (por seguridad)
        if re.search(r"\b\d+\b", linea):
            break

        # Separar por punto y coma o por coma
        if ';' in linea:
            palabras = [p.strip() for p in linea.split(';') if p.strip()]
            palabras_clave.extend(palabras)
        elif ',' in linea:
            palabras = [p.strip() for p in linea.split(',') if p.strip()]
            palabras_clave.extend(palabras)
        else:
            # Si no hay separador y hay más de 3 palabras, se asume que no es parte de palabras clave
            if len(linea.split()) > 3:
                break
            palabras_clave.append(linea)

    return ', '.join(palabras_clave).strip() if palabras_clave else None

def extraer_titulo_rae(texto):
    patron = re.compile(
        r"(?i)T[íi]tulo\s+del\s+documento\s*:?\s*\n*(.+?)(?=\n\s*(AUTOR\(ES\)|AUTOR|DIRECTOR|INFORMACIÓN GENERAL|PALABRAS CLAVE|FECHA DE PUBLICACIÓN))",
        re.DOTALL
    )
    match = patron.search(texto)
    if match:
        titulo = match.group(1)
        # Limpiar saltos de línea y espacios
        return " ".join(titulo.strip().splitlines()).strip()
    return None

def extraer_info_general(texto):
    """ Extrae la información general sin mezclar datos. """
    info = {
        "TÍTULO": "No encontrado",
        "AUTOR(ES)": "No encontrado",
        "DIRECTOR": "No registrado",
        "PALABRAS CLAVE": "No disponibles",
        "UNIDAD PATROCINANTE": "No disponible",
        "PUBLICACIÓN": "No disponible",
    }

    # Extraer título (tomando hasta 6 líneas para evitar truncamientos)
    titulo = extraer_titulo_rae(texto)
    if titulo:
        info["TÍTULO"] = titulo

    match_info_general = re.search(r"(?i)Información General\s*(.*)", texto, re.DOTALL)
    if match_info_general:
        texto_info_general = match_info_general.group(1)

        # Aplicar patrones individuales (excepto palabras clave)
        patrones = {
            "AUTOR(ES)": r"(?is)autor(?:\(es\))?\s*:?\s*(.*?)\s*(?:director|tutor|jurado|asesor)",
            "DIRECTOR": r"(?i)director\s*:?\s*\n*([^\n]+)",
            "UNIDAD PATROCINANTE": r"(?i)unidad\s*\n*patrocinante\s*:?\s*(.+)",
            "PUBLICACIÓN": r"(?i)publicaci[oó]n\s*:?\s*(.*?)(?=\n\s*unidad\s*\n*patrocinante)"
        }

        for clave, patron in patrones.items():
            match = re.search(patron, texto_info_general)
            if match:
                info[clave] = match.group(1).strip()

        # Usar función especializada para palabras clave
        palabras_clave = extraer_palabras_c(texto_info_general)
        if palabras_clave:
            info["PALABRAS CLAVE"] = palabras_clave

    return info

def extraer_secciones(texto, num_paginas):
    """ Extrae las secciones del documento. """
    secciones = {
        "Información General": extraer_info_general(texto),
        "Descripción": "No encontrado",
        "Fuentes": [],
        "Contenidos": "No encontrado",
        "Metodología": "No encontrado",
        "Conclusiones": "No encontrado"
    }

    patrones = {
        "Descripción": r"(?i)(?:1|2)\.\s*Descripci[oó]n\s*(.*?)(?=\n\d+\.\s|\Z)",
        "Metodología": r"(?i)(?:4|5)\.\s*Metodología\s*(.*?)(?=\n\d+\.\s|\Z)",
        # Usamos grupo no capturante (?:...) para que solo capture el contenido real
        "Conclusiones": r"(?i)(?:5|6)\.\s*(?:Conclusión|Conclusiones)\s*(.*?)(?=\n(?:Elaborado por|Revisado por|Bibliografía|Referencias|\Z))",
        "Contenidos": r"(?i)(?:4|3)\.\s*Contenidos\s*:?\s*\n*([\s\S]+?)(?=\n5\.)",
    }

    for seccion, patron in patrones.items():
        match = re.search(patron, texto, re.DOTALL)
        if match:
            contenido = match.group(1).strip()
            # Solo limpiar saltos de línea en las secciones textuales
            if seccion != "Contenidos":
                contenido = re.sub(r'\n+', ' ', contenido)
            contenido = limpiar_encabezados(contenido)
            secciones[seccion] = contenido

    # Extraer fuentes como lista
    fuentes_match = re.search(r"(?i)(?:2|3)\.\s*(Fuentes|Bibliografía)\s*([\n\s\S]+?)(?=\n\d+\.\s|\Z)", texto, re.DOTALL)
    if fuentes_match:
        lineas = fuentes_match.group(2).strip().split("\n")
        secciones["Fuentes"] = [line.strip() for line in lineas if line.strip()]
    
    return secciones

def limpiar_encabezados(texto):
    """Elimina encabezados innecesarios y limpia el texto."""
    patrones_excluir = [
        r"(?i)contenido\s*\d+",  
        r"(?i)FORMATO\s+RESUMEN\s+ANALÍTICO\s+EN\s+EDUCACIÓN\s+-\s+RAE",  
        r"(?i)Código:\s*FOR\d+\w*",  
        r"(?i)Versión:\s*\d+",  
        r"(?i)Fecha de Aprobación:\s*\d{2}-\d{2}-\d{4}",  
        r"(?i)Página\s*\d+\s*de\s*\d+",  
    ]
    
    for patron in patrones_excluir:
        texto = re.sub(patron, "", texto)

    # ✅ Elimina líneas vacías y espacios extra
    texto = "\n".join([line.strip() for line in texto.split("\n") if line.strip()])

    return texto.strip()

def procesar_documento(path_pdf):
    texto, num_paginas, ruta_pdf = extraer_texto(path_pdf)

    # Verificar si tiene formato RAE directamente por las frases clave
    if (re.search(r"Tipo\s*de\s*documento", texto, re.IGNORECASE) and
        re.search(r"Acceso\s*al\s*documento", texto, re.IGNORECASE) and
        re.search(r"T[ií]tulo\s*del\s*documento", texto, re.IGNORECASE)):
        
        print("✅ Documento con formato RAE detectado.")
        info_general = extraer_info_general(texto)
        secciones = extraer_secciones(texto, num_paginas)
    else:
        print("⚠️ Documento posiblemente sin formato RAE. Aplicando extractor alternativo.")
        info_general = extraer_info_sin_formato_rae(texto, num_paginas, path_pdf)
        secciones = extraer_secciones_sin_formato_rae(texto, num_paginas, path_pdf)

    info_general = info_general or {}
    secciones = secciones or {}

    return {**info_general, **secciones}