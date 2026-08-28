# Deployment Notes - Correo_DGGD_Respuestas

## Current Status
- ✅ System fully functional and tested
- ✅ Governmental account (gobiernodigital@cdmx.gob.mx) configured
- ✅ Email monitoring, PDF processing, and OCR extraction working
- ⚠️ **Pending**: Google Drive folder configuration

## Drive Folder Configuration

### Current Setup
**Working Folder ID**: `199VjS1itopR4_AZSiIRegbaZmeH5BTo3`
- Status: ✅ Fully accessible and tested
- Use this while verifying original folder access

### Target Setup  
**Original Folder ID**: `1mqd9JOsYyX3x1zKufFd5iuXZeTLkSck0`
- Created by: gobiernodigital@cdmx.gob.mx
- Status: ⏳ Pending access verification
- Next steps: Contact Google Workspace admin to verify:
  1. Folder is active (not deleted)
  2. gobiernodigital@cdmx.gob.mx has Editor permissions
  3. OAuth scopes include Drive access

## To Deploy in Production

1. Update `config.yaml`:
```yaml
drive_folder: "1mqd9JOsYyX3x1zKufFd5iuXZeTLkSck0"  # Once access verified
```

2. Test with:
```bash
python -m src.main
```

3. Monitor logs:
```bash
tail -f logs/tecnico.log
tail -f logs/auditoria.log
```

## OAuth Token

- Account: gobiernodigital@cdmx.gob.mx
- Configured: Yes
- Token expiry: 1 hour (refresh manually or implement refresh token flow)

## GitHub Repository

- URL: https://github.com/cmoranp/Correo_DGGD_Respuestas
- Branch: main
- Commits: 4 (fully documented)

---

**Generated:** 2026-08-27  
**Status:** Ready for production (pending folder access verification)
