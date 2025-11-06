from database.connection import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), default="usuario")
    estado = db.Column(db.String(20), default="activo")
    conectado = db.Column(db.Boolean, default=False)
    ultima_conexion = db.Column(db.DateTime, default=None)

    VALID_ROLES = ('usuario', 'admin')
    VALID_ESTADOS = ('activo', 'inactivo')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_rol(self, rol):
        if rol not in self.VALID_ROLES:
            raise ValueError(f"Rol inválido. Valores válidos: {self.VALID_ROLES}")
        self.rol = rol

    def set_estado(self, estado):
        if estado not in self.VALID_ESTADOS:
            raise ValueError(f"Estado inválido. Valores válidos: {self.VALID_ESTADOS}")
        self.estado = estado
