#!/usr/bin/env python3
"""
Genera alertas en TheHive basadas en análisis de logs generados por simulador_logs_2.0.ps1
Los logs son analizados y se crean alertas inteligentemente según los patrones detectados
"""

import requests
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Configuración
THEHIVE_URL = "http://localhost:9000/api/alert"
API_KEY = "dIVmJS4fK9m7QxJdygdf6RpVhH2hxRa5"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# ============================================================
# FUNCIONES DE ANÁLISIS DE LOGS
# ============================================================

def parse_logs(log_file):
    """Lee y parsea los eventos del archivo de log"""
    events = []
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(line)
    except FileNotFoundError:
        print(f"[ERROR] Archivo de log no encontrado: {log_file}")
        sys.exit(1)
    
    print(f"[INFO] {len(events)} eventos leídos del log")
    return events

def detect_patterns(events):
    """Detecta patrones de ataque en los logs"""
    patterns = defaultdict(list)
    
    # Detectar Port Scan
    port_scans = [e for e in events if '[UFW BLOCK]' in e]
    if port_scans:
        patterns['port_scan'] = {
            'events': port_scans,
            'count': len(port_scans),
            'ips': set(re.findall(r'SRC=([0-9\.]+)', ' '.join(port_scans)))
        }
    
    # Detectar SSH Brute Force
    ssh_failures = [e for e in events if 'Failed password' in e]
    if ssh_failures:
        patterns['ssh_brute_force'] = {
            'events': ssh_failures,
            'count': len(ssh_failures),
            'ips': set(re.findall(r'from ([0-9\.]+)', ' '.join(ssh_failures))),
            'users': set(re.findall(r'invalid user (\w+)', ' '.join(ssh_failures)))
        }
    
    # Detectar Anomalías de Red
    anomalies = [e for e in events if '[ANOMALY]' in e or '[ANOMLAY]' in e or 'SYN FLOOD' in e]
    if anomalies:
        patterns['network_anomaly'] = {
            'events': anomalies,
            'count': len(anomalies),
            'ips': set(re.findall(r'SRC=([0-9\.]+)', ' '.join(anomalies)))
        }
    
    # Detectar Malware
    malware = [e for e in events if '[MALWARE]' in e or '[THREAT]' in e or 'ClamAV' in e]
    if malware:
        patterns['malware'] = {
            'events': malware,
            'count': len(malware),
            'files': set(re.findall(r'in ([^\s]+)', ' '.join(malware))),
            'threats': set(re.findall(r'detected ([A-Z0-9\-\.]+)', ' '.join(malware)))
        }
    
    # Detectar Privilege Escalation
    privesc = [e for e in events if '[PRIVESC]' in e or 'Buffer overflow' in e or 'sudo' in e and 'USER=root' in e]
    if privesc:
        patterns['privilege_escalation'] = {
            'events': privesc,
            'count': len(privesc),
            'users': set(re.findall(r'(\w+) :', ' '.join(privesc)))
        }
    
    # Detectar Exfiltración
    exfil = [e for e in events if '[DATA_EXFIL]' in e or 'ET MALWARE' in e or 'HIGH_DATA_TRANSFER' in e or 'SHELLCODE' in e]
    if exfil:
        patterns['data_exfiltration'] = {
            'events': exfil,
            'count': len(exfil),
            'ips': set(re.findall(r'(?:SRC=|from |src=)([0-9\.]+)', ' '.join(exfil))),
            'protocols': set(re.findall(r'(FTP|SSH|TCP|HTTPS?)', ' '.join(exfil)))
        }
    
    return patterns

def print_detection_summary(patterns):
    """Imprime un resumen de patrones detectados"""
    print("\n" + "="*60)
    print("📊 PATRONES DETECTADOS EN LOGS")
    print("="*60)
    
    if not patterns:
        print("[!] No se detectaron patrones de ataque")
        return
    
    for pattern_type, data in patterns.items():
        print(f"\n✓ {pattern_type.upper().replace('_', ' ')} ({data['count']} eventos)")
        
        if 'ips' in data and data['ips']:
            print(f"  IPs involucradas: {', '.join(sorted(data['ips']))}")
        
        if 'users' in data and data['users']:
            print(f"  Usuarios: {', '.join(sorted(data['users']))}")
        
        if 'files' in data and data['files']:
            print(f"  Archivos: {', '.join(sorted(data['files']))}")
        
        if 'protocols' in data and data['protocols']:
            print(f"  Protocolos: {', '.join(sorted(data['protocols']))}")

# ============================================================
# FUNCIONES DE CREACIÓN DE ALERTAS
# ============================================================

