# config_routes.py (Ejemplo de implementación de rutas Flask)

from flask import Blueprint, jsonify, request
from database.connection import db
from database.models.voice_config import VoiceConfig 

voice_bp = Blueprint('config', __name__)

# --- GET: Obtener la configuración (Usado por el Usuario) ---
@voice_bp.route('/voice', methods=['GET'])
def get_voice_config():
    """
    Recupera la configuración de voz guardada. Si no existe, devuelve el valor por defecto.
    """
    config = VoiceConfig.query.get(1) # Intentar obtener la única fila
    
    if config:
        return jsonify(config.to_dict()), 200
    else:
        # Si la tabla está vacía, devuelve valores por defecto y status OK.
        default_config = VoiceConfig() 
        return jsonify(default_config.to_dict()), 200


# --- POST: Guardar la configuración (Usado por el Administrador) ---
@voice_bp.route('/voice', methods=['POST'])
# NOTA: En una aplicación real, agregarías aquí una verificación de rol de Administrador
def save_voice_config():
    """
    Guarda o actualiza la configuración de voz (siempre en la fila con id=1).
    """
    data = request.json
    
    # Validación simple de los datos de entrada
    if 'voice_gender' not in data or 'voice_pitch' not in data:
        return jsonify({"message": "Faltan parámetros: voice_gender y voice_pitch"}), 400

    gender = data.get('voice_gender')
    pitch = data.get('voice_pitch')
    
    try:
        # Intenta obtener la configuración existente
        config = VoiceConfig.query.get(1)
        
        if config is None:
            # Si no existe, crea una nueva fila
            config = VoiceConfig(id=1, voice_gender=gender, voice_pitch=pitch)
            db.session.add(config)
        else:
            # Si existe, actualiza los campos
            config.voice_gender = gender
            config.voice_pitch = pitch
            
        db.session.commit()
        return jsonify(config.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error al guardar la configuración: {str(e)}"}), 500

# Asegúrate de registrar este Blueprint en tu aplicación principal de Flask:
# app.register_blueprint(config_bp)