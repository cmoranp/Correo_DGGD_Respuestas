# Arquitectura - Correo_DGGD_Respuestas

## Diagrama General

```
┌─────────────────┐
│  Gmail Reader   │  Monitorea dguerreron@cdmx.gob.mx
└────────┬────────┘
         │ Correos + PDFs adjuntos
         ▼
┌─────────────────┐
│  PDF Extractor  │  OCR + Extrae número de oficio
└────────┬────────┘
         │ Número de oficio validado
         ▼
┌─────────────────┐
│ Matching Engine │  Busca en Sheets, valida
└────────┬────────┘
         │ Oficio encontrado
         ▼
┌─────────────────┐
│ Drive Uploader  │  Carga PDF a Google Drive
└────────┬────────┘
         │ File ID + URL
         ▼
┌─────────────────┐
│ Sheets Handler  │  Actualiza columna U con URL
└────────┬────────┘
         │
         ▼
    ✓ Vinculación exitosa
```

## Capas de Procesamiento

### 1. Ingesta (Gmail Reader)
- **Responsabilidad:** Lectura de correos
- **Fuente:** `dguerreron@cdmx.gob.mx`
- **Output:** Lista de correos con adjuntos PDF
- **Deduplicación:** SHA256 de (msg_id + attachment_id)

**Clase:** `GmailReader`  
**Métodos principales:**
- `buscar_correos(desde, max_resultados)` → List[Dict]
- `descargar_adjunto(msg_id, att_id, nombre)` → bytes
- `marcar_como_leido(msg_id)` → bool

---

### 2. Lectura de PDF (PDF Extractor)
- **Responsabilidad:** Extracción de número de oficio
- **Input:** Contenido PDF (bytes)
- **Output:** Número de oficio validado
- **Método:** Primero texto digital (poppler), luego OCR (Tesseract español)

**Clase:** `PDFExtractor`  
**Métodos principales:**
- `extraer_numero_oficio(pdf_bytes)` → str|None
- `_leer_texto_digital(pdf_bytes)` → str|None
- `_leer_ocr(pdf_bytes)` → str|None
- `_extraer_numero_de_texto(texto)` → str|None
- `_validar_formato(numero)` → bool

---

### 3. Búsqueda y Vinculación (Matching Engine)
- **Responsabilidad:** Buscar oficio en Sheets, validar, actualizar
- **Input:** Número de oficio, URL Drive
- **Output:** Éxito/Fracaso de vinculación
- **Validaciones:**
  - Oficio existe en columna M
  - Columna U está vacía (sin respuesta anterior)
  - Formato correcto

**Clase:** `MatchingEngine`  
**Métodos principales:**
- `procesar_respuesta(numero_oficio, url_drive, nombre)` → bool
- `validar_oficio_formato(numero)` → bool

---

### 4. Almacenamiento en Drive (Drive Uploader)
- **Responsabilidad:** Subir PDF y generar URL compartible
- **Input:** Nombre archivo + contenido PDF
- **Output:** File ID + URL compartible
- **Carpeta destino:** `1mqd9JOsYyX3x1zKufFd5iuXZeTLkSck0`

**Clase:** `DriveUploader`  
**Métodos principales:**
- `subir_archivo(nombre, contenido)` → str|None (file_id)
- `obtener_url_compartible(file_id)` → str|None
- `buscar_archivo(nombre)` → str|None (file_id)

---

### 5. Integración Sheets (Sheets Handler)
- **Responsabilidad:** Lectura y escritura en Google Sheets
- **Input:** Número de fila + URL + nombre oficio
- **Output:** Confirmación de escritura
- **Hoja destino:** ENTRADAS 2026_DGGD

**Clase:** `SheetsHandler`  
**Métodos principales:**
- `buscar_oficio(numero_oficio)` → Dict|None
- `actualizar_oficio_respuesta(fila, url, nombre)` → bool
- `verificar_respuesta_existe(fila)` → bool
- `actualizar_timestamp(fila, timestamp)` → bool

---

## Componentes Transversales

