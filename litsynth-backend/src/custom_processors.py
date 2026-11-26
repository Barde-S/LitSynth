import os
import uuid
import pymupdf
from langchain_core.documents import Document

from dotenv import load_dotenv
load_dotenv()

DEBUG = os.getenv('DEBUG', 'false').lower() in ['true', '1', 'yes']

class LitSynthPdfLoader:
    """
    Extract text with formatted tables from PDF files.
    Powered by PyMuPDF library

    Extracted tables are returned as a separate dictionary
    with keys representing their placeholders inside the docs

    Extracted text is returned as Langchain Document (see: load())
    """
    def __init__(self, file_path) -> None:
        self.file_path = file_path

    def _get_page_content(self, page: pymupdf.Page) -> tuple[str, dict]:
        """
        return a string with page content with placeholders for extracted tables
        + the extracted tables

        Link place holders with tables by their placeholder name uniquness

        Usage:
        page_text, tables_data = extract_tables_and_text(page)

        Fill placeholders:
        for k,v in tables_data.items():
            page_text = page_text.replace(k, v)
        """
        # ROTATION DETECTION (NEW)
        rotation = page.rotation
        derotation_needed = rotation != 0

        if DEBUG and derotation_needed:
            print(f"[PDF LOADER] Page {page.number} has {rotation}° rotation - applying derotation")

        # Get derotation matrix if needed
        derotation_matrix = page.derotation_matrix if derotation_needed else None

        # Identify tables and get their bounding boxes + data
        tables = page.find_tables()
        table_bboxes = []
        extracted_tables_data = []

        for table in tables:
            bbox = table.bbox

            # Transform bbox coordinates if page is rotated (NEW)
            if derotation_needed:
                # Apply inverse rotation transformation to bbox
                rect = pymupdf.Rect(bbox)
                transformed_rect = rect * derotation_matrix
                bbox = tuple(transformed_rect)

                if DEBUG:
                    print(f"[PDF LOADER] Transformed table bbox from {table.bbox} to {bbox}")

            table_bboxes.append(bbox)
            extracted_tables_data.append(table.to_markdown())

        returned_tables_data = {} 
        returned_page_content = ""    
        
        # Collect text between tables

        top = page.rect.y0  # top of the page
        for idx, bbox in enumerate(table_bboxes):
            table_place_holder = "TABLE_PLACEHOLDER_" + str(uuid.uuid4())[:5]

            bottom = bbox[1]  # top of the next table
            clip_rect = pymupdf.Rect(0, top, page.rect.x1, bottom)

            # Transform clip rect if page is rotated (NEW)
            if derotation_needed:
                clip_rect = clip_rect * derotation_matrix

            try:
                text = page.get_text("text", clip=clip_rect)
            except Exception:
                text = ""

            if text.strip():
                returned_page_content += "\n" + text.strip()

            # add placeholder for the table
            returned_page_content += "\n" + table_place_holder
            # save table data to be returned
            returned_tables_data[table_place_holder] = extracted_tables_data[idx]

            top = bbox[3]  # update top to bottom of current table

        # Capture text after the last table
        clip_rect = pymupdf.Rect(0, top, page.rect.x1, page.rect.y1)

        # Transform clip rect if page is rotated (NEW)
        if derotation_needed:
            clip_rect = clip_rect * derotation_matrix

        try:
            text = page.get_text("text", clip=clip_rect)
        except Exception:
            text = ""
        if text.strip():
            returned_page_content += "\n" + text.strip()

        return returned_page_content, returned_tables_data


    def load(self) -> tuple[list[Document], dict]:
        """
        returns list of Langchain Docs (doc per page)
            + dictionary of tables 
        [Doc1, Doc2, ..], {"table_placeholder":"table text", ..}
        """
        docs = []
        tables = {}

        pdf_doc = pymupdf.open(self.file_path)

        for page in pdf_doc:
            try:
                page_content, page_tables = self._get_page_content(page)
                tables.update(page_tables)
            except Exception as e:
                # Fallback: extract full page text without clip regions or table handling
                if DEBUG:
                    print(f"[PDF LOADER] Page {page.number} clip extraction failed ({e}), using fallback")
                try:
                    page_content = page.get_text()
                except Exception:
                    page_content = ""
            docs.append(
                Document(
                    page_content=page_content,
                    metadata={"page": page.number})
                )
        
        return docs, tables