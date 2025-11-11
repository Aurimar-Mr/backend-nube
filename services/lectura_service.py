from database.models.lectura import Lectura
from database.models.proceso_biodigestor import ProcesoBiodigestor
from database.connection import db
from datetime import datetime
from sqlalchemy import desc
# Asegúrate de importar hay_proceso_activo si la usas en otros lugares
from services.proceso_service import hay_proceso_activo 

def obtener_proceso_activo():
    """Retorna el objeto ProcesoBiodigestor activo, si existe, de lo contrario None."""
    # Usamos la consulta directa que devuelve el objeto, no un booleano
    return ProcesoBiodigestor.query.filter_by(estado='ACTIVO').first()

def registrar_lectura(sensor_id, valor, observaciones=None):
    """
    Registra una lectura asociada a un proceso activo.
    Lanza excepción si no hay proceso activo.
    """
    proceso = obtener_proceso_activo()
    if not proceso:
        # Lanza una excepción que será capturada en el endpoint
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

def eliminar_lecturas_sensor(sensor_id):
    """Elimina todas las lecturas asociadas a un sensor."""
    try:
        Lectura.query.filter_by(sensor_id=sensor_id).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Error al eliminar lecturas del sensor {sensor_id}: {e}")

# --- FUNCIÓN DE FILTRADO CORREGIDA ---
def obtener_lecturas_por_sensor(sensor_id, limite=None):
    """
    Obtiene las últimas lecturas para un sensor, FILTRANDO por el proceso activo actual.
    Si no hay proceso activo, devuelve una lista vacía.
    """
    # 💡 CORRECCIÓN: Usamos obtener_proceso_activo() para asegurarnos de recibir el objeto o None.
    proceso_activo = obtener_proceso_activo() 

    if not proceso_activo:
        print("❌ DB LOG: No hay proceso activo. Retornando lista vacía para gráficas.")
        return []

    proceso_id = proceso_activo.id # Ahora es seguro acceder al ID
    
    query = Lectura.query.filter_by(
        sensor_id=sensor_id,
        proceso_id=proceso_id # FILTRO POR ID DE PROCESO
    ).order_by(desc(Lectura.fecha_hora))

    if limite is not None:
        query = query.limit(limite)
        
    print(f"✅ DB LOG: Obteniendo lecturas (Sensor: {sensor_id}, Proceso: {proceso_id})")
    return query.all()
# -------------------------------------