"""
Naive LLM Demo - Shows what happens WITHOUT RAG and compliance verification.

This demonstrates the "wrong but confident" answers that naive prompting produces.
Perfect for video demos showing the problem before showing the solution.

Usage:
    python naive_llm_demo.py
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


def naive_answer(question: str) -> str:
    """
    Generate answer using ONLY the LLM's general knowledge.

    NO RAG, NO compliance checking, NO policy documents.
    This is what most teams try first - and it fails.
    """
    llm = ChatGroq(
        model=os.getenv("MODEL_NAME", "llama-3.3-70b-versatile"),
        temperature=0
    )

    # Generic prompt with no grounding
    prompt = f"""You are a B2B SaaS company responding to an RFP security questionnaire.

Question: {question}

Provide a professional, confident answer about your company's security and compliance capabilities. Be specific and thorough.

Answer:"""

    response = llm.invoke(prompt)
    return response.content.strip()


# Demo questions that typically produce hallucinations
DEMO_QUESTIONS = [
    "Are you FedRAMP authorized?",
    "Do you support customer-managed encryption keys (BYOK)?",
    "Do you offer on-premise deployment options?",
    "Are you HIPAA compliant?",
    "Can we get a dedicated single-tenant environment?",
]


def main():
    print("=" * 70)
    print("NAIVE LLM DEMO - What Goes Wrong Without Verification")
    print("=" * 70)
    print()
    print("This shows what happens when you just paste RFP questions into an LLM")
    print("without grounding in actual policy documents or compliance verification.")
    print()
    print("-" * 70)
    print()

    for idx, question in enumerate(DEMO_QUESTIONS, 1):
        print(f"\n[Question {idx}]")
        print(f"Q: {question}")
        print()
        print("Naive LLM Answer:")
        print("-" * 70)

        answer = naive_answer(question)
        print(answer)

        print()
        print("⚠️  WARNING: This answer may contain hallucinations!")
        print("   The LLM is guessing based on general knowledge, not your actual policies.")
        print()
        print("=" * 70)

        # Pause between questions for readability
        if idx < len(DEMO_QUESTIONS):
            input("\nPress Enter for next question...")
            print()


if __name__ == "__main__":
    main()
