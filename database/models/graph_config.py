from database.connection import db
from datetime import datetime

class GraphConfig(db.Model):
    """
    Configuración de gráficas para cada sensor.
    - sensor_id único: 1 sensor → 1 configuración de gráfica
    """
    __tablename__ = "graficas_config"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensores.id"), nullable=False, unique=True)
    tipo_grafica = db.Column(db.String(20), nullable=False)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sensor = db.relationship("Sensor", back_populates="grafica_config")
