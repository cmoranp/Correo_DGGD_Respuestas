# Troubleshooting - Correo_DGGD_Respuestas

## Problemas Comunes y Soluciones

---

## 1. Error: "config.yaml no encontrado"

**Síntoma:**
```
FileNotFoundError: config.yaml no encontrado. 
Copia config.example.yaml a config.yaml
```

**Solución:**
```bash
cp config.example.yaml config.yaml
# Edita config.yaml con tus credenciales OAuth
chmod 600 config.yaml
```

**Verificación:**
```bash
ls -la config.yaml  # Debe existir
grep oauth_token config.yaml  # Debe tener el token
```

---

## 2. Error: "Configuración requerida no encontrada: google.oauth_token"

**Síntoma:**
```
ValueError: Configuración requerida no encontrada: google.oauth_token
```

**Causa:** Token no configurado en config.yaml

**Solución:**
1. Obtén token OAuth de Google Cloud Console
2. Edita config.yaml:
   ```yaml
   google:
     oauth_token: "[TU_TOKEN_AQUI]"
   ```
3. Reinicia

**Verificación:**
```bash
python -c "from src.config import Config; c = Config(); print('✓ Config OK')"
```

---

## 3. Error: "Error autenticando Gmail"

**Síntoma:**
```
google.auth.exceptions.RefreshError: ...
```

**Causa:**
- Token expirado
- Token inválido
- Permisos insuficientes

**Solución:**
1. Genera nuevo token OAuth en Google Cloud Console
2. Asegúrate de que tiene permisos:
   - Gmail API (read)
   - Google Drive API (write)
   - Google Sheets API (read/write)
3. Reemplaza token en config.yaml
4. Reinicia

**Verificación:**
```bash
python -c "
from src.gmail_reader import GmailReader
from src.config import Config
c = Config()
g = GmailReader(c.oauth_token)
print('✓ Gmail autenticado')
"
```

---

## 4. Error: "No hay correos nuevos que procesar"

**Síntoma:**
```
INFO: No hay correos nuevos que procesar
```

**Causa:**
- No hay correos sin leer en dguerreron@cdmx.gob.mx
- Los que hay ya fueron procesados
- Filtro está excesivamente restrictivo

**Solución:**
1. Verifica que hay correos en `dguerreron@cdmx.gob.mx`
2. Si ya fueron procesados, marca como sin leer:
   ```
   Gmail > Seleccionar correo > "Mark as unread" (botón)
   ```
3. Para testing, envía un correo de prueba a esa dirección

**Verificación:**
```bash
# Manual: Abre Gmail y verifica correos sin leer
# Programático: Ver en logs/tecnico.log la búsqueda
```

---

## 5. Error: "Error en OCR"

**Síntoma:**
```
ERROR: Error en OCR: [pytesseract.TesseractNotFoundError...]
```

**Causa:** Tesseract no está instalado

**Solución (macOS con Homebrew):**
```bash
brew install tesseract
# Verifica instalación
tesseract --version
```

**Solución (Linux):**
```bash
sudo apt-get install tesseract-ocr
```

**Solución (Windows):**
1. Descarga installer desde: https://github.com/UB-Mannheim/tesseract/wiki
2. Ejecuta el instalador
3. Verifica: `tesseract --version`

**Verificación:**
```bash
python -c "
from src.pdf_extractor import PDFExtractor
e = PDFExtractor()
print('✓ Extractor OK')
"
```

---

## 6. Error: "No se pudo extraer número de oficio"

**Síntoma:**
```
WARNING: No se pudo extraer número de oficio
```

**Causa:**
- PDF es muy borroso o de mala calidad
- Número de oficio no aparece en primeras 3 páginas
- Formato de número es diferente al esperado

**Solución:**
1. Verifica que el PDF tiene el número de oficio visible
2. Si es escaneado, asegúrate que la imagen es clara
3. Aumenta la confianza mínima en config.yaml:
   ```yaml
   ocr:
     confianza_minima: 50  # Por defecto es 70
   ```
4. Para testing manual:
   ```bash
   # Ver logs para debug
   tail -f logs/tecnico.log
   ```

**Validación:**
1. Descarga el PDF manualmente
2. Lee el número de oficio visualmente
3. Compara con lo que extrajo el OCR en logs

---

## 7. Error: "Oficio no encontrado en Sheets"

**Síntoma:**
```
WARNING: Oficio SEDECO/DGDE/DEANDESI/DDEyPE/048/2026 no encontrado en Sheets
```

**Causa:**
- Número extraído tiene error de OCR
- Número está mal formateado
- Oficio no existe en el registro (aún no registrado)

**Solución:**
1. Verifica el número extraído vs. el real en PDF
2. Compara con columna M de Google Sheets manualmente
3. Si no existe, registra primero en CorreoDGGD

**Verificación:**
```bash
# Ver en logs qué número se extrajo
grep "Oficio" logs/tecnico.log | head -5
```

---

## 8. Error: "Oficio ya tiene respuesta"

