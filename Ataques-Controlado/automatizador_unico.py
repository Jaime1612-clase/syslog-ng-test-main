#!/usr/bin/env python3
"""
automatizador_unico.py

Orquesta: 1) ejecutar simulador de ataque (PowerShell),
2) esperar ingestión en Elasticsearch (poll),
3) analizar logs (por ES o por archivo) y crear alertas en TheHive.

El usuario gestionará manualmente los casos/alertas luego.
"""

import subprocess
import time
import requests
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Config
# Detectar el script de simulador disponible (prefiere _2.0 si existe)
sim_candidates = ["simulador_logs_2.0.ps1", "simulador_logs.ps1"]
PS_SIMULATOR = None
for s in sim_candidates:
    p = Path(__file__).parent / s
    if p.exists():
        PS_SIMULATOR = p
        break
if PS_SIMULATOR is None:
    PS_SIMULATOR = Path(__file__).parent / sim_candidates[0]
LOGS_DIR = Path(__file__).parent.parent / "logs" / "server" / "syslog-client"
ES_URL = "http://localhost:9200"
THEHIVE_ALERT_URL = "http://localhost:9000/api/alert"
API_KEY = "hZo3qYekLTwks35KUJAHkfsw9CL6GPW0" # Cambiar por la API key que este configurada en theHive
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# Parameters
ES_POLL_SECONDS = 30
ES_POLL_INTERVAL = 3

# Alerting policy
# Umbral por IP para crear alerta individual (cambiar a 1 para crear alerta por cada IP)
THRESHOLD_IP = 1
TIME_WINDOW_MIN = 15

# -------------------- Utilities --------------------

def run_simulator():
    print("[1/4] Ejecutando simulador de logs (PowerShell)...")
    cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(PS_SIMULATOR)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        raise RuntimeError("El simulador devolvió error")
    print(proc.stdout)


def latest_log_file():
    files = sorted(LOGS_DIR.glob('ataque*.log'), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def es_has_logs():
    """Intenta buscar en Elasticsearch si hay documentos que coincidan con 'Failed password'"""
    try:
        q = {"query": {"match_phrase": {"message": "Failed password"}}}
        r = requests.get(f"{ES_URL}/_search", json=q, timeout=5)
        if r.status_code == 200:
            hits = r.json().get('hits', {}).get('total', {})
            # ES 7+ total can be dict or int
            if isinstance(hits, dict):
                total = hits.get('value', 0)
            else:
                total = int(hits)
            return total > 0
    except Exception:
        return False
    return False


def fetch_es_events(time_window_min=15, size=1000):
    """Query Elasticsearch for recent log messages matching common patterns."""
    try:
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"match_phrase": {"message": "Failed password"}}
                    ],
                    "filter": [
                        {"range": {"@timestamp": {"gte": f"now-{time_window_min}m"}}}
                    ]
                }
            },
            "size": size,
            "_source": ["message", "@timestamp"]
        }
        r = requests.get(f"{ES_URL}/_search", json=query, timeout=10)
        if r.status_code == 200:
            hits = r.json().get('hits', {}).get('hits', [])
            events = []
            for h in hits:
                src = h.get('_source', {})
                msg = src.get('message') or src.get('msg') or ''
                if msg:
                    events.append(msg)
            return events
    except Exception:
        return []
    return []


def group_counts_by_ip(events):
    counts = defaultdict(int)
    for e in events:
        m = re.findall(r'from ([0-9\.]+)', e)
        if not m:
            m = re.findall(r'SRC=([0-9\.]+)', e)
        for ip in m:
            counts[ip] += 1
    return counts


def parse_logs_file(path):
    events = []
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(line)
    return events


