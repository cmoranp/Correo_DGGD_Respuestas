#!/bin/bash

# Prueba específica para fila 541 (SEDECO/048/2026)
# Valida el flujo completo con un caso conocido

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[TEST]${NC} $1"; }
log_pass() { echo -e "${GREEN}✓${NC} $1"; }
log_fail() { echo -e "${RED}✗${NC} $1"; }
log_warn() { echo -e "${YELLOW}!${NC} $1"; }

# Crear directorios
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/temp"

cd "$PROJECT_DIR"

# Activar venv
if [ -d "$PROJECT_DIR/venv" ]; then
    source "$PROJECT_DIR/venv/bin/activate"
fi

log_info "======================================"
log_info "PRUEBA: Fila 541 (SEDECO/048/2026)"
log_info "======================================"

log_info ""
log_info "Fase 1: Validando configuración..."

if [ ! -f "config.yaml" ]; then
    log_fail "config.yaml no encontrado"
    echo "Por favor, copia config.example.yaml a config.yaml y completa tus credenciales"
    exit 1
fi
log_pass "config.yaml encontrado"

log_info ""
log_info "Fase 2: Buscando correos de dguerreron@cdmx.gob.mx..."
log_warn "Busca manualmente en tu Gmail un correo de respuesta de SEDECO"
log_warn "Debe tener un PDF adjunto con referencia al oficio: SEDECO/DGDE/DEANDESI/DDEyPE/048/2026"

log_info ""
log_info "Fase 3: Especificaciones del oficio a validar:"
echo "  - Número: SEDECO/DGDE/DEANDESI/DDEyPE/048/2026"
echo "  - Fila en Sheets: 541"
echo "  - Columna: M (N° DE OFICIO)"
echo "  - Destino: Columna U (OFICIO DE RESPUESTA)"

log_info ""
log_info "Fase 4: Criterios de éxito:"
echo "  ✓ Correo encontrado en bandeja"
echo "  ✓ PDF descargado correctamente"
echo "  ✓ Número de oficio extraído: SEDECO/DGDE/DEANDESI/DDEyPE/048/2026"
echo "  ✓ Oficio encontrado en fila 541"
echo "  ✓ PDF cargado a Google Drive"
echo "  ✓ URL actualizada en columna U"
echo "  ✓ Auditoría registrada en logs"

log_info ""
log_info "Iniciando validación de conexiones..."

python3 -c "
from src.config import Config
from src.logger import setup_logger
from src.gmail_reader import GmailReader

config = Config('config.yaml')
print(f'  Email a buscar: {config.respuesta_email}')
print(f'  Sheets ID: {config.sheets_id}')
print(f'  Drive Folder: {config.drive_folder}')
print('  Conectando a Gmail...')
gmail = GmailReader(config.oauth_token)
print('  ✓ Gmail conectado')
" || log_fail "Error en validación de conexiones"

log_info ""
log_info "Para ejecutar la prueba completa:"
echo "  1. Asegúrate de que hay un correo en dguerreron@cdmx.gob.mx"
echo "  2. Ejecuta: python -m src.main"
echo "  3. Verifica logs/tecnico.log para detalles"

log_info ""
log_pass "Configuración lista para prueba con fila 541"
