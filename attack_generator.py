#!/usr/bin/env python3
"""
attack_generator.py - Generador de 50-100 Logs Reales de Ataque
"""

import sys
import time
import random
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs" / "server" / "syslog-client"
LOG_FILE = LOG_DIR / "ataque.log"
LOG_DIR.mkdir(parents=True, exist_ok=True)

ATTACKER_IPS = ["192.168.1.100", "10.0.0.5", "172.16.0.50", "203.0.113.45", "198.51.100.10"]
USERS = ["admin", "root", "user", "test", "nginx", "apache", "postgres"]
PORTS = [22, 80, 443, 3306, 5432, 8080, 8443]

def log_event(msg):
    ts = datetime.now().strftime("%b %d %H:%M:%S")
    full = f"{ts} syslog-client {msg}"
    with open(LOG_FILE, "a") as f:
        f.write(full + "\n")
    print(full)

def ssh_attack():
    print("\n[*] SSH Brute Force (10-20 intentos)...")
    ip = random.choice(ATTACKER_IPS)
    for _ in range(random.randint(10, 20)):
        log_event(f"sshd[{random.randint(1000,9999)}]: Failed password for {random.choice(USERS)} from {ip} port 22 ssh2")
        time.sleep(0.05)

def port_scan():
    print("\n[*] Port Scanning (15-25 scans)...")
    ip = random.choice(ATTACKER_IPS)
    for _ in range(random.randint(15, 25)):
        port = random.choice(PORTS)
        log_event(f"kernel: [UFW BLOCK] IN=eth0 SRC={ip} DST=192.168.1.1 PROTO=TCP DPT={port}")
        time.sleep(0.02)

def sql_inject():
    print("\n[*] SQL Injection (8-15 intentos)...")
    ip = random.choice(ATTACKER_IPS)
    payloads = ["' OR '1'='1", "UNION SELECT * FROM users--", "DROP TABLE users;--", "'; DELETE FROM logs;--"]
    for _ in range(random.randint(8, 15)):
        log_event(f"webapp: SQL INJECTION from {ip}: payload='{random.choice(payloads)}'")
        time.sleep(0.03)

def web_attack():
    print("\n[*] Web Attacks (15-25 requests)...")
    ip = random.choice(ATTACKER_IPS)
    paths = ["/admin/login", "/api/users", "/upload.php", "/config.php", "/admin.php"]
    for _ in range(random.randint(15, 25)):
        log_event(f"httpd: {ip} - - \"{random.choice(['GET','POST'])} {random.choice(paths)} HTTP/1.1\" {random.choice([403,401,404])} - \"-\" \"Mozilla/5.0\"")
        time.sleep(0.02)

def malware():
    print("\n[*] Malware Detection (5-10 eventos)...")
    files = ["/tmp/malware.sh", "/var/tmp/payload.exe", "/.ssh/backdoor.py", "/tmp/trojan"]
    threats = ["Trojan.Generic", "Backdoor.Linux", "Dropper", "Rootkit.Generic"]
    for _ in range(random.randint(5, 10)):
        log_event(f"ClamAV: [MALWARE] {random.choice(files)}: {random.choice(threats)} from {random.choice(ATTACKER_IPS)}")
        time.sleep(0.05)

def exfil():
    print("\n[*] Data Exfiltration (8-15 eventos)...")
    ip = random.choice(ATTACKER_IPS)
    for _ in range(random.randint(8, 15)):
        bytes_val = random.randint(1000000, 10000000)
        log_event(f"ET MALWARE: Outbound {random.choice(['FTP','SSH','HTTPS'])} from 192.168.1.50 to {ip} transferring {bytes_val} bytes")
        time.sleep(0.03)

def priv_esc():
    print("\n[*] Privilege Escalation (3-5 intentos)...")
    user = random.choice(USERS)
    ip = random.choice(ATTACKER_IPS)
    for _ in range(random.randint(3, 5)):
        log_event(f"sudo: {user} : TTY=pts/0 ; USER=root ; COMMAND=/bin/bash")
        time.sleep(0.03)
    log_event(f"kernel: [PRIVESC] Buffer overflow from {ip} via {user}")


print("="*70)
print("ATTACK GENERATOR - Generador de 50-100 Logs Reales de Ataque")
print("="*70)

start = time.time()
ssh_attack()
port_scan()
sql_inject()
web_attack()
priv_esc()
malware()
exfil()

elapsed = time.time() - start
size = LOG_FILE.stat().st_size
print("\n" + "="*70)
print(f"[OK] Completado en {elapsed:.1f}s | {size:,} bytes | ~50-100 eventos reales")
print("[OK] Esperando que Filebeat ingeste los logs en Elasticsearch...")
print("="*70)
