#!/usr/bin/env python3
import requests
import json
from datetime import datetime

# Test simple
THEHIVE_URL = "http://localhost:9000/api/alert"
API_KEY = "dIVmJS4fK9m7QxJdygdf6RpVhH2hxRa5"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Una sola alerta simple para test
test_alert = {
    "title": "Test Alert v2.0",
    "description": "Esta es una alerta de prueba para verificar conectividad",
    "severity": 2,  # Probando con número
    "type": "external",
    "source": "Test Script",
    "sourceRef": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}"
}

print("Intentando crear alerta de test...")
print(f"URL: {THEHIVE_URL}")
print(f"Headers: {HEADERS}")
print(f"Payload: {json.dumps(test_alert, indent=2)}")

try:
    response = requests.post(THEHIVE_URL, json=test_alert, headers=HEADERS, timeout=10)
    print(f"\nRespuesta: HTTP {response.status_code}")
    print(f"Contenido: {response.text}")
except Exception as e:
    print(f"Error: {e}")
