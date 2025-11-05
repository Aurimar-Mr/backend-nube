import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

# --- Importaciones de las funciones del servicio ---
# ASUME que estas funciones están en services.user_service
# Necesitas una estructura de proyecto donde 'services' sea accesible,
# o ajustar la ruta de importación si es necesario.
from services.user_service import (
    crear_usuario, 
    login_usuario, 
    verificar_existencia_telefono, 
    restablecer_contrasena
)

# --- RUTAS DE MOCKEO ---
# Estas rutas DEBEN coincidir con dónde se importan 'db' y 'User' dentro de user_service.py
DB_PATCH = 'services.user_service.db'
USER_MODEL_PATCH = 'services.user_service.User'


# =================================================================
# 1. PRUEBAS UNITARIAS para crear_usuario
# =================================================================

@patch(DB_PATCH)
@patch(USER_MODEL_PATCH)
def test_crear_usuario_exitoso(MockUser, mock_db):
    """Prueba que un usuario es creado y la DB es llamada correctamente (commit)."""
    
    # 1. Configurar Mock: Simular que el teléfono NO existe
    MockUser.query.filter_by.return_value.first.return_value = None
    
    # 2. Configurar el retorno de la instancia de usuario creada (para el 'return user')
    mock_user_instance = MagicMock()
    MockUser.return_value = mock_user_instance 

    user, error = crear_usuario("TestName", "111", "pass")
    
    # 3. Verificaciones de resultado
    assert error is None
    assert user == mock_user_instance
    
    # 4. Verificaciones de comportamiento (Llamadas a Mocks)
    MockUser.assert_called_once_with(
        nombre="TestName", telefono="111", rol="usuario", estado="activo", conectado=False
    )
    mock_user_instance.set_password.assert_called_once_with("pass")
    
    mock_db.session.add.assert_called_once_with(mock_user_instance)
    mock_db.session.commit.assert_called_once()
    mock_db.session.rollback.assert_not_called()


@patch(DB_PATCH)
@patch(USER_MODEL_PATCH)
def test_crear_usuario_existente(MockUser, mock_db):
    """Prueba que falla si el teléfono ya está registrado, sin tocar la DB."""
    
    # Simular que el usuario YA existe
    MockUser.query.filter_by.return_value.first.return_value = MagicMock() 

    user, error = crear_usuario("TestName", "111", "pass")
    
    assert user is None
    assert "El teléfono ya está registrado" in error
    
    # Verificación: La lógica de guardar NUNCA debe ser llamada
    mock_db.session.add.assert_not_called()
    mock_db.session.commit.assert_not_called()


@patch(DB_PATCH)
@patch(USER_MODEL_PATCH)
def test_crear_usuario_falla_db(MockUser, mock_db):
    """Prueba que maneja errores de la DB (rollback) durante el commit."""
    
    MockUser.query.filter_by.return_value.first.return_value = None
    MockUser.return_value = MagicMock()
    
    # Simular que db.session.commit lanza una excepción
    mock_db.session.commit.side_effect = Exception("DB Error")

    user, error = crear_usuario("TestName", "111", "pass")
    
    assert user is None
    assert "Error al guardar el usuario" in error
    
    # Verificación: Se debe haber llamado a rollback
    mock_db.session.add.assert_called_once()
    mock_db.session.rollback.assert_called_once()


# =================================================================
# 2. PRUEBAS UNITARIAS para login_usuario
# =================================================================

# Mockeamos datetime para controlar el valor de ultima_conexion
@patch('services.user_service.datetime') 
@patch(USER_MODEL_PATCH)
def test_login_usuario_exitoso(MockUser, mock_datetime):
    """Debe retornar el usuario, verificar la password y actualizar la conexión."""
    
    mock_user_instance = MagicMock()
    # 1. Configurar Mock: Simular éxito en la verificación de password
    mock_user_instance.check_password.return_value = True 
    MockUser.query.filter_by.return_value.first.return_value = mock_user_instance
    
    # 2. Configurar el valor de la fecha actual
    now = datetime(2025, 1, 1, 12, 0, 0)
    mock_datetime.now.return_value = now
    
    user = login_usuario("111", "pass_correcta")
    
    assert user == mock_user_instance
    
    # 3. Verificaciones de comportamiento
    mock_user_instance.check_password.assert_called_once_with("pass_correcta")
    
    # Verificaciones de actualización de campos y commit
    assert user.conectado is True
    assert user.ultima_conexion == now
    # El commit se llama en la sesión del objeto usuario mockeado
    mock_user_instance._obj_session.commit.assert_called_once()


