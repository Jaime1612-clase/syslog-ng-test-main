# Elasticsearch Watcher - Alertas Automáticas a TheHive
# Guía de Configuración

## 1. CREAR UN WATCHER PARA SSH BRUTE FORCE

Ejecuta este comando en Kibana Dev Tools o via curl:

```json
PUT _watcher/watch/ssh_brute_force_alert
{
  "trigger": {
    "schedule": {
      "interval": "5m"
    }
  },
  "input": {
    "search": {
      "request": {
        "index": "*",
        "body": {
          "query": {
            "bool": {
              "must": [
                {
                  "match_phrase": {
                    "message": "Failed password"
                  }
                }
              ],
              "filter": [
                {
                  "range": {
                    "@timestamp": {
                      "gte": "now-10m"
                    }
                  }
                }
              ]
            }
          },
          "aggs": {
            "source_ips": {
              "terms": {
                "field": "message",
                "size": 10
              }
            }
          }
        }
      }
    }
  },
  "condition": {
    "compare": {
      "ctx.payload.hits.total.value": {
        "gte": 10
      }
    }
  },
  "actions": {
    "send_to_thehive": {
      "webhook": {
        "scheme": "http",
        "host": "localhost",
        "port": 9000,
        "method": "post",
        "path": "/api/alert",
        "headers": {
          "Authorization": "TU_API_KEY_AQUI",
          "Content-Type": "application/json"
        },
        "body": """
{
  "title": "SSH Brute Force - {{ctx.payload.hits.total.value}} intentos",
  "description": "Se detectaron {{ctx.payload.hits.total.value}} intentos fallidos de SSH en los últimos 10 minutos",
  "type": "external",
  "source": "Elasticsearch Watcher",
  "sourceRef": "ssh_brute_{{ctx.execution.trigger.triggered_time}}",
  "severity": 2
}
"""
      }
    }
  }
}
```

## 2. CREAR WATCHER PARA PORT SCANNING

```json
PUT _watcher/watch/port_scanning_alert
{
  "trigger": {
    "schedule": {
      "interval": "5m"
    }
  },
  "input": {
    "search": {
      "request": {
        "index": "*",
        "body": {
          "query": {
            "bool": {
              "must": [
                {
                  "match_phrase": {
                    "message": "[UFW BLOCK]"
                  }
                }
              ],
              "filter": [
                {
                  "range": {
                    "@timestamp": {
                      "gte": "now-10m"
                    }
                  }
                }
              ]
            }
          }
        }
      }
    }
  },
  "condition": {
    "compare": {
      "ctx.payload.hits.total.value": {
        "gte": 15
      }
    }
  },
  "actions": {
    "send_to_thehive": {
      "webhook": {
        "scheme": "http",
        "host": "localhost",
        "port": 9000,
        "method": "post",
        "path": "/api/alert",
        "headers": {
          "Authorization": "TU_API_KEY_AQUI",
          "Content-Type": "application/json"
        },
        "body": """
{
  "title": "Port Scanning - {{ctx.payload.hits.total.value}} eventos",
  "description": "Se detectaron {{ctx.payload.hits.total.value}} intentos de escaneo de puertos (UFW BLOCK)",
  "type": "external",
  "source": "Elasticsearch Watcher",
  "sourceRef": "port_scan_{{ctx.execution.trigger.triggered_time}}",
  "severity": 2
}
"""
      }
    }
  }
}
```

## 3. CREAR WATCHER PARA MALWARE

```json
PUT _watcher/watch/malware_detection_alert
{
  "trigger": {
    "schedule": {
      "interval": "3m"
    }
  },
  "input": {
    "search": {
      "request": {
        "index": "*",
        "body": {
          "query": {
            "bool": {
              "must": [
                {
                  "match_phrase": {
                    "message": "[MALWARE]"
                  }
                }
              ],
              "filter": [
                {
                  "range": {
                    "@timestamp": {
                      "gte": "now-10m"
                    }
                  }
                }
              ]
            }
          }
        }
      }
    }
  },
  "condition": {
    "compare": {
      "ctx.payload.hits.total.value": {
        "gte": 1
      }
    }
  },
  "actions": {
    "send_to_thehive": {
      "webhook": {
        "scheme": "http",
        "host": "localhost",
        "port": 9000,
        "method": "post",
        "path": "/api/alert",
        "headers": {
          "Authorization": "TU_API_KEY_AQUI",
          "Content-Type": "application/json"
        },
        "body": """
{
  "title": "CRITICAL - Malware Detectado - {{ctx.payload.hits.total.value}} eventos",
  "description": "Se ha detectado malware. {{ctx.payload.hits.total.value}} eventos encontrados.",
  "type": "external",
  "source": "Elasticsearch Watcher",
  "sourceRef": "malware_{{ctx.execution.trigger.triggered_time}}",
  "severity": 4
}
"""
      }
    }
  }
}
```

---

## CÓMO DESPLEGAR EN KIBANA:

1. Abre Kibana: http://localhost:5602
2. Ve a **Stack Management** → **Watcher**
3. Haz click en **Create Watch**
4. Copia y pega el JSON del watcher que quieras
5. Guarda

O usa la API directamente:

```powershell
$headers = @{"Content-Type" = "application/json"}

$watch_ssh = @{
    "trigger" = @{
        "schedule" = @{
            "interval" = "5m"
        }
    }
    "input" = @{
        "search" = @{
            "request" = @{
                "index" = "*"
                "body" = @{
                    "query" = @{
                        "bool" = @{
                            "must" = @(
                                @{
                                    "match_phrase" = @{
                                        "message" = "Failed password"
                                    }
                                }
                            )
                            "filter" = @(
                                @{
                                    "range" = @{
                                        "@timestamp" = @{
                                            "gte" = "now-10m"
                                        }
                                    }
                                }
                            )
                        }
                    }
                    "size" = 0
                }
            }
        }
    }
    "condition" = @{
        "compare" = @{
            "ctx.payload.hits.total.value" = @{
                "gte" = 10
            }
        }
    }
    "actions" = @{
        "send_to_thehive" = @{
            "webhook" = @{
                "scheme" = "http"
                "host" = "localhost"
                "port" = 9000
                "method" = "post"
                "path" = "/api/alert"
                "headers" = @{
                    "Authorization" = "TU_API_KEY"
                    "Content-Type" = "application/json"
                }
                "body" = '{"title":"SSH Brute Force","description":"Detectado SSH BruteForce","type":"external","source":"Watcher","sourceRef":"ssh_{{execution.trigger.triggered_time}}"}'
            }
        }
    }
} | ConvertTo-Json -Depth 10

Invoke-WebRequest -Uri "http://localhost:9200/_watcher/watch/ssh_brute_force" -Method PUT -Headers $headers -Body $watch_ssh
```

---

## VENTAJAS DE ELASTICSEARCH WATCHER:

✅ **Nativo de Elasticsearch** - Sin scripts externos
✅ **Tiempo real** - Monitoreo continuo cada 5 minutos
✅ **Sin dependencias** - Solo Elasticsearch y TheHive
✅ **Escalable** - Funciona con millones de eventos
✅ **Flexible** - Puedes custom queries y actions

---

## PASOS RÁPIDOS:

1. Abre Kibana Dev Tools
2. Copia un watch del JSON arriba
3. Reemplaza `TU_API_KEY_AQUI` con tu API key de TheHive
4. Ejecuta el comando PUT
5. ¡Listo! Las alertas se crearán automáticamente

¿Quieres que te ayude a configurar los watchers directamente en tu Elasticsearch?
