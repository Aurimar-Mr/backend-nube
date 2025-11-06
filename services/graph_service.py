from database.models.graph_config import GraphConfig
from database.connection import db
from datetime import datetime

def guardar_o_actualizar_config(sensor_id, tipo_grafica):
    """
    Guarda o actualiza la configuración de una gráfica para un sensor.
    Lanza excepción si falla la operación.
    """
    try:
        config = GraphConfig.query.filter_by(sensor_id=sensor_id).first()
        if config:
            config.tipo_grafica = tipo_grafica
            config.fecha_modificacion = datetime.utcnow()
        else:
            config = GraphConfig(sensor_id=sensor_id, tipo_grafica=tipo_grafica)
            db.session.add(config)
        db.session.commit()
        return config
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Error al guardar/actualizar configuración: {e}")

def obtener_todas_configs():
    """Retorna todas las configuraciones de gráficas."""
    return GraphConfig.query.all()

def obtener_config_por_sensor(sensor_id):
    """Retorna la configuración de gráfica para un sensor específico."""
    return GraphConfig.query.filter_by(sensor_id=sensor_id).first()
