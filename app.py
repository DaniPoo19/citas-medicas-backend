from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:DuLtaMvyFzmYRXcNybXpYmpirKCDmZCg@mysql.railway.internal:3306/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialización de la base de datos
db = SQLAlchemy(app)

# Habilitar CORS para permitir solicitudes desde tu frontend
CORS(app, resources={r"/*": {"origins": "https://danipoo19.github.io"}})

# Modelo de ejemplo (puedes adaptarlo a tus necesidades)
class Cita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente = db.Column(db.String(100), nullable=False)
    doctor = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.String(50), nullable=False)
    hora = db.Column(db.String(50), nullable=False)

# Ruta de prueba para verificar conexión
@app.route('/')
def home():
    return jsonify({"message": "API is running!"})

# Ruta para obtener citas médicas
@app.route('/api/citas', methods=['GET'])
def get_citas():
    citas = Cita.query.all()
    return jsonify([{
        "id": cita.id,
        "paciente": cita.paciente,
        "doctor": cita.doctor,
        "fecha": cita.fecha,
        "hora": cita.hora
    } for cita in citas])

# Ruta para crear una nueva cita
@app.route('/api/citas', methods=['POST'])
def create_cita():
    data = request.json
    nueva_cita = Cita(
        paciente=data['paciente'],
        doctor=data['doctor'],
        fecha=data['fecha'],
        hora=data['hora']
    )
    db.session.add(nueva_cita)
    db.session.commit()
    return jsonify({"message": "Cita creada con éxito"}), 201

# Ruta para eliminar una cita
@app.route('/api/citas/<int:id>', methods=['DELETE'])
def delete_cita(id):
    cita = Cita.query.get(id)
    if not cita:
        return jsonify({"message": "Cita no encontrada"}), 404
    db.session.delete(cita)
    db.session.commit()
    return jsonify({"message": "Cita eliminada con éxito"})

# Inicializar base de datos (opcional, para desarrollo)
@app.before_first_request
def setup_database():
    db.create_all()

# Ejecutar aplicación
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
