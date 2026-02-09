# Guía de Ejecución - Demo de Plataforma de Detección de Ataques

## 📋 Requisitos Previos

- **Docker Desktop** instalado y ejecutándose
- **PowerShell 5.1+** (Windows)
- **Python 3.8+** con librería `requests` instalada
- Mínimo **4GB de RAM** disponibles para los contenedores
- Conexión a internet para descargar imágenes Docker (primera ejecución)

### Instalación de dependencias Python

Si aún no tienes `requests` instalado:
```powershell
pip install requests
```

---

## 🚀 Ejecución Rápida

Desde la raíz del proyecto, ejecuta:

```powershell
.\automatizador.ps1
```

**Tiempo aproximado de ejecución:** 3-5 minutos

### Ejecución con opciones avanzadas

```powershell
# Verbose: muestra más detalles del flujo
.\automatizador.ps1 -Verbose

# Clean: Limpia entorno anterior antes de ejecutar
.\automatizador.ps1 -Clean

# Combinar opciones
.\automatizador.ps1 -Clean -Verbose
```

---

## 📊 Flujo de Ejecución

El automatizador ejecuta los siguientes pasos:

### 1. **Validaciones** (10-15 segundos)
   - Verifica que Docker esté disponible
   - Comprueba que PowerShell tenga permisos suficientes

### 2. **Levantamiento de Servicios** (30-40 segundos)
   - Elasticsearch (motor de búsqueda)
   - Logstash (procesamiento de logs)
   - Kibana (visualización de logs)
   - Filebeat (recolector de logs)
   - TheHive (gestión de incidentes)
   - Syslog-ng Server & Client (simulación de red)

### 3. **Generación de Eventos** (5-10 segundos)
   Fases del ataque simulado:
   - **Reconocimiento:** Port scanning
   - **Acceso:** Intentos de fuerza bruta SSH
   - **Movimiento lateral:** Tráfico anómalo de red
   - **Escalada:** Detección de malware, elevación de privilegios
   - **Exfiltración:** Transferencia de datos anómala

### 4. **Procesamiento de Logs** (15-20 segundos)
   - Filebeat recoge los eventos del archivo
   - Logstash procesa y enriquece los logs
   - Elasticsearch indexa los datos

### 5. **Creación de Alertas** (10 segundos)
   - 5 alertas de seguridad creadas en TheHive
   - Cada alerta contiene artefactos relacionados (IPs, hashes, archivos)

### 6. **Creación de Casos** (10 segundos)
   - 5 casos de incidentes creados con clasificación VERIS/ENISA
   - Incluyen descripción detallada, SLA y criticidad
   - Estado inicial: Abierto / Para investigar

**Tiempo total aproximado: 3-5 minutos**

---

## 🌐 Acceso a las Herramientas

Una vez completado el automatizador, accede a:

### Kibana (Búsqueda y visualización de logs)
- **URL:** http://localhost:5602
- **Usuario:** Sin autenticación (por defecto)
- **Acción recomendada:**
  1. Crea un index pattern `logstash-*`
  2. Usa la sección **Discover** para ver los logs
  3. Filtra por términos clave:
     - `Failed password` - Intentos SSH fallidos
     - `UFW BLOCK` - Escaneo de puertos
     - `Accepted password` - Accesos exitosos
     - `Malware` - Detección de malware
     - `PRIVESC` - Escalada de privilegios

### TheHive (Gestión de incidentes)
- **URL:** http://localhost:9000
- **Usuario:** `admin`
- **Contraseña:** `secret`
- **Secciones a revisar:**
  - **Alerts:** 5 alertas de seguridad con artefactos
  - **Cases:** 5 casos de incidentes clasificados
  - Verifica SLA, criticidad y clasificación VERIS

### Elasticsearch API (Consulta directa)
- **URL:** http://localhost:9200
- **Ejemplo de consulta:**
  ```
  GET http://localhost:9200/_cat/indices
  GET http://localhost:9200/logstash-*/_search
  ```

---

## 🔍 Qué Buscar en la Demo

### En Kibana
1. **Dashboard de seguridad:**
   - Número total de eventos
   - Eventos por IP origen
   - Eventos por tipo de ataque

2. **Búsquedas específicas:**
   - `kubectl` → Ver eventos de red
   - `ssh` → Ver intentos de acceso SSH
   - `malware` → Ver detecciones de malware

