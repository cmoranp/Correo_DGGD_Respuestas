import logging
import hashlib
from pathlib import Path
from typing import Optional, Set
from datetime import datetime

from src.config import Config
from src.logger import setup_logger
from src.gmail_reader import GmailReader
from src.pdf_extractor import PDFExtractor
from src.sheets_handler import SheetsHandler
from src.drive_uploader import DriveUploader
from src.matching_engine import MatchingEngine


class CorreoDGGDResponstas:
    """Orquestador principal del sistema de respuestas"""

    def __init__(self, config_path: str = "config.yaml"):
        self.config = Config(config_path)
        self.config.ensure_directories()

        self.logger, self.auditoria = setup_logger(
            self.config.tecnico_log,
            self.config.auditoria_log,
            self.config.log_level
        )

        self.logger.info("Inicializando Correo_DGGD_Respuestas...")

        self.gmail = GmailReader(self.config.oauth_token)
        self.extractor = PDFExtractor(
            self.config.ocr_idioma,
            self.config.ocr_timeout
        )
        self.sheets = SheetsHandler(
            self.config.oauth_token,
            self.config.sheets_id
        )
        self.drive = DriveUploader(
            self.config.oauth_token,
            self.config.drive_folder
        )
        self.matcher = MatchingEngine(self.sheets, self.auditoria)

        self.logger.info("Inicialización completada")

    def procesar_respuestas(self, max_correos: Optional[int] = None) -> dict:
        """
        Procesa respuestas de correos nuevos.

        Args:
            max_correos: Máximo número de correos a procesar (default: del config)

        Returns:
            Dict con estadísticas del procesamiento
        """
        if max_correos is None:
            max_correos = self.config.max_correos

        stats = {
            "correos_encontrados": 0,
            "pdfs_procesados": 0,
            "oficios_extraidos": 0,
            "vinculos_exitosos": 0,
            "errores": 0,
        }

        self.logger.info(
            f"Iniciando búsqueda en {self.config.respuesta_email}..."
        )

        # Buscar correos
        correos = self.gmail.buscar_correos(
            self.config.respuesta_email,
            max_correos
        )

        stats["correos_encontrados"] = len(correos)

        if not correos:
            self.logger.info("No hay correos nuevos que procesar")
            return stats

        # Procesar cada correo
        procesados = set()

        for correo in correos:
            for adjunto in correo["adjuntos"]:
                # Deduplicación por hash
                hash_adjunto = self._calcular_hash_adjunto(
                    correo["id"], adjunto["id"]
                )

                if hash_adjunto in procesados:
                    self.logger.debug(
                        f"Adjunto duplicado ignorado: {adjunto['nombre']}"
                    )
                    continue

                procesados.add(hash_adjunto)

                # Descargar adjunto
                contenido_pdf = self.gmail.descargar_adjunto(
                    correo["id"],
                    adjunto["id"],
                    adjunto["nombre"]
                )

                if not contenido_pdf:
                    stats["errores"] += 1
                    continue

                stats["pdfs_procesados"] += 1

                # Extraer número de oficio
                numero_oficio = self.extractor.extraer_numero_oficio(
                    contenido_pdf
                )

                if not numero_oficio:
                    self.logger.warning(
                        f"No se pudo extraer número de oficio de: "
                        f"{adjunto['nombre']}"
                    )
                    stats["errores"] += 1
                    continue

                stats["oficios_extraidos"] += 1

                # Validar formato
                if not self.matcher.validar_oficio_formato(numero_oficio):
                    self.logger.warning(
                        f"Formato de oficio inválido: {numero_oficio}"
                    )
                    stats["errores"] += 1
                    continue

                # Subir a Drive
                nombre_archivo = f"{numero_oficio.replace('/', '_')}_respuesta.pdf"

                file_id = self.drive.subir_archivo(
                    nombre_archivo,
                    contenido_pdf
                )

                if not file_id:
                    stats["errores"] += 1
                    continue

                # Obtener URL
                url_drive = self.drive.obtener_url_compartible(file_id)

                if not url_drive:
                    stats["errores"] += 1
                    continue

                # Vinculación
                if self.matcher.procesar_respuesta(
                    numero_oficio,
                    url_drive,
                    nombre_archivo
                ):
                    stats["vinculos_exitosos"] += 1
                    self.gmail.marcar_como_leido(correo["id"])
                else:
                    stats["errores"] += 1

        # Registrar resumen
        self.logger.info(
            f"Procesamiento completado: {stats['correos_encontrados']} "
            f"correos, {stats['pdfs_procesados']} PDFs, "
            f"{stats['oficios_extraidos']} oficios, "
            f"{stats['vinculos_exitosos']} vínculos exitosos"
        )

        self.auditoria.registrar_operacion(
            "RESUMEN_SESION",
            f"Correos={stats['correos_encontrados']}, "
            f"PDFs={stats['pdfs_procesados']}, "
            f"Oficios={stats['oficios_extraidos']}, "
            f"Vínculos={stats['vinculos_exitosos']}, "
            f"Errores={stats['errores']}"
        )

        return stats

    def procesar_fila_especifica(self, numero_fila: int) -> bool:
        """
        Procesa una fila específica manualmente (para testing).

        Útil para validar una respuesta conocida.
        """
        self.logger.info(f"Procesando fila {numero_fila}...")

        fila_data = self.sheets.obtener_fila_completa(numero_fila)

        if not fila_data:
            self.logger.error(f"No se pudo obtener fila {numero_fila}")
            return False

        self.logger.info(f"Fila {numero_fila} obtenida correctamente")
        return True

    def _calcular_hash_adjunto(self, msg_id: str, att_id: str) -> str:
        """Calcula hash único para deduplicación"""
        datos = f"{msg_id}_{att_id}".encode()
        return hashlib.sha256(datos).hexdigest()

    def validar_configuracion(self) -> bool:
        """Valida que la configuración sea correcta"""
        try:
            # Probar conexiones
            self.logger.info("Validando Gmail...")
            correos = self.gmail.buscar_correos(
                self.config.respuesta_email,
                max_resultados=1
            )

            self.logger.info("Validando Google Sheets...")
            self.sheets.obtener_rango("A1:A2")

            self.logger.info("Validando Google Drive...")
            self.drive.buscar_archivo("test_validacion")

            self.logger.info("Configuración validada exitosamente")
            return True

        except Exception as e:
            self.logger.error(f"Error validando configuración: {e}")
            return False


def main():
    import sys

    try:
        app = CorreoDGGDResponstas()

        if len(sys.argv) > 1:
            if sys.argv[1] == "validar":
                app.validar_configuracion()
            elif sys.argv[1] == "fila" and len(sys.argv) > 2:
                app.procesar_fila_especifica(int(sys.argv[2]))
            else:
                app.procesar_respuestas()
        else:
            app.procesar_respuestas()

    except Exception as e:
        logging.error(f"Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
