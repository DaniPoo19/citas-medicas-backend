import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate

# Inicializar la app y configurar CORS
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Cambiar "*" por un dominio específico en producción

# Configuración de la base de datos usando variables de entorno
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:password@localhost/db_name')  # Proporciona un valor por defecto para desarrollo local
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos y las migraciones
db = SQLAlchemy(app)
migrate = Migrate(app, db)
