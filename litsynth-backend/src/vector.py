# vector.py
# ChromaDB vector database initialization and management
# Manages vector store actions (loading/fetching/deleting)

import os
from uuid import uuid4
import chromadb
from chromadb.config import Settings

from langchain_chroma import Chroma
from langchain_core.documents import Document

from dotenv import load_dotenv
load_dotenv()
DEBUG = os.getenv('DEBUG', 'false').lower() in ['true', '1', 'yes']

# ChromaDB persistent storage directory
CHROMA_PERSIST_DIR = os.getenv('CHROMA_PERSIST_DIR', './data/chromadb')

def init_chroma_client() -> chromadb.Client:
    """
    Initialize ChromaDB client with persistent storage
    Usage: mainly stored in root app
    main.py > app.chroma_client = init_chroma_client()
    """
    # Ensure persist directory exists
    os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)

    if DEBUG:
        print(f'VECTOR: Initializing ChromaDB with persist_directory: {CHROMA_PERSIST_DIR}')

    client = chromadb.PersistentClient(
        path=CHROMA_PERSIST_DIR,
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )

    if DEBUG:
        collections = client.list_collections()
        print(f'VECTOR: ChromaDB initialized successfully!')
        print(f'VECTOR: Found {len(collections)} existing collections')

    return client


# Env setup for embeddings ---------
# Using FREE Sentence Transformers for embeddings (no API key needed!)
# This runs locally and is completely free
from langchain_huggingface import HuggingFaceEmbeddings

# Get embedding model from environment or use default
# Using nomic-embed-text-v1.5: 8192 token context (vs 512 for MiniLM), better for academic papers
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'nomic-ai/nomic-embed-text-v1.5')

print(f"VECTOR: Using free embedding model: {EMBEDDING_MODEL}")
print(f"VECTOR: Model will be downloaded on first run (~275MB)")

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={'device': 'cpu', 'trust_remote_code': True},
    encode_kwargs={'normalize_embeddings': True}
)


# Client based utilities ------------------

def get_vectore_store(client, namespace):
    """
    Get or create ChromaDB collection for a namespace (workspace)
    ChromaDB uses collections instead of Pinecone's namespaces

    Args:
        client: ChromaDB client
        namespace: workspace_id (used as collection name)

    Returns:
        Chroma vectorstore for the namespace
    """
    return Chroma(
        client=client,
        collection_name=namespace,
        embedding_function=embeddings
    )

def get_raw_collection(client, namespace):
    """Get raw ChromaDB collection (not LangChain wrapper) for direct insert with pre-computed embeddings."""
    return client.get_or_create_collection(name=namespace)


def delete_all_namespace(client):
    """
    Delete all collections (namespaces) from ChromaDB

    Args:
        client: ChromaDB client

    Returns:
        List of deleted collection names
    """
    collections = client.list_collections()
    collection_names = [c.name for c in collections]

    for collection_name in collection_names:
        client.delete_collection(collection_name)
        if DEBUG:
            print(f"VECTOR: Deleted collection: {collection_name}")

    print("Deleted Collections", collection_names)
    return collection_names

def get_index_info(client):
    """
    Get information about all collections in ChromaDB

    Args:
        client: ChromaDB client

    Returns:
        Dict with collection statistics
    """
    collections = client.list_collections()

    info = {
        "total_collections": len(collections),
        "collections": {}
    }

    for collection in collections:
        info["collections"][collection.name] = {
            "count": collection.count(),
            "metadata": collection.metadata
        }

    return info


# Vector store based utilities -----------

async def upsert_documents(documents: list[Document], vector_store: Chroma, prefix: str):
    """
    Add documents to ChromaDB collection with prefix-based IDs

    Args:
        documents: List of LangChain documents
        vector_store: Chroma vectorstore
        prefix: Prefix for document IDs (for deletion tracking)
    """
    # Generate UUIDs with prefix for tracking
    # ChromaDB doesn't have id_prefix param, so we prefix the IDs manually
    uuids = [f"{prefix}#{str(uuid4())}" for _ in range(len(documents))]

    await vector_store.aadd_documents(documents=documents, ids=uuids)

    if DEBUG:
        print(f"VECTOR: Upserted {len(documents)} documents with prefix {prefix}")

def delete_document(client, namespace, prefix):
    """
    Delete a document's chunks from ChromaDB using prefix metadata

    Uses ChromaDB's metadata filtering to find all chunks for a document
    and delete them completely.

    Args:
        client: ChromaDB client
        namespace: workspace_id (collection name)
        prefix: Document prefix to delete (stored in metadata)

    Returns:
        bool: True if any documents were deleted
    """
    if DEBUG:
        print(f"VECTOR: Deleting document with prefix {prefix} from namespace {namespace}")

    try:
        collection = client.get_collection(namespace)
    except Exception as e:
        if DEBUG:
            print(f"VECTOR: Collection {namespace} not found: {e}")
        return False

    # Get total count for logging
    total_count = collection.count()
    if DEBUG:
        print(f"VECTOR: Collection {namespace} has {total_count} total vectors")

    try:
        # Query by metadata prefix (more reliable than ID filtering)
        # This uses ChromaDB's native filtering
        results = collection.get(
            where={"prefix": prefix},  # Exact match on prefix metadata
            limit=100000,  # Large limit to ensure we get all matching vectors
            include=['metadatas']  # Include metadata for debugging
        )

        ids_to_delete = results.get('ids', [])

        if DEBUG:
            print(f"VECTOR: Found {len(ids_to_delete)} vectors with prefix {prefix}")

        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            if DEBUG:
                print(f"VECTOR: Successfully deleted {len(ids_to_delete)} vectors with prefix {prefix}")
                # Verify deletion
                remaining = collection.get(where={"prefix": prefix}, limit=10)
                if remaining.get('ids'):
                    print(f"VECTOR: WARNING - {len(remaining['ids'])} vectors still remain!")
            return True
        else:
            if DEBUG:
                print(f"VECTOR: No documents found with prefix {prefix}")
            return False

    except Exception as e:
        if DEBUG:
            print(f"VECTOR: Error deleting documents: {e}")
            import traceback
            traceback.print_exc()
        return False


def get_workspace_document_names(client, namespace: str) -> list[str]:
    """
    Get all unique document filenames in a workspace's ChromaDB collection.

    Args:
        client: ChromaDB client
        namespace: workspace_id (collection name)

    Returns:
        Sorted list of unique document filenames
    """
    try:
        collection = client.get_collection(namespace)
    except Exception:
        return []

    count = collection.count()
    if count == 0:
        return []

    results = collection.get(
        limit=min(10000, count),
        include=['metadatas']
    )

    sources = set()
    for metadata in results.get('metadatas', []):
        source = metadata.get('source')
        if source:
            sources.add(source)

    return sorted(sources)


def get_vectorstore_docs(vector_store: Chroma) -> list[Document]:
    """
    Return (all) documents in the vector store
    Uses similarity search with empty query to get documents

    Args:
        vector_store: Chroma vectorstore

    Returns:
        List of documents (limited to k=5000 for performance)
    """
    return vector_store.similarity_search("", k=5000)
