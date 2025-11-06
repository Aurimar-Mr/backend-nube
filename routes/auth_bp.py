from flask import Blueprint, request, jsonify
from services.user_service import (
    crear_usuario, 
    login_usuario, 
    verificar_existencia_telefono, 
    restablecer_contrasena
)
from sqlalchemy.exc import SQLAlchemyError 
auth_bp = Blueprint("auth", __name__)


# Función auxiliar para manejar la validación de datos JSON
def validate_request_data(required_fields):
    # Verifica que todos los campos requeridos estén presentes en el cuerpo JSON.
    data = request.json
    if not data:
        return {"error": "El cuerpo de la solicitud no puede estar vacío."}, 400
    
    for field in required_fields:
        if field not in data:
            return {"error": f"Falta el campo requerido: '{field}'."}, 400
    return data, None


@auth_bp.post("/register")
def register():
    # Validación de campos requeridos
    required = ["nombre", "telefono", "password", "confirm_password"]
    data, error_response = validate_request_data(required)
    if error_response:
        return jsonify(error_response), 400
    
    # Validación de coincidencia de contraseñas
    if data["password"] != data["confirm_password"]:
        return jsonify({"error": "Las contraseñas no coinciden."}), 400

    try:
        # Llamada al servicio de creación de usuario
        user, error = crear_usuario(
            nombre=data["nombre"],
            telefono=data["telefono"],
            password=data["password"]
        )
        
        # Manejo de errores de negocio (ej: teléfono ya existe)
        if error:
            return jsonify({"error": error}), 409 # 409 Conflict si ya existe
        
        # Respuesta exitosa
        return jsonify({
            "message": "Usuario creado exitosamente.",
            "id": user.id,
            "rol": user.rol,
            "estado": user.estado
        }), 201
        
    except SQLAlchemyError:
        # Manejo de errores de base de datos
        return jsonify({"error": "Error de base de datos al registrar usuario."}), 500
    except Exception:
        # Manejo de errores internos inesperados
        return jsonify({"error": "Error interno del servidor."}), 500


@auth_bp.post("/login")
def login():
    # Validación de campos requeridos
    required = ["telefono", "password"]
    data, error_response = validate_request_data(required)
    if error_response:
        return jsonify(error_response), 400

    try:
        # Llamada al servicio de login
        user = login_usuario(data["telefono"], data["password"])
        
        # Validación de credenciales
        if not user:
            return jsonify({"error": "Teléfono o contraseña incorrecta."}), 401
        
        # Validación de estado de cuenta
        if user.estado == "bloqueado":
            return jsonify({
                "error": "El usuario está bloqueado.",
                "detalle": "Comuníquese con el administrador."
            }), 403 # 403 Forbidden
            
        # Respuesta exitosa
        return jsonify({
            "message": "Login exitoso.",
            "usuario": user.nombre,
            "rol": user.rol,
            "ultima_conexion": user.ultima_conexion.strftime("%Y-%m-%d %H:%M:%S") 
                               if user.ultima_conexion else None
        }), 200

    except SQLAlchemyError:
        # Manejo de errores de base de datos
        return jsonify({"error": "Error de base de datos durante el login."}), 500
    except Exception:
        # Manejo de errores internos inesperados
        return jsonify({"error": "Error interno del servidor."}), 500


@auth_bp.post("/password/reset-request")
def verificar_telefono_ruta():
    #  Validación de campo requerido
    required = ["telefono"]
    data, error_response = validate_request_data(required)
    if error_response:
        return jsonify(error_response), 400

    try:
        # Llamada al servicio de verificación
        usuario = verificar_existencia_telefono(data['telefono'])
        
        # Validación de existencia
        if usuario:
            return jsonify({
                "mensaje": "Teléfono válido. Procede con el cambio de contraseña."
            }), 200
        else:
            return jsonify({"error": "No existe un usuario con ese número."}), 404
            
    except SQLAlchemyError:
        # Manejo de errores de base de datos
        return jsonify({"error": "Error de base de datos al verificar teléfono."}), 500
    except Exception:
        # Manejo de errores internos inesperados
        return jsonify({"error": "Error interno del servidor."}), 500


@auth_bp.patch("/password")
def cambiar_contrasena_ruta():
    # Validación de campos requeridos
    required = ["telefono", "nueva_contrasena", "confirmar_contrasena"]
    data, error_response = validate_request_data(required)
    if error_response:
        return jsonify(error_response), 400

    # Validación de coincidencia de contraseñas
    if data["nueva_contrasena"] != data["confirmar_contrasena"]:
        return jsonify({"error": "Las contraseñas no coinciden."}), 400
    
    try:
        # Llamada al servicio de restablecimiento
        exito, error = restablecer_contrasena(data["telefono"], data["nueva_contrasena"])
        
        # Manejo de error de servicio (ej: usuario no encontrado)
        if error:
            return jsonify({"error": error}), 404

        # Respuesta exitosa
        return jsonify({"mensaje": "Contraseña actualizada correctamente."}), 200
        
    except SQLAlchemyError:
        # Manejo de errores de base de datos
        return jsonify({"error": "Error de base de datos al actualizar contraseña."}), 500
    except Exception:
        # Manejo de errores internos inesperados
        return jsonify({"error": "Error interno del servidor."}), 500