from database.connection import db
from datetime import datetime

class ProcesoBiodigestor(db.Model):
    """
    Modelo de Proceso del Biodigestor.
    - fecha_fin nullable significa que el proceso sigue activo.
    - lecturas relacionadas.
    """
    __tablename__ = "proceso_biodigestor"

    id = db.Column(db.Integer, primary_key=True)
    fecha_inicio = db.Column(db.DateTime, nullable=False, default=datetime.now)
    fecha_fin = db.Column(db.DateTime, nullable=True)
    estado = db.Column(db.Enum('ACTIVO', 'FINALIZADO'), default='ACTIVO')
    observaciones = db.Column(db.String(255), nullable=True)

    lecturas = db.relationship("Lectura", back_populates="proceso") 
