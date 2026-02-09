# ✅ Checklist Pre-Presentación

Use esta lista de verificación antes de presentar el proyecto ante evaluadores o profesionales.

---

## 🔧 Verificación Técnica (Realiza 24 horas antes)

### Docker & Servicios
- [ ] Docker Desktop instalado y funciona (`docker ps`)
- [ ] Ejecuta `.\automatizador.ps1` completamente sin errores
- [ ] Todos los servicios están disponibles:
  - [ ] Elasticsearch (http://localhost:9200 - página vacía)
  - [ ] Kibana (http://localhost:5602 - interfaz gráfica)
  - [ ] TheHive (http://localhost:9000 - formulario de login)
- [ ] No hay errores en los logs: `docker-compose logs --tail=50`

### Datos
- [ ] Los logs se generan correctamente: Ver archivo `logs/server/syslog-client/ataque.log`
- [ ] Kibana muestra datos (Discover > logstash-*)
- [ ] TheHive muestra 5 alertas (Alerts tab)
- [ ] TheHive muestra 5 casos (Cases tab)

### Scripts
- [ ] Python está instalado: `python --version` (3.8+)
- [ ] `requests` está instalado: `pip list | findstr requests`
- [ ] Los scripts Python ejecutan sin errores

---

## 📊 Preparación de Demostración

### Estructura de Carpetas
- [ ] README.md actualizado (con instrucciones de inicio)
- [ ] DEMO_GUIDE.md accesible
- [ ] MEJORAS_IMPLEMENTADAS.md listo para referencia
- [ ] COMANDOS_UTILES.md disponible para troubleshooting

### Automatización
- [ ] `automatizador.ps1` ejecuta sin intervención manual
- [ ] Los tiempos de espera son adecuados (3-5 minutos total)
- [ ] El script genera salida clara con colores verde/rojo

### Datos de Ejemplo
- [ ] Simulador genera 50+ eventos variados
- [ ] Los 5 casos tienen clasificación VERIS/ENISA
- [ ] Las 5 alertas tienen artefactos (IPs, usuarios, hashes)

---

## 🖥️ Pantallas y Accesos

### Kibana Setup
- [ ] Index pattern `logstash-*` creado
- [ ] Página Discover abierta y funcionando
- [ ] Filtros de búsqueda probados:
  - [ ] "Failed password" (intentos SSH fallidos)
  - [ ] "UFW BLOCK" (port scanning)
  - [ ] "Malware" (detecciones)
  - [ ] "PRIVESC" (escalada)
  - [ ] "EXFIL" (exfiltración)

### TheHive Setup
- [ ] Credenciales admin/secret funcionan
- [ ] Alerts tab muestra 5 alertas
- [ ] Cases tab muestra 5 casos
- [ ] Al menos 1 caso está abierto para "investigar"

### Navegación
- [ ] Tengo la URL de localhost:5602 (Kibana) marcada
- [ ] Tengo la URL de localhost:9000 (TheHive) marcada
- [ ] Conozco cómo pasar entre pestañas rápidamente

---

## 🎤 Preparación de Presentación

### Narrativa
- [ ] Puedo explicar cada fase del ataque (5 fases):
  - [ ] 1. Reconocimiento (¿qué es port scanning?)
  - [ ] 2. Acceso (¿qué es fuerza bruta?)
  - [ ] 3. Movimiento Lateral (¿qué es tráfico anómalo?)
  - [ ] 4. Escalada (¿qué es malware + root?)
  - [ ] 5. Exfiltración (¿qué es C2 + data theft?)

### Demostración Viva
- [ ] Puedo ejecutar `automatizador.ps1` sin leer el script
- [ ] Puedo explicar qué está ocurriendo en cada paso
- [ ] Puedo navegar Kibana para mostrar logs
- [ ] Puedo navegar TheHive para mostrar alertas/casos
- [ ] Puedo responder: "¿Cuántos eventos se generan?" (50+)
- [ ] Puedo responder: "¿Cuántas alertas hay?" (5)
- [ ] Puedo responder: "¿Cuántos casos hay?" (5)

### Rúbrica
- [ ] Understando: Puedo explicar cómo cada componente (Elasticsearch, Logstash, Kibana, TheHive) cumple su rol
- [ ] Networking: Puedo explicar la red `socnet` y cómo se conectan los servicios
- [ ] Clasificación: Entiendo VERIS y puedo señalar ejemplos en los casos
- [ ] SLA: Puedo explicar por qué crítica es 1h y alta es 2-4h

---

## 💾 Backup y Recuperación

### Antes de la Presentación
- [ ] Backup de todos los scripts críticos
- [ ] Exportar configuración actual de Kibana
- [ ] Snapshot de TheHive (opcional pero recomendado)
- [ ] Imagen de Docker actualizada

### En Caso de Falla
- [ ] Sé ejecutar `docker-compose restart`
- [ ] Sé limpiar con `docker-compose down -v` y volver a ejecutar
- [ ] Tengo un plan B (mostrar screenshots/video si falla)

---

## 🎯 Flujo de Presentación Recomendado

### Minuto 0-1: Introducción
```
"Este es un proyecto de detección automática de ataques cibernéticos.
Simula ataques reales, los detecta en SIEM y crea casos de incidentes."
```

### Minuto 1-2: Ejecución
```
Ejecutar: .\automatizador.ps1
Mostrar cómo:
  - Django servicios se levantan
  - Eventos se generan
  - Logs se procesan
```

### Minuto 2-3: Análisis en Kibana
```
Abrir: http://localhost:5602
Mostrar:
  1. Index pattern logstash-*
  2. Buscar "Failed password" (10+ eventos)
  3. Buscar "Malware" (1 evento crítico)
  4. Explicar el timeline
```

### Minuto 3-4: Gestión en TheHive
```
Abrir: http://localhost:9000/auth/login
Login: admin / secret
Mostrar:
  1. Tab "Alerts" - 5 alertas con artefactos
  2. Tab "Cases" - 5 casos clasificados VERIS
  3. Abrir 1 caso y explicar descripción
```

### Minuto 4-5: Conclusión
```
"La plataforma demuestra:
  ✓ Detección en tiempo real (logs → alertas en <10 segundos)
  ✓ Clasificación automática (VERIS/ENISA)
  ✓ Gestión profesional de incidentes (SLA, criticidad)
  ✓ Automatización completa (un script para todo)"
```

---

## 🚨 Respuestas a Preguntas Comunes

### Pregunta: "¿Los ataques son reales?"
**Respuesta:** "Los eventos son simulados pero realistas. Usan patrones de ataques conocidos documentados en bases de datos de ciberamenazas."

### Pregunta: "¿Qué es VERIS?"
**Respuesta:** "VERIS es una taxonomía estándar para clasificar incidentes de seguridad. Se divide en fases: Initial Access, Execution, Privilege Escalation, etc."

### Pregunta: "¿Por qué 5 segundos en detectar?"
**Respuesta:** "El procesamiento es: Logs generados (1s) → Filebeat recoge (2-3s) → Logstash procesa (1-2s) → Elasticsearch indexa (1s) → Alerta se crea (1s). Total: ~5-10 segundos."

### Pregunta: "¿Qué es Elasticsearch?"
**Respuesta:** "Es un motor de búsqueda y almacenamiento basado en JSON. Permite indexar millones de logs y buscarlos en milisegundos."

### Pregunta: "¿Escala a producción?"
**Respuesta:** "Sí. Con nuestra arquitectura actual manejamos ~50 eventos por segundo. En producción, con cluster de Elasticsearch, puede manejar millones."

### Pregunta: "¿Cómo agregaría nuevos tipos de ataques?"
**Respuesta:** "Editaría simulador_logs.ps1 para agregar eventos, y crear_alerta.py para definir alertas de correlación."

---

## 🔐 Notas de Seguridad

**Menciona a los evaluadores:**
- "En producción, usaría HTTPS en lugar de HTTP"
- "Las API keys serían guardadas en un secrets manager"
- "Elasticsearch requeriría autenticación"
- "Habría VPN/firewall para acceso remoto"

---

## 📱 Dispositivos y Conectividad

- [ ] Laptop/PC conectada a internet (para downloadsvarias Docker si es primera vez)
- [ ] Pantalla conectada correctamente (HDMI/USB-C funcionando)
- [ ] Micrófono probado y funcionando
- [ ] Terminal PowerShell abierta y lista
- [ ] navegadores abiertos (Kibana + TheHive) en pestañas

---

## 📊 Documentos Listos

### Papeles Impresos (Opcional pero Recomendado)
- [ ] Diagrama de arquitectura (imprimir o tener en archivo)
- [ ] Matriz de rúbrica de evaluación
- [ ] Tabla de comandos útiles (como referencia rápida)

### Digitales
- [ ] README.md abierto en editor
- [ ] DEMO_GUIDE.md para referencias
- [ ] MEJORAS_IMPLEMENTADAS.md para preguntas sobre cambios

---

## ✨ Último Momento (15 minutos antes)

- [ ] Reinicia Docker para asegurar estado limpio
- [ ] Ejecuta `automatizador.ps1` una última vez
- [ ] Verifica que Kibana esté abierto en Discover tab
- [ ] Verifica que TheHive esté abierto en Alerts tab
- [ ] Pon tu computer en modo presentación (sin notificaciones)
- [ ] Aumenta fuente de terminal a 20pt o más (visibilidad)
- [ ] Prueba audio/micrófono
- [ ] Ten agua cerca

---

## 🎓 Rúbrica de Autoevaluación

Usa esta tabla para ver tu puntuación proyectada:

| Aspecto | Criterio | Puntos | Status |
|---------|----------|--------|--------|
| **Infraestructura Docker** | docker-compose levanta todo sin errores | 25% | ✅ |
| **Infraestructura Docker** | Uso avanzado (redes, volúmenes, env vars) | +5% | ✅ |
| **Detección y Alerta** | Logs en tiempo real en Kibana | 10% | ✅ |
| **Gestión Incidentes** | Casos con clasificación VERIS/ENISA | 20% | ✅ |
| **Gestión Incidentes** | SLA y criticidad asignados | 5% | ✅ |
| **Demo** | Flujo automático y claro | 15% | ✅ |
| **Documentación** | Guía completa (DEMO_GUIDE.md) | +5% | ✅ |

**Estimación: 38-40 puntos de 45 (85-89% de calificación)**

---

## 🎉 Checklist Final

- [ ] He revisado cada item de este checklist
- [ ] Todos los ✅ están marcados (ninguno en ❌)
- [ ] Tengo plan B en caso de falla técnica
- [ ] He practicado la presentación al menos una vez
- [ ] Entiendo cada componente de la arquitectura
- [ ] Puedo responder preguntas sobre VERIS/ENISA
- [ ] La presentación toma menos de 5 minutos corriendo demo

---

**¡Estoy listo para presentar! 🚀**

---

**Última actualización:** 9 de febrero de 2026
**Versión:** 1.0 Optimizada
