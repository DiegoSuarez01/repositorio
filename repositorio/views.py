from django.shortcuts import render

from django.views.generic import ListView, DetailView
from .models import Trabajodegrado


def lista_trabajos(request):
    trabajos = Trabajodegrado.objects.all()
    return render(request, 'lista_trabajos.html', {'trabajos': trabajos})

class TrabajodegradoListView(ListView):
    model = Trabajodegrado
    template_name = 'lista_trabajos.html'   

class TrabajodegradoDetailView(DetailView):
    model = Trabajodegrado
    template_name = 'base.html'


"""
TrabajoGradoListView: Muestra una lista de todos los trabajos de grado utilizando el modelo TrabajoGrado.
                      Se asocia con la plantilla trabajos_grado_list.html para renderizar los datos.
TrabajoGradoDetailView: Muestra los detalles de un trabajo de grado específico. Recibe el ID (o pk) del trabajo, 
                        lo busca en la base de datos y utiliza la plantilla trabajo_grado_detail.html para mostrar
                        la información.
Uso: Estas vistas permiten listar los trabajos de grado y mostrar detalles específicos de cada trabajo en páginas separadas.
"""
# Create your views here.
