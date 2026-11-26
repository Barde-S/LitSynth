import os
import re
import json
from typing import Any, List, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableSerializable
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_google_genai import ChatGoogleGenerativeAI
from vector import get_vectore_store
from retrieval import bm25_search, reciprocal_rank_fusion, expand_query

from dotenv import load_dotenv
load_dotenv()
DEBUG = os.getenv('DEBUG', 'false').lower() in ['true', '1', 'yes']


def _extract_highlight_text(page_content: str) -> str:
    """Extract a clean, matchable text fragment from a chunk for PDF highlighting.

    Chunks often start with noise: page numbers, broken words from split boundaries,
    reference markers like '[56]', or partial sentences. This function finds the first
    clean, complete sentence or phrase that will reliably match in the PDF text layer.

    Returns up to 300 chars for better fuzzy matching in the frontend viewer.
    """
    text = page_content.strip()

    # Strip table placeholder residue from processing
    text = re.sub(r'TABLE_PLACEHOLDER_[a-f0-9]+', '', text)

    # Strip leading page numbers (e.g. "8\n", "12\n") that come from PDF extraction
    text = re.sub(r'^\d{1,3}\s*\n', '', text)

    # Strip leading reference markers like "[56]", "(2019)", etc.
    text = re.sub(r'^\[\d+\]\s*', '', text)
    text = re.sub(r'^\(\d{4}\)\s*', '', text)

    # Strip leading whitespace/newlines again after cleanup
    text = text.strip()

    max_len = 300

    # Find the first sentence that starts with a capital letter or a meaningful word
    # Skip fragments that start mid-word (lowercase after chunk split)
    lines = text.split('\n')

    # Try to find a line that starts a proper sentence (capital letter, at least 20 chars)
    for line in lines:
        line = line.strip()
        if len(line) >= 20 and (line[0].isupper() or line[0] == '"' or line[0] == "'"):
            # Found a good starting line - take up to max_len chars from here
            idx = text.find(line)
            if idx != -1:
                fragment = text[idx:idx + max_len].strip()
                # Trim to last complete word
                if len(fragment) >= max_len:
                    last_space = fragment.rfind(' ')
                    if last_space > 100:
                        fragment = fragment[:last_space]
                return fragment

    # Fallback: just use the cleaned text, trimmed to word boundary
    fragment = text[:max_len].strip()
    if len(fragment) >= max_len:
        last_space = fragment.rfind(' ')
        if last_space > 100:
            fragment = fragment[:last_space]
    return fragment

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)


async def get_relevant_context(index, workspace_id: str, query: str, k: int = 5):
    """
    Retrieve relevant document chunks using HYBRID SEARCH (BM25 + Vector).
    Uses query expansion for improved recall and diversification for multi-document coverage.
    Returns: (context_text, sources_list)
    """
    vstore = get_vectore_store(index, workspace_id)

    # Step 1: Query Expansion - LLM generates alternative phrasings
    expanded_queries = await expand_query(query, llm)
    if DEBUG:
        print(f"CHAT: Query expansion: {query} -> {expanded_queries}")

    # Step 2: Semantic search with all query variants
    all_semantic_docs = []
    for q in expanded_queries:
        docs = await vstore.asimilarity_search(q, k=k * 2)
        all_semantic_docs.extend(docs)

    # Deduplicate semantic results by content
    seen_content = set()
    semantic_docs = []
    for doc in all_semantic_docs:
        content_key = doc.page_content[:200]
        if content_key not in seen_content:
            seen_content.add(content_key)
            semantic_docs.append(doc)

    # Step 3: BM25 keyword search (catches exact terms like acronyms: LSTM, RAGAS)
    bm25_results = bm25_search(query, workspace_id, k=k * 2, vector_store=vstore)

    # Step 4: Merge results using Reciprocal Rank Fusion
    if bm25_results:
        docs = reciprocal_rank_fusion(
            semantic_docs[:k * 2],
            bm25_results,
            semantic_weight=0.7,
            bm25_weight=0.3
        )
        if DEBUG:
            print(f"CHAT: Hybrid search merged {len(semantic_docs)} semantic + {len(bm25_results)} BM25 results")
    else:
        docs = semantic_docs
        if DEBUG:
            print(f"CHAT: Using semantic search only ({len(docs)} results)")

    if not docs:
        return "", []

    # Step 5: Diversify results to include chunks from multiple documents
    # This ensures cross-document questions get context from all relevant docs
    docs_by_source = {}
    for doc in docs:
        source = doc.metadata.get('source', 'Unknown')
        if source not in docs_by_source:
            docs_by_source[source] = []
        docs_by_source[source].append(doc)

    # Select chunks ensuring representation from multiple documents
    # Take at least 2 chunks from each document (if available), then fill remaining
    diversified_docs = []
    min_per_doc = 2

    # First pass: get minimum chunks from each document
    for source, source_docs in docs_by_source.items():
        diversified_docs.extend(source_docs[:min_per_doc])

    # Second pass: fill remaining slots with highest relevance chunks
    remaining_slots = k - len(diversified_docs)
    if remaining_slots > 0:
        # Get remaining docs not yet included
        used_ids = set(id(d) for d in diversified_docs)
        remaining_docs = [d for d in docs if id(d) not in used_ids]
        diversified_docs.extend(remaining_docs[:remaining_slots])

    # Limit to k total
    diversified_docs = diversified_docs[:k]

    # Build context text and collect sources
    context_parts = []
    sources = []

    for idx, doc in enumerate(diversified_docs, 1):
        source_name = doc.metadata.get('source', 'Unknown')
        page_num = doc.metadata.get('page', 'N/A')

        # Format page number for display
        page_display = int(page_num) if isinstance(page_num, (int, float)) and page_num != 'N/A' else page_num

        # Add to context with page number reference marker (e.g., [p.5] instead of [Source 1])
        context_parts.append(f"[p.{page_display}, {source_name}]:\n{doc.page_content}\n")

        # Collect source information (frontend expects 'source' not 'filename')
        sources.append({
            "source": source_name,
            "page": page_display,
            "snippet": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
            "highlightText": _extract_highlight_text(doc.page_content)
        })

    context_text = "\n".join(context_parts)
    return context_text, sources


