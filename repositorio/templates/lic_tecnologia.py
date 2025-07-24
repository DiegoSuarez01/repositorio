{% extends 'base.html' %}
{% load static %}

<!-- Enlaza Font Awesome y Material Icons -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">

{% block content %}
  <style>
    body {
      background-color: #e0f7fa; /* Azul claro */
      font-family: Arial, sans-serif;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px;
      background-color: #00796b; /* Verde oscuro */
      color: white;
    }

    .header h1 {
      margin: 0;
      color: white;
      font-size: 24px;
    }

    .header img {
      width: 150px;
      height: auto;
    }

    .document-list {
      background-color: white;
      border-radius: 8px;
      padding: 20px;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }

    .document-list h1 {
      color: #00796b;
      text-align: center;
      margin-bottom: 20px;
    }

    .search-bar {
      display: flex;
      justify-content: center;
      margin-bottom: 20px;
    }

    .search-bar input[type="text"] {
      width: 50%;
      padding: 10px;
      border: 2px solid #00796b;
      border-radius: 5px;
      font-size: 16px;
    }

    .document-item {
      padding: 15px;
      margin-bottom: 10px;
      background-color: #f1f1f1;
      border: 1px solid #004d40;
      border-radius: 5px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .letra a {
      color: #00796b; /* Color del texto */
      font-weight: bold; /* Negrita */
      text-decoration: none; /* Sin subrayado */
      flex-grow: 1; /* Ocupa el espacio disponible */
    }
    .delete-button {
      background-color: #e57373;
      color: white;
      border: none;
      padding: 8px 12px;
      cursor: pointer;
      border-radius: 5px;
    }

    .delete-button:hover {
      background-color: #d32f2f;
    }
  </style>

  <div class="header">
    <h1>REPOSITORIO DIGITAL DEPARTAMENTO DE TECNOLOGÍA</h1>
    <img src="https://www.upn.edu.co/wp-content/uploads/2023/07/Logo-blanco-fondo-azul-UPN.jpg">
  </div>

  <div class="document-list">
    <h1>Trabajos de grado - Licenciatura en Electrónica</h1>

    <!-- Cuadro de búsqueda con un evento que llama a la función AJAX -->
    <div class="search-bar">
      <input type="text" id="search-input" placeholder="Buscar trabajos por título, autor o metodología">
    </div>

    <div id="document-list">
      {% for documento in object_list %}
        <div class="document-item">
          <div class="letra"> 
              <a href="{% url 'documento_detalle' documento.pk %}">{{ documento.titulo }}</a>
          </div>
          <!-- Formulario para eliminar el documento -->
          <form action="{% url 'documento_eliminar' documento.pk %}" method="POST" style="display:inline;">
            {% csrf_token %}
            <button type="submit" class="delete-button" onclick="return confirm('¿Estás seguro de que deseas eliminar este documento?');">
              <i class="fas fa-trash-alt"></i> Eliminar
            </button>
          </form>
        </div>
      {% endfor %}
    </div>
  </div>

  <script>
    document.getElementById('search-input').addEventListener('input', function() {
      const query = this.value;
      const xhr = new XMLHttpRequest();
      xhr.open('GET', `{% url 'documento_busqueda_ajax' %}?q=` + query, true);
      xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

      xhr.onload = function() {
        if (xhr.status === 200) {
          const results = JSON.parse(xhr.responseText);
          const documentList = document.getElementById('document-list');
          documentList.innerHTML = '';

          results.forEach(function(documento) {
            const div = document.createElement('div');
            div.className = 'document-item';
            div.innerHTML = `
              <div class="letra">
                <a href="/documento/detalle/${documento.pk}">${documento.titulo}</a>
              </div>
              <form action="/documento_eliminar/${documento.pk}" method="POST" style="display:inline;">
                <button type="submit" class="delete-button">
                  <i class="fas fa-trash-alt"></i> Eliminar
                </button>
              </form>
            `;
            documentList.appendChild(div);
          });
        }
      };

      xhr.send();
    });
  </script>

{% endblock %}