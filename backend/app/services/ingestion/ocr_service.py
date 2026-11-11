"""
OCR service using PyTesseract with fallback handling and configuration.
"""
import os
import shutil
import logging
from typing import Optional
from PIL import Image
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class OCRService:
    """
    Manages OCR availability and execution with PyTesseract.
    """

    def __init__(self, tesseract_cmd: Optional[str] = None):
        self._cmd = tesseract_cmd or settings.TESSERACT_CMD
        self._available: Optional[bool] = None
        self._setup()

    def _setup(self):
        try:
            import pytesseract
            # Common Windows installation locations
            candidates = [
                self._cmd,
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                os.environ.get("TESSERACT_PATH"),
            ]
            found_cmd = None
            for cand in candidates:
                if cand and os.path.exists(cand):
                    found_cmd = cand
                    break

            if found_cmd:
                pytesseract.pytesseract.tesseract_cmd = found_cmd
                self._available = True
                logger.info(f"Tesseract OCR found at: {found_cmd}")
            elif shutil.which("tesseract"):
                self._available = True
                logger.info("Tesseract OCR found in system PATH")
            else:
                self._available = False
                logger.warning("Tesseract OCR binary not found. OCR fallbacks will be unavailable.")
        except ImportError:
            self._available = False
            logger.warning("pytesseract package not installed. OCR unavailable.")

    def is_available(self) -> bool:
        return bool(self._available)

    def extract_text_from_image(self, image: Image.Image) -> str:
        """
        Extract text from a PIL Image using OCR.
        Returns extracted text, or raises RuntimeError if OCR is not available.
        """
        if not self.is_available():
            raise RuntimeError("OCR is requested but Tesseract OCR engine is not installed or available on this system.")

        import pytesseract
        try:
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            raise RuntimeError(f"OCR execution failed: {str(e)}")


ocr_service = OCRService()

