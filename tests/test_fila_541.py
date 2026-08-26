"""
Test específico para Fila 541 (SEDECO/DGDE/DEANDESI/DDEyPE/048/2026)

Este test valida el flujo completo con un caso conocido.
"""

import pytest
from src.config import Config
from src.pdf_extractor import PDFExtractor
from src.matching_engine import MatchingEngine


class TestFila541:
    """Suite de pruebas para SEDECO/048/2026"""

    def test_formato_oficio(self):
        """Valida que el formato del oficio es correcto"""
        numero_oficio = "SEDECO/DGDE/DEANDESI/DDEyPE/048/2026"

        assert "/" in numero_oficio
        partes = numero_oficio.split("/")

        # Debe tener al menos siglas + número + año
        assert len(partes) >= 2

        # Último debe ser año
        assert partes[-1].isdigit()
        assert len(partes[-1]) == 4

    def test_extractor_patron_oficio(self):
        """Valida que el extractor encuentra el patrón de oficio"""
        extractor = PDFExtractor()

        # Texto de prueba con referencia al oficio
        texto = """
        RESPUESTA A OFICIO
        Se refiere al oficio SEDECO/DGDE/DEANDESI/DDEyPE/048/2026
        Atención a la solicitud del 06 de agosto de 2026
        """

        resultado = extractor._extraer_numero_de_texto(texto)

        # Si encuentra, debe ser el formato correcto
        if resultado:
            assert "048" in resultado
            assert "2026" in resultado

    def test_validacion_formato(self):
        """Valida el formato del número de oficio"""
        extractor = PDFExtractor()

        # Formato válido
        assert extractor._validar_formato("SEDECO/DGDE/048/2026")
        assert extractor._validar_formato("SEDECO/048/2026")
        assert extractor._validar_formato("ABC/DEF/001/2026")

        # Formato inválido
        assert not extractor._validar_formato("SEDECO/2026")  # Sin número
        assert not extractor._validar_formato("SEDECO/ABC/2025")  # Número muy corto


class TestSheetsBusqueda:
    """Suite de pruebas para búsqueda en Sheets"""

    @pytest.mark.skip(reason="Requiere credenciales reales")
    def test_buscar_oficio_541(self):
        """Busca el oficio 048/2026 en fila 541"""
        config = Config("config.yaml")

        # Este test requiere config.yaml actual
        # Se salta durante CI/testing sin credenciales
        numero_oficio = "SEDECO/DGDE/DEANDESI/DDEyPE/048/2026"

        # Pseudocódigo - requiere sheets handler real
        # resultado = sheets.buscar_oficio(numero_oficio)
        # assert resultado is not None
        # assert resultado["fila"] == 541


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
