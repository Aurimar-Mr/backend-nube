from flask import Blueprint, request, jsonify
from services.lectura_service import (
    registrar_lectura, obtener_lecturas,
    obtener_lecturas_por_sensor, eliminar_lecturas_sensor
)

lectura_bp = Blueprint("lectura", __name__)

"""
Registra una nueva lectura para un sensor.
"""
@lectura_bp.post("/lecturas")
def create_lectura():
    data = request.json
    sensor_id = data.get("sensor_id")
    valor = data.get("valor")
    observaciones = data.get("observaciones")

    if not sensor_id or valor is None:
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    try:
        lectura = registrar_lectura(sensor_id, valor, observaciones)
    except RuntimeError as e:
        # Captura el error si no hay proceso activo
        return jsonify({"error": str(e)}), 409 

    return jsonify({
        "message": "Lectura registrada exitosamente",
        "id": lectura.id,
        "sensor_id": lectura.sensor_id,
        "valor": lectura.valor,
        "fecha_hora": lectura.fecha_hora.isoformat(),
        "observaciones": lectura.observaciones
    }), 201

# Obtiene todas las lecturas registradas.
@lectura_bp.get("/lecturas")
def get_lecturas():
    lecturas = obtener_lecturas()
    result = [{
        "id": l.id,
        "sensor_id": l.sensor_id,
        "valor": l.valor,
        "fecha_hora": l.fecha_hora.isoformat(),
        "observaciones": l.observaciones
    } for l in lecturas]
    return jsonify(result), 200

# Obtiene las últimas lecturas de un sensor específico (máx 20) del PROCESO ACTIVO.
@lectura_bp.get("/lecturas/<int:sensor_id>")
def get_lecturas_por_sensor_endpoint(sensor_id):
    try:
        # Esta llamada ahora trae solo datos del proceso activo o []
        lecturas = obtener_lecturas_por_sensor(sensor_id, limite=20)
        
        if not lecturas:
            # Si no hay lecturas, retorna lista vacía 200 OK.
            return jsonify([]), 200 
        
        result = [{
            "id": l.id,
            "sensor_id": l.sensor_id,
            "valor": l.valor,
            "fecha_hora": l.fecha_hora.isoformat(),
            "observaciones": l.observaciones
        } for l in lecturas]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Error al obtener lecturas del sensor {sensor_id}: {e}"}), 500