from flask import Blueprint, jsonify
from services.ai_service import predecir_alerta
from database.db_service import obtener_ultima_lectura_combinada, hay_proceso_activo, LecturaException

ai_bp = Blueprint("ai_bp", __name__)

@ai_bp.get("/analizar")
def analizar_biodigestor():
    """
    Endpoint de análisis de biodigestor que unifica la respuesta de error de 'no datos' y 'no proceso'.
    """
    try:
        # Verifica si hay proceso activo
        proceso = hay_proceso_activo()  # retorna objeto ProcesoBiodigestor o None
        print(f"DEBUG LOG: Valor de 'proceso' en el endpoint: {proceso}")
        
        if proceso is None:
            # Caso 1: No hay proceso activo
            return jsonify({
                "alerta_ia": 0,
                "dia_proceso": 0,
                "mensaje_lectura": "No hay proceso activo. No se generan predicciones.",
                "recomendacion": "Inicie un nuevo proceso biodigestor.",
                "tipo_estado": "Proceso finalizado"
            }), 200

        # Intentamos obtener la última lectura combinada del proceso activo
        try:
            lectura = obtener_ultima_lectura_combinada()
        except LecturaException as le:
            # Caso 2: Proceso activo pero aún no hay lecturas completas
            return jsonify({
                "alerta_ia": 0,
                "dia_proceso": 0,
                "mensaje_lectura": "Proceso activo, pero aún no hay datos completos de sensores.",
                "recomendacion": "Espere a que se registren todas las lecturas.",
                "tipo_estado": "Proceso activo",
                "detalle": str(le)
            }), 200

        # Caso 3: Lecturas completas → hacer predicción
        temperatura, presion, gas, timestamp = lectura
        resultado = predecir_alerta(temperatura, presion, gas, timestamp)

        return jsonify(resultado), 200

    except Exception as e:
        # Cualquier otro error inesperado
        print(f"Error durante el procesamiento de la predicción de IA: {e}")
        return jsonify({
            "alerta_ia": 0,
            "dia_proceso": 0,
            "mensaje_lectura": "Error interno del servidor al procesar la predicción.",
            "recomendacion": "Revise los logs del servidor.",
            "tipo_estado": "Error",
            "detalle": str(e)
        }), 500
