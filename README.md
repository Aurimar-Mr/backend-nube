# BMIS Backend - Biodigestor Monitoring Intelligent System

## Descripción
Este proyecto es un **backend en Flask** para un sistema de monitoreo de biodigestores. Permite:  

- Registrar lecturas de sensores.  
- Gestionar sensores y procesos.  
- Configurar gráficas.  
- Administrar usuarios.  
- Configurar alertas de voz.  

---

## Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/bmis-backend.git
cd bmis-backend
```

### 2.  Crear Entorno virtual
```bash
python -m venv venv
# Linux / Mac
source venv/bin/activate
# Windows
venv\Scripts\activate

```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```
### 4. Configurar variables de entorno

Crear un archivo .env si es necesario y agregar las variables de configuración (BD).

## Running
Ejecutar la aplicación:
```bash
py main.py
```
El backend quedará corriendo por defecto en: http://localhost:5000

## Versioning
Se uso Github con la metodología Git Flow

## Built With
Flask - Framework
Python - Programming languague