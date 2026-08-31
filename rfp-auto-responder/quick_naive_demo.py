"""
Quick single-question naive LLM demo for video recording.

Usage:
    python quick_naive_demo.py "Your question here"

Example:
    python quick_naive_demo.py "Are you FedRAMP authorized?"
"""

import sys
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


def quick_naive_answer(question: str) -> str:
    """Generate naive answer without any verification."""
    llm = ChatGroq(
        model=os.getenv("MODEL_NAME", "llama-3.3-70b-versatile"),
        temperature=0
    )

    prompt = f"""You are a B2B SaaS company responding to an RFP security questionnaire.

Question: {question}

Provide a professional, confident answer about your company's security and compliance capabilities.

Answer:"""

    response = llm.invoke(prompt)
    return response.content.strip()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python quick_naive_demo.py \"Your question\"")
        print()
        print("Example questions that produce hallucinations:")
        print('  python quick_naive_demo.py "Are you FedRAMP authorized?"')
        print('  python quick_naive_demo.py "Do you support BYOK?"')
        print('  python quick_naive_demo.py "Do you offer on-premise deployment?"')
        sys.exit(1)

    question = " ".join(sys.argv[1:])

    print()
    print("Question:", question)
    print()
    print("Naive LLM Answer (NO verification, NO policy grounding):")
    print("-" * 70)

    answer = quick_naive_answer(question)
    print(answer)

    print()
    print("-" * 70)
    print("WARNING: This answer is NOT verified against actual policies!")
    print()
