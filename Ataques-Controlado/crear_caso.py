import requests

# Configuración
thehive_url = "http://localhost:9000/api/alert"
api_key = "dIVmJS4fK9m7QxJdygdf6RpVhH2hxRa5"  # Reemplaza por tu clave real

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Ejemplo de caso
alert = {
    "title": "Alerta de ataque detectado",
    "description": "Evento de ataque detectado en logs",
    "type": "external",
    "source": "Simulador",
    "sourceRef": "ataque.log",
    "artifacts": [
        {"dataType": "ip", "data": "192.168.1.100", "message": "IP atacante"}
    ]
}

response = requests.post(thehive_url, json=alert, headers=headers)
print(response.status_code, response.text)