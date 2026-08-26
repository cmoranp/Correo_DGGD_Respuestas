#!/bin/bash

# Correo_DGGD_Respuestas - Punto de entrada para procesamiento de respuestas
# Uso: ./procesar_respuestas.sh [opciones]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funciones
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Validar que estamos en el directorio correcto
if [ ! -f "$PROJECT_DIR/config.example.yaml" ]; then
    log_error "No se encontró config.example.yaml"
    exit 1
fi

# Validar que config.yaml existe
if [ ! -f "$PROJECT_DIR/config.yaml" ]; then
    log_error "config.yaml no encontrado. Copia config.example.yaml a config.yaml"
    exit 1
fi

# Crear directorios necesarios
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/temp"

log_info "Correo_DGGD_Respuestas - Procesador de Respuestas"
log_info "=================================================="

# Activar venv si existe
if [ -d "$PROJECT_DIR/venv" ]; then
    log_info "Activando entorno virtual..."
    source "$PROJECT_DIR/venv/bin/activate"
fi

# Ir al directorio del proyecto
cd "$PROJECT_DIR"

# Ejecutar procesamiento
log_info "Iniciando procesamiento..."
python -m src.main

log_info "Procesamiento completado"
log_info "Revisa los logs en: logs/tecnico.log y logs/auditoria.log"
