# Automatizador del flujo completo de la plataforma
# 1. Levanta los servicios
# 2. Ejecuta simulador de ataques
# 3. Espera a que los logs sean recolectados
# 4. Ejecuta scripts de alerta y caso

# Este script debe ejecutarse en PowerShell con permisos suficientes

# Levantar los servicios
Write-Host "Levantando servicios docker-compose..."
docker-compose up -d

# Esperar unos segundos para que los servicios estén listos
Start-Sleep -Seconds 20

# Ejecutar simulador de ataques
Write-Host "Ejecutando simulador de ataques..."
& "D:\syslog-ng-test-main\Ataques-Controlado\simulador_logs.ps1"

# Esperar para que Filebeat recoja los logs
Start-Sleep -Seconds 10

# Ejecutar scripts de alerta y caso
Write-Host "Creando alerta en TheHive..."
python "D:\syslog-ng-test-main\Ataques-Controlado\crear_alerta.py"

Write-Host "Creando caso en TheHive..."
python "D:\syslog-ng-test-main\Ataques-Controlado\crear_caso.py"

Write-Host "Flujo automatizado completado. Revisa Kibana y TheHive para resultados."
