from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # Importa CORS

# Crear instancia de la aplicación
app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:vQXKrEivnMiXrhWioRJniLfCIXTlwNOS@junction.proxy.rlwy.net:42172/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Instanciar la base de datos
db = SQLAlchemy(app)

# Configurar CORS para la aplicación
CORS(app, resources={r"/*": {"origins": "https://danipoo19.github.io"}})  # Aquí va la configuración de CORS

