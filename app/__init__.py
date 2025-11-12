from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()  # Carga las variables de entorno del archivo .env

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Lee la clave secreta del entorno

from app import routes  # Importa las rutas después de crear la aplicación