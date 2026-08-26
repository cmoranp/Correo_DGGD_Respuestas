import logging
from typing import List, Dict, Optional, Tuple
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class SheetsHandler:
    """Manejador de lectura/escritura en Google Sheets"""

    def __init__(self, oauth_token: str, sheets_id: str):
        self.oauth_token = oauth_token
        self.sheets_id = sheets_id
        self.service = None
        self._authenticate()

    def _authenticate(self) -> None:
        try:
            credentials = Credentials(token=self.oauth_token)
            self.service = build("sheets", "v4", credentials=credentials)
            logger.info("Autenticación Google Sheets exitosa")
        except Exception as e:
            logger.error(f"Error autenticando Sheets: {e}")
            raise

    def buscar_oficio(self, numero_oficio: str) -> Optional[Dict[str, str]]:
        """
        Busca un oficio en la columna M (N° DE OFICIO).

        Returns:
            Dict con info de la fila o None si no encuentra
        """
        try:
            # Leer columna M completa
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheets_id,
                range="ENTRADAS 2026_DGGD!M:M"
            ).execute()

            valores = result.get("values", [])

            for idx, row in enumerate(valores, start=1):
                if row and row[0].strip() == numero_oficio.strip():
                    logger.info(
                        f"Oficio {numero_oficio} encontrado en fila {idx}"
                    )
                    return {
                        "fila": idx,
                        "numero_oficio": numero_oficio,
                    }

            logger.warning(f"Oficio {numero_oficio} no encontrado en Sheets")
            return None

        except Exception as e:
            logger.error(f"Error buscando oficio: {e}")
            return None

    def obtener_fila_completa(self, numero_fila: int) -> Optional[Dict[str, str]]:
        """Obtiene todos los datos de una fila específica"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheets_id,
                range=f"ENTRADAS 2026_DGGD!{numero_fila}:{numero_fila}"
            ).execute()

            valores = result.get("values", [])
            if valores:
                return {"fila": numero_fila, "datos": valores[0]}

            return None

        except Exception as e:
            logger.error(f"Error obteniendo fila {numero_fila}: {e}")
            return None

    def verificar_respuesta_existe(self, numero_fila: int) -> bool:
        """Verifica si columna U (OFICIO DE RESPUESTA) está vacía"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheets_id,
                range=f"ENTRADAS 2026_DGGD!U{numero_fila}"
            ).execute()

            valores = result.get("values", [])
            if not valores or not valores[0]:
                return False  # Columna vacía, respuesta no existe

            return True  # Columna tiene valor, respuesta ya existe

        except Exception as e:
            logger.error(f"Error verificando respuesta en fila {numero_fila}: {e}")
            return True  # Por seguridad, asumir que existe si hay error

    def actualizar_oficio_respuesta(
        self, numero_fila: int, url: str, oficio_nombre: str
    ) -> bool:
        """
        Actualiza columna U (OFICIO DE RESPUESTA) con URL y nombre.

        Args:
            numero_fila: Número de fila (1-indexed)
            url: URL de Google Drive del documento
            oficio_nombre: Nombre legible del oficio para referencia

        Returns:
            True si escritura fue exitosa
        """
        try:
            valor = f'{oficio_nombre}\n{url}'

            body = {
                "values": [[valor]]
            }

            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.sheets_id,
                range=f"ENTRADAS 2026_DGGD!U{numero_fila}",
                valueInputOption="RAW",
                body=body
            ).execute()

            logger.info(
                f"Actualizado: Fila {numero_fila}, Columna U, "
                f"Valor: {oficio_nombre} ({url[:30]}...)"
            )
            return True

        except Exception as e:
            logger.error(
                f"Error actualizando fila {numero_fila}: {e}"
            )
            return False

    def actualizar_timestamp(self, numero_fila: int, timestamp: str) -> bool:
        """Actualiza timestamp de actualización (si existe columna T o similar)"""
        try:
            body = {"values": [[timestamp]]}

            self.service.spreadsheets().values().update(
                spreadsheetId=self.sheets_id,
                range=f"ENTRADAS 2026_DGGD!T{numero_fila}",
                valueInputOption="RAW",
                body=body
            ).execute()

            return True

        except Exception as e:
            logger.debug(f"No se pudo actualizar timestamp: {e}")
            return False

    def obtener_rango(self, rango: str) -> List[List[str]]:
        """Obtiene valores de un rango específico"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheets_id,
                range=f"ENTRADAS 2026_DGGD!{rango}"
            ).execute()

            return result.get("values", [])

        except Exception as e:
            logger.error(f"Error obteniendo rango {rango}: {e}")
            return []