def create_alert_from_pattern(pattern_type, data):
    """Crea un objeto de alerta basado en el patrón detectado"""
    
    timestamp = datetime.now().isoformat()
    
    if pattern_type == 'port_scan':
        return {
            "title": f"Port Scan Detectado - {len(data['ips'])} IPs origen",
            "description": f"""
DETECCIÓN AUTOMÁTICA POR ANÁLISIS DE LOGS

Tipo: Reconnaissance - Port Scan
Severidad: Alto
Eventos correlacionados: {data['count']} intentos

IPs atacantes detectadas:
{', '.join(sorted(data['ips']))}

Evidencia: Múltiples intentos de conexión a puertos bloqueados detectados por UFW.
Indica fase inicial de reconocimiento de infraestructura.
            """.strip(),
            "severity": 3,
            "type": "external",
            "source": "SIEM - Log Analysis v2.0",
            "sourceRef": f"port_scan_{timestamp}",
            "artifacts": [
                {"dataType": "ip", "data": ip, "message": f"IP origen - Port Scan"}
                for ip in sorted(list(data['ips']))[:3]
            ]
        }
    
    elif pattern_type == 'ssh_brute_force':
        return {
            "title": f"SSH Brute Force Detectado - {len(data['ips'])} IPs",
            "description": f"""
DETECCIÓN AUTOMÁTICA POR ANÁLISIS DE LOGS

Tipo: Initial Access - Credential Access
Severidad: Alto
Eventos correlacionados: {data['count']} intentos fallidos

IPs atacantes:
{', '.join(sorted(data['ips']))}

Usuarios atacados:
{', '.join(sorted(data['users']))}

Evidencia: Múltiples intentos de autenticación SSH fallidos desde la misma IP.
Patrón típico de ataque de fuerza bruta contra el servicio SSH.
            """.strip(),
            "severity": 3,
            "type": "external",
            "source": "SIEM - Log Analysis v2.0",
            "sourceRef": f"ssh_brute_{timestamp}",
            "artifacts": [
                {"dataType": "ip", "data": ip, "message": f"IP atacante - SSH Brute Force"}
                for ip in sorted(list(data['ips']))
            ]
        }
    
    elif pattern_type == 'network_anomaly':
        return {
            "title": f"Anomalía de Red Detectada - Tráfico anómalo",
            "description": f"""
DETECCIÓN AUTOMÁTICA POR ANÁLISIS DE LOGS

Tipo: Lateral Movement - Command & Control
Severidad: Alto
Eventos correlacionados: {data['count']} anomalías

IPs origen:
{', '.join(sorted(data['ips'])) if data['ips'] else 'Múltiples'}

Evidencia: Patrones de tráfico anómalo detectados
- Posibles ataques SYN Flood
- Intentos de escalada de privilegios
- Accesos no autorizados a recursos

Indicadores de movimiento lateral en la red.
            """.strip(),
            "severity": 3,
            "type": "external",
            "source": "SIEM - Log Analysis v2.0",
            "sourceRef": f"anomaly_{timestamp}",
            "artifacts": [
                {"dataType": "ip", "data": ip, "message": f"IP sospechosa"}
                for ip in sorted(list(data['ips']))[:3]
            ] if data['ips'] else []
        }
    
    elif pattern_type == 'malware':
        return {
            "title": f"Detección de Malware - {len(data['threats'])} amenazas",
            "description": f"""
DETECCIÓN AUTOMÁTICA POR ANÁLISIS DE LOGS

Tipo: Malware - Threat Detection
Severidad: CRÍTICO
Eventos correlacionados: {data['count']} detecciones

Amenazas detectadas:
{', '.join(sorted(data['threats']))}

Archivos comprometidos:
{', '.join(sorted(data['files'])) if data['files'] else 'Múltiples'}

Evidencia: Antivirus (ClamAV) ha detectado código malicioso.
Archivos sospechosos encontrados en el sistema.
Requiere aislamiento inmediato del hosts comprometido.
            """.strip(),
            "severity": 4,
            "type": "external",
            "source": "SIEM - Log Analysis v2.0",
            "sourceRef": f"malware_{timestamp}",
            "artifacts": [
                {"dataType": "file", "data": f, "message": f"Archivo con malware"}
                for f in sorted(list(data['files']))
            ] if data['files'] else []
        }
    
    elif pattern_type == 'privilege_escalation':
        return {
            "title": f"Escalada de Privilegios Detectada",
            "description": f"""
DETECCIÓN AUTOMÁTICA POR ANÁLISIS DE LOGS

Tipo: Privilege Escalation - Exploitation
Severidad: CRÍTICO
Eventos correlacionados: {data['count']} intentos

Usuarios involucrados:
{', '.join(sorted(data['users'])) if data['users'] else 'root'}

Evidencia: Intentos de escalada de privilegios detectados
- Buffer overflow en librerías del sistema
- Acceso a comandos root sin autorización
- Ejecución de sudo sin credenciales válidas

Ataque avanzado que requiere respuesta inmediata.
            """.strip(),
            "severity": 4,
            "type": "external",
            "source": "SIEM - Log Analysis v2.0",
            "sourceRef": f"privesc_{timestamp}",
            "artifacts": []
        }
    
    elif pattern_type == 'data_exfiltration':
        return {
            "title": f"Exfiltración de Datos - Transferencia masiva",
            "description": f"""
DETECCIÓN AUTOMÁTICA POR ANÁLISIS DE LOGS

Tipo: Exfiltration - Data Theft
Severidad: CRÍTICO
Eventos correlacionados: {data['count']} eventos

IPs destino:
{', '.join(sorted(data['ips'])) if data['ips'] else 'Externas'}

Protocolos utilizados:
{', '.join(sorted(data['protocols'])) if data['protocols'] else 'Múltiples'}

Evidencia: Transferencia masiva de datos hacia el exterior
- Conexiones FTP/SSH a servidores externos conocidos
- Tráfico de alta velocidad hacia IPs externas
- Ejecución de shellcode y herramientas de exfiltración

Indicación clara de robo de datos en progreso.
Requiere BLOQUEO INMEDIATO de conexiones externas.
            """.strip(),
            "severity": 4,
            "type": "external",
            "source": "SIEM - Log Analysis v2.0",
            "sourceRef": f"exfil_{timestamp}",
            "artifacts": [
                {"dataType": "ip", "data": ip, "message": f"IP destino - Exfiltración"}
                for ip in sorted(list(data['ips']))[:5]
            ] if data['ips'] else []
        }

