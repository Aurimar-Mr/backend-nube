from flask import Blueprint, jsonify
from services.ai_service import predecir_alerta
from database.db_service import obtener_ultima_lectura_combinada 

ai_bp = Blueprint("ai_bp", __name__)

@ai_bp.get("/analizar")
def analizar_biodigestor():
    """
    Endpoint de análisis que unifica la respuesta de error de 'no datos' y 'no proceso'.
    """
    try:
        lectura = obtener_ultima_lectura_combinada()

        if not lectura: 
            return jsonify({
                "error": "El nuevo proceso no tiene datos de sensores registrados.",
                "codigo_error": 1001
            }), 400
            
        temperatura, presion, gas, timestamp = lectura 
        
        resultado = predecir_alerta(temperatura, presion, gas, timestamp)
        
        if resultado.get("dia_proceso") == 0:
            return jsonify({
                "error": resultado.get("mensaje_lectura", "No hay proceso activo o el proceso ha finalizado."),
                "codigo_error": 1002
            }), 400
        
        return jsonify(resultado), 200
        
    except Exception as e:
        print(f"Error durante el procesamiento de la predicción de IA: {e}")
        return jsonify({
            "error": "Error interno del servidor al procesar la predicción.",
            "detalle": str(e)
        }), 500
