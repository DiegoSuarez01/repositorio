{% extends 'base.html' %}
{% load static %}

{% block content %}

<!-- Enlaza Font Awesome y Material Icons -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">

<style>
  body {
    background-color: #e0f7fa;
    font-family: Arial, sans-serif;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
  }

  .header h1 {
    margin: 0;
    color: #013220;
    font-size: 45px;
  }

  .header img {
    width: 150px;
    height: auto;
  }

  table {
    width: 100%;
    border: 2px solid #004d40;
    border-collapse: collapse;
    background-color: white;
  }

  th, td {
    border: 1px solid #004d40;
    padding: 15px;
    text-align: left;
  }

  th {
    background-color: #00796b;
    color: white;
    text-align: center;
  }

  td {
    color: #004d40;
    word-wrap: break-word;
    overflow-wrap: break-word;
    white-space: normal;
    max-width: 1000px;
  }

  .edit-button {
    background-color: #ffa726;
    color: white;
    border: none;
    padding: 10px;
    cursor: pointer;
    width: 100%;
    margin-bottom: 10px;
  }

  .edit-button:hover {
    background-color: #ef6c00;
  }

  .delete-button {
    background-color: #e57373;
    color: white;
    border: none;
    padding: 10px;
    cursor: pointer;
    width: 100%;
  }

  .delete-button:hover {
    background-color: #d32f2f;
  }

  .content-box {
    background-color: #f1f8e9;
    padding: 10px;
    border-radius: 5px;
  }
</style>

<div class="header">
  <h1>Detalle del Documento</h1>
  <img src="https://www.upn.edu.co/wp-content/uploads/2023/07/Logo-blanco-fondo-azul-UPN.jpg">
</div>

<table>
  <tr>
    <th>TÍTULO</th>
    <td>{{ object.titulo }}</td>
  </tr>
  <tr>
    <th>AUTOR(ES)</th>
    <td>{{ object.autor }}</td>
  </tr>
  <tr>
    <th>DIRECTOR</th>
    <td>{{ object.director|default:"No registrado" }}</td>
  </tr>
  <tr>
    <th>CATEGORÍA</th>
    <td>{{ object.categoria|default:"No especificada" }}</td>
  </tr>
  <tr>
    <th>PALABRAS CLAVE</th>
    <td>{{ object.palabras_clave|default:"No disponibles" }}</td>
  </tr>
  <tr>
    <th>UNIDAD PATROCINANTE</th>
    <td>{{ object.unidad_patrocinante|default:"No disponible" }}</td>
  </tr>
  <tr>
    <th>FECHA DE PUBLICACIÓN</th>
    <td>{{ object.fecha_publicacion|default:"No disponible" }}</td>
  </tr>
  <tr>
    <th>DESCRIPCIÓN</th>
    <td class="content-box">{{ object.descripcion|default:"No disponible" }}</td>
  </tr>
  <tr>
    <th>METODOLOGÍA</th>
    <td class="content-box">{{ object.metodologia|default:"No disponible" }}</td>
  </tr>
  <tr>
    <th>CONCLUSIONES</th>
    <td class="content-box">{{ object.conclusiones|default:"No disponibles" }}</td>
  </tr>
  <tr>
    <th>Fuentes</th>
    <td class="content-box">
        {% if object.fuentes %}
            <ul>
                {% for fuente in object.fuentes %}
                    <li>{{ fuente }}</li>
                {% endfor %}
            </ul>
        {% else %}
            No disponible
        {% endif %}
    </td>
   <tr>
  <tr>
    <th>FECHA DE CREACIÓN</th>
    <td>{{ object.fecha_creacion|default:"No disponible" }}</td>
  </tr>
  <tr>
    <th>ÚLTIMA MODIFICACIÓN</th>
    <td>{{ object.fecha_modificacion|default:"No disponible" }}</td>
  </tr>
  <tr>
    <th>ESTADO DEL DOCUMENTO</th>
    <td>{{ object.estado|default:"No especificado" }}</td>
  </tr>
  <tr>
    <th>Enlace del Documento</th>
    <td>
      {% if object.enlace %}
        <a href="{{ object.enlace }}" target="_blank">{{ object.enlace }}</a>
      {% else %}
        No disponible
      {% endif %}
    </td>
  </tr>
  <tr>
    <th>ARCHIVO</th>
    <td>
      {% if object.archivo %}
        📂 El documento está disponible en el repositorio de la Universidad Pedagógica Nacional.
      {% else %}
        <form method="post" enctype="multipart/form-data">
          {% csrf_token %}
          <label for="archivo">Subir archivo:</label>
          <input type="file" name="archivo">
          <button type="submit">Subir</button>
        </form>
      {% endif %}
    </td>
  </tr>
  <tr>
    <th>Acciones</th>
    <td>
      <a href="{% url 'documento_editar' object.pk %}" class="edit-button">
        <i class="fas fa-edit"></i> Editar
      </a>

      <form method="POST" action="{% url 'documento_eliminar' object.pk %}">
        {% csrf_token %}
        <button type="submit" class="delete-button">
          <i class="fas fa-trash-alt"></i> Eliminar
        </button>
      </form>
    </td>
  </tr>
</table>

{% endblock %}
