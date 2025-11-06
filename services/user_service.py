from database.models.user import User
from database.connection import db
from datetime import datetime

def crear_usuario(nombre, telefono, password):
    """Crea un nuevo usuario asegurando que no exista el teléfono previamente."""
    if User.query.filter_by(telefono=telefono).first():
        raise ValueError("El teléfono ya está registrado.")
    user = User(nombre=nombre, telefono=telefono, rol="usuario", estado="activo", conectado=False)
    user.set_password(password)
    try:
        db.session.add(user)
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Error al guardar el usuario: {e}")

def login_usuario(telefono, password):
    """Verifica credenciales y actualiza la conexión del usuario."""
    user = User.query.filter_by(telefono=telefono).first()
    if user and user.check_password(password):
        user.conectado = True
        user.ultima_conexion = datetime.utcnow()
        db.session.commit()
        return user
    raise ValueError("Credenciales inválidas.")

def verificar_existencia_telefono(telefono):
    """Verifica si existe un usuario con el teléfono dado."""
    return User.query.filter_by(telefono=telefono).first() is not None

def restablecer_contrasena(telefono, nueva_contrasena):
    """Actualiza la contraseña de un usuario identificado por teléfono."""
    usuario = User.query.filter_by(telefono=telefono).first()
    if not usuario:
        raise ValueError("No se encontró el usuario.")
    usuario.set_password(nueva_contrasena)
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Error al restablecer contraseña: {e}")
