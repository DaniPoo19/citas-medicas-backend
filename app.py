from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Crear la aplicación Flask
app = Flask(__name__)

# Habilitar CORS para permitir solicitudes desde el frontend
CORS(app, resources={r"/*": {"origins": "*"}})

# Configurar la URI de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:dtxvIMHOmEKJIwQkqWfMMWWLKwpDXmMw@mysql.railway.internal:3306/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos
db = SQLAlchemy(app)

# Modelos de la base de datos
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
    especialidad = db.Column(db.String(50), nullable=False)
    horario = db.Column(db.String(100), nullable=False)

class Cita(db.Model):
    __tablename__ = 'citas'
    id = db.Column(db.Integer, primary_key=True)
    tipo_documento = db.Column(db.String(20), nullable=False)  # Si lo estás duplicando en la tabla Cita
    cedula = db.Column(db.String(20), nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.String(20), nullable=False)
    especialidad = db.Column(db.String(50), nullable=False)
    doctor = db.Column(db.String(50), nullable=False)

# Rutas de la API
@app.route('/validate_cedula', methods=['POST'])
def validate_cedula():
    data = request.json
    tipo_documento = data.get('tipo_documento')
    cedula = data.get('cedula')

    if not (tipo_documento and cedula):
        return jsonify({'valid': False, 'message': 'Tipo de documento y cédula son obligatorios'}), 400

    persona = Persona.query.filter_by(tipo_documento=tipo_documento, cedula=cedula).first()
    if persona:
        return jsonify({'valid': True, 'nombre': persona.nombre, 'apellido': persona.apellido}), 200
    else:
        return jsonify({'valid': False, 'message': 'Documento no encontrado'}), 404


@app.route('/add_appointment', methods=['POST'])
def add_appointment():
    data = request.json
    tipo_documento = data.get('tipo_documento')
    cedula = data.get('cedula')
    nombre = data.get('nombre')
    apellido = data.get('apellido')
    fecha = data.get('fecha')
    hora = data.get('hora')
    especialidad = data.get('especialidad')
    doctor = data.get('doctor')

    if not (tipo_documento and cedula and nombre and apellido and fecha and hora and especialidad and doctor):
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400

    nueva_cita = Cita(
        tipo_documento=tipo_documento, cedula=cedula, nombre=nombre, apellido=apellido,
        fecha=fecha, hora=hora, especialidad=especialidad, doctor=doctor
    )
    db.session.add(nueva_cita)
    db.session.commit()

    return jsonify({'message': 'Cita registrada con éxito'}), 201


@app.route('/appointments', methods=['GET'])
def get_appointments():
    citas = Cita.query.all()
    result = []
    for cita in citas:
        result.append({
            'id': cita.id,
            'tipoDocumento': cita.tipo_documento,  # Asegúrate de devolver este campo
            'cedula': cita.cedula,
            'nombre': cita.nombre,
            'apellido': cita.apellido,
            'fecha': cita.fecha.strftime('%Y-%m-%d'),
            'hora': cita.hora,
            'especialidad': cita.especialidad,
            'doctor': cita.doctor
        })
    return jsonify(result), 200


@app.route('/delete_appointment/<int:id>', methods=['DELETE'])
def delete_appointment(id):
    cita = Cita.query.get(id)
    if not cita:
        return jsonify({'error': 'Cita no encontrada'}), 404

    db.session.delete(cita)
    db.session.commit()
    return jsonify({'message': 'Cita eliminada con éxito'}), 200

@app.route('/doctors/<especialidad>', methods=['GET'])
def get_doctors(especialidad):
    doctores = Doctor.query.filter_by(especialidad=especialidad).all()
    result = [{'id': doctor.id, 'nombre': doctor.nombre} for doctor in doctores]
    return jsonify(result), 200

@app.route('/occupied_times/<fecha>/<doctor>', methods=['GET'])
def get_occupied_times(fecha, doctor):
    citas = Cita.query.filter_by(fecha=fecha, doctor=doctor).all()
    occupied_times = [cita.hora for cita in citas]
    return jsonify(occupied_times), 200

@app.route('/available_times/<doctor>/<fecha>', methods=['GET'])
def available_times(doctor, fecha):
    horarios_totales = [
        "09:00 AM", "10:00 AM", "11:00 AM", "02:00 PM", "03:00 PM", "04:00 PM"
    ]
    citas = Cita.query.filter_by(fecha=fecha, doctor=doctor).all()
    horarios_ocupados = [cita.hora for cita in citas]
    horarios_disponibles = [hora for hora in horarios_totales if hora not in horarios_ocupados]
    return jsonify(horarios_disponibles), 200

# Ejecutar la aplicación
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8080)
