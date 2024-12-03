from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:vQXKrEivnMiXrhWioRJniLfCIXTlwNOS@junction.proxy.rlwy.net:42172/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
