import logging
from pathlib import Path
from typing import Optional
from datetime import datetime


class AuditoriaLogger:
    """Logger especializado para auditoría de cambios en APIs"""

    def __init__(self, log_file: str):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("auditoria")
        self._setup_logger()

    def _setup_logger(self) -> None:
        handler = logging.FileHandler(self.log_file, encoding="utf-8")
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def registrar_operacion(self, operacion: str, detalles: str) -> None:
        self.logger.info(f"{operacion}: {detalles}")

    def registrar_escritura(
        self, tabla: str, fila: int, columna: str, valor: str, usuario: str = "sistema"
    ) -> None:
        self.registrar_operacion(
            "ESCRITURA",
            f"Tabla={tabla}, Fila={fila}, Columna={columna}, Valor={valor[:50]}..., Usuario={usuario}",
        )

    def registrar_lectura(
        self, tabla: str, consulta: str, resultados: int
    ) -> None:
        self.registrar_operacion(
            "LECTURA",
            f"Tabla={tabla}, Consulta={consulta[:50]}..., Resultados={resultados}",
        )

    def registrar_descarga(self, archivo: str, tamaño: int) -> None:
        self.registrar_operacion(
            "DESCARGA", f"Archivo={archivo}, Tamaño={tamaño} bytes"
        )

    def registrar_carga(self, archivo: str, drive_id: str) -> None:
        self.registrar_operacion(
            "CARGA", f"Archivo={archivo}, DriveID={drive_id}"
        )

    def registrar_extraccion(self, archivo: str, resultado: str) -> None:
        self.registrar_operacion(
            "EXTRACCION", f"Archivo={archivo}, Resultado={resultado}"
        )


def setup_logger(
    tecnico_log: str,
    auditoria_log: str,
    level: str = "INFO",
) -> tuple[logging.Logger, AuditoriaLogger]:
    """Configura loggers técnico y de auditoría"""

    log_dir = Path(tecnico_log).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    tecnico = logging.getLogger("tecnico")
    tecnico.setLevel(getattr(logging, level))

    handler = logging.FileHandler(tecnico_log, encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    tecnico.addHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    tecnico.addHandler(console_handler)

    auditoria = AuditoriaLogger(auditoria_log)

    return tecnico, auditoria
