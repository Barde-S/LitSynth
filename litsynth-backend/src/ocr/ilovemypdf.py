import os
from time import sleep
import requests
from .ocr import OcrPDF

from dotenv import load_dotenv
load_dotenv()

DEBUG = os.getenv('DEBUG', 'false').lower() in ['true', '1', 'yes']
PARANOID_DEBUG = False


ILOVEMYPDF_OCR_PUB_KEY = os.getenv('ILOVEMYPDF_OCR_PUB_KEY')
ILOVEMYPDF_OCR_SECRET = os.getenv('ILOVEMYPDF_OCR_SECRET')


class ILoveMyPDF(OcrPDF):
    provider_name = "I_LOVE_MYPDF"

    def __init__(self, file_path):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.max_retries = 3
        self.retry_delay = 1

        # auth stuff
        self.public_key = ILOVEMYPDF_OCR_PUB_KEY
        self.secret_key = ILOVEMYPDF_OCR_SECRET
        self.headers = {}
        self.token = ''

        # intial server to start task (to get working server)
        self.base_url = "https://api.ilovepdf.com/v1"
        self.working_server = ''
        self.task = ''
        
        # file details
        self.server_filename = ''

        
    
    def _get(self, url: str, headers=None, params=None, **kwargs):
        for attempt in range(self.max_retries):
            try:
                # auto auth if possible
                if not headers and self.headers:
                    headers = self.headers

                # let caller build url
                response = requests.get(url, headers=headers, params=params, **kwargs)
                response.raise_for_status()
                
                # let caller handle response type (file/ json)
                return response
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"[ERROR: failed GET] ILoveMyPDF OCR: {e}")
                sleep(self.retry_delay)
                
        return None

    def _post(self, url: str, headers=None, payload=None, files=None, **kwargs):
        for attempt in range(self.max_retries):
            try:
                # auto auth if possible
                if not headers and self.headers:
                    headers = self.headers

                # let caller build url
                response = requests.post(url, headers=headers, json=payload, files=files, **kwargs)
                response.raise_for_status()
                
                # let caller handle response type (file/ json)
                return response
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"[ERROR: failed POST] ILoveMyPDF OCR: {e}")
                sleep(self.retry_delay)
                
        return None

    def _delete(self, url: str, headers=None, params=None):
        for attempt in range(self.max_retries):
            try:
                # auto auth if possible
                if not headers and self.headers:
                    headers = self.headers

                # let caller build url
                response = requests.delete(url, headers=headers, params=params)
                response.raise_for_status()
                
                # let caller handle response type (file/ json)
                return response
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"[ERROR: failed DELETE] ILoveMyPDF OCR: {e}")
                sleep(self.retry_delay)
                
        return None

    def auth(self):
        # only auth when not already
        # TODO: consider setting and getting Token from cache (redis)
        if not self.headers:
            url = f"{self.base_url}/auth"
            payload = {"public_key": self.public_key}

            response = self._post(url=url, payload=payload)
            token = response.json()['token']
            self.headers = {"Authorization": "Bearer " + token}
            if PARANOID_DEBUG: print(f"ILoveMyPDF OCR: Authenticated successfully. {token[:5]}..")
        else:
            if PARANOID_DEBUG: print("ILoveMyPDF OCR: already authenticated")
            return

    def start(self):
        url = f"{self.base_url}/start/pdfocr"
        response = self._get(url=url)
        jsponse = response.json()

        self.working_server = jsponse['server'].rstrip('/')
        self.task = jsponse['task']
        if PARANOID_DEBUG:
            print(f"ILoveMyPDF OCR: started task successfully.\n{self.task}\n{self.working_server}")

    def delete_task(self):
        url = f"https://{self.working_server}/v1/task/{self.task}"
        if self.task:
            response = self._delete(url=url, params=self.secret_key)

            if PARANOID_DEBUG: print(f"ILoveMyPDF OCR: deleted task")
        

    def upload(self):
        url = f"https://{self.working_server}/v1/upload"
        payload = {"task": self.task}

        with open(self.file_path, 'rb') as f:
            response = self._post(url=url, data=payload, files={"file": f},)
            jsponse = response.json()
            self.server_filename = jsponse['server_filename']

            if PARANOID_DEBUG:
                print(f"ILoveMyPDF OCR: uploaded file successfully\n{jsponse}")
    
    def process_file(self):
        """
        trigger processing the uploaded file
        """
        if not self.server_filename:
            raise Exception(f"ILoveMyPDF OCR: Proccess file: no file was uploaded to working server")

        url = f"https://{self.working_server}/v1/process"
        payload = {
            "task": self.task,
            "tool": "pdfocr",
            'ignore_errors': True,
            "files": [
                {"server_filename": self.server_filename, "filename": self.file_name},
            ]
        }

        response = self._post(url=url, payload=payload)
        jsponse = response.json()
        
        if DEBUG:
            print('ILoveMyPDF OCR: Proccess file: DONE')
            print(jsponse)
        
        self.task_status = jsponse['status']


    def download(self):
        url = f"https://{self.working_server}/v1/download/{self.task}"

        response = self._get(url=url, stream=True,)

        with open(self.output_file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)

        if DEBUG: print(f"ILoveMyPDF OCR: Downloaded the the file successfully")


    def get_task_info(self):
        """
        mainly for debug purpose
            (e.g: check if tasks are being removed correctly)
        """
        pass

    def load(self) -> str:
        try:
            self.auth()
            self.start()
            self.upload()
            self.process_file()
            self.download()
            self.delete_task()


            if self.task_status == "TaskSuccess":
                return self.output_file_path
            else:
                return ''

        except BaseException as e:
            self.delete_task()
            # raise e
            if DEBUG:
                print(f"[ERROR] ILoveMyPDF OCR: Failed: {e}")
            
            return ""