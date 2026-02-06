# Personalización de scripts para otros tipos de ataques

Puedes adaptar los scripts para simular y detectar diferentes tipos de ataques según tus necesidades:

## Simulación de ataques

- Modifica el archivo `simulador_logs.ps1` para generar logs de otros eventos:
	- Ejemplo: Para simular un ataque de ransomware, añade una línea como:
		```powershell
		Add-Content -Path $logPath -Value "$(Get-Date -Format 'MMM dd HH:mm:ss') syslog-client kernel: [RANSOMWARE DETECTED] SRC=10.0.0.5 DST=10.0.0.10 ..."
		```
	- Puedes simular ataques de phishing, malware, escaneo de puertos, etc., cambiando el mensaje generado.

## Detección y gestión de nuevos eventos

- Modifica la consulta en `integracion_kibana_thehive.py` para buscar otros patrones:
	- Ejemplo: Para detectar eventos de ransomware:
		```python
		query = {
				"query": {
						"match_phrase": {"message": "RANSOMWARE DETECTED"}
				}
		}
		```
	- Puedes combinar varios patrones usando `bool` y `should` para detectar múltiples tipos de ataques.

- Personaliza los campos enviados a TheHive para documentar el tipo de ataque, IP, usuario, etc.

## Recomendaciones

- Documenta cada nuevo tipo de ataque simulado y detectado en TheHive.
- Actualiza el playbook para incluir procedimientos ante nuevos tipos de alertas.

---
# Memoria Técnica

## Esquema de red

La plataforma está compuesta por los siguientes servicios conectados en la red interna `socnet` (docker-compose):

- syslog-client → syslog-server → filebeat → logstash → elasticsearch → kibana → thehive

Cada servicio cumple una función específica en el flujo de seguridad y gestión de incidentes.

## Justificación de herramientas

- **syslog-ng**: Permite la recepción y almacenamiento flexible de logs de red, ideal para pruebas y simulación.
- **Filebeat**: Ligero y eficiente para recolectar logs y enviarlos a Logstash.
- **Logstash**: Potente para procesar, transformar y enrutar logs hacia Elasticsearch.
- **Elasticsearch**: Motor de búsqueda y almacenamiento escalable, facilita la consulta y análisis de grandes volúmenes de logs.
- **Kibana**: Interfaz gráfica para visualizar, analizar y crear dashboards de los datos almacenados en Elasticsearch.
- **TheHive**: Plataforma de gestión de incidentes, permite documentar, clasificar y hacer seguimiento de casos.

## Política de retención de logs

- Los logs se almacenan en volúmenes persistentes definidos en docker-compose.
- La retención depende del espacio asignado a los volúmenes y la configuración de Elasticsearch.
- Se recomienda establecer políticas de rotación y eliminación automática en Elasticsearch para evitar saturación.
- Ejemplo: Retención de logs críticos por 90 días, logs generales por 30 días.

---

# Manual de Operación (Playbook)

## Procedimiento ante alerta específica

1. El analista recibe una alerta en TheHive (por ejemplo, intento de login fallido detectado).
2. Accede a TheHive y revisa la información del caso:
	- IP atacante
	- Fecha y hora del evento
	- Tipo de ataque
3. Consulta Kibana para obtener contexto adicional:
	- Busca logs relacionados con la IP o el evento
	- Analiza patrones de actividad sospechosa
4. Documenta acciones en TheHive:
	- Clasifica el incidente (por ejemplo, brute force, escaneo de puertos)
	- Añade notas y evidencia
5. Si el incidente es crítico:
	- Escala el caso al equipo de respuesta
	- Aplica medidas de contención (bloqueo de IP, revisión de accesos)
6. Cierra el caso en TheHive una vez resuelto, indicando las acciones tomadas.

## Ejemplo de alerta: "Failed password for invalid user"

- El analista detecta la alerta en TheHive.
- Busca en Kibana otros intentos fallidos desde la misma IP.
- Si hay múltiples intentos, clasifica como ataque de fuerza bruta.
- Documenta y escala según la política interna.

---

# Manual y Playbook de la Plataforma CyberSOC

## Diagrama de flujo actualizado

- Ataques simulados → syslog-client → syslog-server → Filebeat → Logstash → Elasticsearch → Kibana → TheHive

## Componentes principales

- **syslog-client**: Simula endpoints que generan logs de ataques.
- **syslog-server**: Recibe y almacena logs de red vía syslog.
- **Filebeat**: Recolecta logs del syslog-server y los envía a Logstash.
- **Logstash**: Procesa y transforma los logs, los envía a Elasticsearch.
- **Elasticsearch**: Almacena y permite consultar los logs.
- **Kibana**: Visualiza y analiza los logs.
- **TheHive**: Gestiona alertas e incidentes.

## Scripts y su función

- **automatizador.ps1**: Automatiza el flujo completo. Levanta los servicios, ejecuta el simulador de ataques, espera la recolección de logs y crea alertas/casos en TheHive.
	- Uso: Ejecutar en PowerShell con permisos suficientes.
	- Flujo: docker-compose up → simulador_logs.ps1 → crear_alerta.py → crear_caso.py

- **simulador_logs.ps1**: Simula ataques generando logs (intentos de login fallidos, escaneo de puertos, accesos exitosos).
	- Uso: Ejecutar para generar logs de prueba en syslog-client.

- **crear_alerta.py**: Envía una alerta a TheHive usando la API, basada en un evento detectado.
	- Uso: Ejecutar tras la generación de logs para crear una alerta de ataque.

- **crear_caso.py**: Similar a crear_alerta.py, permite crear un caso en TheHive.
	- Uso: Ejecutar para documentar un incidente detectado.

- **integracion_kibana_thehive.py**: Automatiza la integración entre Elasticsearch (Kibana) y TheHive. Busca logs de ataques en Elasticsearch y crea alertas en TheHive.
	- Uso: Ejecutar para enviar automáticamente los eventos detectados a TheHive.

## Ejecución paso a paso

1. Levanta todos los servicios:
	 ```
	 docker-compose up -d
	 ```
2. Ejecuta el script automatizador para simular ataques y automatizar el flujo:
	 ```
	 powershell -ExecutionPolicy Bypass -File automatizador.ps1
	 ```
3. Visualiza los logs en Kibana:
	 - Accede a http://localhost:5602
4. Gestiona alertas y casos en TheHive:
	 - Accede a http://localhost:9000
	 - Revisa la sección de alertas y casos.
5. (Opcional) Ejecuta integracion_kibana_thehive.py para automatizar la creación de alertas desde logs detectados:
	 ```
	 python integracion_kibana_thehive.py
	 ```

## Recomendaciones

- Asegúrate de que todos los contenedores estén levantados y conectados.
- Personaliza los scripts según los eventos o ataques que quieras simular.
- Puedes ajustar la consulta de logs en integracion_kibana_thehive.py para detectar diferentes tipos de eventos.
- Revisa Kibana y TheHive para validar el flujo y la gestión de incidentes.

---

# Resumen del flujo

1. Ataques simulados → syslog-client genera logs
2. syslog-server almacena los logs
3. Filebeat recolecta y envía los logs a Logstash
4. Logstash procesa y envía los logs a Elasticsearch
5. Kibana visualiza y permite analizar los logs
6. TheHive gestiona alertas e incidentes
7. Scripts automatizan la creación de alertas y casos

---
