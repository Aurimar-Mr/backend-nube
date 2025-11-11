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
    Solo considera lecturas del proceso ACTIVO.
    Lanza LecturaException si faltan datos.
    """
    try:
        # Obtiene el proceso activo
        proceso_activo = hay_proceso_activo()
        if not proceso_activo:
            raise LecturaException("No hay proceso activo para obtener lecturas.")

        proceso_id = proceso_activo.id

        # Obtener la última lectura de cada sensor para el proceso activo
        ultima_temp = Lectura.query.filter_by(sensor_id=SENSOR_IDS["temperatura"], proceso_id=proceso_id)\
            .order_by(desc(Lectura.fecha_hora)).first()
        ultima_pres = Lectura.query.filter_by(sensor_id=SENSOR_IDS["presion"], proceso_id=proceso_id)\
            .order_by(desc(Lectura.fecha_hora)).first()
        ultima_gas = Lectura.query.filter_by(sensor_id=SENSOR_IDS["gas"], proceso_id=proceso_id)\
            .order_by(desc(Lectura.fecha_hora)).first()

        # Verificación: si alguna lectura falta
        if not (ultima_temp and ultima_pres and ultima_gas):
            raise LecturaException("Proceso activo sin lecturas completas aún.")

        temperatura = float(ultima_temp.valor)
        presion = float(ultima_pres.valor)
        gas = float(ultima_gas.valor)
        # Usamos la fecha más reciente entre las tres lecturas
        timestamp = max(ultima_temp.fecha_hora, ultima_pres.fecha_hora, ultima_gas.fecha_hora)

        return (temperatura, presion, gas, str(timestamp))

    except Exception as e:
        raise LecturaException(f"{e}")


def obtener_fecha_inicio_proceso_activo():
    """
    Retorna la fecha de inicio del proceso ACTIVO o None si no hay.
    """
    proceso = ProcesoBiodigestor.query.filter_by(estado='ACTIVO').first()
    return proceso.fecha_inicio if proceso else None

def hay_proceso_activo():
    """
    Verifica si existe un registro de ProcesoBiodigestor con estado 'ACTIVO'.

    :return: El objeto ProcesoBiodigestor activo si existe, de lo contrario None.
    """
    # 1. Ejecuta la consulta
    proceso_activo = ProcesoBiodigestor.query.filter_by(estado='ACTIVO').first()

    # 2. 🚨 LOG DE VERIFICACIÓN 🚨
    if proceso_activo:
        print(f"✅ DB LOG: Proceso ACTIVO encontrado. ID: {proceso_activo.id}, Estado: {proceso_activo.estado}")
    else:
        print("❌ DB LOG: NO se encontró ningún Proceso ACTIVO.")
    
    return proceso_activo
