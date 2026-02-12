import requests
from datetime import datetime

# Configuración
thehive_url = "http://localhost:9000/api/alert"
api_key = "68wSRNnhHOZ99aqIvdgZhNJU7OHXIzn6"  # Tu API key real

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Lista de alertas a crear
alertas = [
    {"title": "Ataque SSH detectado", "ip": "192.168.1.100"},
    {"title": "Intento de intrusión", "ip": "10.0.0.55"},
    {"title": "Malware detectado", "ip": "172.16.0.22"}
]

# Función para crear una alerta
def crear_alerta(alert_info):
    alert = {
        "title": alert_info["title"],
        "description": f"Evento detectado en logs desde IP {alert_info['ip']}",
        "type": "external",
        "source": "Simulador",
        # sourceRef único combinando título + timestamp
        "sourceRef": f"{alert_info['title'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "artifacts": [
            {"dataType": "ip", "data": alert_info["ip"], "message": "IP atacante"}
        ]
    }

    response = requests.post(thehive_url, json=alert, headers=headers)
    print(f"{alert_info['title']}: {response.status_code} {response.text}")

# Crear todas las alertas
for alerta in alertas:
    crear_alerta(alerta)
