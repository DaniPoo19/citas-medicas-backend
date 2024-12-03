from flask import Flask, request, jsonify
from flask_cors import CORS
from config import app, db
from modelos import Paciente, Especialidad, Medico, Cita, HorarioMedico, DiaFestivo
import datetime

CORS(app)

# Ruta para agregar un paciente
@app.route('/pacientes', methods=['POST'])
def agregar_paciente():
    data = request.json
    try:
        paciente = Paciente(**data)
        db.session.add(paciente)
        db.session.commit()
        return jsonify({'message': 'Paciente agregado con éxito'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400

# Ruta para agendar una cita
@app.route('/citas', methods=['POST'])
def agendar_cita():
    data = request.json
    paciente_id = data.get('paciente_id')
    especialidad_id = data.get('especialidad_id')
    medico_id = data.get('medico_id')
    fecha_cita = datetime.datetime.strptime(data.get('fecha_cita'), '%Y-%m-%d').date()
    hora_cita = datetime.datetime.strptime(data.get('hora_cita'), '%H:%M:%S').time()
    
    try:
        # Verificar si el paciente ya tiene una cita para esa especialidad
        cita_existente = Cita.query.filter_by(paciente_id=paciente_id, especialidad_id=especialidad_id).first()
        if cita_existente:
            return jsonify({'message': 'Ya tiene una cita para esta especialidad'}), 400

        # Verificar si el paciente ya tiene una cita en el mismo horario con otra especialidad
        cita_misma_hora = Cita.query.filter_by(paciente_id=paciente_id, fecha_cita=fecha_cita, hora_cita=hora_cita).first()
        if cita_misma_hora:
            return jsonify({'message': 'No puede sacar citas en diferente especialidad a la misma hora'}), 400

        # Verificar si el médico ya tiene una cita en el mismo horario
        cita_medico = Cita.query.filter_by(medico_id=medico_id, fecha_cita=fecha_cita, hora_cita=hora_cita).first()
        if cita_medico:
            return jsonify({'message': 'El médico ya tiene una cita en este horario'}), 400

        # Registrar la nueva cita
        cita = Cita(
            paciente_id=paciente_id,
            medico_id=medico_id,
            especialidad_id=especialidad_id,
            fecha_cita=fecha_cita,
            hora_cita=hora_cita
        )
        db.session.add(cita)
        db.session.commit()
        return jsonify({'message': 'Cita agendada con éxito'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400


    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400

# Ruta para obtener las especialidades
@app.route('/especialidades', methods=['GET'])
def obtener_especialidades():
    try:
        especialidades = Especialidad.query.all()
        result = [{'id': esp.especialidad_id, 'nombre': esp.nombre} for esp in especialidades]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# Ruta para obtener los médicos de una especialidad
@app.route('/doctors/<int:especialidad_id>', methods=['GET'])
def obtener_medicos(especialidad_id):
    try:
        medicos = Medico.query.filter_by(especialidad_id=especialidad_id).all()
        result = [{'id': med.medico_id, 'nombre': f'{med.nombre} {med.apellido}'} for med in medicos]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# Ruta para validar la cédula de un paciente
@app.route('/validate_cedula', methods=['POST'])
def validar_cedula():
    data = request.json
    tipo_documento = data.get('tipoDocumento')
    numero_documento = data.get('cedula')
    try:
        paciente = Paciente.query.filter_by(tipo_documento=tipo_documento, numero_documento=numero_documento).first()
        if paciente:
            return jsonify({
                'paciente_id': paciente.paciente_id,  # Enviar el ID del paciente
                'nombre': paciente.nombre,
                'apellido': paciente.apellido
            }), 200
        else:
            return jsonify({'message': 'Documento no encontrado'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 400


# Ruta para obtener los horarios disponibles de un médico en una fecha
@app.route('/available_times/<int:medico_id>/<string:fecha>', methods=['GET'])
def obtener_horarios_disponibles(medico_id, fecha):
    try:
        fecha_cita = datetime.datetime.strptime(fecha, '%Y-%m-%d').date()
        horarios_medico = HorarioMedico.query.filter_by(medico_id=medico_id).all()

        if not horarios_medico:
            return jsonify({'message': 'No se encontraron horarios para este médico'}), 404

        # Obtener las citas ya agendadas para el médico y la fecha
        horarios_ocupados = Cita.query.filter_by(medico_id=medico_id, fecha_cita=fecha_cita).all()
        horas_ocupadas = [cita.hora_cita for cita in horarios_ocupados]

        horarios_disponibles = []  # Lista para almacenar los horarios disponibles

        # Recorrer los horarios del médico y generar los horarios disponibles
        for horario in horarios_medico:
            hora_inicio = datetime.datetime.strptime(str(horario.hora_inicio), '%H:%M:%S').time()
            hora_fin = datetime.datetime.strptime(str(horario.hora_fin), '%H:%M:%S').time()
            hora_actual = hora_inicio

            # Generar horarios cada 30 minutos y verificar disponibilidad
            while hora_actual < hora_fin:
                # Solo agregar si la hora no está ocupada
                if hora_actual not in horas_ocupadas:
                    horarios_disponibles.append(hora_actual.strftime('%H:%M:%S'))

                # Incrementar en intervalos de 30 minutos
                hora_actual = (datetime.datetime.combine(datetime.date.today(), hora_actual) + datetime.timedelta(minutes=30)).time()

        # Ordenar los horarios disponibles y asegurarse de no duplicarlos
        horarios_disponibles = sorted(list(set(horarios_disponibles)))

        return jsonify(horarios_disponibles), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# Ruta para cargar las citas registradas
@app.route('/appointments', methods=['GET'])
def obtener_citas():
    try:
        citas = Cita.query.all()
        result = []
        for cita in citas:
            paciente = Paciente.query.get(cita.paciente_id)
            medico = Medico.query.get(cita.medico_id)
            especialidad = Especialidad.query.get(cita.especialidad_id)

            result.append({
                'id': cita.cita_id,
                'tipo_documento': paciente.tipo_documento,
                'cedula': paciente.numero_documento,
                'nombre': paciente.nombre,
                'apellido': paciente.apellido,
                'fecha': cita.fecha_cita.strftime('%Y-%m-%d'),
                'hora': cita.hora_cita.strftime('%H:%M:%S'),
                'especialidad': especialidad.nombre,
                'doctor': f'{medico.nombre} {medico.apellido}'
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)

