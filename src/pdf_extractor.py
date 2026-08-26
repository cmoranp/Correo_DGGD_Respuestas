import re
import tempfile
import logging
from pathlib import Path
from typing import Optional, Tuple, List
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io

try:
    import poppler
except ImportError:
    poppler = None

logger = logging.getLogger(__name__)

# Patrón para número de oficio: SIGLAS/AREA/NUMERO/AAAA o variantes
OFICIO_PATTERN = r'([A-Z]+(?:/[A-Z0-9]+)*)/([0-9]{4})'


class PDFExtractor:
    """Extractor de número de oficio desde PDFs"""

    def __init__(self, idioma: str = "spa", timeout: int = 30):
        self.idioma = idioma
        self.timeout = timeout

    def extraer_numero_oficio(self, pdf_bytes: bytes) -> Optional[str]:
        """
        Extrae número de oficio de un PDF.

        Intenta primero lectura de texto digital (poppler),
        luego OCR (Tesseract) si es escaneado.

        Returns:
            Número de oficio en formato SIGLAS/AREA/NUMERO/AAAA o None
        """

        # Intenta lectura digital
        texto = self._leer_texto_digital(pdf_bytes)

        if not texto:
            # Fallback a OCR si es escaneado
            texto = self._leer_ocr(pdf_bytes)

        if texto:
            numero = self._extraer_numero_de_texto(texto)
            if numero:
                logger.info(f"Oficio extraído: {numero}")
                return numero

        logger.warning("No se pudo extraer número de oficio")
        return None

    def _leer_texto_digital(self, pdf_bytes: bytes) -> Optional[str]:
        """Lee texto directamente de un PDF digital"""
        try:
            # Usar pdfplumber si está disponible
            import pdfplumber

            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                texto = ""
                for page in pdf.pages[:3]:  # Revisar primeras 3 páginas
                    texto += page.extract_text() or ""

            return texto if texto.strip() else None

        except ImportError:
            logger.debug("pdfplumber no disponible, usando OCR")
            return None
        except Exception as e:
            logger.debug(f"Error en lectura digital: {e}")
            return None

    def _leer_ocr(self, pdf_bytes: bytes) -> Optional[str]:
        """Lee texto mediante OCR de imágenes del PDF"""
        try:
            images = convert_from_bytes(pdf_bytes)
            texto = ""

            for i, image in enumerate(images[:3]):  # Primeras 3 páginas
                logger.debug(f"Procesando página {i+1} con OCR...")
                page_text = pytesseract.image_to_string(
                    image, lang=self.idioma, timeout=self.timeout
                )
                texto += page_text + "\n"

            return texto if texto.strip() else None

        except Exception as e:
            logger.error(f"Error en OCR: {e}")
            return None

    def _extraer_numero_de_texto(self, texto: str) -> Optional[str]:
        """Extrae número de oficio del texto usando regex y patrones"""

        # Normalizar texto
        texto = texto.upper()
        lineas = texto.split('\n')

        # Buscar número de oficio con varios patrones
        patrones = [
            r'(?:REFIERE\s+AL\s+)?OFICIO\s+([A-Z]+(?:/[A-Z0-9]+)*)/(\d{4})',
            r'ATENCIÓN\s+AL\s+OFICIO\s+([A-Z]+(?:/[A-Z0-9]+)*)/(\d{4})',
            r'RESPUESTA\s+A\s+([A-Z]+(?:/[A-Z0-9]+)*)/(\d{4})',
            r'([A-Z]{4,}(?:/[A-Z0-9]{2,})+)/(\d{4})',
        ]

        for linea in lineas:
            for patron in patrones:
                match = re.search(patron, linea)
                if match:
                    oficio = f"{match.group(1)}/{match.group(2)}"
                    if self._validar_formato(oficio):
                        return oficio

        # Búsqueda más general sin contexto
        match = re.search(OFICIO_PATTERN, texto)
        if match:
            oficio = f"{match.group(1)}/{match.group(2)}"
            if self._validar_formato(oficio):
                return oficio

        return None

    def _validar_formato(self, numero: str) -> bool:
        """Valida que el formato de número de oficio sea correcto"""

        # Formato esperado: SIGLAS/AREA/NUMERO/AAAA
        # Ejemplo: SEDECO/DGDE/DEANDESI/DDEyPE/048/2026

        partes = numero.split('/')
        if len(partes) < 2:
            return False

        # Última parte debe ser año (4 dígitos)
        if not partes[-1].isdigit() or len(partes[-1]) != 4:
            return False

        # Penúltima o anterior debe ser número de oficio (2-4 dígitos)
        for parte in partes[:-1]:
            if parte.isdigit() and 1 <= len(parte) <= 4:
                return True

        return False

    def guardar_pdf_temp(self, pdf_bytes: bytes) -> Optional[str]:
        """Guarda PDF en archivo temporal y retorna la ruta"""
        try:
            with tempfile.NamedTemporaryFile(
                suffix=".pdf", delete=False
            ) as tmp_file:
                tmp_file.write(pdf_bytes)
                logger.debug(f"PDF guardado en: {tmp_file.name}")
                return tmp_file.name
        except Exception as e:
            logger.error(f"Error guardando PDF temporal: {e}")
            return None
