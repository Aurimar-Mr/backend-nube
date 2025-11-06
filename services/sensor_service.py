from database.models.sensor import Sensor
from database.connection import db

def crear_sensor(nombre, tipo, unidad):
    """Crea un nuevo sensor si no existe otro con el mismo nombre."""
    if Sensor.query.filter_by(nombre=nombre).first():
        raise ValueError("Ya existe un sensor con ese nombre.")
    sensor = Sensor(nombre=nombre, tipo=tipo, unidad=unidad)
    try:
        db.session.add(sensor)
        db.session.commit()
        return sensor
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Error al crear sensor: {e}")

def obtener_sensores():
    return Sensor.query.all()

def obtener_sensor_por_id(sensor_id):
    return Sensor.query.get(sensor_id)

def actualizar_sensor(sensor_id, nombre=None, tipo=None, unidad=None, activo=None):
    sensor = Sensor.query.get(sensor_id)
    if not sensor:
        raise ValueError("Sensor no encontrado.")
    if nombre: sensor.nombre = nombre
    if tipo: sensor.tipo = tipo
    if unidad: sensor.unidad = unidad
    if activo is not None: sensor.activo = activo
    try:
        db.session.commit()
        return sensor
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Error al actualizar sensor: {e}")

def eliminar_sensor(sensor_id):
    """Marca un sensor como inactivo en lugar de eliminarlo."""
    sensor = Sensor.query.get(sensor_id)
    if not sensor:
        raise ValueError("Sensor no encontrado.")
    sensor.activo = False
    try:
        db.session.commit()
        return sensor
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Error al desactivar sensor: {e}")
