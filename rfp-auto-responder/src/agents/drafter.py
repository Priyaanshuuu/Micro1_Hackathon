"""
Drafter Agent: Generates answers strictly from retrieved policy chunks.

Must not add information from general knowledge - only from the provided context.
If context doesn't cover the question, explicitly state that.
"""

import os
from typing import Dict

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from src.types import RFPState

load_dotenv()


def drafter_node(state: RFPState) -> Dict:
    """
    Draft an answer to the RFP question using only the retrieved chunks.

    Returns only the 'answer' field for state update.
    """
    question = state["question"]
    retrieved_chunks = state["retrieved_chunks"]

    # Build context from retrieved chunks
    context_parts = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        context_parts.append(
            f"[Source {i}: {chunk.source}]\n{chunk.content}\n"
        )

    context = "\n".join(context_parts)

    # Draft prompt
    prompt = f"""You are answering an RFP security/compliance questionnaire on behalf of a B2B SaaS company.

Question: {question}

Context from company policy documents:
{context}

Instructions:
- Answer STRICTLY based on the provided context above
- If the context doesn't contain enough information to answer, say "Our policy documentation does not currently cover this specific requirement" rather than guessing
- Be direct and factual - this will be reviewed by security and legal teams
- Include specific details from the context (certifications, timelines, technical specs)
- Do NOT add information from general knowledge
- Keep the answer concise (2-4 sentences typically)

Answer:"""

    llm = ChatGroq(
        model=os.getenv("MODEL_NAME", "llama-3.3-70b-versatile"),
        temperature=0
    )

    response = llm.invoke(prompt)
    answer = response.content.strip()

    return {"answer": answer}
