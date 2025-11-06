from database.connection import db
from datetime import datetime

class Lectura(db.Model):
    """
    Modelo de lecturas de sensores.
    - proceso_id nullable permite lecturas fuera de procesos activos.
    """
    __tablename__ = "lecturas"

    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensores.id'), nullable=False)
    proceso_id = db.Column(db.Integer, db.ForeignKey('proceso_biodigestor.id'), nullable=True)  
    fecha_hora = db.Column(db.DateTime, default=datetime.now)
    valor = db.Column(db.Float, nullable=False)
    observaciones = db.Column(db.String(255), nullable=True)

    sensor = db.relationship("Sensor", back_populates="lecturas")
    proceso = db.relationship("ProcesoBiodigestor", back_populates="lecturas")
