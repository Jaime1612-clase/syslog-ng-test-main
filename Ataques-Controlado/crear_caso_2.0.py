#!/usr/bin/env python3
import requests
import json
from datetime import datetime
import time
import sys

# Configuración
THEHIVE_URL = "http://localhost:9000/api"
API_KEY = "dIVmJS4fK9m7QxJdygdf6RpVhH2hxRa5"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Casos de incidentes para crear manualmente (si no se pueden obtener de alertas)
CASOS = [
    {
        "title": "INC-2026-001: Reconocimiento de infraestructura",
        "description": """
DESCRIPCIÓN DEL INCIDENTE:
Se detectó un escaneo de puertos masivo dirigido contra la infraestructura corporativa.
Se identificaron intentos de reconocimiento de red desde múltiples direcciones IP externas.

SEVERIDAD: Alta
TIPO: Reconnaissance (Fase inicial de ataque)
ESTADO: Abierto
PRIORIDAD: 1

INDICADORES DE COMPROMISO (IOCs):
- Múltiples sondeos ICMP desde rango 192.168.1.0/24
- Port scanning hacia puertos estándar (22, 80, 443, 3389)
- Respuestas anormales de servicios
        """,
        "severity": 3,
        "tlp": 2,
        "pap": 2,
        "status": "Open",
        "resolutionStatus": "Unresolved",
        "owner": "admin",
        "tags": ["ciberseguridad", "intrusion-detection", "network-scanning"],
        "customFields": {
            "Clasificacion": "VERIS/Initial Access",
            "SLA": "4h",
            "Criticidad": "Alta"
        }
    },
    {
        "title": "INC-2026-002: Intento de acceso no autorizado SSH",
        "description": """
DESCRIPCIÓN DEL INCIDENTE:
Se detectaron múltiples intentos de fuerza bruta en el servicio SSH (puerto 22).
Se probaron usuarios comunes (admin, root, oracle, backup, test) con diferentes contraseñas.

SEVERIDAD: Alta
TIPO: Credential Access (Ataque de diccionario)
ESTADO: Abierto
PRIORIDAD: 1

INDICADORES DE COMPROMISO (IOCs):
- 20 intentos fallidos de autenticación SSH
- Patrones de ataque de fuerza bruta (timing < 400ms entre intentos)
- IP origen: 192.168.1.100
- Puertos dinámicos utilizados: 22
        """,
        "severity": 3,
        "tlp": 2,
        "pap": 2,
        "status": "Open",
        "resolutionStatus": "Unresolved",
        "owner": "admin",
        "tags": ["ciberseguridad", "brute-force", "authentication"],
        "customFields": {
            "Clasificacion": "VERIS/Credential Access",
            "SLA": "2h",
            "Criticidad": "Alta"
        }
    },
    {
        "title": "INC-2026-003: Detección de malware EICAR",
        "description": """
DESCRIPCIÓN DEL INCIDENTE:
Antivirus (ClamAV) detectó archivo malicioso conocido (EICAR test file) en el sistema de archivos.
Este archivo es comúnmente usado para probar funcionalidad de antivirus pero su presencia indica 
exposición a riesgos.

SEVERIDAD: Crítica
TIPO: Execution / Malicious Code (Malware Detection)
ESTADO: Abierto
PRIORIDAD: 0 (Crítica)

INDICADORES DE COMPROMISO (IOCs):
- Firma antivirus: EICAR-STANDARD-ANTIVIRUS-TEST-FILE
- Ruta del archivo: /home/user/downloads/setup.exe
- Fecha de detección: 2026-02-09
- Sistema afectado: syslog-client
        """,
        "severity": 4,
        "tlp": 1,
        "pap": 2,
        "status": "Open",
        "resolutionStatus": "Unresolved",
        "owner": "admin",
        "tags": ["ciberseguridad", "malware", "execution"],
        "customFields": {
            "Clasificacion": "VERIS/Malware",
            "SLA": "1h",
            "Criticidad": "Crítica"
        }
    },
    {
        "title": "INC-2026-004: Escalada de privilegios detectada",
        "description": """
DESCRIPCIÓN DEL INCIDENTE:
Se detectó un intento exitoso de escalada de privilegios con acceso root no autorizado.
El usuario 'attacker' ejecutó comandos con permisos elevados sin autorización.

SEVERIDAD: Crítica
TIPO: Privilege Escalation (Acceso root comprometido)
ESTADO: Abierto
PRIORIDAD: 0 (Crítica)

INDICADORES DE COMPROMISO (IOCs):
- Usuario: attacker (cuenta comprometida)
- IP origen: 172.16.0.22
- Comando ejecutado: /bin/bash con UID=0
- Método: Cadena de explotación multi-stage
        """,
        "severity": 4,
        "tlp": 1,
        "pap": 2,
        "status": "Open",
        "resolutionStatus": "Unresolved",
        "owner": "admin",
        "tags": ["ciberseguridad", "privilege-escalation", "root-access"],
        "customFields": {
            "Clasificacion": "VERIS/Privilege Escalation",
            "SLA": "1h",
            "Criticidad": "Crítica"
        }
    },
    {
        "title": "INC-2026-005: Exfiltración de datos sospechosa",
        "description": """
DESCRIPCIÓN DEL INCIDENTE:
Se detectó tráfico de red anómalo indicativo de exfiltración de datos hacia servidores de control remoto.
Transferencia de archivos sensibles (/etc/shadow) a través de canales no autorizados.

SEVERIDAD: Crítica
TIPO: Exfiltration (Robo de datos)
ESTADO: Abierto
PRIORIDAD: 0 (Crítica)

INDICADORES DE COMPROMISO (IOCs):
- Servidores C2 (Command & Control): 10.0.0.55:21 (FTP), múltiples puertos Snort
- Volumen transferido: 1.250 GB
- Nivel de confianza: Alto (patrones conocidos de APT)
- Archivos accedidos: /etc/shadow, credenciales del sistema
        """,
        "severity": 4,
        "tlp": 1,
        "pap": 2,
        "status": "Open",
        "resolutionStatus": "Unresolved",
        "owner": "admin",
        "tags": ["ciberseguridad", "exfiltration", "data-breach"],
        "customFields": {
            "Clasificacion": "VERIS/Exfiltration",
            "SLA": "1h",
            "Criticidad": "Crítica"
        }
    }
]

