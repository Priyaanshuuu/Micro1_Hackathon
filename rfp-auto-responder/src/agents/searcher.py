"""
Searcher Agent: Retrieves relevant policy chunks from the vector store.

On the first attempt, searches based on the raw question.
On retries, incorporates compliance feedback to refine the search query.
"""

import os
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

from src.types import RFPState, RetrievedChunk

load_dotenv()


def searcher_node(state: RFPState) -> Dict:
    """
    Generate search query and retrieve relevant policy chunks.

    On first attempt: uses the raw question.
    On retry: incorporates verdict.feedback to refine the search.
    """
    question = state["question"]
    retry_count = state.get("retry_count", 0)
    verdict = state.get("verdict")

    # Build search query
    if retry_count == 0 or verdict is None or verdict.feedback is None:
        # First attempt - use raw question
        search_query = question
    else:
        # Retry - incorporate feedback to refine search
        feedback = verdict.feedback
        llm = ChatGroq(model=os.getenv("MODEL_NAME", "llama-3.3-70b-versatile"), temperature=0)

        refine_prompt = f"""Given this RFP question and compliance feedback, generate a refined search query to find the correct policy information.

Question: {question}

Previous compliance feedback: {feedback}

Generate a search query that specifically addresses the compliance issue raised. Return ONLY the search query text, nothing else."""

        search_query = llm.invoke(refine_prompt).content.strip()

    # Load vector store and retrieve
    vector_store_path = Path("data/vector_store.json")
    if not vector_store_path.exists():
        raise FileNotFoundError(
            f"Vector store not found at {vector_store_path}. "
            "Run 'python -m src.ingest' first."
        )

    embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)

    vector_store = InMemoryVectorStore.load(
        str(vector_store_path),
        embedding=embeddings
    )

    # Retrieve top K chunks
    k = int(os.getenv("RETRIEVAL_K", "4"))
    results = vector_store.similarity_search_with_score(search_query, k=k)

    # Convert to RetrievedChunk format
    retrieved_chunks = [
        RetrievedChunk(
            content=doc.page_content,
            source=doc.metadata.get("source", "unknown"),
            score=float(score)
        )
        for doc, score in results
    ]

    return {
        "search_query": search_query,
        "retrieved_chunks": retrieved_chunks
    }
