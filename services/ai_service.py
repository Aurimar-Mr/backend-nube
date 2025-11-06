import os
import joblib
import pandas as pd
from datetime import datetime
from ml.utils import obtener_recomendacion
from database.db_service import obtener_fecha_inicio_proceso_activo

# --- Rutas de Modelos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ML_DIR = os.path.join(BASE_DIR, '..', 'ml')

# --- Carga de modelos ---
try:
    modelo_alerta = joblib.load(os.path.join(ML_DIR, "modelo_alerta.pkl"))
    modelo_tipo = joblib.load(os.path.join(ML_DIR, "modelo_tipo_alerta.pkl"))
except FileNotFoundError:
    print("FATAL ERROR: No se pudieron cargar los modelos de IA. Ejecute el script de entrenamiento.")
    modelo_alerta = None
    modelo_tipo = None

# -------------------------------------------------------------------
# AI SERVICE FUNCTIONS
# -------------------------------------------------------------------

def calcular_dia_proceso(timestamp_str):
    """
    Calcula el día del proceso basándose en el timestamp de la lectura.
    Devuelve 0 si no hay proceso activo.
    Soporta formatos: '%Y-%m-%d %H:%M:%S' y '%d/%m/%Y %H:%M'.
    """
    fecha_inicio = obtener_fecha_inicio_proceso_activo()
    if fecha_inicio is None:
        return 0

    for fmt in ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M"):
        try:
            timestamp = datetime.strptime(timestamp_str, fmt)
            break
        except ValueError:
            continue
    else:
        return 1

    delta = timestamp - fecha_inicio
    return delta.days + 1

def predecir_alerta(temperatura, presion, gas, timestamp):
    """
    Realiza predicción de alerta utilizando modelos de IA.
    Maneja escenarios donde no hay proceso activo o modelos no cargados.
    Retorna un diccionario estandarizado con resultados y recomendaciones.
    """
    if modelo_alerta is None or modelo_tipo is None:
        return {
            "alerta_ia": 0,
            "tipo_estado": "Error de Sistema",
            "mensaje_lectura": "Modelos de IA no cargados. Revisar logs del servidor.",
            "recomendacion": "Ejecute el script de entrenamiento de modelos.",
            "dia_proceso": 0
        }

    dia_proceso = calcular_dia_proceso(timestamp)
    if dia_proceso == 0:
        return {
            "alerta_ia": 0,
            "tipo_estado": "Proceso finalizado",
            "mensaje_lectura": "No hay proceso activo. No se generan predicciones.",
            "recomendacion": "Inicie un nuevo proceso biodigestor.",
            "dia_proceso": 0
        }

    entrada = pd.DataFrame([{
        "temperatura_celsius": temperatura,
        "presion_biogas_kpa": presion,
        "mq4_ppm": gas,
        "dia_proceso": dia_proceso
    }])

    alerta_pred = int(modelo_alerta.predict(entrada)[0])
    tipo_pred = str(modelo_tipo.predict(entrada)[0])

    recomendacion_data = obtener_recomendacion(
        estado=alerta_pred,
        temperatura=temperatura,
        presion=presion,
        gas=gas
    )

    return {
        "alerta_ia": alerta_pred,
        "tipo_alerta_modelo": tipo_pred,
        "tipo_estado": recomendacion_data.get("tipo", ""),
        "mensaje_lectura": recomendacion_data.get("mensaje", ""),
        "recomendacion": recomendacion_data.get("recomendacion", ""),
        "dia_proceso": dia_proceso
    }
