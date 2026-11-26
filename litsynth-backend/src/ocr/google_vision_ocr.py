import os
import io
import asyncio
from concurrent.futures import ThreadPoolExecutor
from .ocr import OcrPDF
from google.cloud import vision
from google.oauth2 import service_account
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import json

from dotenv import load_dotenv
load_dotenv()

DEBUG = os.getenv('DEBUG', 'false').lower() in ['true', '1', 'yes']

# Thread pool for concurrent API calls
_ocr_executor = ThreadPoolExecutor(max_workers=5)

# Google Vision credentials
GOOGLE_VISION_CREDENTIALS_JSON = os.getenv('GOOGLE_VISION_CREDENTIALS_JSON')
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')


class GoogleVisionOCR(OcrPDF):
    provider_name = "GOOGLE_VISION"

    def __init__(self, file_path):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)

        # Initialize Google Vision client
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize Google Vision client with credentials"""
        try:
            # Option 1: Use credentials from JSON string in env variable
            if GOOGLE_VISION_CREDENTIALS_JSON:
                credentials_dict = json.loads(GOOGLE_VISION_CREDENTIALS_JSON)
                credentials = service_account.Credentials.from_service_account_info(credentials_dict)
                self.client = vision.ImageAnnotatorClient(credentials=credentials)
                if DEBUG:
                    print("[GOOGLE VISION OCR] Initialized with JSON credentials from env variable")

            # Option 2: Use credentials file path
            elif GOOGLE_APPLICATION_CREDENTIALS:
                self.client = vision.ImageAnnotatorClient()
                if DEBUG:
                    print(f"[GOOGLE VISION OCR] Initialized with credentials file: {GOOGLE_APPLICATION_CREDENTIALS}")

            # Option 3: Use default credentials (gcloud auth)
            else:
                self.client = vision.ImageAnnotatorClient()
                if DEBUG:
                    print("[GOOGLE VISION OCR] Initialized with default credentials")

        except Exception as e:
            if DEBUG:
                print(f"[GOOGLE VISION OCR] Failed to initialize client: {e}")
            self.client = None

    def _extract_text_from_page(self, image_bytes) -> str:
        """Extract text from a single page using Google Vision API"""
        if not self.client:
            raise Exception("[GOOGLE VISION OCR] Client not initialized. Check credentials.")

        try:
            image = vision.Image(content=image_bytes)

            # Perform text detection
            response = self.client.text_detection(image=image)

            if response.error.message:
                raise Exception(f"Google Vision API error: {response.error.message}")

            # Get full text annotation
            texts = response.text_annotations

            if texts:
                # First annotation contains the full detected text
                full_text = texts[0].description
                return full_text
            else:
                return ""

        except Exception as e:
            if DEBUG:
                print(f"[GOOGLE VISION OCR] Error extracting text from page: {e}")
            return ""

    def _extract_text_from_page_sync(self, args) -> tuple[int, str]:
        """Sync wrapper for parallel processing - returns (page_index, text)"""
        page_index, image_bytes = args
        text = self._extract_text_from_page(image_bytes)
        if DEBUG:
            print(f"[GOOGLE VISION OCR] Page {page_index + 1}: Extracted {len(text)} characters")
        return (page_index, text)

    def _pdf_to_images(self):
        """Convert PDF pages to images with rotation normalization"""
        try:
            # Use PyMuPDF (fitz) for better image extraction
            import fitz

            doc = fitz.open(self.file_path)
            images = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                rotation = page.rotation  # NEW: Detect rotation

                # Apply derotation matrix to ensure normalized rendering (MODIFIED)
                if rotation != 0:
                    if DEBUG:
                        print(f"[GOOGLE VISION OCR] Page {page_num + 1} has {rotation}° rotation - normalizing")
                    pix = page.get_pixmap(dpi=300, matrix=page.derotation_matrix)
                else:
                    pix = page.get_pixmap(dpi=300)

                img_bytes = pix.tobytes("png")
                images.append(img_bytes)

                if DEBUG:
                    print(f"[GOOGLE VISION OCR] Converted page {page_num + 1}/{len(doc)} to image (normalized orientation)")

            doc.close()
            return images

        except ImportError:
            # Fallback with rotation normalization (MODIFIED)
            if DEBUG:
                print("[GOOGLE VISION OCR] PyMuPDF not available, using pdf2image with rotation handling")

            from pdf2image import convert_from_path
            from PIL import Image
            import fitz

            # Get rotation metadata from original PDF
            doc = fitz.open(self.file_path)
            rotations = [page.rotation for page in doc]
            doc.close()

            # Convert to images
            pil_images = convert_from_path(self.file_path, dpi=300)
            images = []

            for i, (pil_img, rotation) in enumerate(zip(pil_images, rotations)):
                # Normalize rotation using PIL if needed (NEW)
                if rotation != 0:
                    if rotation == 90:
                        pil_img = pil_img.transpose(Image.ROTATE_270)
                    elif rotation == 180:
                        pil_img = pil_img.transpose(Image.ROTATE_180)
                    elif rotation == 270:
                        pil_img = pil_img.transpose(Image.ROTATE_90)

                    if DEBUG:
                        print(f"[GOOGLE VISION OCR] Normalized page {i + 1} rotation ({rotation}° → 0°)")

                img_byte_arr = io.BytesIO()
                pil_img.save(img_byte_arr, format='PNG')
                images.append(img_byte_arr.getvalue())

            return images

    def _create_searchable_pdf(self, extracted_texts):
        """Create searchable PDF with rotation-aware text positioning"""
        try:
            # Read original PDF and get rotation info
            import fitz
            reader = PdfReader(self.file_path)
            writer = PdfWriter()

            # Get rotation info from original PDF (NEW)
            doc = fitz.open(self.file_path)

            for page_num, text in enumerate(extracted_texts):
                original_page = reader.pages[page_num]
                rotation = doc[page_num].rotation  # NEW: Get rotation

                # Create text overlay with rotation awareness (MODIFIED)
                packet = io.BytesIO()

                # Adjust canvas size based on rotation (NEW)
                page_width = float(original_page.mediabox.width)
                page_height = float(original_page.mediabox.height)

                if rotation in [90, 270]:
                    # Swap width/height for 90° and 270° rotations
                    pagesize = (page_height, page_width)
                else:
                    pagesize = (page_width, page_height)

                can = canvas.Canvas(packet, pagesize=pagesize)

                # Invisible text layer
                can.setFillColorRGB(1, 1, 1, alpha=0.0)  # Transparent white
                can.setFont("Helvetica", 10)

                # Adjust text positioning based on rotation (NEW)
                if rotation == 0:
                    text_object = can.beginText(10, pagesize[1] - 50)
                elif rotation == 90:
                    can.rotate(90)
                    text_object = can.beginText(10, -pagesize[0] + 50)
                elif rotation == 180:
                    can.rotate(180)
                    text_object = can.beginText(-pagesize[0] + 10, -50)
                elif rotation == 270:
                    can.rotate(270)
                    text_object = can.beginText(-pagesize[1] + 10, pagesize[0] - 50)
                else:
                    # Default to 0° if unexpected rotation
                    text_object = can.beginText(10, pagesize[1] - 50)

                # Add OCR text
                for line in text.split('\n'):
                    text_object.textLine(line)

                can.drawText(text_object)
                can.save()

                # Move to the beginning of the BytesIO buffer
                packet.seek(0)

                # Merge with original page
                overlay_page = PdfReader(packet).pages[0]
                original_page.merge_page(overlay_page)
                writer.add_page(original_page)

            doc.close()

            # Write to output file
            with open(self.output_file_path, 'wb') as output_file:
                writer.write(output_file)

            if DEBUG:
                print(f"[GOOGLE VISION OCR] Created searchable PDF with rotation-aware text overlay: {self.output_file_path}")

            return True

        except Exception as e:
            if DEBUG:
                print(f"[GOOGLE VISION OCR] Error creating searchable PDF: {e}")
            return False

    def load(self) -> str:
        """
        Main OCR processing method
        Returns path to OCR'd PDF file, or empty string on failure
        """
        try:
            if not self.client:
                raise Exception("[GOOGLE VISION OCR] Client not initialized. Check Google Vision credentials.")

            if DEBUG:
                print(f"[GOOGLE VISION OCR] Starting OCR for: {self.file_name}")

            # Step 1: Convert PDF pages to images
            if DEBUG:
                print("[GOOGLE VISION OCR] Converting PDF to images...")
            images = self._pdf_to_images()

            if not images:
                raise Exception("[GOOGLE VISION OCR] Failed to convert PDF to images")

            # Step 2: Extract text from each page (PARALLEL for speed)
            if DEBUG:
                print(f"[GOOGLE VISION OCR] Extracting text from {len(images)} pages in parallel...")

            # Process all pages concurrently using thread pool
            page_args = [(i, img) for i, img in enumerate(images)]
            results = list(_ocr_executor.map(self._extract_text_from_page_sync, page_args))

            # Sort by page index and extract texts
            results.sort(key=lambda x: x[0])
            extracted_texts = [text for _, text in results]

            if DEBUG:
                total_chars = sum(len(t) for t in extracted_texts)
                print(f"[GOOGLE VISION OCR] Extracted {total_chars} total characters from {len(images)} pages")

            # Step 3: Create searchable PDF with extracted text
            if DEBUG:
                print("[GOOGLE VISION OCR] Creating searchable PDF...")

            success = self._create_searchable_pdf(extracted_texts)

            if success:
                if DEBUG:
                    print(f"[GOOGLE VISION OCR] Successfully completed OCR for {self.file_name}")
                return self.output_file_path
            else:
                return ""

        except Exception as e:
            if DEBUG:
                print(f"[ERROR] Google Vision OCR: Failed: {e}")
            return ""
