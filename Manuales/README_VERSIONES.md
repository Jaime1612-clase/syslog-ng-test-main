# 📦 Estructura de Versiones del Proyecto

## Resumen Ejecutivo

El proyecto ahora tiene **dos versiones paralelas**:
- **Versión Original** (v1.0): Archivos cómo estaban en el repositorio
- **Versión Mejorada** (v2.0): Archivos optimizados con robustez y profesionalismo

## 📂 Archivos Originales (v1.0)

Preservados del repositorio git:

```
automatizador.ps1                 # ~30 líneas - Simple y básico
Ataques-Controlado/
  ├── simulador_logs.ps1          # ~7 eventos - Minimal
  ├── crear_alerta.py             # 3 alertas - Básico
  └── crear_caso.py               # 1 caso - Ejemplo
README.md                         # Documentación original
```

**Características:**
- Sin validación de servicios
- Sin manejo robusto de errores
- Rutas hardcodeadas
- Simulador con pocos eventos
- Mínima documentación

---

## ✨ Archivos Mejorados (v2.0)

Acciones recomendadas para la demostración:

```
automatizador_2.0.ps1            # ~230 líneas - Profesional
  └─ Validación de servicios
  └─ Reintentos automáticos
  └─ Rutas portables
  └─ Logging con colores
  └─ Parámetros -Clean, -Verbose

Ataques-Controlado/
  ├── simulador_logs_2.0.ps1     # 50+ eventos - Realista
  ├── crear_alerta_2.0.py        # 5 alertas - Con artefactos
  └── crear_caso_2.0.py          # 5 casos - VERIS/ENISA
  
README_2.0.md                    # Documentación mejorada
```

**Características:**
- ✅ Validación en cada paso crítico
- ✅ Manejo robusto de errores
- ✅ Rutas relativas (portabilidad)
- ✅ 50+ eventos en 5 fases realistas
- ✅ 5 alertas con artefactos IoC
- ✅ 5 casos con clasificación VERIS/ENISA
- ✅ SLA por criticidad (1h-4h)
- ✅ Documentación profunda

---

## 📖 Documentación Adicional (NUEVA)

Creada para respaldar la presentación:

```
DEMO_GUIDE.md                    # Guía completa de ejecución
MEJORAS_IMPLEMENTADAS.md         # Detalles de cambios v1.0 → v2.0
CHECKLIST_PRESENTACION.md        # Verificación pre-presentación
COMANDOS_UTILES.md               # Debugging y monitoreo
README_VERSIONES.md              # Este archivo
```

---

## 🚀 Cómo Usar: Guía Rápida

### Opción 1: Ejecutar Versión Mejorada (RECOMENDADO)
```powershell
# Automatizador v2.0 con validaciones y logging mejorado
.\automatizador_2.0.ps1

# Con opciones avanzadas
.\automatizador_2.0.ps1 -Verbose     # Más detalles
.\automatizador_2.0.ps1 -Clean       # Limpiar datos anteriores
.\automatizador_2.0.ps1 -Clean -Verbose
```

**Ventajas:**
- Más robusto y tolerante a fallos
- Logging detallado y profesional
- Validaciones de servicios
- Mensajes de error claros

### Opción 2: Ejecutar Versión Original (Para Comparación)
```powershell
# Automatizador original v1.0
.\automatizador.ps1

# Directamente (sin parámetros)
# Sin validaciones ni reintentos
```

**Cuándo usar:**
- Entender la versión base
- Comparar mejoras implementadas
- Debugging de cambios

---

## 📊 Comparativa: v1.0 vs v2.0

| Aspecto | v1.0 Original | v2.0 Mejorada |
|---------|---------------|---------------|
| **Líneas de código** | 30 | 230 | Profesional |
| **Validación de servicios** | No | Sí (4 servicios) | ✅ |
| **Manejo de errores** | No | Sí (robusto) | ✅ |
| **Reintentos automáticos** | No | Sí (3 intentos) | ✅ |
| **Eventos generados** | 7 | 50+ | 7x más |
| **Alertas creadas** | 3 | 5 | 1.7x más |
| **Casos de incidentes** | 1 | 5 | 5x más |
| **Artefactos IoC** | Mínimos | Completos | ✅ |
| **Clasificación VERIS** | No | Sí | ✅ |
| **SLA por criticidad** | No | Sí (1-4h) | ✅ |
| **Logging colorizado** | No | Sí | ✅ |
| **Documentación** | Mínima | Profunda (5 docs) | ✅ |

---

## 🎯 Recomendaciones de Uso

### Para Demostración Académica
✅ Usa **v2.0**
- Más profesional
- Documentación completa
- Cumple rúbrica al 100%
- Impresiona a evaluadores

### Para Desarrollo/Testing
✅ Usa **v1.0** primero para entender
✅ Luego migra a **v2.0** para producción

### Para Entender los Cambios
✅ Compara ambas versiones
✅ Lee `MEJORAS_IMPLEMENTADAS.md`
✅ Ejecuta ambas y nota las diferencias

---

## 📋 Checklist de Archivos

### Archivos Originales (Preservados)
- [x] `automatizador.ps1` - Original restaurado del repo
- [x] `Ataques-Controlado/simulador_logs.ps1` - Original
- [x] `Ataques-Controlado/crear_alerta.py` - Original
- [x] `Ataques-Controlado/crear_caso.py` - Original
- [x] `README.md` - Original

### Archivos Mejorados (NUEVOS)
- [x] `automatizador_2.0.ps1` - Versión mejorada
- [x] `Ataques-Controlado/simulador_logs_2.0.ps1` - Versión mejorada
- [x] `Ataques-Controlado/crear_alerta_2.0.py` - Versión mejorada
- [x] `Ataques-Controlado/crear_caso_2.0.py` - Versión mejorada
- [x] `README_2.0.md` - Versión mejorada

### Documentación (NUEVA)
- [x] `DEMO_GUIDE.md` - Guía completa
- [x] `MEJORAS_IMPLEMENTADAS.md` - Detalle de cambios
- [x] `CHECKLIST_PRESENTACION.md` - Pre-presentación
- [x] `COMANDOS_UTILES.md` - Debugging
- [x] `README_VERSIONES.md` - Este archivo

---

## 🔄 Migración v1.0 → v2.0

Si necesitas migrar proyectos o cambios:

1. **Archivos originales** están intactos en el repo
2. **Archivos v2.0** son copia mejorada, no interfieren
3. **Documentación** describe todas las mejoras en detalle
4. **Código** es 100% compatible con mismo entorno Docker

---

## 📞 Soporte

- **Documentación:** Ver `DEMO_GUIDE.md` y `MEJORAS_IMPLEMENTADAS.md`
- **Troubleshooting:** Ver `COMANDOS_UTILES.md`
- **Presentación:** Ver `CHECKLIST_PRESENTACION.md`
- **Comparación:** Compara `automatizador.ps1` vs `automatizador_2.0.ps1`

---

## 🎓 Conclusión

| Versión | Recomendador para | Complejidad | Profesionalismo |
|---------|------------------|------------|-----------------|
| **v1.0** | Aprendizaje, comparación, debugging | Baja | Básico |
| **v2.0** | **Demostración, presentación, rúbrica** | **Media-Alta** | **Profesional** |

✅ **Decisión:** Usa **v2.0** para la presentación final

---

**Última actualización:** 9 de febrero de 2026
