import base64
import hashlib
from typing import List, Dict, Optional, Tuple
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
import logging

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailReader:
    """Lector de correos desde Gmail"""

    def __init__(self, oauth_token: str):
        self.oauth_token = oauth_token
        self.service = None
        self._authenticate()

    def _authenticate(self) -> None:
        try:
            credentials = Credentials(token=self.oauth_token)
            self.service = build("gmail", "v1", credentials=credentials)
            logger.info("Autenticación Gmail exitosa")
        except Exception as e:
            logger.error(f"Error autenticando Gmail: {e}")
            raise

    def buscar_correos(
        self, desde: str, max_resultados: int = 50
    ) -> List[Dict[str, str]]:
        """
        Busca correos de un email específico.

        Args:
            desde: Email de origen (ej: dguerreron@cdmx.gob.mx)
            max_resultados: Máximo número de correos a retornar

        Returns:
            Lista de diccionarios con info de correos
        """
        try:
            query = f'from:{desde} is:unread has:attachment'
            results = self.service.users().messages().list(
                userId="me", q=query, maxResults=max_resultados
            ).execute()

            mensajes = results.get("messages", [])
            correos = []

            for msg in mensajes:
                msg_data = self.service.users().messages().get(
                    userId="me", id=msg["id"], format="full"
                ).execute()

                headers = msg_data["payload"]["headers"]
                subject = next(
                    (h["value"] for h in headers if h["name"] == "Subject"), "Sin asunto"
                )
                from_addr = next(
                    (h["value"] for h in headers if h["name"] == "From"), ""
                )
                date = next(
                    (h["value"] for h in headers if h["name"] == "Date"), ""
                )

                attachments = self._extraer_adjuntos(msg_data)

                correos.append({
                    "id": msg["id"],
                    "asunto": subject,
                    "de": from_addr,
                    "fecha": date,
                    "adjuntos": attachments,
                })

            logger.info(f"Encontrados {len(correos)} correos de {desde}")
            return correos

        except Exception as e:
            logger.error(f"Error buscando correos: {e}")
            return []

    def _extraer_adjuntos(self, msg_data: Dict) -> List[Dict[str, str]]:
        """Extrae información de adjuntos del mensaje"""
        adjuntos = []

        if "parts" not in msg_data["payload"]:
            return adjuntos

        for part in msg_data["payload"]["parts"]:
            if part["filename"]:
                if part["filename"].lower().endswith(".pdf"):
                    adjuntos.append({
                        "nombre": part["filename"],
                        "id": part["body"].get("attachmentId", ""),
                        "mimetype": part["mimeType"],
                    })

        return adjuntos

    def descargar_adjunto(
        self, mensaje_id: str, attachment_id: str, nombre_archivo: str
    ) -> Optional[bytes]:
        """Descarga un adjunto y retorna su contenido"""
        try:
            adjunto = self.service.users().messages().attachments().get(
                userId="me", messageId=mensaje_id, id=attachment_id
            ).execute()

            data = adjunto["data"]
            file_data = base64.urlsafe_b64decode(data)

            logger.info(f"Descargado: {nombre_archivo} ({len(file_data)} bytes)")
            return file_data

        except Exception as e:
            logger.error(f"Error descargando adjunto: {e}")
            return None

    def marcar_como_leido(self, mensaje_id: str) -> bool:
        """Marca un mensaje como leído"""
        try:
            self.service.users().messages().modify(
                userId="me", id=mensaje_id, body={"removeLabelIds": ["UNREAD"]}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error marcando como leído: {e}")
            return False