def detect_patterns(events):
    patterns = defaultdict(dict)
    port_scans = [e for e in events if '[UFW BLOCK]' in e]
    if port_scans:
        patterns['port_scan'] = {'events': port_scans, 'count': len(port_scans), 'ips': set(re.findall(r'SRC=([0-9\.]+)', ' '.join(port_scans)))}
    ssh_failures = [e for e in events if 'Failed password' in e]
    if ssh_failures:
        patterns['ssh_brute_force'] = {'events': ssh_failures, 'count': len(ssh_failures), 'ips': set(re.findall(r'from ([0-9\.]+)', ' '.join(ssh_failures))), 'users': set(re.findall(r'invalid user (\w+)', ' '.join(ssh_failures)))}
    malware = [e for e in events if '[MALWARE]' in e or 'ClamAV' in e or '[THREAT]' in e]
    if malware:
        patterns['malware'] = {'events': malware, 'count': len(malware), 'files': set(re.findall(r'in ([^\s]+)', ' '.join(malware))), 'threats': set(re.findall(r'detected ([A-Z0-9\-\.]+)', ' '.join(malware)))}
    privesc = [e for e in events if '[PRIVESC]' in e or 'Buffer overflow' in e or ('sudo' in e and 'USER=root' in e)]
    if privesc:
        patterns['privilege_escalation'] = {'events': privesc, 'count': len(privesc), 'users': set(re.findall(r'(\w+) :', ' '.join(privesc)))}
    exfil = [e for e in events if '[DATA_EXFIL]' in e or 'HIGH_DATA_TRANSFER' in e or 'ET MALWARE' in e or 'SHELLCODE' in e]
    if exfil:
        patterns['data_exfiltration'] = {'events': exfil, 'count': len(exfil), 'ips': set(re.findall(r'(?:SRC=|from |src=)([0-9\.]+)', ' '.join(exfil))), 'protocols': set(re.findall(r'(FTP|SSH|TCP|HTTPS?)', ' '.join(exfil)))}
    return patterns


def create_alert_from_pattern(pattern_type, data):
    ts = datetime.now().isoformat()
    if pattern_type == 'port_scan':
        return {"title": f"Port Scan Detectado - {len(data['ips'])} IPs origen", "description": f"Detección automática: {data['count']} eventos.", "severity": 3, "type": "external", "source": "SIEM - Automated", "sourceRef": f"port_scan_{ts}", "artifacts": [{"dataType":"ip","data":ip} for ip in sorted(list(data['ips']))[:5]]}
    if pattern_type == 'ssh_brute_force':
        return {"title": f"SSH Brute Force Detectado - {len(data['ips'])} IPs", "description": f"Detección automática: {data['count']} intentos SSH fallidos.", "severity": 3, "type": "external", "source": "SIEM - Automated", "sourceRef": f"ssh_brute_{ts}", "artifacts": [{"dataType":"ip","data":ip} for ip in sorted(list(data['ips']))[:5]]}
    if pattern_type == 'malware':
        return {"title": "Detección de Malware", "description": f"Detección automática: {data['count']} eventos.", "severity": 4, "type": "external", "source": "SIEM - Automated", "sourceRef": f"malware_{ts}", "artifacts": [{"dataType":"file","data":f} for f in sorted(list(data.get('files',[])))[:5]]}
    if pattern_type == 'privilege_escalation':
        return {"title": "Escalada de Privilegios Detectada", "description": f"Detección automática: {data['count']} eventos.", "severity": 4, "type": "external", "source": "SIEM - Automated", "sourceRef": f"privesc_{ts}", "artifacts": []}
    if pattern_type == 'data_exfiltration':
        return {"title": "Exfiltración de Datos Detectada", "description": f"Detección automática: {data['count']} eventos.", "severity": 4, "type": "external", "source": "SIEM - Automated", "sourceRef": f"exfil_{ts}", "artifacts": [{"dataType":"ip","data":ip} for ip in sorted(list(data.get('ips',[])))[:5]]}
    return None