def create_alerts_in_thehive(patterns):
    """Crea alertas en TheHive basadas en patrones detectados"""
    
    if not patterns:
        print("\n[!] No hay patrones para crear alertas")
        return 0
    
    print("\n" + "="*60)
    print("🚨 CREANDO ALERTAS EN THEHIVE")
    print("="*60)
    
    successful = 0
    
    for pattern_type, data in patterns.items():
        # Crear alerta
        alert = create_alert_from_pattern(pattern_type, data)
        
        # Enviar a TheHive
        try:
            response = requests.post(
                THEHIVE_URL,
                json=alert,
                headers=HEADERS,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                alert_id = response.json().get('id', 'N/A')
                print(f"\n✓ Alerta creada: {alert['title']}")
                print(f"  ID: {alert_id}")
                print(f"  Severidad: {'CRÍTICO' if alert['severity'] == 4 else 'ALTO'}")
                print(f"  Eventos correlacionados: {data['count']}")
                successful += 1
            else:
                print(f"\n✗ Error al crear alerta: {alert['title']}")
                print(f"  Status: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
        
        except requests.exceptions.ConnectionError:
            print(f"\n✗ Error: No se puede conectar a TheHive en {THEHIVE_URL}")
            print("  Asegúrate que: docker-compose up -d")
            return 0
        except Exception as e:
            print(f"\n✗ Error inesperado: {str(e)}")
    
    return successful

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("ANALIZADOR DE LOGS Y GENERADOR DE ALERTAS v2.0")
    print("="*60)
    
    # Ruta del archivo de logs - buscar dinámicamente
    logs_dir = Path(__file__).parent.parent / "logs" / "server" / "syslog-client"
    
    # Buscar el archivo más reciente que empiece con "ataque"
    log_files = list(logs_dir.glob("ataque*.log"))
    
    if not log_files:
        print(f"\n[ERROR] No se encontraron archivos ataque*.log en {logs_dir}")
        sys.exit(1)
    
    # Usar el más reciente
    log_file = max(log_files, key=lambda p: p.stat().st_mtime)
    
    print(f"\nAnalizando: {log_file}")
    
    # Leer y parsear logs
    events = parse_logs(str(log_file))
    
    # Detectar patrones
    patterns = detect_patterns(events)
    
    # Mostrar resumen de detecciones
    print_detection_summary(patterns)
    
    # Crear alertas en TheHive
    created = create_alerts_in_thehive(patterns)
    
    print("\n" + "="*60)
    print(f"✓ {created} alertas creadas exitosamente")
    print("="*60 + "\n")
