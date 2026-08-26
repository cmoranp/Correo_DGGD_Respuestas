# Flujo de Procesamiento Detallado

## Vista General

El sistema procesa respuestas en **5 pasos** secuenciales:

```
Ingesta → Extracción → Búsqueda → Almacenamiento → Actualización
```

---

## Paso 1: Ingesta de Respuestas (Gmail Reader)

### Objetivo
Buscar y descargar correos de respuesta con adjuntos PDF.

### Entrada
- Email: `dguerreron@cdmx.gob.mx`
- Filtro: `from:dguerreron@cdmx.gob.mx is:unread has:attachment`
- Máximo: 50 correos por ejecución (configurable)

### Proceso
```
1. Conectar a Gmail API con OAuth token
2. Ejecutar búsqueda
3. Para cada correo encontrado:
   a. Extraer metadatos (asunto, fecha, remitente)
   b. Identificar adjuntos PDF
   c. Descargar PDF (bytes)
   d. Calcular SHA256(msg_id + att_id) para deduplicación
4. Retornar lista de correos procesados
```

### Salida
```json
[
  {
    "id": "abc123...",
    "asunto": "RESPUESTA a solicitud SEDECO/048/2026",
    "de": "Gabriel Guerra <dguerreron@cdmx.gob.mx>",
    "fecha": "Tue, 26 Aug 2026 14:30:45 +0000",
    "adjuntos": [
      {
        "nombre": "respuesta_sedeco.pdf",
        "id": "xyz789...",
        "mimetype": "application/pdf"
      }
    ]
  }
]
```

### Manejo de Errores
- **Conexión fallida:** Log error, exit
- **No hay correos:** Log info, continuar
- **Descarga de PDF falla:** Log error, saltar correo

### Auditoría
- Registra: Email, cantidad de correos encontrados, cantidad de adjuntos

---

## Paso 2: Extracción de Número de Oficio (PDF Extractor)

### Objetivo
Extraer el número de oficio referenciado en el PDF de respuesta.

### Entrada
```
PDF (bytes) → 500 KB a 5 MB típicamente
```

### Proceso

#### Sub-paso 2.1: Lectura Digital
```
IF PDF tiene texto embebido:
  1. Usar pdfplumber para extraer texto
  2. Leer primeras 3 páginas
  3. Retornar texto
ELSE:
  Pasar a OCR
```

#### Sub-paso 2.2: OCR (si no hay texto digital)
```
1. Convertir PDF a imágenes (usando pdf2image)
2. Para cada página (máx 3):
   a. Ejecutar Tesseract en español
   b. Timeout: 30 segundos
   c. Extraer texto
3. Concatenar textos
```

#### Sub-paso 2.3: Búsqueda de Patrón
```
FOR EACH patrón EN [
  r"(?:REFIERE|ATENCIÓN) AL OFICIO ([A-Z/0-9]+)/([0-9]{4})",
  r"RESPUESTA A ([A-Z/0-9]+)/([0-9]{4})",
  r"([A-Z/0-9]{4,})/([0-9]{4})"
]:
  IF MATCH en texto:
    numero_oficio = match.group(1) + "/" + match.group(2)
    VALIDATE formato
    IF válido:
      RETURN numero_oficio

RETURN None
```

#### Sub-paso 2.4: Validación de Formato
```
FUNCTION validar_formato(numero):
  partes = split(numero, "/")
  IF len(partes) < 2:
    RETURN False
  IF última_parte NO es año (4 dígitos):
    RETURN False
  RETURN True
```

### Salida
```
"SEDECO/DGDE/DEANDESI/DDEyPE/048/2026"
```

### Manejo de Errores
- **PDF corrupto:** Log error, saltar
- **OCR timeout:** Log warn, retomar manual
- **No se encuentra número:** Log warning, marcar como no procesable

### Auditoría
- Registra: Nombre archivo PDF, número extraído, método (digital/OCR)

---

## Paso 3: Búsqueda en Google Sheets (Matching Engine)

### Objetivo
Localizar el oficio en el registro final y validar que puede ser actualizado.

### Entrada
```
numero_oficio = "SEDECO/DGDE/DEANDESI/DDEyPE/048/2026"
```

### Proceso

#### Sub-paso 3.1: Búsqueda en Columna M
```
1. Leer Google Sheets columna M (N° DE OFICIO) completa
2. Para cada fila:
   IF celda.strip() == numero_oficio.strip():
     numero_fila = idx
     BREAK
3. IF no encontrado:
     LOG "Oficio no existe en Sheets"
     RETURN None
```

#### Sub-paso 3.2: Verificación de Respuesta Anterior
```
1. Leer celda U{numero_fila} (OFICIO DE RESPUESTA)
2. IF celda NO está vacía:
     LOG "Oficio ya tiene respuesta"
     RETURN False
3. ELSE:
     RETURN True
```

### Salida
```json
{
  "fila": 541,
  "numero_oficio": "SEDECO/DGDE/DEANDESI/DDEyPE/048/2026",
  "puede_actualizar": true
}
```

### Manejo de Errores
- **Oficio no existe:** Log warning, no procesar
- **Ya tiene respuesta:** Log info, no sobrescribir
- **Error de Sheets API:** Log error, retry

### Auditoría
- Registra: LECTURA | Oficio buscado | Fila encontrada o NO_ENCONTRADO

---

## Paso 4: Almacenamiento en Google Drive (Drive Uploader)

### Objetivo
Subir el PDF de respuesta a Google Drive y generar URL compartible.