def create_alerts_in_thehive(patterns):
    if not patterns:
        print("[INFO] No se detectaron patrones, no se crearán alertas.")
        return 0
    created = 0
    for ptype, data in patterns.items():
        alert = create_alert_from_pattern(ptype, data)
        if not alert:
            continue
        try:
            r = requests.post(THEHIVE_ALERT_URL, json=alert, headers=HEADERS, timeout=10)
            if r.status_code in (200,201):
                created += 1
                print(f"[OK] Alerta creada: {alert['title']}")
            else:
                print(f"[ERR] TheHive responded {r.status_code}: {r.text[:200]}")
        except Exception as e:
            print(f"[ERR] No se pudo conectar a TheHive: {e}")
            return created
    return created

# -------------------- Main flow --------------------

if __name__ == '__main__':
    print('\n--- Automatizador único: simulador -> ES -> TheHive ---\n')
    # 1) Ejecutar simulador
    try:
        run_simulator()
    except Exception as e:
        print(f"[FATAL] Error ejecutando simulador: {e}")
        sys.exit(1)

    # 2) Esperar ingestión en ES (poll)
    print('[2/4] Esperando que Elasticsearch indexe eventos (poll)...')
    es_seen = False
    start = time.time()
    while time.time() - start < ES_POLL_SECONDS:
        if es_has_logs():
            es_seen = True
            print('[INFO] Elasticsearch devuelve documentos relacionados con los logs.')
            break
        print('.', end='', flush=True)
        time.sleep(ES_POLL_INTERVAL)
    print()

    # 3) Analizar logs (preferente: desde Elasticsearch, sino por archivo)
    print('[3/4] Analizando logs para detectar patrones...')
    events = []
    # Preferir ES como fuente de verdad
    events = fetch_es_events(time_window_min=TIME_WINDOW_MIN)
    if events:
        print(f"[INFO] {len(events)} eventos leídos desde Elasticsearch (ult {TIME_WINDOW_MIN} min)")
        patterns = detect_patterns(events)
    else:
        logfile = latest_log_file()
        if logfile and logfile.exists():
            events = parse_logs_file(str(logfile))
            print(f"[INFO] {len(events)} eventos leídos desde {logfile.name}")
            patterns = detect_patterns(events)
        else:
            print('[WARN] No se encontraron eventos en ES ni archivo local. Intentando usar indicador de ingestión...')
            patterns = {}
            if es_seen:
                patterns['es_ingest'] = {'events': [], 'count': 1, 'ips': set()}

    # 4) Crear alertas en TheHive
    print('[4/4] Creando alertas en TheHive (si se detectaron patrones)...')
    created = 0

    # Crear alertas por IP para SSH brute-force si supera umbral
    if 'ssh_brute_force' in patterns:
        ip_counts = group_counts_by_ip(patterns['ssh_brute_force']['events'])
        for ip, cnt in ip_counts.items():
            if cnt >= THRESHOLD_IP:
                data = {'events': [], 'count': cnt, 'ips': {ip}}
                alert = create_alert_from_pattern('ssh_brute_force', data)
                try:
                    r = requests.post(THEHIVE_ALERT_URL, json=alert, headers=HEADERS, timeout=10)
                    if r.status_code in (200,201):
                        created += 1
                        print(f"[OK] Alerta por IP creada: {alert['title']}")
                    else:
                        print(f"[ERR] TheHive responded {r.status_code}: {r.text[:200]}")
                except Exception as e:
                    print(f"[ERR] No se pudo conectar a TheHive: {e}")

    # Crear alertas resumen por cada patrón detectado
    for ptype, data in patterns.items():
        alert = create_alert_from_pattern(ptype, data)
        if not alert:
            continue
        try:
            r = requests.post(THEHIVE_ALERT_URL, json=alert, headers=HEADERS, timeout=10)
            if r.status_code in (200,201):
                created += 1
                print(f"[OK] Alerta resumen creada: {alert['title']}")
            else:
                print(f"[ERR] TheHive responded {r.status_code}: {r.text[:200]}")
        except Exception as e:
            print(f"[ERR] No se pudo conectar a TheHive: {e}")

    print(f"\nResultado: {created} alertas creadas.")
    print('\nHecho. Revisa TheHive para gestionar alertas manualmente.')
