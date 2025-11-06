"""
Funciones para interpretar las predicciones del biodigestor.
"""

def obtener_recomendacion(estado, temperatura, presion, gas):
    """
    Retorna una recomendación según el estado binario (0 = normal, 1 = alerta).
    Usa los valores crudos de los sensores para refinar el tipo de alerta.
    
    :param estado: Predicción binaria del modelo (0 o 1).
    :param temperatura: Valor de la temperatura en Celsius.
    :param presion: Valor de la presión en kPa.
    :param gas: Valor de la concentración de gas en ppm.
    :return: Diccionario con tipo, mensaje y recomendación.
    """

    if estado == 0:
        return {
            "tipo": "Normal",
            "mensaje": (
                f"Sistema estable. "
                f"Temperatura: {temperatura}°C | Presión: {presion} kPa | Gas: {gas} ppm."
            ),
            "recomendacion": (
                "Mantén el sistema monitoreado. Revisa válvulas y conexiones semanalmente."
            )
        }

    elif estado == 1:
        # 💡 Lógica basada en rangos típicos de biodigestores para refinar la recomendación
        
        # Temperatura: El rango mesofílico va de 20-45°C. Usamos 25-40 para alertas preventivas.
        if temperatura < 25:
            tipo = "Temperatura baja"
            recomendacion = "Aumenta la temperatura del biodigestor o mejora el aislamiento térmico."
        elif temperatura > 40:
            tipo = "Temperatura alta"
            recomendacion = "Evita exposición directa al sol o usa una cubierta parcial."
        
        # Presión: Valores de biogás saludables pueden variar, pero una caída es crítica.
        elif presion < 90:
            tipo = "Presión baja"
            recomendacion = "Verifica fugas o bloqueos en las tuberías. Puede indicar baja actividad."
        
        # Gas (MQ-4, metano): Los valores altos de metano son buenos, pero un sensor MQ-4 con lectura muy alta 
        # sin liberar puede indicar riesgo o un problema de ventilación.
        elif gas > 700:
            tipo = "Nivel alto de gas"
            recomendacion = "Libera gas gradualmente o verifica el sistema de ventilación/almacenamiento."
            
        else:
            tipo = "Alerta general o anómala"
            recomendacion = "Revisa todos los sensores. La anomalía no se explica por un solo parámetro clave. Considera la fase del proceso."

        return {
            "tipo": f"Alerta: {tipo}",
            "mensaje": (
                f"Se detectó una condición anómala. "
                f"Temperatura: {temperatura}°C | Presión: {presion} kPa | Gas: {gas} ppm."
            ),
            "recomendacion": recomendacion
        }