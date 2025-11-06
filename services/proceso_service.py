from database.models.proceso_biodigestor import ProcesoBiodigestor
from database.connection import db
from datetime import datetime

def obtener_proceso_activo():
    return ProcesoBiodigestor.query.filter_by(estado='ACTIVO').first()

def iniciar_proceso():
    """Inicia un nuevo proceso biodigestor si no hay uno activo."""
    if obtener_proceso_activo():
        raise RuntimeError("Ya existe un proceso activo.")
    try:
        nuevo = ProcesoBiodigestor()
        db.session.add(nuevo)
        db.session.commit()
        return nuevo
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Error al iniciar proceso: {e}")

def finalizar_proceso():
    """Finaliza el proceso biodigestor activo."""
    activo = obtener_proceso_activo()
    if not activo:
        raise RuntimeError("No hay procesos activos para finalizar.")
    try:
        activo.estado = "FINALIZADO"
        activo.fecha_fin = datetime.utcnow()
        db.session.commit()
        return activo
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Error al finalizar proceso: {e}")

def hay_proceso_activo():
    """Retorna True si existe un proceso activo."""
    return obtener_proceso_activo() is not None
