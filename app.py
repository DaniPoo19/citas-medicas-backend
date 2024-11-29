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

# Ruta para validar la cédula
@app.route('/validate_cedula', methods=['POST'])
def validate_cedula():
    data = request.json
    tipo_documento = data.get('tipoDocumento')
    cedula = data.get('cedula')

    if not (tipo_documento and cedula):
        return jsonify({'valid': False, 'message': 'Tipo de documento y cédula son obligatorios'}), 400

    # Buscar la persona en la base de datos, insensible a mayúsculas/minúsculas
    persona = Persona.query.filter(
        db.func.lower(Persona.tipo_documento) == tipo_documento.lower(),
        db.func.lower(Persona.cedula) == cedula.lower()
    ).first()

    if persona:
        return jsonify({'valid': True, 'nombre': persona.nombre, 'apellido': persona.apellido}), 200
    else:
        return jsonify({'valid': False, 'message': 'Documento no encontrado'}), 404

# Ruta para agregar una nueva cita
@app.route('/add_appointment', methods=['POST'])
def add_appointment():
    data = request.json
    persona_id = data.get('persona_id')
    doctor_id = data.get('doctor')
    fecha = data.get('fecha')
    hora = data.get('hora')
    especialidad = data.get('especialidad')

    if not (persona_id and doctor_id and fecha and hora and especialidad):
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400

    try:
        fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({'error': 'Formato de fecha incorrecto, debe ser YYYY-MM-DD'}), 400

    nueva_cita = Cita(
        persona_id=persona_id, doctor_id=doctor_id, fecha=fecha, hora=hora, especialidad=especialidad
    )
    db.session.add(nueva_cita)
    db.session.commit()

    return jsonify({'message': 'Cita registrada con éxito'}), 201

# Ruta para obtener todas las citas
@app.route('/appointments', methods=['GET'])
def get_appointments():
    citas = Cita.query.all()
    result = []
    for cita in citas:
        result.append({
            'id': cita.id,
            'tipo_documento': cita.persona.tipo_documento,
            'cedula': cita.persona.cedula,
            'nombre': cita.persona.nombre,
            'apellido': cita.persona.apellido,
            'fecha': cita.fecha.strftime('%Y-%m-%d'),
            'hora': cita.hora,
            'especialidad': cita.especialidad,
            'doctor': cita.doctor.nombre
        })
    return jsonify(result), 200

# Ruta para obtener las especialidades
@app.route('/especialidades', methods=['GET'])
def get_especialidades():
    especialidades = Especialidad.query.all()
    result = [{'id': especialidad.id, 'nombre': especialidad.nombre} for especialidad in especialidades]
    return jsonify(result), 200

# Ruta para obtener los doctores según la especialidad
@app.route('/doctors/<especialidad_id>', methods=['GET'])
def get_doctors(especialidad_id):
    # Buscar la especialidad en la base de datos
    especialidad_obj = Especialidad.query.get(especialidad_id)
    
    if not especialidad_obj:
        return jsonify({'error': 'Especialidad no encontrada'}), 404

    # Obtener doctores que pertenezcan a esa especialidad
    doctores = Doctor.query.filter_by(especialidad_id=especialidad_obj.id).all()

    result = [{'id': doctor.id, 'nombre': doctor.nombre} for doctor in doctores]
    return jsonify(result), 200

# Ruta para obtener los horarios disponibles de un doctor en una fecha
@app.route('/available_times/<doctor_id>/<fecha>', methods=['GET'])
def available_times(doctor_id, fecha):
    doctor = Doctor.query.get(doctor_id)
    
    if not doctor:
        return jsonify({'error': 'Doctor no encontrado'}), 404

    # Definir los horarios de trabajo para el doctor según la especialidad
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

# Función para generar horarios disponibles en intervalos de 20 minutos
def generate_available_times(start_time, end_time):
    available_times = []
    start = datetime.strptime(start_time, "%I:%M %p")
    end = datetime.strptime(end_time, "%I:%M %p")
    
    while start < end:
        available_times.append(start.strftime("%I:%M %p"))
        start += timedelta(minutes=20)
    
    return available_times

# Ejecutar la aplicación
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crear las tablas si no existen
    app.run(host='0.0.0.0', port=8080)
