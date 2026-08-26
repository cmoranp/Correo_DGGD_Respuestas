# Correo_DGGD_Respuestas

Sistema automatizado para identificación y registro de **respuestas a oficios** en la Dirección General de Gobierno Digital (DGGD).

## ¿Qué hace?

Este sistema cierra el ciclo de correspondencia institucional:

1. **Monitorea** la bandeja de entrada de `dguerreron@cdmx.gob.mx`
2. **Extrae** el número de oficio referenciado en documentos PDF (usando OCR)
3. **Busca** ese oficio en el registro final de ENTRADAS 2026_DGGD
4. **Vincula** la respuesta al registro con una URL de Google Drive

**Resultado:** Cierre automático del ciclo sin intervención manual.

## Requisitos

### Tecnología
- Python 3.9+
- Tesseract OCR (incluida en Docker, o instala localmente)
- Acceso a:
  - Gmail API (lectura de correos)
  - Google Drive API (almacenamiento de PDFs)
  - Google Sheets API (actualización de registro)

### Infraestructura
- Credenciales OAuth 2.0 de Google (mismo token que CorreoDGGD)
- Carpeta de Google Drive: `1mqd9JOsYyX3x1zKufFd5iuXZeTLkSck0`
- Google Sheets: ENTRADAS 2026_DGGD

## Instalación Rápida

### 1. Clonar repositorio
```bash
git clone https://github.com/CorreoDGGD/Correo_DGGD_Respuestas.git
cd Correo_DGGD_Respuestas
```

### 2. Instalar dependencias
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar credenciales
```bash
cp config.example.yaml config.yaml
# Edita config.yaml con tus credenciales OAuth
chmod 600 config.yaml
```

### 4. Crear directorios
```bash
mkdir -p logs temp
```

## Uso

### Procesar respuestas del día
```bash
bash ops/procesar_respuestas.sh
```

### Prueba con fila específica (541 - SEDECO/048/2026)
```bash
bash ops/test_fila_541.sh
```

### Ver logs
```bash
tail -f logs/tecnico.log      # Logs técnicos
tail -f logs/auditoria.log    # Auditoría de cambios
```

## Estructura

```
Correo_DGGD_Respuestas/
├── src/                      # Módulos Python
│   ├── config.py            # Carga de configuración
│   ├── logger.py            # Auditoría y logging
│   ├── gmail_reader.py      # Lectura de correos
│   ├── pdf_extractor.py     # OCR y extracción
│   ├── sheets_handler.py    # Integración con Sheets
│   ├── drive_uploader.py    # Carga a Drive
│   ├── matching_engine.py   # Búsqueda de oficio
│   └── main.py              # Orquestador
├── tests/                    # Suite de pruebas
├── ops/                      # Scripts operacionales
├── docs/                     # Documentación técnica
├── config.example.yaml       # Template de configuración
└── requirements.txt          # Dependencias Python
```

## Documentación

- **[HANDOFF.md](docs/HANDOFF.md)** — Especificación técnica completa, arquitectura, flujo de procesamiento
- **[arquitectura.md](docs/arquitectura.md)** — Diagrama de capas y componentes
- **[flujo_procesamiento.md](docs/flujo_procesamiento.md)** — Detalle paso a paso
- **[troubleshooting.md](docs/troubleshooting.md)** — Solución de problemas comunes

## Características Principales

### ✅ Monitoreo de Respuestas
- Lectura desde `dguerreron@cdmx.gob.mx`
- Deduplicación por huella de contenido
- Manejo de PDFs digitales y escaneados

### ✅ Extracción Inteligente
- OCR en español (Tesseract)
- Busca patrones: "refiere al oficio [NÚMERO]" o formato directo
- Validación de formato: `SIGLAS/AREA/NUMERO/AAAA`

### ✅ Vinculación Automática
- Búsqueda exacta en Google Sheets (columna M)
- Validación de que no existe respuesta anterior (columna U vacía)
- URL con nombre de oficio para referencia

### ✅ Auditoría Completa
- Logs de acceso a APIs
- Registro de cambios en Sheets
- Timestamps de cada operación

## Primeros Pasos

1. Lee [docs/HANDOFF.md](docs/HANDOFF.md) para entender el flujo completo
2. Configura `config.yaml` con tus credenciales
3. Ejecuta `bash ops/test_fila_541.sh` para validar con el caso de prueba
4. Si todo funciona, inicia con `bash ops/procesar_respuestas.sh`

## Seguridad

⚠️ **IMPORTANTE:**
- **NUNCA** versionees `config.yaml` — contiene credenciales de OAuth
- Usa `config.example.yaml` como referencia
- Asegúrate de que `config.yaml` tiene permisos `chmod 600`
- No publiques tokens en issues o discussions

## Soporte

- **Bugs o errores:** Abre un issue en GitHub
- **Problemas de configuración:** Consulta [troubleshooting.md](docs/troubleshooting.md)
- **Seguridad:** Contacta al mantenedor en privado

## Licencia

Este proyecto es parte de la iniciativa CorreoDGGD de la DGGD.

---

**Autor:** Claude (Claude Code)  
**Última actualización:** 26 de agosto de 2026  
**Versión:** 1.0 — Setup inicial
