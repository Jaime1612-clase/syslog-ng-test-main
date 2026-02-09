$logPath = $PSScriptRoot + "\..\..\logs\server\syslog-client\ataque.log"
$logDir = Split-Path -Parent $logPath
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

function Write-LogEvent {
    param(
        [string]$LogEntry
    )
    Add-Content -Path $logPath -Value $LogEntry
}

function Get-Timestamp {
    Get-Date -Format 'MMM dd HH:mm:ss'
}

Write-Host "Generando eventos de seguridad simulados (v2.0)..."

# === FASE 1: RECONOCIMIENTO ===
Write-Host "  [1/5] Fase de Reconocimiento (Port Scan)"
$ips = @("192.168.1.100", "10.0.0.55", "172.16.0.22")
foreach ($ip in $ips) {
    for ($port = 1; $port -le 3; $port++) {
        Write-LogEvent "$(Get-Timestamp) syslog-client kernel: [UFW BLOCK] IN=eth0 OUT= MAC=00:11:22:33:44:55 SRC=$ip DST=10.0.0.10 PROTO=TCP SPT=54321 DPT=$((20+$port)) WINDOW=65535"
        Start-Sleep -Milliseconds 300
    }
}

# === FASE 2: INTENTOS DE ACCESO NO AUTORIZADO ===
Write-Host "  [2/5] Fase de Acceso (Intentos SSH fallidos)"
$usuarios = @("admin", "root", "oracle", "backup", "test")
foreach ($usuario in $usuarios) {
    for ($intento = 1; $intento -le 4; $intento++) {
        Write-LogEvent "$(Get-Timestamp) syslog-client sshd[1234]: Failed password for invalid user $usuario from $($ips[0]) port 22 ssh2"
        Start-Sleep -Milliseconds 400
    }
}

# === FASE 3: ANOMALÍAS DE RED ===
Write-Host "  [3/5] Fase de Movimiento Lateral (Tráfico anómalo)"
Write-LogEvent "$(Get-Timestamp) syslog-client kernel: [ANOMLAY] POSSIBLE SYN FLOOD ATTACK SRC=$($ips[1]) DST=10.0.0.10 PROTOCOL=TCP COUNT=250"
Write-LogEvent "$(Get-Timestamp) syslog-client auditd: USER_AUTH acct=root exe=/usr/bin/sudo hostname=? addr=$($ips[1]) terminal=ssh res=failure"
Write-LogEvent "$(Get-Timestamp) syslog-client kernel: [MALWARE] Suspicious process detected: /tmp/.x11-unix/apache2 spawned by uid=0"
Start-Sleep -Seconds 1

# === FASE 4: ESCALADA DE PRIVILEGIOS ===
Write-Host "  [4/5] Fase de Escalada (Detección de Malware)"
Write-LogEvent "$(Get-Timestamp) syslog-client kernel: [THREAT] ClamAV detected EICAR-STANDARD-ANTIVIRUS-TEST-FILE!.Malware.Text in /home/user/downloads/setup.exe"
Write-LogEvent "$(Get-Timestamp) syslog-client sshd[5678]: Accepted publickey for attacker from $($ips[2]) port 50123 ssh2"
Write-LogEvent "$(Get-Timestamp) syslog-client sudo: attacker : TTY=pts/0 ; PWD=/home/attacker ; USER=root ; COMMAND=/bin/bash"
Write-LogEvent "$(Get-Timestamp) syslog-client kernel: [PRIVESC] Buffer overflow attempt detected in libc.so.6"
Start-Sleep -Seconds 1

# === FASE 5: EXFILTRACIÓN ===
Write-Host "  [5/5] Fase de Exfiltración (Actividad sospechosa)"
Write-LogEvent "$(Get-Timestamp) syslog-client suricata: ET MALWARE Suspicious Outbound FTP Traffic to Known Bad IP $($ips[1]):21"
Write-LogEvent "$(Get-Timestamp) syslog-client snort[9999]: {SHELLCODE x86 NOOP} $($ips[2]):1337 -> 10.0.0.10:443 {TCP}"
Write-LogEvent "$(Get-Timestamp) syslog-client filebeat: HIGH_DATA_TRANSFER user=attacker src=$($ips[2]) bytes_transferred=1250000000 destination=external"
Write-LogEvent "$(Get-Timestamp) syslog-client kernel: [DATA_EXFIL] Sensitive file accessed /etc/shadow by PID=6666 UID=0"

# === EVENTOS LIMPIOS (para comparación) ===
Write-Host "`n  Agregando eventos de tráfico legítimo para contraste..."
Write-LogEvent "$(Get-Timestamp) syslog-client sshd[7777]: Accepted password for user1 from 10.0.0.50 port 22 ssh2"
Write-LogEvent "$(Get-Timestamp) syslog-client sudo: user1 : TTY=pts/1 ; PWD=/home/user1 ; USER=root ; COMMAND=/usr/bin/systemctl status nginx"
Write-LogEvent "$(Get-Timestamp) syslog-client cron[8888]: (root) CMD (/usr/local/bin/backup.sh)"

Write-Host "`n[OK] $($((Get-Content $logPath).Count)) eventos generados en $logPath"