def get_chat_chain():

    system_prompt = """
You are LitSynth, an intelligent research assistant for analyzing uploaded academic research papers.

CRITICAL INSTRUCTIONS:
- You MUST ONLY answer questions based on the research papers in this workspace
- DO NOT use web search or external knowledge
- DO NOT answer questions completely unrelated to academic research or the uploaded papers
- If the context excerpts AND the document list are both empty, respond with: "No documents have been uploaded to this workspace yet. Please upload research papers to get started."
- If the context excerpts are empty or not directly relevant BUT documents exist in the workspace, use the document list to identify which papers are likely relevant based on their titles, and mention them by name. Suggest the user ask a more specific question about those papers.
- If the context contains content from multiple documents, you CAN and SHOULD analyze relationships, comparisons, and connections between them

When answering from the provided context:
1. Base your detailed analysis on the context excerpts below, citing with the format [p.X, DocumentName]
2. When referencing multiple sources, cite each one appropriately
3. When asked about relationships between documents, analyze their themes, topics, connections, and differences
4. Compare and contrast papers when relevant or when asked
5. Explain concepts found in the papers clearly
6. Be precise and academically rigorous
7. When asked to list or identify papers, ALWAYS use the full document list — not just the excerpts

IMPORTANT: You have access to TWO sources of information:
1. The DOCUMENT LIST — the complete inventory of all papers uploaded to this workspace (use this for questions about what papers exist, which papers cover a topic, etc.)
2. The CONTEXT EXCERPTS — the most relevant text passages retrieved for the user's question (use this for detailed content questions)

ALL DOCUMENTS IN THIS WORKSPACE ({document_count} papers):
{document_list}

RELEVANT EXCERPTS FROM UPLOADED RESEARCH PAPERS:
{context}

CHAT HISTORY:
{history}

Remember: Use the document list to identify relevant papers. Use the context excerpts for detailed answers. Always cite sources with page numbers and document names when quoting from excerpts.
"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("human", system_prompt + "\n\nUser question: {query}"),
        ]
    )

    chain = prompt | llm
    return chain


async def generate_chat_title(first_message: str, llm: BaseChatModel) -> str:
    """
    Generate a concise chat title from the first user message.
    Returns a short, descriptive title (max 50 chars).
    """
    prompt = ChatPromptTemplate.from_messages([
        ("human", """Generate a short, descriptive title (max 6 words, 50 chars) for a research chat based on the user's first message.

Rules:
- Be specific and descriptive
- Use title case
- No quotes or punctuation at the end
- Focus on the research topic/question
- Keep it concise

Examples:
User: "What are the main findings in this paper about neural networks?"
Title: "Neural Networks Research Findings"

User: "Compare the methodologies used in these three papers on climate change"
Title: "Climate Change Methodology Comparison"

User: "Summarize the key contributions of this LSTM paper"
Title: "LSTM Paper Key Contributions"

User message: {message}""")
    ])

    chain = prompt | llm
    try:
        response = await chain.ainvoke({"message": first_message})
        title = response.content.strip()

        # Enforce length limit
        if len(title) > 50:
            title = title[:47] + "..."

        return title
    except Exception as e:
        # Fallback to truncated message if generation fails
        if DEBUG:
            print(f"CHAT: Title generation failed: {e}")
        return first_message[:50] + ("..." if len(first_message) > 50 else "")
