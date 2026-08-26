import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Cargador centralizado de configuración desde config.yaml"""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.data: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"config.yaml no encontrado. Copia config.example.yaml a config.yaml"
            )

        with open(self.config_path, "r", encoding="utf-8") as f:
            self.data = yaml.safe_load(f) or {}

        self._validate_config()

    def _validate_config(self) -> None:
        required_keys = [
            "google.oauth_token",
            "google.sheets_id",
            "google.drive_folder",
            "gmail.respuesta_email",
        ]

        for key in required_keys:
            if not self._get_nested(key):
                raise ValueError(f"Configuración requerida no encontrada: {key}")

    def _get_nested(self, key: str, default: Optional[Any] = None) -> Any:
        keys = key.split(".")
        value = self.data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self._get_nested(key, default)

    @property
    def oauth_token(self) -> str:
        return self.get("google.oauth_token")

    @property
    def sheets_id(self) -> str:
        return self.get("google.sheets_id")

    @property
    def drive_folder(self) -> str:
        return self.get("google.drive_folder")

    @property
    def respuesta_email(self) -> str:
        return self.get("gmail.respuesta_email")

    @property
    def auditoria_log(self) -> str:
        return self.get("logging.auditoria", "logs/auditoria.log")

    @property
    def tecnico_log(self) -> str:
        return self.get("logging.tecnico", "logs/tecnico.log")

    @property
    def log_level(self) -> str:
        return self.get("logging.nivel", "INFO")

    @property
    def ocr_idioma(self) -> str:
        return self.get("ocr.idioma", "spa")

    @property
    def ocr_timeout(self) -> int:
        return self.get("ocr.timeout", 30)

    @property
    def ocr_confianza_minima(self) -> int:
        return self.get("ocr.confianza_minima", 70)

    @property
    def max_correos(self) -> int:
        return self.get("procesamiento.max_correos", 50)

    @property
    def temp_dir(self) -> str:
        return self.get("rutas.temp_downloads", "temp/")

    def ensure_directories(self) -> None:
        for dir_path in [self.temp_dir, Path(self.auditoria_log).parent]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