### En TheHive
1. **Alerts tab:**
   - Verifica los 5 tipos de alertas creadas
   - Revisa los artefactos asociados (IPs, hashes, dominios)

2. **Cases tab:**
   - Casos con clasificación VERIS (Initial Access, Credential Access, etc.)
   - SLA asignado (crítica = 1h, alta = 2-4h)
   - Estado: Abierto, con información detallada

---

## ⚠️ Solución de Problemas

### Error: "Docker no está disponible"
```powershell
# Solución: Abre Docker Desktop y espera a que esté completamente iniciado
# Luego ejecuta de nuevo el automatizador
```

### Error: "TheHive/Kibana aún no disponible después de reintentos"
```powershell
# Solución 1: Más tiempo de inicialización
.\automatizador.ps1 -Clean

# Solución 2: Verifica recursos del sistema
# Abre Task Manager > Rendimiento y verifica RAM disponible

# Solución 3: Aumenta memoria disponible para Docker
# Docker Desktop > Preferences > Resources > Memory (aumenta a 4GB+)
```

### Error: "Python no encontrado"
```powershell
# Verifica que Python esté en PATH
python --version

# Si no aparece, instala Python desde python.org
# y marca "Add Python to PATH" durante la instalación
```

### Los logs no aparecen en Kibana
```powershell
# 1. Verifica que el archivo de logs existe:
#    E:\syslog-ng-test-main\logs\server\syslog-client\ataque.log

# 2. Crea el index pattern en Kibana:
#    - Management > Index Patterns > Create pattern > logstash-*

# 3. Espera 1-2 minutos adicionales para que se procesen todos los logs
```

### TheHive no muestra alertas/casos
```powershell
# Verifica la clave API:
# 1. Ve a http://localhost:9000/
# 2. Settings > API Keys
# 3. Copia la clave correcta en crear_alerta.py y crear_caso.py
```

---

## 📝 Notas Importantes

### Para la Demostración
- **No desactives Docker** durante los 3-5 minutos de ejecución
- Los logs toman ~5-10 segundos en aparecer en Kibana después de generarse
- Las alertas se crean después de que los logs son procesados
- Los casos pueden tardar 2-3 segundos en aparecer en TheHive

### Seguridad
- **API Key de TheHive:** Cambia la clave por defecto antes de llevar a producción
- **Elasticsearch:** Habilita autenticación en docker-compose.yml
- **Kibana:** Agrega autenticación si se expone a red externa

### Limpieza
Para liberar recursos después de la demo:
```powershell
cd E:\syslog-ng-test-main
docker-compose down -v
```

---

## 📊 Rúbrica de Evaluación

Este proyecto cubre los siguientes aspectos:

✅ **Infraestructura Docker (25%):**
   - `docker-compose` levanta 7 servicios sin errores
   - Uso avanzado de redes, volúmenes persistentes y variables de entorno

✅ **Detección y Alerta (10%):**
   - Logs llegan en tiempo real a Kibana
   - 5 reglas de correlación personalizadas crean alertas automáticamente

✅ **Gestión de Incidentes:**
   - Casos profesionales en TheHive
   - Clasificación VERIS/ENISA implementada
   - SLA y criticidad asignados correctamente

✅ **Demo:**
   - Flujo automático sin intervención manual
   - Demostración clara de detección en tiempo real

---

## 🎯 Tips para Presentación

1. **Abre las herramientas en orden:**
   - Primero: Kibana (muestra los logs en vivo)
   - Segundo: TheHive (muestra alertas y casos)

2. **Explica el flujo:**
   "Aquí ves cómo detectamos ataques en 5 fases: reconocimiento, acceso, movimiento lateral, escalada y exfiltración"

3. **Muestra métricas:**
   - Número de eventos procesados
   - Tiempo de detección (casi real-time)
   - Clasificación automática de amenazas

4. **Responde preguntas sobre:**
   - Escalabilidad: "Elasticsearch puede manejar millones de eventos"
   - Integración: "Logstash puede parsear cualquier formato de log"
   - Automatización: "Las alertas se crean automáticamente según correlaciones"

---

## 📞 Soporte

Si encuentras problemas:
1. Revisa el log del automatizador con `-Verbose`
2. Verifica estado de contenedores: `docker-compose ps`
3. Ve logs de un servicio: `docker-compose logs elasticsearch`

---

**Última actualización:** 9 de febrero de 2026
**Versión del proyecto:** 1.0 (Demo optimizada)
