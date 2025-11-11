from database.models.user import User
from database.connection import db
from datetime import datetime

# -----------------------------------------------------------------
# 1. Crear Usuario
# -----------------------------------------------------------------
def crear_usuario(nombre, telefono, password):
    """Crea un nuevo usuario en la base de datos."""
    # Verificar si ya existe un usuario con ese teléfono
    if User.query.filter_by(telefono=telefono).first():
        return None, "El teléfono ya está registrado"

    user = User(
        nombre=nombre,
        telefono=telefono,
        rol="usuario",      # siempre usuario por defecto
        estado="activo",
        conectado=False
    )
    # Asume que el modelo User tiene un método set_password que hashea la contraseña
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
        return user, None
    except Exception as e:
        db.session.rollback()
        # Capturar un error más específico si es necesario
        return None, "Error al guardar el usuario en la base de datos"


# -----------------------------------------------------------------
# 2. Login de Usuario
# -----------------------------------------------------------------
def login_usuario(telefono, password):
    """Verifica credenciales y actualiza la conexión del usuario."""
    user = User.query.filter_by(telefono=telefono).first()
    
    # Asume que el modelo User tiene un método check_password para verificar el hash
    if user and user.check_password(password):
        # actualizar conexión
        user.conectado = True
        user.ultima_conexion = datetime.now()
        db.session.commit()
        return user
    return None

# -----------------------------------------------------------------
# 3. Verificar Existencia de Teléfono (Para recuperación)
# -----------------------------------------------------------------
def verificar_existencia_telefono(telefono):
    """Verifica si existe un usuario con el número de teléfono dado."""
    return User.query.filter_by(telefono=telefono).first()

# -----------------------------------------------------------------
# 4. Restablecer Contraseña (Actualizar Contraseña)
# -----------------------------------------------------------------
def restablecer_contrasena(telefono, nueva_contrasena):
    """Encuentra un usuario por teléfono y actualiza su contraseña."""
    usuario = User.query.filter_by(telefono=telefono).first()

    if not usuario:
        return False, "No se encontró el usuario"

    try:
        # Asume el método set_password para hashear la nueva contraseña
        usuario.set_password(nueva_contrasena)
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, "Error al actualizar la contraseña en la base de datos"