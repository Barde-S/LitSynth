# retrieval.py
# Advanced RAG Retrieval Module for LitSynth
# - Hybrid Search: BM25 (keyword) + Vector (semantic)
# - Query Expansion: LLM rewrites queries before retrieval

import os
import re
from typing import List, Tuple, Dict, Any
from rank_bm25 import BM25Okapi
from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel

from dotenv import load_dotenv
load_dotenv()
DEBUG = os.getenv('DEBUG', 'false').lower() in ['true', '1', 'yes']

# BM25 index storage (in-memory per namespace)
# Structure: {namespace: {"bm25": BM25Okapi, "docs": List[Document], "corpus": List[List[str]]}}
_bm25_indices: Dict[str, Dict[str, Any]] = {}


def tokenize(text: str) -> List[str]:
    """Simple tokenizer for BM25 - extracts words and preserves acronyms"""
    # Convert to lowercase but preserve original tokens for acronym matching
    tokens = re.findall(r'\b\w+\b', text.lower())
    return tokens


def build_bm25_index(documents: List[Document], namespace: str) -> None:
    """
    Build/update BM25 index for a namespace.
    Call this after documents are uploaded to vector store.
    """
    if not documents:
        if DEBUG:
            print(f"RETRIEVAL: No documents to index for namespace {namespace}")
        return

    corpus = [tokenize(doc.page_content) for doc in documents]
    bm25 = BM25Okapi(corpus)
    _bm25_indices[namespace] = {
        "bm25": bm25,
        "docs": documents,
        "corpus": corpus
    }
    if DEBUG:
        print(f"RETRIEVAL: Built BM25 index for namespace {namespace} with {len(documents)} documents")


def clear_bm25_index(namespace: str) -> None:
    """Clear BM25 index for a namespace (call when documents are deleted)"""
    if namespace in _bm25_indices:
        del _bm25_indices[namespace]
        if DEBUG:
            print(f"RETRIEVAL: Cleared BM25 index for namespace {namespace}")


def bm25_search(query: str, namespace: str, k: int = 10, vector_store=None) -> List[Tuple[Document, float]]:
    """
    BM25 keyword search - good for exact term matching (acronyms, specific terms).
    Lazily builds BM25 index on first query if not already built.

    Args:
        query: Search query string
        namespace: Workspace namespace to search in
        k: Number of results to return
        vector_store: Optional vector store for lazy index building (deferred from upload)

    Returns:
        List of (Document, score) tuples sorted by score descending
    """
    if namespace not in _bm25_indices:
        if vector_store:
            # Lazy build: BM25 index was deferred from upload for speed
            if DEBUG:
                print(f"RETRIEVAL: BM25 index missing for {namespace}, building lazily...")
            from vector import get_vectorstore_docs
            docs = get_vectorstore_docs(vector_store)
            if docs:
                build_bm25_index(docs, namespace)
            else:
                return []
        else:
            if DEBUG:
                print(f"RETRIEVAL: No BM25 index found for namespace {namespace}")
            return []

    index_data = _bm25_indices[namespace]
    tokenized_query = tokenize(query)

    if not tokenized_query:
        return []

    scores = index_data["bm25"].get_scores(tokenized_query)

    # Get top-k results with scores
    doc_scores = list(zip(index_data["docs"], scores))
    doc_scores.sort(key=lambda x: x[1], reverse=True)

    # Filter out zero-score results
    doc_scores = [(doc, score) for doc, score in doc_scores if score > 0]

    if DEBUG:
        print(f"RETRIEVAL: BM25 found {len(doc_scores)} results for query: {query[:50]}...")

    return doc_scores[:k]


