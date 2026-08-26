# Instrucciones para Crear Repositorio en GitHub

## Paso 1: Crear Repositorio Vacío en GitHub

1. Abre https://github.com/new
2. Nombre: `Correo_DGGD_Respuestas`
3. Descripción: "Sistema de identificación y registro de respuestas a oficios institucionales"
4. Visibilidad: **Public** (documentado en README, sin credenciales)
5. **NO** inicialices con README (ya existe)
6. Click: **Create repository**

---

## Paso 2: Agregar Remote y Push

En tu terminal en el directorio del proyecto:

```bash
cd /Users/cmoranp/Documents/IA/ANTIGRAVITY/Correo_DGGD_Respuestas

# Agregar remote a GitHub
git remote add origin https://github.com/CorreoDGGD/Correo_DGGD_Respuestas.git

# Renombrar rama a main (si es necesario)
git branch -M main

# Push al repositorio
git push -u origin main
```

---

## Paso 3: Verificar Push

En GitHub:
1. Abre https://github.com/CorreoDGGD/Correo_DGGD_Respuestas
2. Verifica que están los archivos
3. Verifica que NO está `config.yaml` (debe estar en .gitignore)
4. Verifica que hay un commit inicial

---

## Paso 4: Configuración Local

### Setup Inicial (Primera vez)

```bash
cd /Users/cmoranp/Documents/IA/ANTIGRAVITY/Correo_DGGD_Respuestas

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear config local (NO versionada)
cp config.example.yaml config.yaml
chmod 600 config.yaml

# Editar config.yaml con tus credenciales OAuth
# nano config.yaml  # O usa tu editor favorito

# Crear directorios necesarios
mkdir -p logs temp
```

### Configuración de OAuth Token

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea o selecciona tu proyecto
3. Habilita APIs: Gmail, Google Drive, Google Sheets
4. Crea credenciales OAuth 2.0 (cuenta de servicio o credencial de usuario)
5. Descarga el token JSON
6. En `config.yaml`:
   ```yaml
   google:
     oauth_token: "[TU_TOKEN_AQUI]"
   ```

---

## Paso 5: Validar Instalación

```bash
# Activar venv si no está activo
source venv/bin/activate

# Probar imports
python -c "from src.config import Config; print('✓ Config OK')"
python -c "from src.gmail_reader import GmailReader; print('✓ Gmail OK')"
python -c "from src.pdf_extractor import PDFExtractor; print('✓ PDF OK')"

# Ver logs disponibles
ls -lah logs/
```

---

## Paso 6: Prueba con Fila 541

```bash
# Asegurate de tener la carpeta en GitHub primero
# Luego ejecuta la prueba

bash ops/test_fila_541.sh
```

Esto verificará:
- ✓ config.yaml configurado
- ✓ Credenciales válidas
- ✓ Acceso a Gmail, Drive, Sheets
- ✓ Formato de oficio esperado

---

## Paso 7: Procesamiento de Respuestas

### Ejecución Manual

```bash
bash ops/procesar_respuestas.sh
```

### Ejecución Automática (cron)

```bash
# Editar crontab
crontab -e

# Agregar línea para ejecutar diariamente a las 10 AM
0 10 * * * cd /Users/cmoranp/Documents/IA/ANTIGRAVITY/Correo_DGGD_Respuestas && source venv/bin/activate && bash ops/procesar_respuestas.sh >> logs/cron.log 2>&1
```

---

## Paso 8: Monitoreo

```bash
# En una terminal, ver logs técnicos
tail -f logs/tecnico.log

# En otra terminal, ver auditoría
tail -f logs/auditoria.log

# Ver el commit en GitHub
git log --oneline
```

---

## Checklist Final

- [ ] Repositorio creado en GitHub
- [ ] Push realizado exitosamente
- [ ] config.yaml NO está en GitHub (en .gitignore)
- [ ] config.example.yaml SÍ está en GitHub
- [ ] README.md visible en GitHub
- [ ] Venv creado localmente
- [ ] Dependencias instaladas
- [ ] config.yaml con OAuth token
- [ ] Directorios logs/ y temp/ creados
- [ ] Validación de imports OK
- [ ] Prueba test_fila_541.sh OK
- [ ] Procesamiento manual funciona

---

## Troubleshooting Setup

### Error: "fatal: not a git repository"
```bash
cd /Users/cmoranp/Documents/IA/ANTIGRAVITY/Correo_DGGD_Respuestas
git status  # Debe mostrar el estado
```

### Error: "could not read Username"
```bash
# Configurar credenciales de GitHub
git config --global user.name "Tu Nombre"
git config --global user.email "tuemail@ejemplo.com"

# O usar SSH key (recomendado)
# Ver: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
```

### Error: "fatal: destination path already exists"
El directorio ya fue copiado. Verificar:
```bash
ls -la /Users/cmoranp/Documents/IA/ANTIGRAVITY/Correo_DGGD_Respuestas/
```

---

## Próximos Pasos (Fase 2)

Después de validar que todo funciona:

1. ✅ Setup inicial completado
2. **Prueba con fila 541 real** — Encontrar correo de respuesta, validar flujo
3. **Escalado** — Procesar todas las respuestas
4. **Integración** — Sincronización con CorreoDGGD padre
5. **Documentación** — Guía de usuario final

---

## Contacto

- **Issues:** https://github.com/CorreoDGGD/Correo_DGGD_Respuestas/issues
- **Docs:** Ver `/docs/` en el repositorio
- **Seguridad:** No publicar credenciales en issues

---

**Preparado por:** Claude (Claude Code)  
**Fecha:** 26 de agosto de 2026

Estamos listos para la Fase 2: Prueba con fila 541 ✅
