from config import db

class Paciente(db.Model):
    __tablename__ = 'pacientes'
    paciente_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_documento = db.Column(db.Enum('Cédula', 'Tarjeta de Identidad', 'Cédula de Extranjería', 'Registro Civil'), nullable=False)
    numero_documento = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    telefono_movil = db.Column(db.String(20), nullable=False)
    sexo = db.Column(db.Enum('Masculino', 'Femenino', 'Otro'), nullable=False)
    edad = db.Column(db.Integer, nullable=False)

class Especialidad(db.Model):
    __tablename__ = 'especialidades'
    especialidad_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)

class Medico(db.Model):
    __tablename__ = 'medicos'
    medico_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    especialidad_id = db.Column(db.Integer, db.ForeignKey('especialidades.especialidad_id'), nullable=False)
    turno = db.Column(db.Enum('Mañana', 'Tarde'), nullable=False)

class Cita(db.Model):
    __tablename__ = 'citas'
    cita_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.paciente_id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('medicos.medico_id'), nullable=False)
    especialidad_id = db.Column(db.Integer, db.ForeignKey('especialidades.especialidad_id'), nullable=False)
    fecha_cita = db.Column(db.Date, nullable=False)
    hora_cita = db.Column(db.Time, nullable=False)

    # Restricciones de unicidad
    __table_args__ = (
        db.UniqueConstraint('paciente_id', 'especialidad_id', name='unica_cita_especialidad'),
        db.UniqueConstraint('paciente_id', 'fecha_cita', 'hora_cita', name='unica_cita_horario_paciente'),
        db.UniqueConstraint('medico_id', 'fecha_cita', 'hora_cita', name='unica_cita_horario_medico'),
    )

class HorarioMedico(db.Model):
    __tablename__ = 'horarios_medicos'
    horario_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    medico_id = db.Column(db.Integer, db.ForeignKey('medicos.medico_id'), nullable=False)
    dia_semana = db.Column(db.Enum('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'), nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)

class DiaFestivo(db.Model):
    __tablename__ = 'dias_festivos'
    fecha = db.Column(db.Date, primary_key=True)
    descripcion = db.Column(db.String(100))
