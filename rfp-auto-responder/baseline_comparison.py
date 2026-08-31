"""
Baseline Comparison Script: Demonstrates competitive advantage of RFP Auto-Responder.

Compares naive LLM approach (no RAG, no compliance) vs full system pipeline.

Usage:
    python baseline_comparison.py

Generates:
    - output/baseline_comparison.json (raw metrics)
    - output/baseline_report.txt (formatted comparison report)
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from src.graph.orchestrator import build_graph
from src.types import RFPState

load_dotenv()


def load_golden_answers() -> List[Dict]:
    """Load golden answer evaluation set."""
    with open("tests/golden_answers.json", "r") as f:
        data = json.load(f)
    return data["evaluation_set"]


def naive_llm_answer(question: str) -> str:
    """
    Baseline: Direct LLM call with no RAG, no compliance gate.

    This is what most teams try first - just paste the question into an LLM.
    """
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


def system_answer(question: str, question_id: str) -> Dict:
    """
    RFP Auto-Responder: Full pipeline with RAG + compliance verification.
    """
    graph = build_graph()

    initial_state: RFPState = {
        "question_id": question_id,
        "question": question,
        "search_query": "",
        "retrieved_chunks": [],
        "answer": "",
        "verdict": None,
        "retry_count": 0,
        "status": "pending",
        "attempts": [],
    }

    final_state = graph.invoke(initial_state)

    # Get source citations
    sources = set()
    for attempt in final_state["attempts"]:
        for chunk in attempt.retrieved_chunks:
            sources.add(chunk.source)

    return {
        "answer": final_state["answer"],
        "status": final_state["status"],
        "sources": list(sources),
        "retries": final_state["retry_count"],
        "attempts": final_state["attempts"]
    }


def detect_hallucinations(answer: str, golden_answer: str) -> List[str]:
    """
    Detect hallucinations by comparing answer against golden answer.

    Returns list of potential hallucinations found.
    """
    hallucinations = []

    # Check for prohibited certifications
    prohibited = {
        "fedramp": "FedRAMP authorization claim (not held)",
        "hitrust": "HITRUST certification claim (not held)",
        "hipaa": "HIPAA compliance claim (not held)",
        "byok": "BYOK/CMEK support claim (not supported)",
        "customer-managed key": "Customer-managed encryption keys claim (not supported)",
        "on-premise": "On-premise deployment claim (not offered)",
        "self-hosted": "Self-hosted deployment claim (not offered)",
        "single-tenant": "Single-tenant deployment claim (not offered)",
        "dedicated environment": "Dedicated environment claim (not offered)"
    }

    answer_lower = answer.lower()

    for term, description in prohibited.items():
        if term in answer_lower:
            # Check if it's a denial
            denial_markers = ["not", "no ", "do not", "does not", "don't", "doesn't"]

            # Find context around the term
            idx = answer_lower.find(term)
            context_start = max(0, idx - 50)
            context = answer_lower[context_start:idx + len(term) + 20]

            # If no denial marker in context, it's likely a false claim
            if not any(marker in context for marker in denial_markers):
                hallucinations.append(description)

    return hallucinations


def score_answer(answer: str, golden_data: Dict, has_sources: bool) -> int:
    """
    Score answer using 0-3 rubric from evaluation framework.

    0 = Incorrect/Unsupported
    1 = Partially Correct
    2 = Correct, Uncited
    3 = Correct, Cited, Compliant
    """
    golden_answer = golden_data["golden_answer"].lower()
    answer_lower = answer.lower()

    # Check for hallucinations
    hallucinations = detect_hallucinations(answer, golden_answer)
    if hallucinations:
        return 0  # Incorrect - contains hallucination

    # Extract key facts from golden answer
    key_terms = []

    # For encryption questions
    if "aes-256" in golden_answer:
        key_terms.append("aes-256")
    if "aws-managed" in golden_answer or "aws kms" in golden_answer:
        key_terms.append("aws")

    # For certification questions
    if "soc 2" in golden_answer:
        key_terms.append("soc 2")
    if "iso 27001" in golden_answer:
        key_terms.append("iso 27001")

    # For retention questions
    if "30 days" in golden_answer or "30-day" in golden_answer:
        key_terms.append("30 day")
    if "90 days" in golden_answer or "90-day" in golden_answer:
        key_terms.append("90 day")

    # Check how many key terms are present
    terms_found = sum(1 for term in key_terms if term in answer_lower)

    if len(key_terms) == 0:
        # Generic question - check if answer is reasonable
        if len(answer) > 50:
            return 3 if has_sources else 2
        return 1

    coverage = terms_found / len(key_terms) if key_terms else 0

    if coverage >= 0.8:
        return 3 if has_sources else 2
    elif coverage >= 0.5:
        return 1
    else:
        return 0


def main():
    print("=" * 70)
    print("RFP AUTO-RESPONDER: BASELINE COMPARISON")
    print("=" * 70)
    print("\nComparing:")
    print("  [BASELINE] Naive LLM (no RAG, no compliance gate)")
    print("  [SYSTEM]   RFP Auto-Responder (full pipeline)")
    print()

    golden_set = load_golden_answers()

    comparison_results = []

    print(f"Running comparison on {len(golden_set)} questions...\n")

    for idx, golden in enumerate(golden_set, 1):
        question_id = golden["question_id"]
        question = golden["question"]

        print(f"[{idx}/{len(golden_set)}] {question_id}: {question[:50]}...")

        # Run naive LLM
        print("  -> Naive LLM...", end=" ", flush=True)
        start = time.time()
        naive_ans = naive_llm_answer(question)
        naive_time = time.time() - start
        naive_hallucinations = detect_hallucinations(naive_ans, golden["golden_answer"])
        naive_score = score_answer(naive_ans, golden, has_sources=False)
        print(f"Done ({naive_time:.1f}s, score={naive_score})")

        # Run system
        print("  -> System...", end=" ", flush=True)
        start = time.time()
        sys_result = system_answer(question, question_id)
        sys_time = time.time() - start
        sys_hallucinations = detect_hallucinations(sys_result["answer"], golden["golden_answer"])
        sys_score = score_answer(sys_result["answer"], golden, has_sources=len(sys_result["sources"]) > 0)
        print(f"Done ({sys_time:.1f}s, score={sys_score}, status={sys_result['status']})")

        improvement = sys_score - naive_score
        improvement_pct = (improvement / 3) * 100 if naive_score < sys_score else 0

        comparison_results.append({
            "question_id": question_id,
            "question": question,
            "golden_answer": golden["golden_answer"],
            "naive_answer": naive_ans,
            "naive_hallucinations": naive_hallucinations,
            "naive_score": naive_score,
            "naive_time": round(naive_time, 2),
            "system_answer": sys_result["answer"],
            "system_hallucinations": sys_hallucinations,
            "system_score": sys_score,
            "system_status": sys_result["status"],
            "system_sources": sys_result["sources"],
            "system_retries": sys_result["retries"],
            "system_time": round(sys_time, 2),
            "improvement": f"+{improvement}" if improvement > 0 else str(improvement),
            "improvement_pct": f"{improvement_pct:.0f}%"
        })
        print()

    # Calculate aggregate metrics
    total = len(comparison_results)

    naive_with_hallucinations = sum(1 for r in comparison_results if r["naive_hallucinations"])
    system_with_hallucinations = sum(1 for r in comparison_results if r["system_hallucinations"])

    naive_false_pass = sum(1 for r in comparison_results if r["naive_hallucinations"] and r["naive_score"] >= 2)
    system_false_pass = sum(1 for r in comparison_results if r["system_hallucinations"] and r["system_score"] >= 2)

    avg_naive_score = sum(r["naive_score"] for r in comparison_results) / total
    avg_system_score = sum(r["system_score"] for r in comparison_results) / total

    system_with_sources = sum(1 for r in comparison_results if r["system_sources"])
    system_escalated = sum(1 for r in comparison_results if r["system_status"] == "escalated")

    avg_naive_time = sum(r["naive_time"] for r in comparison_results) / total
    avg_system_time = sum(r["system_time"] for r in comparison_results) / total

    aggregate_metrics = {
        "naive_hallucination_rate": f"{(naive_with_hallucinations/total)*100:.1f}%",
        "system_hallucination_rate": f"{(system_with_hallucinations/total)*100:.1f}%",
        "naive_false_pass_rate": f"{(naive_false_pass/total)*100:.1f}%",
        "system_false_pass_rate": f"{(system_false_pass/total)*100:.1f}%",
        "naive_grounding_rate": "0%",
        "system_grounding_rate": f"{(system_with_sources/total)*100:.1f}%",
        "avg_naive_score": round(avg_naive_score, 2),
        "avg_system_score": round(avg_system_score, 2),
        "score_improvement": f"+{round(avg_system_score - avg_naive_score, 2)}",
        "system_escalation_rate": f"{(system_escalated/total)*100:.1f}%",
        "avg_naive_time": f"{avg_naive_time:.2f}s",
        "avg_system_time": f"{avg_system_time:.2f}s"
    }

    # Save JSON results
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    json_output = {
        "comparison_results": comparison_results,
        "aggregate_metrics": aggregate_metrics,
        "total_questions": total
    }

    with open(output_dir / "baseline_comparison.json", "w") as f:
        json.dump(json_output, f, indent=2)

    # Generate formatted report
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("RFP AUTO-RESPONDER: BASELINE COMPARISON REPORT")
    report_lines.append("=" * 80)
    report_lines.append("")
    report_lines.append("AGGREGATE METRICS")
    report_lines.append("-" * 80)
    report_lines.append(f"Total Questions Evaluated: {total}")
    report_lines.append("")
    report_lines.append(f"Hallucination Rate:")
    report_lines.append(f"  Naive LLM:  {aggregate_metrics['naive_hallucination_rate']}")
    report_lines.append(f"  System:     {aggregate_metrics['system_hallucination_rate']}")
    report_lines.append("")
    report_lines.append(f"False-Pass Rate (non-compliant answers scored as correct):")
    report_lines.append(f"  Naive LLM:  {aggregate_metrics['naive_false_pass_rate']}")
    report_lines.append(f"  System:     {aggregate_metrics['system_false_pass_rate']}")
    report_lines.append("")
    report_lines.append(f"Grounding Rate (answers with source citations):")
    report_lines.append(f"  Naive LLM:  {aggregate_metrics['naive_grounding_rate']}")
    report_lines.append(f"  System:     {aggregate_metrics['system_grounding_rate']}")
    report_lines.append("")
    report_lines.append(f"Average Rubric Score (0-3 scale):")
    report_lines.append(f"  Naive LLM:  {aggregate_metrics['avg_naive_score']}")
    report_lines.append(f"  System:     {aggregate_metrics['avg_system_score']}")
    report_lines.append(f"  Improvement: {aggregate_metrics['score_improvement']}")
    report_lines.append("")
    report_lines.append(f"System Escalation Rate: {aggregate_metrics['system_escalation_rate']}")
    report_lines.append(f"  (Questions sent to human review when confidence low)")
    report_lines.append("")
    report_lines.append(f"Average Response Time:")
    report_lines.append(f"  Naive LLM:  {aggregate_metrics['avg_naive_time']}")
    report_lines.append(f"  System:     {aggregate_metrics['avg_system_time']}")
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("DETAILED COMPARISON")
    report_lines.append("=" * 80)
    report_lines.append("")

    for r in comparison_results:
        report_lines.append(f"{r['question_id']}: {r['question']}")
        report_lines.append("-" * 80)
        report_lines.append("")
        report_lines.append("NAIVE LLM:")
        report_lines.append(f"  Answer: {r['naive_answer']}")
        report_lines.append(f"  Score: {r['naive_score']}/3")
        if r['naive_hallucinations']:
            report_lines.append(f"  ⚠ Hallucinations: {'; '.join(r['naive_hallucinations'])}")
        report_lines.append("")
        report_lines.append("SYSTEM:")
        report_lines.append(f"  Answer: {r['system_answer']}")
        report_lines.append(f"  Score: {r['system_score']}/3")
        report_lines.append(f"  Status: {r['system_status']}")
        report_lines.append(f"  Sources: {'; '.join(r['system_sources']) if r['system_sources'] else 'None'}")
        report_lines.append(f"  Retries: {r['system_retries']}")
        if r['system_hallucinations']:
            report_lines.append(f"  ⚠ Hallucinations: {'; '.join(r['system_hallucinations'])}")
        report_lines.append("")
        report_lines.append(f"IMPROVEMENT: {r['improvement']} ({r['improvement_pct']})")
        report_lines.append("")
        report_lines.append("")

    report_text = "\n".join(report_lines)

    with open(output_dir / "baseline_report.txt", "w") as f:
        f.write(report_text)

    # Print summary
    print("\n")
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Naive Hallucination Rate:  {aggregate_metrics['naive_hallucination_rate']}")
    print(f"System Hallucination Rate: {aggregate_metrics['system_hallucination_rate']}")
    print(f"")
    print(f"Naive False-Pass Rate:     {aggregate_metrics['naive_false_pass_rate']}")
    print(f"System False-Pass Rate:    {aggregate_metrics['system_false_pass_rate']}")
    print(f"")
    print(f"Average Score Improvement: {aggregate_metrics['score_improvement']} ({avg_naive_score:.2f} → {avg_system_score:.2f})")
    print(f"")
    print(f"✓ Results saved to:")
    print(f"  - output/baseline_comparison.json")
    print(f"  - output/baseline_report.txt")


if __name__ == "__main__":
    main()
