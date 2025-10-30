from database.connection import db
from datetime import datetime

class VoiceConfig(db.Model):
    """
    Modelo para la configuración global de la voz (TTS) de la aplicación.
    Se utiliza una clave primaria fija (id=1) para asegurar que solo exista una configuración.
    """
    __tablename__ = "voice_config"

    # Usamos id=1 como clave primaria fija para garantizar una única fila de configuración
    id = db.Column(db.Integer, primary_key=True, default=1) 
    
    # Configuración de Género/Tipo de Voz
    # Valores esperados: 'FEMALE', 'MALE', 'ROBOTIC'
    voice_gender = db.Column(db.String(10), nullable=False, default='FEMALE')
    
    # Configuración de Tono (Pitch)
    # Valores esperados: 0.8 (Grave), 1.0 (Normal), 1.3 (Aguda), etc.
    voice_pitch = db.Column(db.Float, nullable=False, default=1.0)

    def to_dict(self):
        """Convierte el objeto del modelo a un diccionario para la respuesta JSON."""
        return {
            "voice_gender": self.voice_gender,
            "voice_pitch": self.voice_pitch
        }