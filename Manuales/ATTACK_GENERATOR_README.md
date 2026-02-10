# Attack Generator - Generador de Logs de Ataque

Genera ataques simulados contra el cliente que producen logs realistas para ser ingestados por Elasticsearch.

## Características

El generador simula los siguientes tipos de ataques:

- **SSH Brute Force**: Intentos fallidos y exitosos de acceso SSH
- **Port Scanning**: Detección UFW de escaneo de puertos
- **Privilege Escalation**: Intentos de escalada de privilegios
- **Malware Detection**: Detección de archivos maliciosos
- **Data Exfiltration**: Transferencias sospechosas de datos
- **SQL Injection**: Intentos de inyección SQL
- **Web Attacks**: Solicitudes HTTP sospechosas

## Uso

### Opción 1: Python

```powershell
python attack_generator.py
```

### Opción 2: PowerShell

```powershell
.\attack_generator.ps1
```

## Salida

- Los logs se generan en: `logs/server/syslog-client/ataque.log`
- Formato estándar syslog compatible con Filebeat/Elasticsearch
- Se sobrescribe el archivo anterior en cada ejecución

## IPs de Atacante Simuladas

El script utiliza un conjunto de IPs realistas:
- 192.168.1.100
- 10.0.0.5
- 172.16.0.50
- 203.0.113.45
- 198.51.100.10

## Usuarios Objetivo

- admin, root, user, test, nginx, apache, postgres

## Flujo

1. Ejecuta el script
2. Genera múltiples tipos de ataques secuencialmente
3. Escribe logs en el archivo de destino
4. Filebeat automáticamente toma los logs
5. Logs se envían a Elasticsearch
6. Puedes ver los logs en Kibana

## Notas

- Los logs se generan con timestamps reales
- Compatible con Elasticsearch e integración con TheHive
- Cada ejecución limpia logs anteriores
- Los ataques se generan con delays aleatorios para ser más realistas
