import os

class OcrPDF:
    """
    process a pdf file using OCR
    usage:
    pdf_ocr = OcrPDF("/some/path/to.pdf")
    output = pdf_ocr.load()

    if output:
        print(f"saved to {output}")
    else:
        print("failed")
    """
    provider_name = "DEFAULT"
    
    def __init__(self, file_path):
        self.file_path = file_path
    
    def load(self) -> str:
        raise NotImplemented

        # if success:
        #     return self.output_file_path
        # else:
        #     return ""


    @property
    def output_file_path(self) -> str:
        """
        Generates a string for output file path based in input file
        """
        directory, filename = os.path.split(self.file_path)
        name, extension = os.path.splitext(filename)

        return f"{directory}/{self.provider_name}_OCR_{name}_{extension}"
