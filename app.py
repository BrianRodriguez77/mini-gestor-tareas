from flask import Flask, request, redirect, url_for, render_template_string
import requests
import json

app = Flask(__name__)

# Almacenamiento en memoria
tareas = []
contador_id = 1

# HTML simple para la interfaz (incrustado para simplificar)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mini Gestor de Tareas</title>
    <style>
        body { font-family: Arial; margin: 40px; }
        .completada { text-decoration: line-through; color: gray; }
        ul { list-style: none; padding: 0; }
        li { margin: 10px 0; }
    </style>
</head>
<body>
    <h1>📋 Mis Tareas</h1>
    <form action="/agregar" method="post">
        <input type="text" name="descripcion" placeholder="Nueva tarea" required>
        <button type="submit">Agregar</button>
    </form>
    <ul>
        {% for tarea in tareas %}
        <li>
            <span class="{% if tarea.completada %}completada{% endif %}">
                {{ tarea.descripcion }}
            </span>
            {% if not tarea.completada %}
                <a href="/completar/{{ tarea.id }}">✅ Completar</a>
            {% else %}
                <span>✅ Hecho</span>
            {% endif %}
            <a href="/eliminar/{{ tarea.id }}">🗑️ Eliminar</a>
        </li>
        {% endfor %}
    </ul>
    {% if consejo %}
        <hr>
        <h3>🎉 ¡Bien hecho! Consejo del día:</h3>
        <p><em>"{{ consejo }}"</em></p>
    {% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    # Si hay un consejo en la sesión (usamos query param para simplificar)
    consejo = request.args.get('consejo', None)
    return render_template_string(HTML_TEMPLATE, tareas=tareas, consejo=consejo)

@app.route('/agregar', methods=['POST'])
def agregar():
    global contador_id
    descripcion = request.form.get('descripcion')
    if descripcion:
        tareas.append({
            'id': contador_id,
            'descripcion': descripcion,
            'completada': False
        })
        contador_id += 1
    return redirect(url_for('index'))

@app.route('/completar/<int:id>')
def completar(id):
    for tarea in tareas:
        if tarea['id'] == id and not tarea['completada']:
            tarea['completada'] = True
            # Llamar a la API de Advice Slip
            try:
                respuesta = requests.get('https://api.adviceslip.com/advice')
                if respuesta.status_code == 200:
                    datos = respuesta.json()
                    consejo = datos['slip']['advice']
                else:
                    consejo = "Sigue así, ¡vas muy bien!"
            except:
                consejo = "No pude obtener un consejo, pero ¡felicitaciones!"
            # Redirigir con el consejo como parámetro
            return redirect(url_for('index', consejo=consejo))
    return redirect(url_for('index'))

@app.route('/eliminar/<int:id>')
def eliminar(id):
    global tareas
    tareas = [t for t in tareas if t['id'] != id]
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)