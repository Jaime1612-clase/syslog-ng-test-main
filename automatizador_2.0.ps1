#============================================================================
# AUTOMATIZADOR DEL FLUJO COMPLETO DE SEGURIDAD v2.0
# Coordina: Docker, logs, detección, alertas e incidentes
#============================================================================

param(
    [switch]$Clean = $false,
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BaseColor = "Cyan"
$SuccessColor = "Green"
$ErrorColor = "Red"
$WarningColor = "Yellow"

#============================================================================
# FUNCIONES AUXILIARES
#============================================================================

function Write-Step {
    param($Message)
    Write-Host "`n► " -NoNewline -ForegroundColor $BaseColor
    Write-Host $Message -ForegroundColor $BaseColor
}

function Write-Success {
    param($Message)
    Write-Host "✓ $Message" -ForegroundColor $SuccessColor
}

function Write-Error-Custom {
    param($Message)
    Write-Host "✗ $Message" -ForegroundColor $ErrorColor
}

function Write-Warning-Custom {
    param($Message)
    Write-Host "⚠ $Message" -ForegroundColor $WarningColor
}

# Verifica si una URL está disponible (tolerancia de errores iniciales)
function Test-ServiceReady {
    param(
        [string]$Url,
        [int]$MaxRetries = 30,
        [int]$DelaySeconds = 2,
        [string]$ServiceName = "Service"
    )
    
    for ($i = 1; $i -le $MaxRetries; $i++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 401) {  # 401 es OK para Kibana/Elasticsearch
                Write-Success "$ServiceName listo (intento $i)"
                return $true
            }
        }
        catch {
            if ($i % 5 -eq 0) {
                Write-Warning-Custom "$ServiceName aún no disponible... (intento $i/$MaxRetries)"
            }
        }
        Start-Sleep -Seconds $DelaySeconds
    }
    return $false
}

# Verifica si Docker está corriendo
function Test-DockerRunning {
    try {
        $result = docker ps 2>&1
        if ($LASTEXITCODE -eq 0) {
            return $true
        }
    }
    catch {
    }
    return $false
}

#============================================================================
# LIMPIEZA (Opcional)
#============================================================================

if ($Clean) {
    Write-Step "Limpiando entorno anterior..."
    try {
        docker-compose down -v
        Write-Success "Entorno limpiado"
    }
    catch {
        Write-Warning-Custom "No se pudo limpiar. Continuando..."
    }
}

#============================================================================
# VERIFICACIONES PREVIAS
#============================================================================

Write-Step "Verificando requisitos..."

if (-not (Test-DockerRunning)) {
    Write-Error-Custom "Docker no está disponible. Inicia Docker Desktop e intenta de nuevo."
    exit 1
}
Write-Success "Docker está disponible"

#============================================================================
# 1. LEVANTAR SERVICIOS
#============================================================================

Write-Step "Levantando servicios docker-compose..."
try {
    Push-Location $ScriptDir
    $output = docker-compose up -d 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "docker-compose falló"
    }
    Write-Success "Servicios iniciados"
    Pop-Location
}
catch {
    Write-Error-Custom "Error al levantar servicios: $_"
    exit 1
}

#============================================================================
# 2. VALIDAR SERVICIOS CRÍTICOS
#============================================================================

Write-Step "Esperando a que los servicios estén listos..."

$services = @(
    @{ Name = "Elasticsearch"; Url = "http://localhost:9200"; Retries = 40 },
    @{ Name = "Logstash"; Url = "http://localhost:9600"; Retries = 30 },
    @{ Name = "Kibana"; Url = "http://localhost:5602"; Retries = 30 },
    @{ Name = "TheHive"; Url = "http://localhost:9000"; Retries = 40 }
)

$allReady = $true
foreach ($service in $services) {
    if (-not (Test-ServiceReady -Url $service.Url -MaxRetries $service.Retries -ServiceName $service.Name)) {
        Write-Warning-Custom "$($service.Name) no respondió a tiempo (puede estar inicializando)"
    }
}

# Tiempo adicional para Elasticsearch e Indexing
Write-Step "Esperando a que Elasticsearch esté completamente listo..."
Start-Sleep -Seconds 5

#============================================================================
# 3. EJECUTAR SIMULADOR DE ATAQUES
#============================================================================

Write-Step "Generando eventos de seguridad simulados..."
try {
    & "$ScriptDir\Ataques-Controlado\simulador_logs_2.0.ps1"
    Write-Success "Eventos generados"
}
catch {
    Write-Error-Custom "Error en simulador: $_"
    # Continuar de todas formas
}

#============================================================================
# 4. ESPERAR PROCESAMIENTO DE LOGS
#============================================================================

Write-Step "Esperando a que Filebeat procese y envíe los logs..."
Start-Sleep -Seconds 8

Write-Step "Esperando a que Logstash procese los eventos..."
Start-Sleep -Seconds 5

#============================================================================
# 5. CREAR ALERTAS EN THEHIVE
#============================================================================

Write-Step "Creando alertas de seguridad en TheHive..."
try {
    $pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $pythonPath) {
        Write-Warning-Custom "Python no encontrado en PATH. Usando 'python'..."
        $pythonPath = "python"
    }
    
    & $pythonPath "$ScriptDir\Ataques-Controlado\crear_alerta_2.0.py" 2>&1 | ForEach-Object {
        if ($Verbose) { Write-Host "  $_" }
    }
    Write-Success "Alertas creadas"
}
catch {
    Write-Error-Custom "Error creando alertas: $_"
}

#============================================================================
# 6. CREAR CASOS EN THEHIVE
#============================================================================

Write-Step "Creando casos de incidentes en TheHive..."
Start-Sleep -Seconds 2  # Pequeña pausa para que las alertas se procesen

try {
    & $pythonPath "$ScriptDir\Ataques-Controlado\crear_caso_2.0.py" 2>&1 | ForEach-Object {
        if ($Verbose) { Write-Host "  $_" }
    }
    Write-Success "Casos creados"
}
catch {
    Write-Error-Custom "Error creando casos: $_"
}

#============================================================================
# 7. RESUMEN Y PRÓXIMOS PASOS
#============================================================================

Write-Step "Flujo de demostración completado"

Write-Host "`nAccede a las herramientas:" -ForegroundColor $BaseColor
Write-Host "  • Kibana (búsqueda de logs):   http://localhost:5602" -ForegroundColor White
Write-Host "  • TheHive (gestión incidentes): http://localhost:9000 (admin/secret)" -ForegroundColor White
Write-Host "  • Elasticsearch API:            http://localhost:9200" -ForegroundColor White
Write-Host "`nTips para la demo:" -ForegroundColor $BaseColor
Write-Host "  1. En Kibana: Crea un index pattern 'logstash-*' si aún no existe" -ForegroundColor White
Write-Host "  2. Busca logs con términos: 'Failed password', 'UFW BLOCK', 'Accepted password'" -ForegroundColor White
Write-Host "  3. En TheHive: Revisa Alerts y Cases para ver la correlación automática" -ForegroundColor White
Write-Host "  4. Ejecuta con '-Verbose' para más detalles: .\automatizador_2.0.ps1 -Verbose" -ForegroundColor White
Write-Host "  5. Limpia en próximas ejecuciones: .\automatizador_2.0.ps1 -Clean" -ForegroundColor White
Write-Host "`n✓ Plataforma lista para demostración`n" -ForegroundColor $SuccessColor
