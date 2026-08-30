"""
Builds the local vector store from the synthetic policy documents in
data/policies/. Run this once (and again any time a policy file changes)
before running the pipeline in main.py.

Usage:
    python -m src.ingest
"""

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

load_dotenv()

POLICIES_DIR = Path("data/policies")
VECTOR_STORE_PATH = Path("data/vector_store.json")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Split on headers first so each chunk stays on a single topic and carries
# its document title / section / subsection as metadata; anything still
# too long after that gets further split by the recursive splitter below.
HEADERS_TO_SPLIT_ON = [
    ("#", "document"),
    ("##", "section"),
    ("###", "subsection"),
]


def load_policy_documents() -> List[Document]:
    """Read every markdown file in data/policies/, split it into
    topic-coherent chunks, and tag each chunk with its source filename.
    """
    if not POLICIES_DIR.exists():
        raise FileNotFoundError(
            f"{POLICIES_DIR} does not exist. Add your synthetic policy "
            "markdown files there before running ingest."
        )

    policy_files = sorted(POLICIES_DIR.glob("*.md"))
    if not policy_files:
        raise FileNotFoundError(f"No .md files found in {POLICIES_DIR}.")

    md_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT_ON,
        strip_headers=False,
    )
    fallback_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

    all_chunks: List[Document] = []
    for policy_file in policy_files:
        raw_text = policy_file.read_text(encoding="utf-8")
        header_chunks = md_splitter.split_text(raw_text)

        for chunk in header_chunks:
            chunk.metadata["source"] = policy_file.name

        # split_documents (not split_text) preserves the header metadata
        # on every resulting piece, and only applies overlap within a
        # section rather than across section boundaries.
        all_chunks.extend(fallback_splitter.split_documents(header_chunks))

    return all_chunks


def build_vector_store(chunks: List[Document]) -> InMemoryVectorStore:
    """Build vector store using HuggingFace embeddings (free, local)."""
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    store = InMemoryVectorStore(embeddings)
    store.add_documents(documents=chunks)
    return store


def main() -> None:
    """Ingest policies into vector store. No API key required (uses local embeddings)."""
    chunks = load_policy_documents()
    store = build_vector_store(chunks)

    VECTOR_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    store.dump(str(VECTOR_STORE_PATH))

    source_count = len({chunk.metadata["source"] for chunk in chunks})
    print(f"✅ Ingested {len(chunks)} chunks from {source_count} policy document(s)")
    print(f"   Saved to: {VECTOR_STORE_PATH}")
    print(f"   Embedding model: {EMBEDDING_MODEL}")
    print(f"\n   Ready to run: python -m src.main --input samples/sample_rfp.csv --output output/responses.csv")


if __name__ == "__main__":
    main()