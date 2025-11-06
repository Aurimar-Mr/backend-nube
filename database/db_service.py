from database.models.lectura import Lectura
from database.connection import db
from sqlalchemy import desc
from database.models.proceso_biodigestor import ProcesoBiodigestor

SENSOR_IDS = {
    "gas": 1,
    "temperatura": 2,
    "presion": 3
}

class LecturaException(Exception):
    pass

def obtener_ultima_lectura_combinada():
    """
    Retorna una tupla: (temperatura, presion, gas, timestamp)
    Lanza LecturaException si faltan datos.
    """
    try:
        ultima_temp = Lectura.query.filter_by(sensor_id=SENSOR_IDS["temperatura"]).order_by(desc(Lectura.fecha_hora)).first()
        ultima_pres = Lectura.query.filter_by(sensor_id=SENSOR_IDS["presion"]).order_by(desc(Lectura.fecha_hora)).first()
        ultima_gas = Lectura.query.filter_by(sensor_id=SENSOR_IDS["gas"]).order_by(desc(Lectura.fecha_hora)).first()

        ultima_fecha = db.session.query(Lectura.fecha_hora).order_by(desc(Lectura.fecha_hora)).first()

        if not (ultima_temp and ultima_pres and ultima_gas and ultima_fecha):
            raise LecturaException("No se encontraron lecturas suficientes para los sensores.")

        temperatura = float(ultima_temp.valor)
        presion = float(ultima_pres.valor)
        gas = float(ultima_gas.valor)
        timestamp = str(ultima_fecha[0]) if ultima_fecha and ultima_fecha[0] else None

        return (temperatura, presion, gas, timestamp)

    except Exception as e:
        raise LecturaException(f"Error al obtener lecturas combinadas: {e}")

def obtener_fecha_inicio_proceso_activo():
    """
    Retorna la fecha de inicio del proceso ACTIVO o None si no hay.
    """
    proceso = ProcesoBiodigestor.query.filter_by(estado='ACTIVO').first()
    return proceso.fecha_inicio if proceso else None
