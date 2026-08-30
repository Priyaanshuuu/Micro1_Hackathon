"""
Ingestion script: Chunks policy markdown files and builds a local vector store.

Usage:
    python -m src.ingest

Reads all .md files from data/policies/, splits them by markdown headers,
embeds via HuggingFace (local), and saves to data/vector_store.json for runtime loading.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter

load_dotenv()

POLICIES_DIR = Path("data/policies")
VECTOR_STORE_PATH = Path("data/vector_store.json")


def main():
    """Load policy docs, chunk by headers, embed, and persist vector store."""

    embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    print(f"Loading embedding model: {embedding_model}")
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)

    # Collect all policy markdown files
    policy_files = list(POLICIES_DIR.glob("*.md"))
    if not policy_files:
        raise FileNotFoundError(f"No .md files found in {POLICIES_DIR}")

    print(f"Found {len(policy_files)} policy files")

    # Split by markdown headers (## and ###)
    headers_to_split_on = [
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
    ]
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

    all_chunks = []
    for policy_file in policy_files:
        content = policy_file.read_text(encoding="utf-8")
        chunks = splitter.split_text(content)

        # Add source metadata
        for chunk in chunks:
            chunk.metadata["source"] = policy_file.name

        all_chunks.extend(chunks)
        print(f"  {policy_file.name}: {len(chunks)} chunks")

    print(f"\nTotal chunks: {len(all_chunks)}")

    # Build vector store
    print("Embedding chunks (using local HuggingFace model)...")
    vector_store = InMemoryVectorStore.from_documents(
        documents=all_chunks,
        embedding=embeddings
    )

    # Persist to disk
    VECTOR_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    vector_store.dump(str(VECTOR_STORE_PATH))

    print(f"✓ Vector store saved to {VECTOR_STORE_PATH}")


if __name__ == "__main__":
    main()