**Síntoma:**
```
LOG: Oficio SEDECO/048/2026 (fila 541) ya tiene respuesta
```

**Causa:**
- Columna U de esa fila ya tiene un valor
- El oficio fue procesado previamente

**Solución:**
1. Verifica en Google Sheets fila 541, columna U
2. Si la respuesta anterior es incorrecta:
   - Limpia la celda
   - Marca correo como sin leer en Gmail
   - Reinicia procesamiento
3. Si es correcta, no hay nada que hacer

---

## 9. Error: "Error subiendo archivo a Drive"

**Síntoma:**
```
ERROR: Error subiendo archivo a Drive: ...
```

**Causa:**
- Cuota de Drive excedida
- Carpeta destino no existe o no tiene permisos
- Token sin permiso de Drive

**Solución:**
1. Verifica cuota en Google Drive settings
2. Verifica que carpeta `1mqd9JOsYyX3x1zKufFd5iuXZeTLkSck0` existe:
   ```
   https://drive.google.com/drive/folders/1mqd9JOsYyX3x1zKufFd5iuXZeTLkSck0
   ```
3. Verifica permisos de carpeta (debe ser compartida)
4. Regenera token OAuth con permisos Drive

**Verificación:**
```bash
# Manual: Abre Google Drive y verifica que puedes subir archivos a esa carpeta
```

---

## 10. Error: "Error actualizando fila"

**Síntoma:**
```
ERROR: Error actualizando fila 541: ...
```

**Causa:**
- Google Sheets API no tiene permisos
- Hoja "ENTRADAS 2026_DGGD" no existe
- Token expirado

**Solución:**
1. Verifica que hoja existe:
   ```
   https://docs.google.com/spreadsheets/d/1Wkq4rGusUwqBsowANhstYoxnw-neFYLXRc2G953oN8Y/edit
   ```
2. Verifica que puedes editar manualmente
3. Regenera token OAuth con permisos Sheets
4. Actualiza config.yaml

---

## 11. Problema: OCR muy lento

**Síntoma:**
```
OCR tardando más de 60 segundos por página
```

**Causa:**
- Imágenes de muy alta resolución
- Tesseract procesando muchas páginas
- Configuración de timeout muy alta

**Solución:**
1. Reduce timeout en config.yaml:
   ```yaml
   ocr:
     timeout: 15  # segundos (default 30)
   ```
2. Procesa máximo 2-3 páginas (ya está limitado a 3)
3. Considera usar GPU si es disponible (future improvement)

---

## 12. Problema: Deduplicación no funciona

**Síntoma:**
```
Mismo correo procesado múltiples veces
```

**Causa:**
- Correos se marcan como leídos pero vuelven a sin leer
- Deduplicación por hash del adjunto se perdió

**Solución:**
1. Verifica que `gmail.marcar_como_leido()` funciona
2. Alternativamente, mantén lista de processed en archivo:
   ```bash
   echo "msg_id+att_id" >> processed.txt
   ```

---

## 13. Problema: Logs muy grandes

**Síntoma:**
```
logs/tecnico.log tiene tamaño > 100 MB
```

**Causa:**
- Muchas ejecuciones sin limpiar
- Logging a nivel DEBUG

**Solución:**
1. Archiva logs antiguos:
   ```bash
   mv logs/tecnico.log logs/tecnico.$(date +%Y%m%d).log
   ```
2. Comprime:
   ```bash
   gzip logs/tecnico.*.log
   ```
3. Reduce nivel de log en config.yaml:
   ```yaml
   logging:
     nivel: "INFO"  # No DEBUG
   ```

---

## 14. Certificados SSL/TLS

**Síntoma:**
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Causa:**
- Certificados del sistema desactualizados
- Problemas de proxy corporativo

**Solución (macOS):**
```bash
/Applications/Python\ 3.x/Install\ Certificates.command
```

**Solución (Linux):**
```bash
pip install certifi
python -m certifi
```

---

## 15. Cómo Obtener Debug Detallado

### Aumentar Nivel de Log
```yaml
# config.yaml
logging:
  nivel: "DEBUG"  # Muestra todo
```

### Revisar Logs en Tiempo Real
```bash
# Terminal 1: Log técnico
tail -f logs/tecnico.log

# Terminal 2: Log de auditoría
tail -f logs/auditoria.log
```

### Ejecutar Test Manual
```bash
python -m pytest tests/test_fila_541.py -v
```

### Debug de Extracción OCR
```bash
python -c "
from src.pdf_extractor import PDFExtractor
with open('respuesta.pdf', 'rb') as f:
    pdf = f.read()
extractor = PDFExtractor()
numero = extractor.extraer_numero_oficio(pdf)
print(f'Extraído: {numero}')
"
```

---

## Contacto y Soporte

- **Issues técnicos:** Abre un issue en GitHub
- **Problemas de configuración:** Revisa `config.example.yaml`
- **Seguridad:** Contacta al mantenedor en privado (no en issues)

---

**Última actualización:** 26 de agosto de 2026  
**Versión:** 1.0
