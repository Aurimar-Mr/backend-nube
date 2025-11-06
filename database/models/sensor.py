from database.connection import db

class Sensor(db.Model):
    """
    Modelo de sensor que almacena nombre, tipo y unidad.
    Relaciones:
      - 1:1 con GraphConfig
      - 1:N con Lectura
    """
    __tablename__ = "sensores"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    tipo = db.Column(db.String(50), nullable=False)
    unidad = db.Column(db.String(20), nullable=False)

    grafica_config = db.relationship("GraphConfig", back_populates="sensor", uselist=False)
    lecturas = db.relationship("Lectura", back_populates="sensor")
