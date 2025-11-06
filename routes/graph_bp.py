from flask import Blueprint, request, jsonify
from services.graph_service import (
    guardar_o_actualizar_config,
    obtener_todas_configs,
    obtener_config_por_sensor
)

graph_bp = Blueprint("graph", __name__)

# Guarda o actualiza la configuración de una gráfica para un sensor.
# Body JSON esperado: {"sensor_id": int, "tipo_grafica": str}
@graph_bp.post("/graficas/update")
def update_graph():
    data = request.json
    sensor_id = data.get("sensor_id")
    tipo_grafica = data.get("tipo_grafica")

    if not sensor_id or not tipo_grafica:
        return jsonify({"error": "Faltan datos"}), 400

    config = guardar_o_actualizar_config(sensor_id, tipo_grafica)
    return jsonify({
        "message": "Configuración guardada",
        "sensor_id": config.sensor_id,
        "tipo_grafica": config.tipo_grafica
    }), 200

# Obtiene todas las configuraciones de gráficas.
@graph_bp.get("/graficas")
def get_graphs():
    configs = obtener_todas_configs()
    result = [
        {
            "sensor_id": c.sensor_id,
            "tipo_grafica": c.tipo_grafica,
            "fecha_modificacion": c.fecha_modificacion
        }
        for c in configs
    ]
    return jsonify(result), 200

# Obtiene la configuración de gráfica para un sensor específico.
@graph_bp.get("/graficas/<int:sensor_id>")
def get_graph(sensor_id):
    config = obtener_config_por_sensor(sensor_id)
    if not config:
        return jsonify({"error": "No hay configuración para este sensor"}), 404

    return jsonify({
        "sensor_id": config.sensor_id,
        "tipo_grafica": config.tipo_grafica,
        "fecha_modificacion": config.fecha_modificacion
    }), 200
