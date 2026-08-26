# Estructura del Proyecto - Correo_DGGD_Respuestas

```
Correo_DGGD_Respuestas/
├── README.md                           # Descripción general del proyecto
├── config.example.yaml                 # Template de configuración (sin credenciales)
├── requirements.txt                    # Dependencias Python
├── .gitignore                          # Exclusiones de git (credenciales, logs, etc)
│
├── src/                                # Módulos Python principales
│   ├── __init__.py                     # Inicializador del paquete
│   ├── config.py                       # Cargador centralizado de configuración
│   ├── logger.py                       # Logging técnico y auditoría
│   ├── gmail_reader.py                 # Lectura de correos (dguerreron@cdmx.gob.mx)
│   ├── pdf_extractor.py                # OCR + extracción de número de oficio
│   ├── sheets_handler.py               # Lectura/escritura en Google Sheets
│   ├── drive_uploader.py               # Carga de PDFs a Google Drive
│   ├── matching_engine.py              # Búsqueda y vinculación de oficios
│   └── main.py                         # Orquestador principal
│
├── tests/                              # Suite de pruebas
│   ├── __init__.py
│   └── test_fila_541.py                # Pruebas para SEDECO/048/2026
│
├── ops/                                # Scripts operacionales (point of entry)
│   ├── procesar_respuestas.sh          # Ejecución principal
│   └── test_fila_541.sh                # Validación con fila 541
│
├── docs/                               # Documentación técnica
│   ├── arquitectura.md                 # Diagrama y descripción de capas
│   ├── flujo_procesamiento.md          # Detalle paso a paso del flujo
│   └── troubleshooting.md              # Solución de problemas comunes
│
└── HANDOFF/                            # (Será generado después)
    └── HANDOFF_Correo_DGGD_Respuestas.md
```

## Resumen de Archivos Creados

### Configuración y Setup
- **config.example.yaml** — Template para configuración con OAuth token, Sheets ID, Drive folder
- **requirements.txt** — 15 dependencias Python (Google APIs, PDF, OCR, utils)
- **.gitignore** — Excluye config.yaml, logs, PDFs temp (credenciales seguras)

### Módulos Python (src/)

#### 1. **config.py** (60 líneas)
- Carga config.yaml centralizada
- Valida configuración requerida
- Propiedades para acceso fácil

#### 2. **logger.py** (75 líneas)
- Logger técnico (archivo + consola)
- AuditoriaLogger especializado
- Registra cambios en APIs

#### 3. **gmail_reader.py** (120 líneas)
- Lee correos de dguerreron@cdmx.gob.mx
- Descarga adjuntos PDF
- Deduplicación por SHA256
- Marca como leído después de procesar

#### 4. **pdf_extractor.py** (150 líneas)
- Lectura digital (poppler) o OCR (Tesseract español)
- Extrae número de oficio con regex
- Valida formato: SIGLAS/AREA/NUMERO/AAAA
- Manejo de PDFs escaneados

#### 5. **sheets_handler.py** (140 líneas)
- Busca oficio en columna M
- Verifica que columna U está vacía
- Actualiza con URL + nombre de oficio
- Registra timestamp

#### 6. **drive_uploader.py** (125 líneas)
- Sube PDF a Google Drive
- Genera URL compartible
- Busca archivos existentes
- Crea carpetas si necesita

#### 7. **matching_engine.py** (90 líneas)
- Busca oficio en Sheets
- Valida no tiene respuesta
- Actualiza registro
- Registra en auditoría

#### 8. **main.py** (200 líneas)
- Orquestador principal
- Coordina ingesta → extracción → búsqueda → almacenamiento → actualización
- Genera estadísticas
- Manejo de errores y retries

### Scripts Operacionales (ops/)

#### **procesar_respuestas.sh** (Bash)
- Punto de entrada principal
- Activa venv, crea directorios
- Ejecuta procesamiento
- Muestra logs finales

#### **test_fila_541.sh** (Bash)
- Validación específica para fila 541
- 4 fases: config, búsqueda, especificaciones, criterios
- Instrucciones interactivas
- Colores para legibilidad

### Tests (tests/)

#### **test_fila_541.py** (Pytest)
- Tests unitarios de formato
- Tests de patrones de regex
- Validación de fila 541 (marcado skip sin credenciales)

### Documentación (docs/)

#### **arquitectura.md** (400 líneas)
- Diagrama de 4 capas
- Descripción de cada componente
- Flujo de datos
- Manejo de errores
- Estadísticas

#### **flujo_procesamiento.md** (500 líneas)
- 6 pasos detallados
- Sub-pasos y pseudocódigo
- Entrada/salida de cada paso
- Auditoría registrada
- Timing típico
- Troubleshooting por paso

#### **troubleshooting.md** (400 líneas)
- 15 problemas comunes
- Síntomas, causa, solución
- Verificación para cada caso
- Comandos debug
- Cómo obtener logs detallados

## Totales

| Categoría | Cantidad | LOC Aprox |
|-----------|----------|-----------|
| Módulos Python | 8 | 1,100 |
| Scripts Bash | 2 | 120 |
| Tests | 1 | 70 |
| Documentación | 3 | 1,300 |
| Config/Setup | 3 | 50 |
| **Total** | **20 archivos** | **~2,640 LOC** |

## Estado Actual

✅ Estructura completa  
✅ Módulos implementados  
✅ Documentación técnica  
✅ Scripts operacionales  
✅ Git inicializado  
✅ Commit inicial realizado  

## Próximos Pasos

1. **Crear repositorio en GitHub:** `Correo_DGGD_Respuestas`
2. **Push a GitHub:** `git push -u origin main`
3. **Configurar credenciales:** Copiar config.example.yaml a config.yaml + OAuth token
4. **Prueba con fila 541:** `bash ops/test_fila_541.sh`
5. **Procesamiento automático:** `bash ops/procesar_respuestas.sh` (cron/programación)

## Comandos Útiles

```bash
# Clonar (después de push a GitHub)
git clone https://github.com/CorreoDGGD/Correo_DGGD_Respuestas.git
cd Correo_DGGD_Respuestas

# Setup local
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp config.example.yaml config.yaml
# Editar config.yaml con credenciales

# Crear directorios necesarios
mkdir -p logs temp

# Validar configuración
python -m src.main validar

# Ejecutar prueba
bash ops/test_fila_541.sh

# Procesar respuestas
bash ops/procesar_respuestas.sh

# Ver logs
tail -f logs/tecnico.log
tail -f logs/auditoria.log
```

---

**Preparado por:** Claude (Claude Code)  
**Fecha:** 26 de agosto de 2026  
**Versión:** 1.0 — Setup inicial completo
