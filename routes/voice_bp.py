from flask import Blueprint, jsonify, request
from database.connection import db
from database.models.voice_config import VoiceConfig 

voice_bp = Blueprint('voice', __name__)

# Recupera la configuración de voz guardada. Si no existe, devuelve valores por defecto.
@voice_bp.get('/voice')
def get_voice_config():
    config = VoiceConfig.query.get(1)
    if config:
        return jsonify(config.to_dict()), 200
    default_config = VoiceConfig()
    return jsonify(default_config.to_dict()), 200

# Guarda o actualiza la configuración de voz.
# Body JSON esperado: {"voice_gender": str, "voice_pitch": float}
@voice_bp.post('/voice')
def save_voice_config():
    data = request.json
    if 'voice_gender' not in data or 'voice_pitch' not in data:
        return jsonify({"message": "Faltan parámetros: voice_gender y voice_pitch"}), 400

    gender = data.get('voice_gender')
    pitch = data.get('voice_pitch')
    try:
        config = VoiceConfig.query.get(1)
        if config is None:
            config = VoiceConfig(id=1, voice_gender=gender, voice_pitch=pitch)
            db.session.add(config)
        else:
            config.voice_gender = gender
            config.voice_pitch = pitch
        db.session.commit()
        return jsonify(config.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error al guardar la configuración: {str(e)}"}), 500
