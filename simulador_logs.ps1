$logPath = "D:\syslog-ng-test-main\logs\server\syslog-client\ataque.log"

# Simula 5 intentos de login fallidos
for ($i=1; $i -le 5; $i++) {
    Add-Content -Path $logPath -Value "$(Get-Date -Format 'MMM dd HH:mm:ss') syslog-client sshd[1234]: Failed password for invalid user admin from 192.168.1.100 port 22 ssh2"
    Start-Sleep -Milliseconds 500
}

# Simula un escaneo de puertos detectado
Add-Content -Path $logPath -Value "$(Get-Date -Format 'MMM dd HH:mm:ss') syslog-client kernel: [UFW BLOCK] IN=eth0 OUT= MAC=... SRC=10.0.0.5 DST=10.0.0.10 ..."

# Simula un acceso exitoso
Add-Content -Path $logPath -Value "$(Get-Date -Format 'MMM dd HH:mm:ss') syslog-client sshd[1234]: Accepted password for user1 from 192.168.1.101 port 22 ssh2"