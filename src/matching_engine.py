import logging
from typing import Optional, Dict, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class MatchingEngine:
    """Motor de búsqueda y vinculación de oficios con respuestas"""

    def __init__(self, sheets_handler, auditoria_logger):
        self.sheets = sheets_handler
        self.auditoria = auditoria_logger

    def procesar_respuesta(
        self,
        numero_oficio: str,
        url_drive: str,
        archivo_nombre: str,
    ) -> bool:
        """
        Procesa una respuesta encontrada y la vincula al registro.

        Args:
            numero_oficio: Número de oficio extraído del PDF
            url_drive: URL del documento en Google Drive
            archivo_nombre: Nombre del archivo para auditoría

        Returns:
            True si vinculación fue exitosa
        """

        # Paso 1: Buscar oficio en Sheets
        resultado_busqueda = self.sheets.buscar_oficio(numero_oficio)

        if not resultado_busqueda:
            logger.warning(
                f"Oficio {numero_oficio} no encontrado en Sheets"
            )
            self.auditoria.registrar_operacion(
                "NO_ENCONTRADO",
                f"Oficio {numero_oficio} no existe en Sheets"
            )
            return False

        numero_fila = resultado_busqueda["fila"]

        # Paso 2: Verificar que no tiene respuesta anterior
        if self.sheets.verificar_respuesta_existe(numero_fila):
            logger.warning(
                f"Oficio {numero_oficio} (fila {numero_fila}) ya tiene respuesta"
            )
            self.auditoria.registrar_operacion(
                "YA_ATENDIDO",
                f"Oficio {numero_oficio} en fila {numero_fila} ya tiene respuesta"
            )
            return False

        # Paso 3: Actualizar columna U con URL
        oficio_legible = self._formatear_nombre_oficio(numero_oficio)

        if not self.sheets.actualizar_oficio_respuesta(
            numero_fila, url_drive, oficio_legible
        ):
            logger.error(
                f"Error actualizando fila {numero_fila}"
            )
            return False

        # Paso 4: Registrar timestamp
        timestamp = datetime.now().isoformat()
        self.sheets.actualizar_timestamp(numero_fila, timestamp)

        # Paso 5: Auditoría
        self.auditoria.registrar_escritura(
            tabla="ENTRADAS 2026_DGGD",
            fila=numero_fila,
            columna="U",
            valor=url_drive,
            usuario="sistema_respuestas"
        )

        logger.info(
            f"Vinculación exitosa: Fila {numero_fila}, "
            f"Oficio {numero_oficio}, URL {url_drive}"
        )

        return True

    def _formatear_nombre_oficio(self, numero_oficio: str) -> str:
        """Convierte número de oficio a formato legible"""
        # SEDECO/DGDE/DEANDESI/DDEyPE/048/2026 → SEDECO_DGDE_DEANDESI_DDEyPE_048_2026
        return numero_oficio.replace("/", "_")

    def validar_oficio_formato(self, numero_oficio: str) -> bool:
        """Valida que número de oficio tenga formato correcto"""
        partes = numero_oficio.split("/")

        # Debe tener al menos 2 partes
        if len(partes) < 2:
            return False

        # Última parte debe ser año (4 dígitos)
        if not partes[-1].isdigit() or len(partes[-1]) != 4:
            return False

        return True
