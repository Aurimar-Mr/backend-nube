from database.connection import db

class VoiceConfig(db.Model):
    """
    Modelo para la configuración global de la voz (TTS) de la aplicación.
    Solo existe una configuración (id=1).
    """
    __tablename__ = "voice_config"

    id = db.Column(db.Integer, primary_key=True, default=1) 
    voice_gender = db.Column(db.String(10), nullable=False, default='FEMALE')
    voice_pitch = db.Column(db.Float, nullable=False, default=1.0)

    VALID_GENDERS = ('FEMALE', 'MALE', 'ROBOTIC')

    def set_voice_gender(self, gender):
        if gender not in self.VALID_GENDERS:
            raise ValueError(f"voice_gender inválido. Valores válidos: {self.VALID_GENDERS}")
        self.voice_gender = gender

    def to_dict(self):
        return {
            "voice_gender": self.voice_gender,
            "voice_pitch": self.voice_pitch
        }
