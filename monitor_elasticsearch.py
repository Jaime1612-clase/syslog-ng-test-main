#!/usr/bin/env python3
"""
monitor_elasticsearch.py
Monitorea Elasticsearch continuamente y genera reportes de alertas
Guarda alertas en un archivo JSON que puede importarse a TheHive
"""

import requests
import time
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Configuración
ES_URL = "http://localhost:9200"
ALERTS_FILE = Path(__file__).parent / "detected_alerts.json"

# Variables de control
ALERTS_HISTORY = []
MIN_INTERVAL = 300  # Mínimo 5 minutos entre alertas duplicadas

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

def query_elasticsearch(pattern, minutes=10, size=500):
    """Ejecuta una búsqueda en Elasticsearch"""
    query = {
        "query": {
            "bool": {
                "must": [{"match_phrase": {"message": pattern}}],
                "filter": [{"range": {"@timestamp": {"gte": f"now-{minutes}m"}}}]
            }
        },
        "size": size
    }
    
    try:
        r = requests.get(f"{ES_URL}/_search", json=query, timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            log_msg(f"ES error {r.status_code}: {r.text[:100]}", "ERROR")
            return None
    except Exception as e:
        log_msg(f"ES connection error: {e}", "ERROR")
        return None

def extract_ips(events, pattern):
    """Extrae IPs de los eventos"""
    ips = set()
    for event in events:
        msg = event.get('_source', {}).get('message', '')
        matches = re.findall(pattern, msg)
        ips.update(matches)
    return list(ips)

def save_alert_to_file(alert):
    """Guarda la alerta en un archivo JSON"""
    if ALERTS_FILE.exists():
        with open(ALERTS_FILE, 'r', encoding='utf-8') as f:
            alerts = json.load(f)
    else:
        alerts = []
    
    alerts.append(alert)
    
    with open(ALERTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(alerts, f, indent=2, ensure_ascii=True)

def create_alert_record(title, description, severity, ips, count):
    """Crea un registro de alerta"""
    return {
        "timestamp": datetime.now().isoformat(),
        "title": title,
        "description": description,
        "severity": severity,
        "icon_type": "alert",
        "ips_involved": ips[:5],  # Máx 5 IPs
        "total_events": count,
        "source": "Elasticsearch Monitor",
        "status": "New"
    }

def check_ssh_attacks():
    """Detecta SSH Brute Force"""
    result = query_elasticsearch("Failed password", 10)
    if not result:
        return
    
    hits = result.get('hits', {}).get('hits', [])
    if len(hits) > 5:
        ips = extract_ips(hits, r'from ([0-9\.]+)')
        alert = create_alert_record(
            title=f"[ALERT] SSH Brute Force - {len(hits)} intentos desde {len(set(ips))} IPs",
            description=f"Se detectaron {len(hits)} intentos fallidos de SSH en los ultimos 10 min. IPs: {', '.join(set(ips))[:100]}",
            severity=2,
            ips=list(set(ips)),
            count=len(hits)
        )
        save_alert_to_file(alert)
        log_msg(f"OK SSH Alert: {len(hits)} intentos desde {len(set(ips))} IPs", "OK")

def check_port_scanning():
    """Detecta Port Scanning"""
    result = query_elasticsearch("[UFW BLOCK]", 10)
    if not result:
        return
    
    hits = result.get('hits', {}).get('hits', [])
    if len(hits) > 10:
        ips = extract_ips(hits, r'SRC=([0-9\.]+)')
        alert = create_alert_record(
            title=f"[ALERT] Port Scanning - {len(hits)} eventos desde {len(set(ips))} IPs",
            description=f"Se detectaron {len(hits)} intentos de escaneo de puertos (UFW BLOCK). IPs: {', '.join(set(ips))[:100]}",
            severity=2,
            ips=list(set(ips)),
            count=len(hits)
        )
        save_alert_to_file(alert)
        log_msg(f"OK Port Scan Alert: {len(hits)} eventos desde {len(set(ips))} IPs", "OK")

def check_sql_injection():
    """Detecta SQL Injection"""
    result = query_elasticsearch("SQL INJECTION", 10)
    if not result:
        return
    
    hits = result.get('hits', {}).get('hits', [])
    if len(hits) > 3:
        ips = extract_ips(hits, r'from ([0-9\.]+)')
        alert = create_alert_record(
            title=f"[ALERT] SQL Injection - {len(hits)} intentos desde {len(set(ips))} IPs",
            description=f"Se detectaron {len(hits)} intentos de SQL Injection. IPs: {', '.join(set(ips))[:100]}",
            severity=3,
            ips=list(set(ips)),
            count=len(hits)
        )
        save_alert_to_file(alert)
        log_msg(f"OK SQL Injection Alert: {len(hits)} intentos", "OK")

def check_web_attacks():
    """Detecta Web Attacks"""
    result = query_elasticsearch("httpd", 10, 1000)
    if not result:
        return
    
    hits = result.get('hits', {}).get('hits', [])
    # Filtra solo status code sospechosos
    suspicious = [h for h in hits if any(x in h.get('_source', {}).get('message', '') for x in ['403', '401', '404'])]
    
    if len(suspicious) > 15:
        ips = extract_ips(suspicious, r'([0-9\.]+) - -')
        alert = create_alert_record(
            title=f"[ALERT] Web Attacks - {len(suspicious)} solicitudes HTTP sospechosas desde {len(set(ips))} IPs",
            description=f"Se detectaron {len(suspicious)} solicitudes HTTP con status code 403/401/404. IPs: {', '.join(set(ips))[:100]}",
            severity=2,
            ips=list(set(ips)),
            count=len(suspicious)
        )
        save_alert_to_file(alert)
        log_msg(f"OK Web Attack Alert: {len(suspicious)} solicitudes sospechosas", "OK")

def check_malware():
    """Detecta Malware"""
    result = query_elasticsearch("[MALWARE]", 10)
    if not result:
        return
    
    hits = result.get('hits', {}).get('hits', [])
    if len(hits) > 0:
        ips = extract_ips(hits, r'from ([0-9\.]+)')
        alert = create_alert_record(
            title=f"[CRITICAL] MALWARE DETECTION - {len(hits)} eventos criticos",
            description=f"Se han detectado {len(hits)} eventos de malware. IPs: {', '.join(set(ips))[:100]}",
            severity=4,
            ips=list(set(ips)),
            count=len(hits)
        )
        save_alert_to_file(alert)
        log_msg(f"ERROR Malware Alert: {len(hits)} eventos CRITICOS", "ERROR")

def check_data_exfiltration():
    """Detecta Data Exfiltration"""
    result = query_elasticsearch("ET MALWARE", 10)
    if not result:
        return
    
    hits = result.get('hits', {}).get('hits', [])
    if len(hits) > 5:
        ips = extract_ips(hits, r'to ([0-9\.]+)')
        alert = create_alert_record(
            title=f"[CRITICAL] Data Exfiltration - {len(hits)} transferencias sospechosas hacia {len(set(ips))} IPs",
            description=f"Se detectaron {len(hits)} transferencias sospechosas. IPs destino: {', '.join(set(ips))[:100]}",
            severity=4,
            ips=list(set(ips)),
            count=len(hits)
        )
        save_alert_to_file(alert)
        log_msg(f"ERROR Exfiltration Alert: {len(hits)} transferencias sospechosas", "ERROR")

def check_privilege_escalation():
    """Detecta Privilege Escalation"""
    result = query_elasticsearch("[PRIVESC]", 10)
    if not result:
        return
    
    hits = result.get('hits', {}).get('hits', [])
    if len(hits) > 0:
        ips = extract_ips(hits, r'from ([0-9\.]+)')
        alert = create_alert_record(
            title=f"[CRITICAL] Privilege Escalation - {len(hits)} intentos detectados",
            description=f"Se detectaron {len(hits)} intentos de escalada de privilegios. IPs: {', '.join(set(ips))[:100]}",
            severity=4,
            ips=list(set(ips)),
            count=len(hits)
        )
        save_alert_to_file(alert)
        log_msg(f"ERROR PrivEsc Alert: {len(hits)} intentos CRITICOS", "ERROR")

def get_elasticsearch_stats():
    """Obtiene estadísticas generales de Elasticsearch"""
    try:
        r = requests.get(f"{ES_URL}/_count", timeout=10)
        if r.status_code == 200:
            count = r.json().get('count', 0)
            return count
        return 0
    except:
        return 0

def main():
    """Bucle principal de monitoreo"""
    print("="*75)
    print("ELASTICSEARCH MONITOR - Detección de Alertas Automática")
    print("="*75)
    
    log_msg("Iniciando monitoreo continuo de Elasticsearch...", "INFO")
    log_msg(f"Elasticsearch URL: {ES_URL}", "INFO")
    log_msg(f"Alertas se guardarán en: {ALERTS_FILE}", "INFO")
    print()
    
    try:
        iteration = 0
        while True:
            iteration += 1
            log_msg(f"--- Iteración {iteration} ---", "INFO")
            
            # Verificar conexión a ES
            total_docs = get_elasticsearch_stats()
            log_msg(f"Total de documentos en ES: {total_docs}", "INFO")
            
            # Ejecutar todas las detecciones
            check_ssh_attacks()
            check_port_scanning()
            check_sql_injection()
            check_web_attacks()
            check_privilege_escalation()
            check_malware()
            check_data_exfiltration()
            
            # Mostrar resumen
            if ALERTS_FILE.exists():
                with open(ALERTS_FILE, 'r') as f:
                    alerts = json.load(f)
                    log_msg(f"Total alertas guardadas hasta ahora: {len(alerts)}", "OK")
            
            log_msg("Esperando 30 segundos para la siguiente iteración...", "INFO")
            print()
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n" + "="*75)
        log_msg("Monitoreo detenido por el usuario", "WARN")
        if ALERTS_FILE.exists():
            with open(ALERTS_FILE, 'r') as f:
                alerts = json.load(f)
            log_msg(f"Total de alertas generadas: {len(alerts)}", "OK")
            log_msg(f"Revisa: {ALERTS_FILE}", "INFO")
        print("="*75)
        sys.exit(0)

if __name__ == "__main__":
    main()
