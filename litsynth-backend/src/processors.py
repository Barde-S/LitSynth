# processors.py
# manages logic for data sources managements (processing + storage)
import os
import re
from functools import cached_property
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from custom_processors import LitSynthPdfLoader

from uuid import uuid4

from dotenv import load_dotenv
load_dotenv()
DEBUG = os.getenv('DEBUG', 'false').lower() in ['true', '1', 'yes']


# --- Module-level cached text splitter (stateless, reuse everywhere) ---
# Chunk size of 2000 characters ≈ 512 tokens
# Aligned with NVIDIA RAG benchmarks recommending 512 tokens for optimal retrieval
DOC_CHUNK_SIZE = 2000
DOC_CHUNK_OVERLAP = 200  # ~10% overlap for context continuity
_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=DOC_CHUNK_SIZE, chunk_overlap=DOC_CHUNK_OVERLAP
)


# --- Pipeline helper functions (called via asyncio.to_thread) ---

def _sync_embed_texts(texts, embedding_model):
    """Embed all texts in one call. sentence-transformers batches internally for optimal CPU throughput."""
    return embedding_model.embed_documents(texts)


def _sync_store_preembedded(documents, vectors, collection, prefix):
    """Store docs with pre-computed embeddings directly into ChromaDB (bypasses LangChain re-embedding)."""
    ids = [f"{prefix}#{str(uuid4())}" for _ in range(len(documents))]
    collection.add(
        ids=ids,
        embeddings=vectors,
        documents=[doc.page_content for doc in documents],
        metadatas=[doc.metadata for doc in documents]
    )
    return len(documents)


if DEBUG:
    import shutil


# --- Utilities ---

def get_prefix(filename: str, plan_id: str) -> str:
    """
    Generate a prefix from a file name + plan/workspace ID.
    Represents "a specific file in a specific workspace" for per-file operations.
    """
    pre_pfx = re.sub(r'[^\w]', 'a', filename)
    pre_pfx = re.sub(r'\d', lambda m: chr(ord('a') + int(m.group())), pre_pfx)
    return pre_pfx + plan_id


# --- Processors ---

class FileProcessor:

    def __init__(self, file_path: str, **kwargs) -> None:
        self.file_path = file_path
        self.created_files = [file_path]

        self.metadata = kwargs['metadata']
        self.filename = self.metadata['source']

        if 'workspace_id' in self.metadata:
            self.workspace_id = self.metadata['workspace_id']
            self.plan_id = self.workspace_id
        else:
            self.provider = self.metadata.get('provider', 'unknown')
            self.plan_id = self.metadata.get('plan_id', 'unknown')

        self.metadata.update({'prefix': self.document_prefix})

    @staticmethod
    def from_filetype(file_path: str, file_type: str, **kwargs):
        """Return the right FileProcessor subclass based on MIME type."""
        file_type = file_type.lower()
        if file_type in ['application/pdf']:
            return PDFProcessor(file_path, **kwargs)
        elif file_type in ['text/plain']:
            return TextProcessor(file_path, **kwargs)
        else:
            return None

    @cached_property
    def document_prefix(self):
        return get_prefix(filename=self.filename, plan_id=self.plan_id)

    def _sync_get_tagged_splits(self, provider_config):
        """Synchronous parsing + chunking. For use with asyncio.to_thread()."""
        raise NotImplementedError("Subclasses must implement _sync_get_tagged_splits")

    def cleanup(self):
        """Clean any created files during processor's lifespan."""
        removed = 0
        for file_path in self.created_files:
            try:
                os.remove(file_path)
                removed += 1
            except Exception:
                if DEBUG:
                    print(f"[FILE PROCESSOR] {self.filename} | CLEANUP: failed to remove {file_path}")
        if DEBUG:
            print(f"[FILE PROCESSOR] {self.filename} | CLEANUP: cleaned {removed}/{len(self.created_files)} files")


class PDFProcessor(FileProcessor):

    def _sync_get_tagged_splits(self, provider_config):
        """Synchronous PDF parsing + chunking + table filling.
        Runs in a thread. No async, no event loop."""
        loader = LitSynthPdfLoader(self.file_path)
        docs, tables = loader.load()

        if DEBUG:
            print(f"[FILE PROCESSOR] {self.filename} | parsed {len(docs)} pages")

        # Set metadata on each page
        for doc in docs:
            doc.metadata.update(self.metadata)
            doc.metadata['page'] += 1

        # Split into chunks
        splits = _text_splitter.split_documents(docs)

        # Fill table placeholders
        for split in splits:
            for placeholder, table_data in tables.items():
                split.page_content = split.page_content.replace(placeholder, table_data)

        if DEBUG:
            print(f"[FILE PROCESSOR] {self.filename} | {len(splits)} chunks ready")
        return splits


class TextProcessor(FileProcessor):

    def _sync_get_tagged_splits(self, provider_config):
        """Sync text file parsing + chunking."""
        loader = TextLoader(file_path=self.file_path, encoding='UTF-8')
        docs = loader.load()
        for doc in docs:
            doc.metadata.update(self.metadata)

        splits = _text_splitter.split_documents(docs)

        if DEBUG:
            print(f"[FILE PROCESSOR] {self.filename} | {len(splits)} chunks ready")
        return splits
