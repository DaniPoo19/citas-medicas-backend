from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta

# Crear la aplicación Flask
app = Flask(__name__)

# Permitir solicitudes de otros dominios (CORS)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configurar la URI de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:uYloZwwZtRjjWHgFOaXXzuBsDfVjvJiL@autorack.proxy.rlwy.net:23579/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos
db = SQLAlchemy(app)

# Modelos de la base de datos

class Especialidad(db.Model):
    __tablename__ = 'especialidades'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)

class Persona(db.Model):
    __tablename__ = 'personas'
    id = db.Column(db.Integer, primary_key=True)
    tipo_documento = db.Column(db.String(20), nullable=False)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)

class Doctor(db.Model):
    __tablename__ = 'doctores'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    especialidad_id = db.Column(db.Integer, db.ForeignKey('especialidades.id'), nullable=False)
    especialidad = db.relationship('Especialidad', backref='doctores')

class Cita(db.Model):
    __tablename__ = 'citas'
    id = db.Column(db.Integer, primary_key=True)
    persona_id = db.Column(db.Integer, db.ForeignKey('personas.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctores.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.String(20), nullable=False)
    especialidad = db.Column(db.String(50), nullable=False)
    persona = db.relationship('Persona', backref='citas')
    doctor = db.relationship('Doctor', backref='citas')

# Función para generar horarios disponibles en intervalos de 20 minutos
def generate_available_times(start_time, end_time):
    available_times = []
    start = datetime.strptime(start_time, "%I:%M %p")
    end = datetime.strptime(end_time, "%I:%M %p")
    
    while start < end:
        available_times.append(start.strftime("%I:%M %p"))
        start += timedelta(minutes=20)
    
    return available_times

# Ruta para obtener los horarios disponibles de un doctor en una fecha
@app.route('/available_times/<doctor_id>/<fecha>', methods=['GET'])
def available_times(doctor_id, fecha):
    doctor = Doctor.query.get(doctor_id)
    
    if not doctor:
        return jsonify({'error': 'Doctor no encontrado'}), 404

    # Definir los horarios de trabajo para el doctor
    if doctor.especialidad_id == 1:  # Medicina General
        morning_start = "06:00 AM"
        morning_end = "11:00 AM"
        afternoon_start = "01:00 PM"
        afternoon_end = "06:00 PM"
    elif doctor.especialidad_id == 2:  # Dermatología
        morning_start = "06:00 AM"
        morning_end = "11:00 AM"
        afternoon_start = "01:00 PM"
        afternoon_end = "06:00 PM"
    elif doctor.especialidad_id == 3:  # Odontología
        morning_start = "06:00 AM"
        morning_end = "11:00 AM"
        afternoon_start = "01:00 PM"
        afternoon_end = "06:00 PM"
    
    # Generar los horarios posibles en base a los turnos
    available_times = []
    available_times.extend(generate_available_times(morning_start, morning_end))
    available_times.extend(generate_available_times(afternoon_start, afternoon_end))

    # Filtrar horarios ocupados
    citas_ocupadas = Cita.query.filter_by(doctor_id=doctor_id, fecha=fecha).all()
    horarios_ocupados = [cita.hora for cita in citas_ocupadas]

    # Eliminar los horarios ocupados de los disponibles
    horarios_disponibles = [hora for hora in available_times if hora not in horarios_ocupados]

    return jsonify(horarios_disponibles), 200

# Ejecutar la aplicación
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crear las tablas si no existen
    app.run(host='0.0.0.0', port=8080)
