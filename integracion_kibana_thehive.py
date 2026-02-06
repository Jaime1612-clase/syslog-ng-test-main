import requests
from elasticsearch import Elasticsearch
import time

# Configuración
ELASTICSEARCH_HOST = "localhost"
ELASTICSEARCH_PORT = 9200
THEHIVE_URL = "http://localhost:9000/api/alert"
THEHIVE_API_KEY = "ept5rd2DyjgWqIts08itHju1WaKpkkrb"  # Reemplaza por tu clave real

# Inicializar Elasticsearch
es = Elasticsearch([{'host': ELASTICSEARCH_HOST, 'port': ELASTICSEARCH_PORT, 'scheme': 'http'}])

headers = {
    "Authorization": f"Bearer {THEHIVE_API_KEY}",
    "Content-Type": "application/json"
}

# Consulta para buscar logs de ataques (ejemplo: intentos fallidos de login)
query = {
    "query": {
        "match_phrase": {"message": "Failed password"}
    }
}

# Buscar logs recientes
response = es.search(index="*", body=query, size=5)
for hit in response['hits']['hits']:
    log = hit['_source']
    ip = ""
    if "from" in log['message']:
        # Extraer IP del mensaje
        parts = log['message'].split()
        for i, part in enumerate(parts):
            if part == "from":
                ip = parts[i+1]
    # Crear alerta en TheHive
    alert = {
        "title": "Intento de acceso sospechoso",
        "description": log['message'],
        "type": "external",
        "source": "Elasticsearch",
        "sourceRef": hit['_id'],
        "artifacts": [
            {"dataType": "ip", "data": ip, "message": "IP atacante"}
        ]
    }
    r = requests.post(THEHIVE_URL, json=alert, headers=headers)
    print(f"Alerta enviada: {r.status_code} {r.text}")
    time.sleep(1)

print("Integración completada. Revisa TheHive para los casos generados.")
