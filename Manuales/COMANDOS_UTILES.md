# 🔧 Comandos Útiles - Debugging y Monitoreo

## 📋 Tabla Rápida de Comandos

```powershell
# Estado de contenedores
docker-compose ps

# Ver logs de un servicio
docker-compose logs elasticsearch
docker-compose logs logstash
docker-compose logs kibana
docker-compose logs thehive
docker-compose logs filebeat

# Ver logs en tiempo real (últimas 100 líneas)
docker-compose logs -f elasticsearch

# Reiniciar servicios específicos
docker-compose restart logstash

# Detener todo
docker-compose down

# Detener y limpiar volúmenes (¡elimina datos!)
docker-compose down -v

# Recrear desde cero
docker-compose up -d --force-recreate
```

---

## 🔍 Verificación por Componente

### Elasticsearch

```powershell
# Verificar que esté disponible
curl http://localhost:9200

# Ver información del clúster
curl http://localhost:9200/_cluster/health

# Listar índices
curl http://localhost:9200/_cat/indices

# Ver documentos en el índice
curl http://localhost:9200/logstash-*/_search

# Contar documentos en un índice
curl http://localhost:9200/logstash-*/_count

# Ver mapeo de un índice
curl http://localhost:9200/logstash-*/_mapping
```

**Comando PowerShell equivalente:**
```powershell
# En lugar de curl (si no tienes curl instalado)
Invoke-RestMethod -Uri "http://localhost:9200" -Method Get
Invoke-RestMethod -Uri "http://localhost:9200/_cluster/health" -Method Get
Invoke-RestMethod -Uri "http://localhost:9200/_cat/indices" -Method Get
```

---

### Logstash

```powershell
# Ver logs de procesamiento
docker-compose logs logstash

# Verificar que esté escuchando en puerto 5044 (Beats input)
netstat -ano | findstr 5044

# Prueba de conexión con Elasticsearch desde Logstash
docker-compose exec logstash curl http://elasticsearch:9200

# Ver configuración cargada
docker-compose exec logstash cat /usr/share/logstash/pipeline/logstash.conf
```

---

### Kibana

```powershell
# Verificar que responda
curl http://localhost:5602

# Ver logs
docker-compose logs kibana

# Crear index pattern vía API
$pattern = @{
    attributes = @{
        title = "logstash-*"
        timeFieldName = "@timestamp"
    }
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://localhost:5602/api/saved_objects/index-pattern/logstash-*" `
    -Method Post `
    -ContentType "application/json" `
    -Body $pattern
```

---

### TheHive

```powershell
# Verificar disponibilidad
curl http://localhost:9000

# Ver logs
docker-compose logs thehive

# Obtener todas las alertas
curl -H "Authorization: Bearer dIVmJS4fK9m7QxJdygdf6RpVhH2hxRa5" \
     http://localhost:9000/api/alert

# Obtener todos los casos
curl -H "Authorization: Bearer dIVmJS4fK9m7QxJdygdf6RpVhH2hxRa5" \
     http://localhost:9000/api/case

# Obtener estadísticas
curl -H "Authorization: Bearer dIVmJS4fK9m7QxJdygdf6RpVhH2hxRa5" \
     http://localhost:9000/api/stats
```

**PowerShell equivalente:**
```powershell
$headers = @{
    "Authorization" = "Bearer dIVmJS4fK9m7QxJdygdf6RpVhH2hxRa5"
    "Content-Type" = "application/json"
}

Invoke-RestMethod -Uri "http://localhost:9000/api/alert" -Headers $headers
Invoke-RestMethod -Uri "http://localhost:9000/api/case" -Headers $headers
```

---

### Filebeat

```powershell
# Ver logs de Filebeat
docker-compose logs filebeat

# Verificar que esté leyendo archivos
docker-compose exec filebeat ls -la /var/log/syslog-ng

# Ver configuración de Filebeat
docker-compose exec filebeat cat /etc/filebeat/filebeat.yml
```

---

### Syslog-ng Server/Client

```powershell
# Ver logs generados
type "E:\syslog-ng-test-main\logs\server\syslog-client\ataque.log"

# Contar eventos
(Get-Content "E:\syslog-ng-test-main\logs\server\syslog-client\ataque.log").Count

# Ver últimos 20 eventos
Get-Content "E:\syslog-ng-test-main\logs\server\syslog-client\ataque.log" -Tail 20

# Ver eventos específicos
Select-String "Failed password" "E:\syslog-ng-test-main\logs\server\syslog-client\ataque.log"
```

---

## 🚀 Flujo de Verificación Quickstart

```powershell
# 1. Verify Docker is running
docker ps

# 2. Wait 30 seconds, then verify services are up
Start-Sleep -Seconds 30
docker-compose ps

# 3. Check Elasticsearch has received data
Invoke-RestMethod -Uri "http://localhost:9200/_cat/indices" | Select-String "logstash"

# 4. Check if Kibana index pattern exists
Invoke-RestMethod -Uri "http://localhost:5602/api/saved_objects/index-pattern" -Headers @{"kbn-xsrf"="true"}

