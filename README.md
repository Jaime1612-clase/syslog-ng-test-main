## Diagrama de flujo

- Endpoints/Red → Filebeat → Wazuh Manager → (Wazuh Indexer, Dashboard)
- Wazuh Manager → TheHive (alertas)
- TheHive → Cortex (análisis)
- traffic-generator → Filebeat (simulación de logs)

## Notas
- Todos los servicios se comunican en la red interna `socnet` definida en docker-compose.
- Los volúmenes aseguran persistencia de datos y logs.
- El script de traffic-generator debe tener permisos de ejecución en sistemas Linux.

---

# Flujo de Seguridad CyberSOC

## 1. Ingesta y Recolección
- **Wazuh Manager** recibe logs de endpoints (agentes Wazuh instalados en sistemas finales) y de red (por syslog o agentes).
- El contenedor `traffic-generator` simula eventos y ataques para pruebas.

## 2. Análisis y Correlación (SIEM)
- **Wazuh Indexer** y **Wazuh Manager** centralizan, analizan y correlacionan los logs.
- Se detectan patrones sospechosos y eventos relevantes.

## 3. Gestión de Alertas
- **Wazuh** genera alertas automáticas ante eventos críticos.
- Las alertas se visualizan en **Wazuh Dashboard**.
- (Opcional) Las alertas pueden integrarse con TheHive para crear incidentes automáticamente.

## 4. Gestión de Incidentes (Ticketing)
- **TheHive** permite documentar, clasificar, valorar y hacer seguimiento de los incidentes detectados.
- Los analistas pueden triar, investigar y resolver los casos desde la interfaz web de TheHive.

---

### Resumen del flujo
1. Logs → Wazuh Manager → Wazuh Indexer
2. Detección/alerta → Wazuh Dashboard
3. (Opcional) Alerta → TheHive (incidente)
4. Gestión y resolución en TheHive

---
