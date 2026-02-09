#!/usr/bin/env python3
import requests
from datetime import datetime
import time

# Configuración
THEHIVE_URL = "http://localhost:9000/api/alert"
API_KEY = "dIVmJS4fK9m7QxJdygdf6RpVhH2hxRa5"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Alertas simples sin artefactos para test
ALERTAS = [
    {
        "title": "Intento de Fuerza Bruta en SSH",
        "description": "Multiples intentos fallidos de autenticacion SSH desde el rango 192.168.1.100",
        "severity": 3,
        "type": "external",
        "source": "SIEM - Simulador",
        "sourceRef": f"ssh_bruteforce_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    },
    {
        "title": "Deteccion de Malware - EICAR",
        "description": "Antivirus detecto archivo malicioso /home/user/downloads/setup.exe",
        "severity": 4,
        "type": "external",
        "source": "SIEM - Simulador",
        "sourceRef": f"malware_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    },
    {
        "title": "Escalada de Privilegios Detectada",
        "description": "Se detecto acceso root no autorizado desde IP 172.16.0.22",
        "severity": 4,
        "type": "external",
        "source": "SIEM - Simulador",
        "sourceRef": f"privesc_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    },
    {
        "title": "Exfiltracion de Datos - Trafico Anomalo",
        "description": "Transferencia anomala de datos hacia IP externa 10.0.0.55",
        "severity": 3,
        "type": "external",
        "source": "SIEM - Simulador",
        "sourceRef": f"exfil_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    }
]

def crear_alerta(alerta_dict):
    """Crea una alerta en TheHive"""
    max_intentos = 2
    for intento in range(max_intentos):
        try:
            respuesta = requests.post(
                THEHIVE_URL,
                json=alerta_dict,
                headers=HEADERS,
                timeout=10
            )
            
            if respuesta.status_code in [200, 201]:
                print(f"[OK] '{alerta_dict['title']}' creada exitosamente")
                return True
            else:
                print(f"[ERROR] '{alerta_dict['title']}': HTTP {respuesta.status_code}")
                if intento < max_intentos - 1:
                    print(f"  Contenido: {respuesta.text[:200]}")
                    time.sleep(2)
        except Exception as e:
            print(f"[ERROR] {alerta_dict['title']}: {e}")
            if intento < max_intentos - 1:
                time.sleep(2)
    
    return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("CREANDO ALERTAS EN THEHIVE (v2.0 - SIMPLIFICADO)")
    print("="*60)
    
    alertas_creadas = 0
    for alerta in ALERTAS:
        if crear_alerta(alerta):
            alertas_creadas += 1
        time.sleep(1)
    
    print(f"\n{alertas_creadas}/{len(ALERTAS)} alertas creadas")
    print("="*60 + "\n")