def reciprocal_rank_fusion(
    semantic_results: List[Document],
    bm25_results: List[Tuple[Document, float]],
    k: int = 60,
    semantic_weight: float = 0.7,
    bm25_weight: float = 0.3,
    min_score_threshold: float = 0.005
) -> List[Document]:
    """
    Merge semantic and BM25 results using Reciprocal Rank Fusion (RRF).

    RRF score = sum(weight * 1 / (k + rank)) for each ranking list

    This approach:
    - Combines the strengths of semantic (conceptual similarity) and lexical (exact term) matching
    - Handles vocabulary mismatch (acronyms like LSTM, RAGAS)
    - Is robust to score normalization differences between methods
    - Filters out low-relevance results to reduce noise

    Args:
        semantic_results: Documents from vector similarity search (ranked by similarity)
        bm25_results: (Document, score) tuples from BM25 search
        k: RRF constant (default 60, as per original RRF paper)
        semantic_weight: Weight for semantic search results
        bm25_weight: Weight for BM25 results
        min_score_threshold: Minimum RRF score to include (filters noise)

    Returns:
        Merged and re-ranked list of Documents
    """
    # Use content hash as document identifier for deduplication
    def get_doc_id(doc: Document) -> str:
        return doc.page_content[:200]  # First 200 chars as identifier

    scores: Dict[str, Dict[str, Any]] = {}

    # Score semantic results (already ranked by similarity)
    for rank, doc in enumerate(semantic_results):
        doc_id = get_doc_id(doc)
        rrf_score = semantic_weight * (1 / (k + rank + 1))
        if doc_id not in scores:
            scores[doc_id] = {"score": 0, "doc": doc}
        scores[doc_id]["score"] += rrf_score

    # Score BM25 results
    for rank, (doc, _bm25_score) in enumerate(bm25_results):
        doc_id = get_doc_id(doc)
        rrf_score = bm25_weight * (1 / (k + rank + 1))
        if doc_id not in scores:
            scores[doc_id] = {"score": 0, "doc": doc}
        scores[doc_id]["score"] += rrf_score

    # Sort by combined score
    sorted_results = sorted(scores.values(), key=lambda x: x["score"], reverse=True)

    # Filter out low-scoring results to reduce noise
    filtered_results = [item for item in sorted_results if item["score"] >= min_score_threshold]

    if DEBUG:
        filtered_count = len(sorted_results) - len(filtered_results)
        print(f"RETRIEVAL: RRF merged {len(semantic_results)} semantic + {len(bm25_results)} BM25 results into {len(filtered_results)} results (filtered {filtered_count} low-score)")

    return [item["doc"] for item in filtered_results]


async def expand_query(query: str, llm: BaseChatModel) -> List[str]:
    """
    Use LLM to generate expanded query variants for better retrieval.

    This addresses:
    - Vocabulary mismatch (user says "memory networks", paper says "LSTM")
    - Acronym expansion (user says "RAG", expand to "Retrieval Augmented Generation")
    - Query reformulation (make implicit concepts explicit)

    Args:
        query: Original user query
        llm: Language model for query expansion

    Returns:
        List of queries: [original, expansion1, expansion2]
    """
    expansion_prompt = f"""You are a search query optimizer for academic research papers.
Given the user's query, generate 2 alternative search queries that:
1. Use different terminology or synonyms that might appear in academic papers
2. Expand any acronyms (e.g., RAG -> Retrieval Augmented Generation, LSTM -> Long Short-Term Memory)
3. Make implicit concepts explicit

Original query: {query}

Return ONLY the 2 alternative queries, one per line. No numbering, bullets, or explanations."""

    try:
        response = await llm.ainvoke(expansion_prompt)
        expanded_text = response.content.strip()
        expanded = [q.strip() for q in expanded_text.split('\n') if q.strip()]

        # Return original + up to 2 expansions
        result = [query] + expanded[:2]

        if DEBUG:
            print(f"RETRIEVAL: Query expansion: {query} -> {result}")

        return result
    except Exception as e:
        if DEBUG:
            print(f"RETRIEVAL: Query expansion failed: {e}, using original query only")
        # Fallback to original query only
        return [query]


def is_bm25_index_available(namespace: str) -> bool:
    """Check if BM25 index exists for a namespace"""
    return namespace in _bm25_indices


def get_bm25_index_stats(namespace: str) -> Dict[str, Any]:
    """Get statistics about a BM25 index"""
    if namespace not in _bm25_indices:
        return {"exists": False}

    index_data = _bm25_indices[namespace]
    return {
        "exists": True,
        "num_documents": len(index_data["docs"]),
        "avg_doc_length": sum(len(c) for c in index_data["corpus"]) / len(index_data["corpus"]) if index_data["corpus"] else 0
    }