### Configuración (Config)
- **Archivo:** `config.yaml` (no versionado)
- **Template:** `config.example.yaml`
- **Propiedades:** OAuth token, Sheets ID, Drive folder, email, OCR settings

**Clase:** `Config`

---

### Logging (Logger)
- **Log técnico:** `logs/tecnico.log` (DEBUG, INFO, WARNING, ERROR)
- **Log de auditoría:** `logs/auditoria.log` (acceso a APIs, cambios)

**Clases:**
- `setup_logger()` → (logger, auditoria)
- `AuditoriaLogger` (especializado para cambios en APIs)

---

## Orquestación Principal (Main)

**Clase:** `CorreoDGGDResponstas`

Coordina todo el flujo:

```python
1. Leer config → Setup loggers
2. Inicializar módulos (Gmail, PDF, Sheets, Drive, Matching)
3. Para cada correo:
   - Descargar adjuntos
   - Extraer número de oficio
   - Subir a Drive
   - Vincular en Sheets
   - Registrar auditoría
4. Generar reporte de estadísticas
```

---

## Flujo de Datos

```
config.yaml
    ↓
Config ──────────────────┐
                         │
                    setup_logger()
                         │
     ┌────────────────────┼────────────────────┐
     ↓                    ↓                    ↓
Gmail Reader          PDF Extractor      Sheets Handler
     │                    │                    │
     ├─── Matching Engine ─────────────────────┤
     │         │                               │
     ├─────────┼───────────────────────────────┤
     │         ↓                               │
     │    Drive Uploader                       │
     │         │                               │
     └─────────┼───────────────────────────────┘
               │
          Auditoría Logger
               │
          logs/auditoria.log
          logs/tecnico.log
```

---

## Secuencia de Procesamiento (Fila 541)

```
1. Gmail Reader busca correos de dguerreron@cdmx.gob.mx
   Encuentra: correo con PDF adjunto (ej: "respuesta_sedeco_agos2026.pdf")

2. PDF Extractor procesa el PDF
   Extrae: "SEDECO/DGDE/DEANDESI/DDEyPE/048/2026"
   Valida: Formato correcto ✓

3. Matching Engine busca oficio en Sheets
   Busca: Columna M por "SEDECO/DGDE/DEANDESI/DDEyPE/048/2026"
   Encuentra: Fila 541
   Valida: Columna U vacía ✓

4. Drive Uploader sube PDF
   Nombre: "SEDECO_DGDE_DEANDESI_DDEyPE_048_2026_respuesta.pdf"
   Obtiene: File ID + URL compartible

5. Sheets Handler actualiza Sheets
   Fila: 541
   Columna: U
   Valor: "SEDECO_DGDE_DEANDESI_DDEyPE_048_2026_respuesta" + URL
   Timestamp: 2026-08-26 14:30:45

6. Auditoría registra cambio
   ESCRITURA | Tabla=ENTRADAS 2026_DGGD | Fila=541 | Columna=U | ...

7. ✓ Éxito - Email marcado como leído
```

---

## Manejo de Errores

### Nivel 1: Descarga PDF
- Si falla: Registrar error, continuar con siguiente correo
- Reintento: No (evitar duplicación)

### Nivel 2: Extracción de oficio
- Si no encuentra: Registrar warning, no procesar
- Si formato inválido: Registrar error, rechazar

### Nivel 3: Búsqueda en Sheets
- Si no existe: Registrar "NO_ENCONTRADO", no procesar
- Si tiene respuesta: Registrar "YA_ATENDIDO", no sobrescribir

### Nivel 4: Carga a Drive
- Si falla: Registrar error, no vincular
- Reintento: Sí (operación importante)

### Nivel 5: Escritura en Sheets
- Si falla: Registrar error crítico
- Rollback: Marcar adjunto como no procesado

---

## Estadísticas del Procesamiento

Al finalizar, genera reporte:

```json
{
  "correos_encontrados": 5,
  "pdfs_procesados": 5,
  "oficios_extraidos": 4,
  "vinculos_exitosos": 3,
  "errores": 2
}
```

Guardado en auditoría y mostrado en logs.
