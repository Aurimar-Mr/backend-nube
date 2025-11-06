from database.models.lectura import Lectura
from database.models.proceso_biodigestor import ProcesoBiodigestor
from database.connection import db
from datetime import datetime

def obtener_proceso_activo():
    """Retorna el proceso activo, si existe."""
    return ProcesoBiodigestor.query.filter_by(estado='ACTIVO').first()

def registrar_lectura(sensor_id, valor, observaciones=None):
    """
    Registra una lectura asociada a un proceso activo.
    Lanza excepción si no hay proceso activo.
    """
    proceso = obtener_proceso_activo()
    if not proceso:
        raise RuntimeError("No hay proceso biodigestor activo. No se puede registrar lectura.")

    lectura = Lectura(
        sensor_id=sensor_id,
        valor=valor,
        proceso_id=proceso.id,
        observaciones=observaciones,
        fecha_hora=datetime.utcnow()
    )
    try:
        db.session.add(lectura)
        db.session.commit()
        return lectura
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Error al registrar lectura: {e}")

def obtener_lecturas():
    """Retorna todas las lecturas ordenadas por fecha descendente."""
    return Lectura.query.order_by(Lectura.fecha_hora.desc()).all()

def obtener_lecturas_por_sensor(sensor_id, limite=None):
    """Retorna lecturas de un sensor específico."""
    query = Lectura.query.filter_by(sensor_id=sensor_id).order_by(Lectura.fecha_hora.desc())
    if limite:
        query = query.limit(limite)
    return query.all()

def eliminar_lecturas_sensor(sensor_id):
    """Elimina todas las lecturas asociadas a un sensor."""
    try:
        Lectura.query.filter_by(sensor_id=sensor_id).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Error al eliminar lecturas del sensor {sensor_id}: {e}")
