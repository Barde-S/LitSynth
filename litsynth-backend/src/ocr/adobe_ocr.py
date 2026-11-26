import os
from .ocr import OcrPDF

from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.config.client_config import ClientConfig
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.ocr_pdf_job import OCRPDFJob
from adobe.pdfservices.operation.pdfjobs.result.ocr_pdf_result import OCRPDFResult

from dotenv import load_dotenv
load_dotenv()

DEBUG = os.getenv('DEBUG', 'false').lower() in ['true', '1', 'yes']

ADOBE_OCR_CLIENT_ID = os.getenv('ADOBE_OCR_CLIENT_ID')
ADOBE_OCR_CLIENT_SECRET = os.getenv('ADOBE_OCR_CLIENT_SECRET')

class AdobeOcrPDF(OcrPDF):
    provider_name = "ADOBE"

    def __init__(self, file_path):
        self.file_path = file_path
    
    def load(self) -> str:
        try:
            file = open(self.file_path, 'rb')
            input_stream = file.read()
            file.close()

            # Initial setup, create credentials instance
            credentials = ServicePrincipalCredentials(
                client_id=ADOBE_OCR_CLIENT_ID,
                client_secret=ADOBE_OCR_CLIENT_SECRET
            )
            client_config = ClientConfig(connect_timeout=120000, read_timeout=120000)

            # Creates a PDF Services instance
            pdf_services = PDFServices(credentials=credentials, client_config=client_config)

            # Creates an asset(s) from source file(s) and upload
            input_asset = pdf_services.upload(input_stream=input_stream,
                                              mime_type=PDFServicesMediaType.PDF)

            # Creates a new job instance
            ocr_pdf_job = OCRPDFJob(input_asset=input_asset)

            # Submit the job and gets the job result
            location = pdf_services.submit(ocr_pdf_job)
            pdf_services_response = pdf_services.get_job_result(location, OCRPDFResult)

            # Get content from the resulting asset(s)
            result_asset: CloudAsset = pdf_services_response.get_result().get_asset()
            stream_asset: StreamAsset = pdf_services.get_content(result_asset)

            # Output stream asset's content
            with open(self.output_file_path, "wb") as file:
                file.write(stream_asset.get_input_stream())
            
            return self.output_file_path

        except Exception as e:
            if DEBUG:
                print(f"[ERROR] Adobe OCR: {e}")

            return ""
