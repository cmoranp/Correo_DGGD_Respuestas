# Deployment Notes - Correo_DGGD_Respuestas

## Architecture: CorreoDGGD-Compatible (File-Based Credentials)

**Matching CorreoDGGD's security approach:**
- ✅ Credentials loaded from external files (NOT in git)
- ✅ Automatic token refresh via refresh_token
- ✅ No secrets hardcoded or versioned
- ✅ Long-lived tokens (indefinite with auto-refresh)

## Current Status
- ✅ System fully functional and tested  
- ✅ Code architecture complete (CorreoDGGD-compatible)
- ✅ Email monitoring, PDF processing, OCR extraction working
- ⏳ **Pending**: OAuth token generation and folder access

## Setup Instructions

### Step 1: Download Client Secret
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. APIs & Services → Credentials
3. Click "Create Credentials" → OAuth 2.0 Client ID → Desktop application
4. Download JSON file and save as `client_secret.json` (temporary, local only)

### Step 2: Generate Token File
```bash
python3 get_token.py client_secret.json
```
Creates `google_token.json` with refresh_token for indefinite access.

### Step 3: Secure External Storage
```bash
# Move both files to secure location OUTSIDE the repository
mkdir -p /secure/path/secrets
cp google_token.json /secure/path/secrets/google_token.json
cp client_secret.json /secure/path/secrets/client_secret.json
chmod 600 /secure/path/secrets/*

# Clean up repo directory
rm google_token.json client_secret.json
```

### Step 4: Configure config.yaml
```yaml
google:
  google_client_secret_path: "/secure/path/secrets/client_secret.json"
  google_token_path: "/secure/path/secrets/google_token.json"
  sheets_id: "1Wkq4rGusUwqBsowANhstYoxnw-neFYLXRc2G953oN8Y"
  drive_folder: "1mqd9JOsYyX3x1zKufFd5iuXZeTLkSck0"
```

### Step 5: Validate Connection
```bash
python -m src.main validar
```

### Step 6: Run Processing
```bash
bash ops/procesar_respuestas.sh
```

## Drive Folder Access

**Target Folder ID**: `1mqd9JOsYyX3x1zKufFd5iuXZeTLkSck0`
- Created by: gobiernodigital@cdmx.gob.mx
- Status: ⏳ Requires access verification

**To verify access:**
1. Test with valid token: `python -m src.main validar`
2. Check folder exists: https://drive.google.com/drive/folders/1mqd9JOsYyX3x1zKufFd5iuXZeTLkSck0
3. Verify permissions in Google Workspace admin console

## Key Architectural Changes

| Aspect | Before | After |
|--------|--------|-------|
| Token Type | Access token only | Full credentials (with refresh_token) |
| Storage | Inline in config.yaml | External files (mounted) |
| Credentials in git | Yes (risky ⚠️) | No (safe ✅) |
| Token Expiry | 1 hour (manual refresh) | Indefinite (auto-refresh) |
| Compatibility | Standalone | CorreoDGGD-compatible |

## Logs

```bash
# Technical logs
tail -f logs/tecnico.log

# Audit logs (API changes, permissions)
tail -f logs/auditoria.log
```

## Security Checklist

- [ ] client_secret.json stored outside repo
- [ ] google_token.json stored outside repo
- [ ] config.yaml has paths to external files only
- [ ] Both external files have 600 permissions
- [ ] No credentials in git history
- [ ] `.gitignore` includes `config.yaml`, `*.json`

## GitHub Repository

- URL: https://github.com/cmoranp/Correo_DGGD_Respuestas
- Branch: main
- Architecture: CorreoDGGD-compatible

---

**Updated:** 2026-08-27  
**Architecture:** File-based OAuth (CorreoDGGD-compatible)  
**Status:** Ready for production after token generation