def crear_caso(caso_dict):
    """Crea un caso en TheHive"""
    url = f"{THEHIVE_URL}/case"
    max_intentos = 3
    
    for intento in range(max_intentos):
        try:
            respuesta = requests.post(
                url,
                json=caso_dict,
                headers=HEADERS,
                timeout=10
            )
            
            if respuesta.status_code in [200, 201]:
                try:
                    caso_id = respuesta.json().get('id', 'desconocido')
                    print(f"✓ '{caso_dict['title']}' (ID: {caso_id}) creado exitosamente")
                except:
                    print(f"✓ '{caso_dict['title']}' creado exitosamente")
                return True
            else:
                print(f"✗ Error al crear '{caso_dict['title']}': HTTP {respuesta.status_code}")
                if intento < max_intentos - 1:
                    print(f"  Reintentando en 2 segundos...")
                    time.sleep(2)
        except requests.exceptions.ConnectionError:
            print(f"✗ Error de conexión con TheHive.")
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
    print("CREANDO CASOS DE INCIDENTES EN THEHIVE (v2.0)")
    print("="*60)
    
    casos_creados = 0
    for caso in CASOS:
        if crear_caso(caso):
            casos_creados += 1
        time.sleep(1)  # Pausa entre casos
    
    print(f"\n{casos_creados}/{len(CASOS)} casos creados exitosamente")
    
    if casos_creados == 0:
        print("\n⚠ Advertencia: No se crearon casos. Verifica que TheHive esté disponible.")
        sys.exit(1)
    
    print("\nPróximo paso: Ve a http://localhost:9000 para revisar los casos")
    print("Clasificación: Los casos incluyen taxonomía VERIS/ENISA cómo se requiere")
    print("="*60 + "\n")
