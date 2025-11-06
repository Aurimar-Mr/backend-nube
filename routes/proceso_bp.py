from flask import Blueprint, jsonify
from services.proceso_service import iniciar_proceso, finalizar_proceso, hay_proceso_activo

proceso_bp = Blueprint("proceso_bp", __name__)


# Inicia un nuevo proceso de biodigestor.
@proceso_bp.post("/proceso/iniciar")
def iniciar():
    return iniciar_proceso()

# Finaliza el proceso activo.
@proceso_bp.post("/proceso/finalizar")
def finalizar():
    return finalizar_proceso()

# Verifica si hay un proceso activo.
@proceso_bp.get("/proceso/estado")
def verificar_estado_proceso_route():
    try:
        activo = hay_proceso_activo()
        return jsonify({
            "proceso_activo": activo,
            "mensaje": "Proceso activo." if activo else "Proceso inactivo o finalizado."
        }), 200
    except Exception as e:
        print(f"Error al verificar el estado del proceso: {e}")
        return jsonify({
            "proceso_activo": False,
            "error": "Error interno del servidor al verificar el estado.",
            "detalle": str(e)
        }), 500
