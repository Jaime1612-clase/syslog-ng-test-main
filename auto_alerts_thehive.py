#!/usr/bin/env python3
"""
auto_alerts_thehive.py
Monitorea Elasticsearch continuamente y crea alertas automáticas en TheHive
sin necesidad de scripts separados.
"""

import requests
import time
import json
import re
import sys
from datetime import datetime, timedelta
from collections import defaultdict

# Configuración
ES_URL = "http://localhost:9200"
THEHIVE_URL = "http://localhost:9000/api/alert"
API_KEY = "hZo3qYekLTwks35KUJAHkfsw9CL6GPW0"
# TheHive uses simple Authorization header (no Bearer prefix for some versions)
HEADERS = {"Authorization": API_KEY, "Content-Type": "application/json"}

# Variables de control
LAST_ALERT_TIME = {}
MIN_INTERVAL = 300  # Mínimo 5 minutos entre alertas del mismo tipo
THEHIVE_CREATED = []

def log_msg(msg, level="INFO"):
    """Imprime mensaje con timestamp"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    colors = {
        "INFO": "\033[94m",
        "OK": "\033[92m",
        "WARN": "\033[93m",
        "ERROR": "\033[91m"
    }
    reset = "\033[0m"
    color = colors.get(level, "")
    print(f"{color}[{ts}] [{level}]{reset} {msg}")

def query_elasticsearch(query_body):
    """Ejecuta una búsqueda en Elasticsearch"""
    try:
        r = requests.get(f"{ES_URL}/_search", json=query_body, timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            log_msg(f"ES error: {r.status_code}", "ERROR")
            return None
    except Exception as e:
        log_msg(f"ES connection error: {e}", "ERROR")
        return None

def extract_ips_from_events(events, pattern):
    """Extrae IPs de los eventos usando un patrón regex"""
    ips = set()
    for event in events:
        msg = event.get('_source', {}).get('message', '')
        matches = re.findall(pattern, msg)
        ips.update(matches)
    return list(ips)

def create_thehive_alert(title, description, severity, source_ref, artifacts=None):
    """Crea una alerta en TheHive"""
    if artifacts is None:
        artifacts = []
    
    alert = {
        "title": title,
        "description": description,
        "type": "external",
        "source": "SIEM - Auto",
        "sourceRef": source_ref,
        "severity": severity,
        "artifacts": artifacts
    }
    
    try:
        r = requests.post(THEHIVE_URL, json=alert, headers=HEADERS, timeout=10)
        if r.status_code in (200, 201):
            log_msg(f"Alert created: {title}", "OK")
            THEHIVE_CREATED.append(title)
            return True
        else:
            log_msg(f"TheHive error: {r.status_code} - {r.text[:200]}", "ERROR")
            return False
    except Exception as e:
        log_msg(f"TheHive connection error: {e}", "ERROR")
        return False

def can_create_alert(alert_key):
    """Verifica si es tiempo de crear una nueva alerta"""
    now = time.time()
    last_time = LAST_ALERT_TIME.get(alert_key, 0)
    if now - last_time >= MIN_INTERVAL:
        LAST_ALERT_TIME[alert_key] = now
        return True
    return False

def detect_ssh_brute_force():
    """Detecta intentos de SSH Brute Force"""
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match_phrase": {"message": "Failed password"}}
                ],
                "filter": [
                    {"range": {"@timestamp": {"gte": "now-10m"}}}
                ]
            }
        },
        "size": 500
    }
    
    result = query_elasticsearch(query)
    if not result:
        return
    
    hits = result.get('hits', {}).get('hits', [])
    if len(hits) > 5 and can_create_alert("ssh_brute_force"):
        ips = extract_ips_from_events(hits, r'from ([0-9\.]+)')
        unique_ips = list(set(ips))
        artifacts = [{"dataType": "ip", "data": ip} for ip in unique_ips[:5]]
        create_thehive_alert(
            title=f"SSH Brute Force - {len(hits)} intentos desde {len(unique_ips)} IPs",
            description=f"Detectados {len(hits)} intentos fallidos de acceso SSH en los últimos 10 minutos desde {len(unique_ips)} IPs únicas.",
            severity=2,
            source_ref=f"ssh_brute_{int(time.time())}",
            artifacts=artifacts
        )

def detect_port_scanning():
    """Detecta escaneo de puertos"""
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match_phrase": {"message": "[UFW BLOCK]"}}
                ],
                "filter": [
                    {"range": {"@timestamp": {"gte": "now-10m"}}}
                ]
            }
        },
        "size": 500
    }
    
    result = query_elasticsearch(query)
    if not result:
        return
    
    hits = result.get('hits', {}).get('hits', [])
    if len(hits) > 10 and can_create_alert("port_scan"):
        ips = extract_ips_from_events(hits, r'SRC=([0-9\.]+)')
        unique_ips = list(set(ips))
        artifacts = [{"dataType": "ip", "data": ip} for ip in unique_ips[:5]]
        create_thehive_alert(
            title=f"Port Scanning - {len(hits)} eventos desde {len(unique_ips)} IPs",
            description=f"Detectados {len(hits)} intentos de escaneo de puertos (UFW BLOCK) en los últimos 10 minutos desde {len(unique_ips)} IPs.",
            severity=2,
            source_ref=f"port_scan_{int(time.time())}",
            artifacts=artifacts
        )

def detect_sql_injection():
    """Detecta SQL Injection"""
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match_phrase": {"message": "SQL INJECTION"}}
                ],
                "filter": [
                    {"range": {"@timestamp": {"gte": "now-10m"}}}
                ]
            }
        },500
    }
    
    result = query_elasticsearch(query)
    if not result:
        return
    
    hits = result.get('hits', {}).get('hits', [])
    if len(hits) > 3 and can_create_alert("sql_injection"):
        ips = extract_ips_from_events(hits, r'from ([0-9\.]+)')
        unique_ips = list(set(ips))
        artifacts = [{"dataType": "ip", "data": ip} for ip in unique_ips[:5]]
        create_thehive_alert(
            title=f"SQL Injection - {len(hits)} intentos desde {len(unique_ips
            title=f"SQL Injection - {len(hits)} intentos desde {len(set(ips))} IPs",
            description=f"Detectados {len(hits)} intentos de inyección SQL en los últimos 10 minutos.",
            severity=3,
            source_ref=f"sql_inject_{int(time.time())}",
            artifacts=artifacts
        )

def detect_malware():
    """Detecta malware"""
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match_phrase": {"message": "[MALWARE]"}}
                ],
                "filter": [
                    {"range": {"@timestamp": {"gte": "now-10m"}}}
                ]
            }
        },500
    }
    
    result = query_elasticsearch(query)
    if not result:
        return
    
    hits = result.get('hits', {}).get('hits', [])
    if len(hits) > 0 and can_create_alert("malware"):
        ips = extract_ips_from_events(hits, r'from ([0-9\.]+)')
        unique_ips = list(set(ips))
        artifacts = [{"dataType": "ip", "data": ip} for ip in unique_ips
        artifacts = [{"dataType": "ip", "data": ip} for ip in list(set(ips))[:5]]
        create_thehive_alert(
            title=f"Malware Detection - {len(hits)} eventos",
            description=f"Se han detectado {len(hits)} eventos de malware en los últimos 10 minutos.",
            severity=4,
            source_ref=f"malware_{int(time.time())}",
            artifacts=artifacts
        )

def detect_web_attacks():
    """Detecta ataques web"""
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match_phrase": {"message": "httpd"}}
                ],
                "filter": [
                    {"range": {"@timestamp": {"gte": "now-10m"}}}
                ]
            }
        },500
    }
    
    result = query_elasticsearch(query)
    if not result:
        return
    
    hits = result.get('hits', {}).get('hits', [])
    if len(hits) > 20 and can_create_alert("web_attack"):
        ips = extract_ips_from_events(hits, r'([0-9\.]+) - -')
        unique_ips = list(set(ips))
        artifacts = [{"dataType": "ip", "data": ip} for ip in unique_ips[:5]]
        create_thehive_alert(
            title=f"Web Attacks - {len(hits)} solicitudes sospechosas desde {len(unique_ips
            title=f"Web Attacks - {len(hits)} solicitudes sospechosas desde {len(set(ips))} IPs",
            description=f"Se han detectado {len(hits)} solicitudes HTTP sospechosas (403, 401, 404) en los últimos 10 minutos.",
            severity=2,
            source_ref=f"web_attack_{int(time.time())}",
            artifacts=artifacts
        )

def detect_data_exfiltration():
    """Detecta exfiltración de datos"""
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match_phrase": {"message": "ET MALWARE"}}
                ],
                "filter": [
                    {"range": {"@timestamp": {"gte": "now-10m"}}}
                ]
            }500
    }
    
    result = query_elasticsearch(query)
    if not result:
        return
    
    hits = result.get('hits', {}).get('hits', [])
    if len(hits) > 5 and can_create_alert("data_exfil"):
        ips = extract_ips_from_events(hits, r'to ([0-9\.]+)')
        unique_ips = list(set(ips))
        artifacts = [{"dataType": "ip", "data": ip} for ip in unique_ips[:5]]
        create_thehive_alert(
            title=f"Data Exfiltration - {len(hits)} transferencias sospechosas",
            description=f"Se han detectado {len(hits)} transferencias sospechosas de datos hacia {len(unique_ips
            title=f"Data Exfiltration - {len(hits)} transferencias sospechosas",
            description=f"Se han detectado {len(hits)} transferencias sospechosas de datos hacia {len(set(ips))} IPs externas.",
            severity=4,
            source_ref=f"exfil_{int(time.time())}",
            artifacts=artifacts
        )

def detect_privilege_escalation():
    """Detecta escalada de privilegios"""
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match_phrase": {"message": "[PRIVESC]"}}
                ],
                "filter": [
                    {"range": {"@timestamp": {"gte": "now-10m"}}}
                ]
            }500
    }
    
    result = query_elasticsearch(query)
    if not result:
        return
    
    hits = result.get('hits', {}).get('hits', [])
    if len(hits) > 0 and can_create_alert("priv_esc"):
        ips = extract_ips_from_events(hits, r'from ([0-9\.]+)')
        unique_ips = list(set(ips))
        artifacts = [{"dataType": "ip", "data": ip} for ip in unique_ips
        ips = extract_ips_from_events(hits, r'from ([0-9\.]+)')
        artifacts = [{"dataType": "ip", "data": ip} for ip in list(set(ips))[:5]]
        create_thehive_alert(
            title=f"Privilege Escalation - {len(hits)} intentos detectados",
            description=f"Se han detectado {len(hits)} intentos de escalada de privilegios en los últimos 10 minutos.",
            severity=4,
            source_ref=f"privesc_{int(time.time())}",
            artifacts=artifacts
        )

def main():
    """Bucle principal de monitoreo"""
    print("="*70)
    print("AUTO ALERT GENERATOR - Monitoreo Continuo de Elasticsearch -> TheHive")
    print("="*70)
    
    log_msg("Iniciando monitoreo de Elasticsearch...", "INFO")
    log_msg(f"Elasticsearch: {ES_URL}", "INFO")
    log_msg(f"TheHive: {THEHIVE_URL}", "INFO")
    print()
    
    try:
        iteration = 0
        while True:
            iteration += 1
            log_msg(f"--- Iteración {iteration} (cada 30 segundos) ---", "INFO")
            
            # Detectar diferentes tipos de ataques
            detect_ssh_brute_force()
            detect_port_scanning()
            detect_sql_injection()
            detect_web_attacks()
            detect_malware()
            detect_data_exfiltration()
            detect_privilege_escalation()
            
            # Mostrar resumen
            if THEHIVE_CREATED:
                log_msg(f"Total alertas creadas hasta ahora: {len(THEHIVE_CREATED)}", "OK")
            
            log_msg("Esperando 30 segundos para la siguiente iteración...", "INFO")
            print()
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n" + "="*70)
        log_msg("Monitoreo detenido por el usuario", "WARN")
        log_msg(f"Total de alertas creadas: {len(THEHIVE_CREATED)}", "OK")
        print("="*70)
        sys.exit(0)
    except Exception as e:
        log_msg(f"Error fatal: {e}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()
