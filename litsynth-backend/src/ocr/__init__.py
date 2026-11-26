# OCR providers - import conditionally
try:
    from .adobe_ocr import AdobeOcrPDF
except ImportError:
    AdobeOcrPDF = None

# ILOVEMYPDF (OLD - Commented out for Google Vision migration)
# try:
#     from .ilovemypdf import ILoveMyPDF
# except ImportError:
#     ILoveMyPDF = None

# GOOGLE VISION OCR (NEW - Active)
try:
    from .google_vision_ocr import GoogleVisionOCR
except ImportError:
    GoogleVisionOCR = None

# For backward compatibility during migration
ILoveMyPDF = None  # Disabled - use GoogleVisionOCR instead

__all__ = ["AdobeOcrPDF", "GoogleVisionOCR", "ILoveMyPDF"]
