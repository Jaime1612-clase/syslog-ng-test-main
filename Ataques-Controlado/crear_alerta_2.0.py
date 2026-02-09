#!/usr/bin/env python3
import requests
import json
from datetime import datetime
import time
import sys

# Configuración
THEHIVE_URL = "http://localhost:9000/api/alert"
API_KEY = "dIVmJS4fK9m7QxJdygdf6RpVhH2hxRa5"

# TheHive v5.1 requiere Bearer token sin "Bearer" prefix en algunos casos
# Pero la forma más segura es:
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Alertas correspondientes a la simulación de ataques
ALERTAS = [
    {
        "title": "Reconocimiento de Red - Port Scan Detectado",
        "description": "Se detectaron múltiples sondeos de puertos provenientes de múltiples direcciones IP remotas.",
        "severity": 3,
        "type": "external",
        "source": "SIEM - Simulador",
        "sourceRef": f"port_scan_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "artifacts": [
            {"dataType": "ip", "data": "192.168.1.100", "message": "IP atacante - Fase reconnaissance"},
            {"dataType": "ip", "data": "10.0.0.55", "message": "IP atacante - Fase reconnaissance"},
            {"dataType": "ip", "data": "172.16.0.22", "message": "IP atacante - Fase reconnaissance"}
        ]
    },
    {
        "title": "Intento de Fuerza Bruta en SSH",
        "description": "Múltiples intentos fallidos de autenticación SSH con usuarios inválidos y contraseñas.",
        "severity": 3,
        "type": "external",
        "source": "SIEM - Simulador",
        "sourceRef": f"ssh_bruteforce_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "artifacts": [
            {"dataType": "ip", "data": "192.168.1.100", "message": "IP atacante - Intento de fuerza bruta"},
            {"dataType": "user-account", "data": "admin", "message": "Usuario objetivo - Ataque de diccionario"},
            {"dataType": "user-account", "data": "root", "message": "Usuario objetivo - Ataque de diccionario"}
        ]
    },
    {
        "title": "Detección de Malware - EICAR",
        "description": "Antivirus (ClamAV) detectó archivo malicioso conocido en el sistema. Firma EICAR-STANDARD-ANTIVIRUS-TEST-FILE.",
        "severity": 4,
        "type": "external",
        "source": "SIEM - Simulador",
        "sourceRef": f"malware_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "artifacts": [
            {"dataType": "file", "data": "/home/user/downloads/setup.exe", "message": "Archivo malicioso detectado"},
            {"dataType": "hash", "data": "d131dd02c5e6eec4693d61a8a095f2e688df66e7", "message": "SHA-1 de malware conocido"}
        ]
    },
    {
        "title": "Escalada de Privilegios Detectada",
        "description": "Se detectó un intento de escalada de privilegios con comando sudo y acceso root.",
        "severity": 4,
        "type": "external",
        "source": "SIEM - Simulador",
        "sourceRef": f"privesc_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "artifacts": [
            {"dataType": "ip", "data": "172.16.0.22", "message": "IP atacante - Acceso remoto comprometido"},
            {"dataType": "user-account", "data": "attacker", "message": "Cuenta comprometida"},
            {"dataType": "process", "data": "/bin/bash", "message": "Proceso shell de ataque"}
        ]
    },
    {
        "title": "Exfiltración de Datos - Tráfico Anómalo",
        "description": "Se detectó transferencia anómala de datos a dirección IP externa. Posible exfiltración de información sensible.",
        "severity": 3,
        "type": "external",
        "source": "SIEM - Simulador",
        "sourceRef": f"exfil_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "artifacts": [
            {"dataType": "ip", "data": "10.0.0.55", "message": "Servidor C2 (Command & Control)"},
            {"dataType": "domain", "data": "malicious-domain.xyz", "message": "Dominio sospechoso"},
            {"dataType": "file", "data": "/etc/shadow", "message": "Archivo sensible accedido"}
        ]
    }
]

def crear_alerta(alerta_dict):
    """Crea una alerta en TheHive con manejo de reintentos"""
    max_intentos = 3
    for intento in range(max_intentos):
        try:
            respuesta = requests.post(
                THEHIVE_URL, 
                json=alerta_dict, 
                headers=HEADERS, 
                timeout=10
            )
            
            if respuesta.status_code in [200, 201]:
                print(f"✓ '{alerta_dict['title']}' creada exitosamente")
                return True
            else:
                print(f"✗ Error al crear '{alerta_dict['title']}': HTTP {respuesta.status_code}")
                if intento < max_intentos - 1:
                    print(f"  Reintentando en 2 segundos...")
                    time.sleep(2)
        except requests.exceptions.ConnectionError:
            print(f"✗ Error de conexión con TheHive. ¿Está levantado en localhost:9000?")
            if intento < max_intentos - 1:
                time.sleep(2)
        except Exception as e:
            print(f"✗ Error inesperado: {e}")
            if intento < max_intentos - 1:
                time.sleep(2)
    
    return False

# Función principal
if __name__ == "__main__":
    print("\n" + "="*60)
    print("CREANDO ALERTAS DE SEGURIDAD EN THEHIVE (v2.0)")
    print("="*60)
    
    alertas_creadas = 0
    for alerta in ALERTAS:
        if crear_alerta(alerta):
            alertas_creadas += 1
        time.sleep(1)  # Pausa entre alertas para no sobrecargar
    
    print(f"\n{alertas_creadas}/{len(ALERTAS)} alertas creadas exitosamente")
    
    if alertas_creadas == 0:
        print("\n⚠ Advertencia: No se crearon alertas. Verifica que TheHive esté disponible en http://localhost:9000")
        sys.exit(1)
    
    print("\nAlerta: Accede a http://localhost:9000 para ver las alertas (credenciales: admin/secret)")
    print("="*60 + "\n")
