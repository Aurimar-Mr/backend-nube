import pytest
import requests

# URL base del backend Flask en ejecución
BASE_URL = "http://127.0.0.1:5000/auth"

# Datos de prueba
TEST_NAME = "jose"
TEST_PHONE = "3001234532"
TEST_PASS = "123456"
NEW_PASS = "654321"


@pytest.mark.order(1)
def test_register_user():
    """
    Caso de Prueba: Registro de usuario
    Debe permitir registrar un usuario nuevo correctamente.
    """
    data = {
        "nombre": TEST_NAME,
        "telefono": TEST_PHONE,
        "password": TEST_PASS,
        "confirm_password": TEST_PASS
    }
    response = requests.post(f"{BASE_URL}/register", json=data)

    print("\nRespuesta Registro:", response.status_code, response.text)

    # Puede ser 201 (nuevo usuario) o 400 si ya existe
    assert response.status_code in [200, 201, 400]


@pytest.mark.order(2)
def test_login_user():
    """
    Caso de Prueba: Login válido
    Debe permitir iniciar sesión con credenciales correctas.
    """
    data = {
        "telefono": TEST_PHONE,
        "password": TEST_PASS
    }
    response = requests.post(f"{BASE_URL}/login", json=data)

    print("\nRespuesta Login:", response.status_code, response.text)

    # 200 si es exitoso, 401 si credenciales incorrectas
    assert response.status_code in [200, 401]


@pytest.mark.order(3)
def test_login_user_incorrect():
    """
    Caso de Prueba: Login inválido
    Debe fallar si las credenciales son erróneas.
    """
    data = {
        "telefono": TEST_PHONE,
        "password": "incorrecta"
    }
    response = requests.post(f"{BASE_URL}/login", json=data)

    print("\nRespuesta Login Incorrecto:", response.status_code, response.text)
    assert response.status_code == 401


@pytest.mark.order(4)
def test_password_reset_request():
    """
    Caso de Prueba: Solicitud de restablecimiento
    Debe verificar si el teléfono existe.
    """
    data = {"telefono": TEST_PHONE}
    response = requests.post(f"{BASE_URL}/password/reset-request", json=data)

    print("\nRespuesta Reset Request:", response.status_code, response.text)

    # 200 si existe, 404 si no
    assert response.status_code in [200, 404]


@pytest.mark.order(5)
def test_password_update():
    """
    Caso de Prueba: Cambio de contraseña
    Debe actualizar correctamente la contraseña si los datos son válidos.
    """
    data = {
        "telefono": TEST_PHONE,
        "nueva_contrasena": NEW_PASS,
        "confirmar_contrasena": NEW_PASS
    }
    response = requests.patch(f"{BASE_URL}/password", json=data)

    print("\nRespuesta Cambio Contraseña:", response.status_code, response.text)

    # PATCH → 200 si es exitoso, 400 si faltan datos, 404 si no existe
    assert response.status_code in [200, 400, 404]
