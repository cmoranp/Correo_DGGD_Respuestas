import logging
from typing import Optional
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from google.oauth2.credentials import Credentials
import io

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive"]


class DriveUploader:
    """Uploader de archivos a Google Drive"""

    def __init__(self, oauth_token: str, carpeta_destino: str):
        self.oauth_token = oauth_token
        self.carpeta_destino = carpeta_destino
        self.service = None
        self._authenticate()

    def _authenticate(self) -> None:
        try:
            credentials = Credentials(token=self.oauth_token)
            self.service = build("drive", "v3", credentials=credentials)
            logger.info("Autenticación Google Drive exitosa")
        except Exception as e:
            logger.error(f"Error autenticando Drive: {e}")
            raise

    def subir_archivo(
        self, nombre_archivo: str, contenido: bytes
    ) -> Optional[str]:
        """
        Sube un archivo PDF a la carpeta de Drive.

        Args:
            nombre_archivo: Nombre del archivo (ej: SEDECO_048_2026_respuesta.pdf)
            contenido: Contenido del archivo en bytes

        Returns:
            ID del archivo en Drive o None si falla
        """
        try:
            file_metadata = {
                "name": nombre_archivo,
                "parents": [self.carpeta_destino],
                "mimeType": "application/pdf",
            }

            media = MediaIoBaseUpload(
                io.BytesIO(contenido),
                mimetype="application/pdf",
                resumable=True
            )

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id, webViewLink, parents"
            ).execute()

            file_id = file.get("id")
            logger.info(f"Archivo subido a Drive: {nombre_archivo} (ID: {file_id})")

            return file_id

        except Exception as e:
            logger.error(f"Error subiendo archivo a Drive: {e}")
            return None

    def obtener_url_compartible(self, file_id: str) -> Optional[str]:
        """Genera URL compartible para un archivo"""
        try:
            # Hacer archivo compartible
            self.service.permissions().create(
                fileId=file_id,
                body={"role": "reader", "type": "anyone"},
                fields="id"
            ).execute()

            # Obtener URL
            file = self.service.files().get(
                fileId=file_id,
                fields="webViewLink"
            ).execute()

            url = file.get("webViewLink")
            logger.info(f"URL compartible obtenida: {url}")
            return url

        except Exception as e:
            logger.error(f"Error obteniendo URL: {e}")
            return None

    def obtener_metadatos(self, file_id: str) -> Optional[dict]:
        """Obtiene metadatos de un archivo"""
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields="id, name, webViewLink, size, createdTime"
            ).execute()

            return file

        except Exception as e:
            logger.error(f"Error obteniendo metadatos: {e}")
            return None

    def buscar_archivo(self, nombre: str) -> Optional[str]:
        """Busca un archivo por nombre y retorna su ID"""
        try:
            query = (
                f"name='{nombre}' "
                f"and parents='{self.carpeta_destino}' "
                f"and trashed=false"
            )

            results = self.service.files().list(
                q=query,
                spaces="drive",
                fields="files(id, name)",
                pageSize=1
            ).execute()

            files = results.get("files", [])
            if files:
                return files[0]["id"]

            return None

        except Exception as e:
            logger.error(f"Error buscando archivo: {e}")
            return None

    def crear_carpeta(self, nombre_carpeta: str) -> Optional[str]:
        """Crea una subcarpeta dentro de la carpeta destino"""
        try:
            file_metadata = {
                "name": nombre_carpeta,
                "parents": [self.carpeta_destino],
                "mimeType": "application/vnd.google-apps.folder",
            }

            folder = self.service.files().create(
                body=file_metadata,
                fields="id"
            ).execute()

            folder_id = folder.get("id")
            logger.info(f"Carpeta creada: {nombre_carpeta} (ID: {folder_id})")

            return folder_id

        except Exception as e:
            logger.error(f"Error creando carpeta: {e}")
            return None
