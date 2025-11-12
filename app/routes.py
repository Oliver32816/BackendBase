import os
from app import app
from flask import render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import json

UPLOAD_FOLDER = os.path.join('static')  # Carpeta principal para archivos estáticos
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def update_rutas(filename, file_path, tipo):
    rutas_file = os.path.join(app.root_path, 'rutas.json')  # Guarda rutas.json en la raíz del proyecto
    try:
        with open(rutas_file, 'r') as f:
            rutas = json.load(f)
    except FileNotFoundError:
        rutas = {'imagenes': [], 'videos': []}

    if tipo == 'imagenes':
        rutas['imagenes'].append({'filename': filename, 'path': file_path})
    elif tipo == 'videos':
        rutas['videos'].append({'filename': filename, 'path': file_path})

    with open(rutas_file, 'w') as f:
        json.dump(rutas, f, indent=4)


@app.route('/', methods=['GET'])
def index():
    return "¡Hola desde el backend!"


@app.route('/api/data', methods=['GET'])
def get_data():
    data = {'message': 'Datos de la API'}
    return jsonify(data)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No se ha enviado ningún archivo'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': 'Nombre de archivo vacío'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Determinar si es imagen o video y guardar en la carpeta correcta
        if filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'imagenes', filename)
            tipo = 'imagenes'
        elif filename.rsplit('.', 1)[1].lower() in {'mp4', 'avi', 'mov'}:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', filename)
            tipo = 'videos'
        else:
            return jsonify({'message': 'Tipo de archivo no permitido'}), 400

        file.save(file_path)
        update_rutas(filename, file_path, tipo)

        return jsonify({'message': 'Archivo subido con éxito', 'filename': filename, 'path': file_path}), 201
    else:
        return jsonify({'message': 'Tipo de archivo no permitido'}), 400


@app.route('/files/<tipo>/<filename>')
def serve_file(tipo, filename):
    if tipo not in ['imagenes', 'videos']:
        return jsonify({'message': 'Tipo de archivo no válido'}), 400

    folder = os.path.join(app.config['UPLOAD_FOLDER'], tipo)
    return send_from_directory(folder, filename)


@app.route('/rutas', methods=['GET'])
def get_rutas():
    rutas_file = os.path.join(app.root_path, 'rutas.json')
    try:
        with open(rutas_file, 'r') as f:
            rutas = json.load(f)
        return jsonify(rutas)
    except FileNotFoundError:
        return jsonify({'message': 'El archivo rutas.json no se encuentra'}), 404