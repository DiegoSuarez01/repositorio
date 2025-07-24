<!-- Página principal -->
{% extends 'base.html' %}

{% block content %}
  <div class="container mt-5">
    <h1 class="text-center" style="color: #007bff;">Trabajos de Grado por Licenciatura</h1>
    <p class="text-center text-muted">Selecciona la licenciatura para ver la lista de trabajos de grado.</p>
    
    <div class="row mt-4">
      <div class="col-md-4">
        <div class="card shadow-lg">
          <div class="card-body text-center">
            <h3>Licenciatura en Electrónica</h3>
            <a href="{% url 'licenciatura_electronica' %}" class="btn btn-primary mt-3">Ver Trabajos</a>
          </div>
        </div>
      </div>
      
      <div class="col-md-4">
        <div class="card shadow-lg">
          <div class="card-body text-center">
            <h3>Licenciatura en Diseño Tecnológico</h3>
            <a href="{% url 'licenciatura_diseno_tecnologico' %}" class="btn btn-primary mt-3">Ver Trabajos</a>
          </div>
        </div>
      </div>
      
      <div class="col-md-4">
        <div class="card shadow-lg">
          <div class="card-body text-center">
            <h3>Licenciatura en Tecnología</h3>
            <a href="{% url 'licenciatura_tecnologia' %}" class="btn btn-primary mt-3">Ver Trabajos</a>
          </div>
        </div>
      </div>
    </div>
  </div>

  <style>
    .container {
      padding-top: 50px;
    }
    .card {
      border-radius: 10px;
      border: none;
    }
    .btn-primary {
      background-color: #007bff;
      border: none;
    }
    .btn-primary:hover {
      background-color: #0056b3;
    }
  </style>
{% endblock %}