# 5. Check alerts in TheHive
$headers = @{"Authorization" = "Bearer dIVmJS4fK9m7QxJdygdf6RpVhH2hxRa5"}
(Invoke-RestMethod -Uri "http://localhost:9000/api/alert" -Headers $headers).Count

# 6. Check cases in TheHive
(Invoke-RestMethod -Uri "http://localhost:9000/api/case" -Headers $headers).Count
```

---

## 📊 Scripts de Monitoreo Avanzados

### Ver progreso en tiempo real

```powershell
# Script: Monitor-Demo.ps1
# Monitorea el progreso de la demo mientras se ejecuta

param(
    [int]$RefreshInterval = 5  # Actualizar cada 5 segundos
)

Clear-Host
$cycle = 0

while ($true) {
    $cycle++
    Clear-Host
    Write-Host "=== MONITOR DE DEMO (Actualización #$cycle) ===" -ForegroundColor Cyan
    Write-Host "Hora actual: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
    Write-Host ""
    
    # Estado de contenedores
    Write-Host "## Estado de Contenedores" -ForegroundColor Yellow
    $(docker-compose ps --format "table {{.Names}}\t{{.Status}}" | Select-Object -First 10)
    Write-Host ""
    
    # Elasticsearch
    Write-Host "## Elasticsearch" -ForegroundColor Yellow
    try {
        $es = Invoke-RestMethod -Uri "http://localhost:9200/_cluster/health" -ErrorAction SilentlyContinue
        Write-Host "  Estado: $($es.status), Nodos: $($es.number_of_nodes), Índices: $($es.active_shards)"
    } catch {
        Write-Host "  No disponible"
    }
    
    # Logstash
    Write-Host "## Logstash" -ForegroundColor Yellow
    try {
        $ls = Invoke-RestMethod -Uri "http://localhost:9600" -ErrorAction SilentlyContinue
        Write-Host "  Version: $($ls.version), Host: $($ls.host)"
    } catch {
        Write-Host "  No disponible"
    }
    
    # Documento count
    Write-Host "## Logs en Elasticsearch" -ForegroundColor Yellow
    try {
        $count = Invoke-RestMethod -Uri "http://localhost:9200/logstash-*/_count" -ErrorAction SilentlyContinue
        Write-Host "  Documentos indexados: $($count.count)"
    } catch {
        Write-Host "  Documentos indexados: 0 (esperando...)"
    }
    
    # TheHive Alerts
    Write-Host "## Alertas en TheHive" -ForegroundColor Yellow
    try {
        $h = @{"Authorization" = "Bearer dIVmJS4fK9m7QxJdygdf6RpVhH2hxRa5"}
        $alerts = Invoke-RestMethod -Uri "http://localhost:9000/api/alert" -Headers $h -ErrorAction SilentlyContinue
        Write-Host "  Alertas creadas: $(($alerts | Measure-Object).Count)"
    } catch {
        Write-Host "  Alertas creadas: 0 (esperando...)"
    }
    
    # TheHive Cases
    Write-Host "## Casos en TheHive" -ForegroundColor Yellow
    try {
        $cases = Invoke-RestMethod -Uri "http://localhost:9000/api/case" -Headers $h -ErrorAction SilentlyContinue
        Write-Host "  Casos creados: $(($cases | Measure-Object).Count)"
    } catch {
        Write-Host "  Casos creados: 0 (esperando...)"
    }
    
    Write-Host ""
    Write-Host "Actualizando en $RefreshInterval segundos... (Ctrl+C para salir)" -ForegroundColor Gray
    Start-Sleep -Seconds $RefreshInterval
}
```

**Uso:**
```powershell
.\Monitor-Demo.ps1 -RefreshInterval 3
```

---

### Análisis detallado de logs

```powershell
# Script: Analyze-Logs.ps1
# Analiza el archivo de logs generados

$logPath = "E:\syslog-ng-test-main\logs\server\syslog-client\ataque.log"

if (-not (Test-Path $logPath)) {
    Write-Host "Log file not found: $logPath"
    exit 1
}

$logs = Get-Content $logPath
$totalLines = ($logs | Measure-Object).Count

Write-Host "=== ANÁLISIS DE LOGS ===" -ForegroundColor Cyan
Write-Host "Total de eventos: $totalLines"
Write-Host ""

# Contar por tipo de evento
Write-Host "## Eventos por Tipo" -ForegroundColor Yellow
Get-Content $logPath `
    | ForEach-Object {
        if ($_ -match '\[(.*?)\]') {
            $Matches[1]
        }
    } `
    | Group-Object `
    | Sort-Object -Property Count -Descending `
    | ForEach-Object { Write-Host "  $($_.Name): $($_.Count)" }

Write-Host ""