@patch(USER_MODEL_PATCH)
def test_login_usuario_password_incorrecta(MockUser):
    """Debe fallar si la contraseña es incorrecta."""
    
    mock_user_instance = MagicMock()
    # Falla en la verificación de password
    mock_user_instance.check_password.return_value = False 
    MockUser.query.filter_by.return_value.first.return_value = mock_user_instance
    
    user = login_usuario("111", "pass_incorrecta")
    
    assert user is None
    mock_user_instance.check_password.assert_called_once_with("pass_incorrecta")
    
    # No debe haber commit
    mock_user_instance._obj_session.commit.assert_not_called()


@patch(USER_MODEL_PATCH)
def test_login_usuario_no_existe(MockUser):
    """Debe fallar si el teléfono no existe."""
    
    # Simular que NO se encuentra el usuario
    MockUser.query.filter_by.return_value.first.return_value = None
    
    user = login_usuario("999", "pass")
    
    assert user is None
    
    # check_password nunca debe ser llamado si el usuario no existe
    MockUser.query.filter_by.return_value.first.assert_called_once()


# =================================================================
# 3. PRUEBAS UNITARIAS para verificar_existencia_telefono
# =================================================================

@patch(USER_MODEL_PATCH)
def test_verificar_existencia_telefono_encontrado(MockUser):
    """Debe retornar el usuario si existe."""
    mock_user = MagicMock()
    MockUser.query.filter_by.return_value.first.return_value = mock_user
    
    usuario = verificar_existencia_telefono("111")
    
    assert usuario == mock_user

@patch(USER_MODEL_PATCH)
def test_verificar_existencia_telefono_no_encontrado(MockUser):
    """Debe retornar None si el usuario no existe."""
    MockUser.query.filter_by.return_value.first.return_value = None
    
    usuario = verificar_existencia_telefono("999")
    
    assert usuario is None


# =================================================================
# 4. PRUEBAS UNITARIAS para restablecer_contrasena
# =================================================================

@patch(DB_PATCH)
@patch(USER_MODEL_PATCH)
def test_restablecer_contrasena_exitoso(MockUser, mock_db):
    """Debe actualizar la contraseña y hacer commit."""
    
    mock_user_instance = MagicMock()
    MockUser.query.filter_by.return_value.first.return_value = mock_user_instance
    
    exito, error = restablecer_contrasena("111", "nueva_pass")
    
    assert exito is True
    assert error is None
    
    mock_user_instance.set_password.assert_called_once_with("nueva_pass")
    mock_db.session.commit.assert_called_once()
    mock_db.session.rollback.assert_not_called()


@patch(USER_MODEL_PATCH)
def test_restablecer_contrasena_no_encontrado(MockUser):
    """Debe fallar si el usuario no existe."""
    
    MockUser.query.filter_by.return_value.first.return_value = None
    
    exito, error = restablecer_contrasena("999", "nueva_pass")
    
    assert exito is False
    assert "No se encontró el usuario" in error
    

@patch(DB_PATCH)
@patch(USER_MODEL_PATCH)
def test_restablecer_contrasena_falla_db(MockUser, mock_db):
    """Debe llamar a rollback si falla el commit."""
    
    mock_user_instance = MagicMock()
    MockUser.query.filter_by.return_value.first.return_value = mock_user_instance
    
    # Simular que db.session.commit lanza una excepción
    mock_db.session.commit.side_effect = Exception("DB Error")
    
    exito, error = restablecer_contrasena("111", "nueva_pass")
    
    assert exito is False
    assert "Error al actualizar la contraseña" in error
    
    mock_db.session.rollback.assert_called_once()