### Entrada
```
nombre_archivo = "SEDECO_DGDE_DEANDESI_DDEyPE_048_2026_respuesta.pdf"
contenido_pdf = bytes[500KB:5MB]
carpeta_destino = "1mqd9JOsYyX3x1zKufFd5iuXZeTLkSck0"
```

### Proceso

#### Sub-paso 4.1: Preparación de Metadatos
```
file_metadata = {
  "name": nombre_archivo,
  "parents": [carpeta_destino],
  "mimeType": "application/pdf"
}
```

#### Sub-paso 4.2: Upload a Drive
```
1. Crear MediaIoBaseUpload con contenido
2. Llamar Google Drive API files().create()
3. Obtener file_id de respuesta
4. IF file_id:
     LOG "Archivo subido exitosamente"
   ELSE:
     LOG error, RETURN None
```

#### Sub-paso 4.3: Generar URL Compartible
```
1. Crear permiso: role="reader", type="anyone"
2. Llamar files().get(fields="webViewLink")
3. Obtener URL: https://drive.google.com/file/d/{ID}/view
4. RETURN URL
```

### Salida
```
file_id = "1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"
url = "https://drive.google.com/file/d/1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p/view"
```

### Manejo de Errores
- **Upload falla:** Log error, no retornar URL
- **Permiso falla:** Log warn, retornar URL de todas formas
- **API quota:** Log error, esperar o fail

### Auditoría
- Registra: CARGA | Nombre archivo | File ID | Tamaño (bytes)

---

## Paso 5: Actualización en Google Sheets (Sheets Handler)

### Objetivo
Actualizar registro final con URL de respuesta.

### Entrada
```
numero_fila = 541
url_drive = "https://drive.google.com/file/d/1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p/view"
oficio_legible = "SEDECO_DGDE_DEANDESI_DDEyPE_048_2026_respuesta"
```

### Proceso

#### Sub-paso 5.1: Construcción de Valor
```
valor = oficio_legible + "\n" + url_drive

Ejemplo:
SEDECO_DGDE_DEANDESI_DDEyPE_048_2026_respuesta
https://drive.google.com/file/d/1a2b3c4d.../view
```

#### Sub-paso 5.2: Actualización de Celda U
```
1. Llamar spreadsheets().values().update()
2. Range: "ENTRADAS 2026_DGGD!U541"
3. Body: {"values": [[valor]]}
4. ValueInputOption: "RAW"
5. IF success:
     LOG "Fila actualizada"
   ELSE:
     LOG error, RETURN False
```

#### Sub-paso 5.3: Actualización de Timestamp (Opcional)
```
IF columna T existe:
  timestamp = datetime.now().isoformat()
  Actualizar T541 con timestamp
  LOG timestamp
```

### Salida
```
true (exitoso) o false (error)
```

### Manejo de Errores
- **Cell locked:** Log error, no actualizar
- **API error:** Log error, retry 1 vez
- **Quota exceeded:** Log error, dejar para próxima ejecución

### Auditoría
- Registra: ESCRITURA | Fila | Columna | Valor (URL)

---

## Paso 6: Finalización

### Auditoría Final
```
RESUMEN_SESION
Correos=5, PDFs=5, Oficios=4, Vínculos=3, Errores=2
Timestamp=2026-08-26T14:35:20
```

### Marcar Correo como Leído
```
IF vinculacion_exitosa:
  gmail.marcar_como_leido(msg_id)
  LOG "Correo marcado como leído"
ELSE:
  LOG "Correo permanece sin leer para revisión manual"
```

### Generación de Reporte
```
{
  "correos_encontrados": 5,
  "pdfs_procesados": 5,
  "oficios_extraidos": 4,
  "vinculos_exitosos": 3,
  "errores": 2
}
```

---

## Diagrama de Flujo Completo

```
START
  │
  ├─ INGESTA: Buscar correos (Gmail)
  │   └─ Descargar PDFs
  │
  ├─ EXTRACCIÓN: Leer PDF + OCR
  │   └─ Extraer número de oficio
  │
  ├─ BÚSQUEDA: Localizar en Sheets
  │   └─ Validar que puede actualizar
  │
  ├─ ALMACENAMIENTO: Subir a Drive
  │   └─ Generar URL compartible
  │
  ├─ ACTUALIZACIÓN: Escribir en Sheets
  │   └─ Actualizar Columna U
  │
  ├─ AUDITORÍA: Registrar cambios
  │   └─ Generar reporte
  │
  └─ END (éxito) o RETRY (error recuperable)
```

---

## Timing Típico

Por correo:
- **Descarga PDF:** 1-2 segundos
- **OCR (si aplica):** 5-10 segundos
- **Búsqueda Sheets:** 1-2 segundos
- **Upload Drive:** 2-5 segundos
- **Actualización Sheets:** 1-2 segundos

**Total por correo:** 10-22 segundos  
**Para 5 correos:** 50-110 segundos (~2 minutos)

---

## Monitoreo

### Logs a Revisar
- `logs/tecnico.log` — Detalles de cada operación
- `logs/auditoria.log` — Cambios a APIs

### Métricas Importantes
- % de oficios extraidos exitosamente
- % de oficios encontrados en Sheets
- % de vínculos exitosos
- Tiempo promedio por correo
- Cantidad de errores por tipo

---

## Troubleshooting por Paso

Ver [troubleshooting.md](troubleshooting.md) para solución de problemas comunes.
