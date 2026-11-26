"""
Batch embed all un-embedded PDFs in a workspace directly (bypasses uvicorn event loop).
Run inside container: python3 batch_embed.py
"""
import os, sys, time, gc
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import chromadb
from chromadb.config import Settings
from uuid import uuid4

sys.path.insert(0, "/app/src")
from vector import embeddings as embedding_model
from processors import FileProcessor

WORKSPACE_ID = "c27ad7e0-fb70-4a04-a111-10ce70ed08fe"
DOC_DIR = f"/app/data/documents/{WORKSPACE_ID}"
CHROMA_DIR = "./data/chromadb"
EMBED_BATCH = 10

client = chromadb.PersistentClient(
    path=CHROMA_DIR,
    settings=Settings(anonymized_telemetry=False, allow_reset=True),
)

# Get already-embedded papers
collection = client.get_or_create_collection(name=WORKSPACE_ID)
count = collection.count()
if count > 0:
    result = collection.get(limit=count, include=["metadatas"])
    existing = set(m.get("source") for m in result["metadatas"] if "source" in m)
else:
    existing = set()

print(f"Already embedded: {len(existing)} papers ({count} vectors)")

# Find remaining papers
all_papers = sorted(f for f in os.listdir(DOC_DIR) if f.endswith(".pdf"))
remaining = [f for f in all_papers if f not in existing]
print(f"Remaining: {len(remaining)} papers\n")

for idx, filename in enumerate(remaining, 1):
    filepath = os.path.join(DOC_DIR, filename)
    print(f"[{idx}/{len(remaining)}] {filename}")

    # Phase 1: Parse + chunk
    t0 = time.time()
    metadata = {"source": filename, "workspace_id": WORKSPACE_ID}
    fp = FileProcessor.from_filetype(
        file_path=filepath,
        file_type="application/pdf",
        metadata=metadata,
    )
    if not fp:
        print(f"  SKIP: unsupported file type")
        continue

    splits = fp._sync_get_tagged_splits({})
    if not splits:
        print(f"  SKIP: no content extracted")
        continue
    print(f"  Parsed: {len(splits)} chunks ({time.time() - t0:.1f}s)")

    # Phase 2: Embed
    t1 = time.time()
    texts = [doc.page_content for doc in splits]
    all_vectors = []
    for batch_start in range(0, len(texts), EMBED_BATCH):
        batch_end = min(batch_start + EMBED_BATCH, len(texts))
        batch = texts[batch_start:batch_end]
        vectors = embedding_model.embed_documents(batch)
        all_vectors.extend(vectors)
        print(f"  Embedded {len(all_vectors)}/{len(texts)}")
    print(f"  Embedding done ({time.time() - t1:.1f}s)")

    # Phase 3: Store in ChromaDB
    t2 = time.time()
    prefix = fp.document_prefix
    STORE_BATCH = 500
    for bs in range(0, len(splits), STORE_BATCH):
        be = min(bs + STORE_BATCH, len(splits))
        ids = [f"{prefix}#{str(uuid4())}" for _ in range(be - bs)]
        collection.add(
            ids=ids,
            embeddings=all_vectors[bs:be],
            documents=[doc.page_content for doc in splits[bs:be]],
            metadatas=[doc.metadata for doc in splits[bs:be]],
        )
    print(f"  Stored ({time.time() - t2:.1f}s)")
    print(f"  Total: {time.time() - t0:.1f}s\n")
    # Free memory between papers
    del splits, texts, all_vectors
    gc.collect()

print(f"Done! Collection now has {collection.count()} vectors")