# Eventos por IP
Write-Host "## Eventos por IP Origen" -ForegroundColor Yellow
Get-Content $logPath `
    | Where-Object { $_ -match 'SRC=([\d.]+)' } `
    | ForEach-Object {
        if ($_ -match 'SRC=([\d.]+)') {
            $Matches[1]
        }
    } `
    | Group-Object `
    | Sort-Object -Property Count -Descending `
    | ForEach-Object { Write-Host "  $($_.Name): $($_.Count) eventos" }

Write-Host ""

# Eventos por usuario
Write-Host "## Usuarios Mencionados en Logs" -ForegroundColor Yellow
Get-Content $logPath `
    | Where-Object { $_ -match 'user[=:](\w+)' } `
    | ForEach-Object {
        if ($_ -match 'user[=:](\w+)') {
            $Matches[1]
        }
    } `
    | Group-Object `
    | Sort-Object -Property Count -Descending `
    | ForEach-Object { Write-Host "  $($_.Name): $($_.Count) menciones" }
```

**Uso:**
```powershell
.\Analyze-Logs.ps1
```

---

## 🔐 Seguridad - Cambiar API Key de TheHive

```powershell
# Obtener API keys actuales (acceder primero a TheHive)
# 1. http://localhost:9000
# 2. Settings > API Keys
# 3. Copiar nueva clave

# Luego actualizar en los scripts:
# - Ataques-Controlado\crear_alerta.py (línea ~13)
# - Ataques-Controlado\crear_caso.py (línea ~11)

# Cambio:
$oldKey = "dIVmJS4fK9m7QxJdygdf6RpVhH2hxRa5"
$newKey = "[tu_nueva_clave]"

(Get-Content "Ataques-Controlado\crear_alerta.py") -replace $oldKey, $newKey | Set-Content "Ataques-Controlado\crear_alerta.py"
(Get-Content "Ataques-Controlado\crear_caso.py") -replace $oldKey, $newKey | Set-Content "Ataques-Controlado\crear_caso.py"

Write-Host "API Key actualizada en ambos scripts"
```

---

## 💾 Backup y Restauración

```powershell
# Backup de datos de TheHive
docker-compose exec thehive tar czf /tmp/thehive-backup.tar.gz /opt/thehive/data
docker cp syslog-test-thehive-1:/tmp/thehive-backup.tar.gz ./backups/thehive-backup.tar.gz

# Backup de Elasticsearch
docker-compose exec elasticsearch curl -X PUT "localhost:9200/_snapshot/backup" -H "Content-Type: application/json" -d '{"type":"fs","settings":{"location":"/usr/share/elasticsearch/data/backup"}}'

# Restaurar desde backup
docker-compose exec elasticsearch curl -X POST "localhost:9200/_snapshot/backup/latest/_restore" -H "Content-Type: application/json"
```

---

## 📈 Métricas Útiles

```powershell
# Ver tamaño total de datos en Elasticsearch
Invoke-RestMethod -Uri "http://localhost:9200/_cat/indices?v" | Select-String "logstash"

# Ver consumo de CPU y memoria de contenedores
docker stats --no-stream

# Ver tamaño de volumen de datos
docker volume inspect syslog-ng-test-main_esdata

# Ver tiempo de respuesta de APIs
Measure-Command {
    Invoke-RestMethod -Uri "http://localhost:9200/_cluster/health"
}
```

---

## 🐛 Debugging de Scripts Python

```powershell
# Ejecutar crear_alerta.py con verbosidad
python -u "Ataques-Controlado\crear_alerta.py"

# Ejecutar con depuración (más detalles)
python -v "Ataques-Controlado\crear_alerta.py" 2>&1 | Tee-Object -FilePath debug.log

# Probar conexión con TheHive manualmente
python -c "import requests; print(requests.get('http://localhost:9000/api/alert', headers={'Authorization': 'Bearer dIVmJS4fK9m7QxJdygdf6RpVhH2hxRa5'}).status_code)"
```

---

## 🔄 Troubleshooting Rápido

### Problema: Elasticsearch no indexa datos

```powershell
# Verificar logs de Logstash
docker-compose logs logstash | Select-String "error|ERROR|Error"

# Verificar conexión Logstash → Elasticsearch
docker-compose exec logstash curl -v http://elasticsearch:9200

# Reiniciar Logstash
docker-compose restart logstash
docker-compose logs -f logstash  # Ver si inicia correctamente
```

### Problema: Filebeat no recolecta logs

```powershell
# Verificar que el archivo de logs existe
Test-Path "E:\syslog-ng-test-main\logs\server\syslog-client\ataque.log"

# Verificar permisos
Get-Acl "E:\syslog-ng-test-main\logs\server\syslog-client\ataque.log"

# Ver logs de Filebeat
docker-compose logs filebeat

# Reiniciar Filebeat
docker-compose restart filebeat
```

### Problema: TheHive no recibe alertas

```powershell
# Verificar API key
$headers = @{"Authorization" = "Bearer dIVmJS4fK9m7QxJdygdf6RpVhH2hxRa5"}
Invoke-RestMethod -Uri "http://localhost:9000/api/alert" -Headers $headers

# Ver logs de TheHive
docker-compose logs thehive | Select-String "ERROR|error"

# Probar con curl/PowerShell
$alert = @{
    title = "Test"
    description = "Test Alert"
    type = "external"
    source = "test"
    sourceRef = "test123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:9000/api/alert" -Method Post -Headers $headers -Body $alert -ContentType "application/json"
```

---

**Última actualización:** 9 de febrero de 2026
