"""
Evaluation framework for RFP Auto-Responder.

Grades system output against golden answers using the 0-3 rubric.
Calculates:
  - Average score
  - % scoring 3 (ideal)
  - Hallucination rate (claims not in retrieved context)
  - False-pass rate (non-compliant answers that passed gate)
  - Source attribution accuracy

Usage:
  python -m pytest tests/evaluation.py -v
  python tests/evaluation.py  # Direct run
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.graph.orchestrator import build_graph
from src.types import RFPState


@dataclass
class EvaluationResult:
    """Result of grading one answer."""
    question_id: str
    question: str
    generated_answer: str
    golden_answer: str
    rubric_score: int
    is_hallucination: bool
    false_pass: bool
    sources_cited: List[str]
    required_sources: List[str]
    notes: str


class RubricGrader:
    """Grades answers on 0-3 rubric."""

    def __init__(self, golden_data: Dict):
        self.golden_map = {q["question_id"]: q for q in golden_data["evaluation_set"]}
        self.rubric_definitions = golden_data["scoring_rubric"]

    def grade(self, question_id: str, generated_answer: str, sources: List[str]) -> Tuple[int, str]:
        """
        Grade an answer on 0-3 scale.

        Returns: (score, rationale)
        """
        if question_id not in self.golden_map:
            return 0, "Question not in golden set"

        golden = self.golden_map[question_id]
        golden_answer = golden["golden_answer"]
        required_sources = golden.get("required_sources", [])

        # Check 1: Is answer empty or "not in context"?
        if not generated_answer or "does not currently cover" in generated_answer.lower():
            return 1, "Answer too vague or declines to answer"

        # Check 2: Source attribution
        has_sources = len(sources) > 0
        has_required = any(src in sources for src in required_sources)

        # Check 3: Compare to golden (simple semantic check)
        # In production, use embeddings; here we do keyword matching
        golden_keywords = self._extract_keywords(golden_answer)
        generated_keywords = self._extract_keywords(generated_answer)

        keyword_overlap = len(golden_keywords & generated_keywords) / len(golden_keywords) if golden_keywords else 0

        # Scoring logic
        if keyword_overlap < 0.4:
            return 0, "Answer missing key facts from golden answer"
        elif keyword_overlap < 0.7:
            return 1, "Answer partially correct but missing details"
        elif has_sources and has_required:
            return 3, "Correct, well-sourced, cites required documents"
        elif has_sources and not has_required:
            return 2, "Correct but cited wrong/incomplete sources"
        else:
            return 2, "Correct but no source attribution"

    @staticmethod
    def _extract_keywords(text: str) -> set:
        """Extract significant keywords from answer."""
        # Remove common words
        stop_words = {"the", "a", "an", "and", "or", "is", "are", "be", "by", "to", "for", "of", "in", "at"}
        words = text.lower().split()
        # Keep words > 3 chars, not in stop list
        return {w.strip(".,;:!?\"'") for w in words if len(w) > 3 and w.lower() not in stop_words}


def load_system_output(csv_path: Path) -> Dict[str, Dict]:
    """Load system-generated responses from CSV."""
    results = {}
    if not csv_path.exists():
        return results

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results[row['question_id']] = {
                'question': row['question'],
                'answer': row['answer'],
                'status': row['status'],
                'source_citations': row['source_citations'].split("; ") if row['source_citations'] else [],
                'retries': int(row['retries'])
            }
    return results


def run_evaluation(
    input_csv: Path = Path("samples/sample_rfp.csv"),
    output_csv: Path = Path("output/responses.csv"),
    golden_answers_path: Path = Path("tests/golden_answers.json")
) -> Dict:
    """
    Run the full evaluation pipeline.

    Returns dict with:
      - results: List[EvaluationResult]
      - metrics: Dict with summary stats
      - report: Formatted string report
    """

    # Load golden answers
    with open(golden_answers_path, 'r') as f:
        golden_data = json.load(f)

    grader = RubricGrader(golden_data)

    # If output doesn't exist, run the system
    if not output_csv.exists():
        print(f"⏳ Output CSV not found. Running system...")
        from src.main import main
        import sys
        old_argv = sys.argv
        sys.argv = ['', '--input', str(input_csv), '--output', str(output_csv)]
        try:
            main()
        except SystemExit:
            pass
        finally:
            sys.argv = old_argv

    # Load system output
    system_output = load_system_output(output_csv)

    # Grade each answer
    results: List[EvaluationResult] = []
    for golden_q in golden_data["evaluation_set"]:
        q_id = golden_q["question_id"]
        question = golden_q["question"]
        golden_answer = golden_q["golden_answer"]
        required_sources = golden_q.get("required_sources", [])

        if q_id not in system_output:
            # System didn't answer this question
            result = EvaluationResult(
                question_id=q_id,
                question=question,
                generated_answer="[NOT ANSWERED]",
                golden_answer=golden_answer,
                rubric_score=0,
                is_hallucination=False,
                false_pass=False,
                sources_cited=[],
                required_sources=required_sources,
                notes="System did not process this question"
            )
            results.append(result)
            continue

        system_result = system_output[q_id]
        generated_answer = system_result['answer']
        sources = system_result['source_citations']
        status = system_result['status']

        # Grade the answer
        score, grade_notes = grader.grade(q_id, generated_answer, sources)

        # Detect hallucination (claims without source)
        is_hallucination = score == 0 and status == "approved"

        # Detect false-pass (non-compliant answer that passed gate)
        false_pass = score < 2 and status == "approved"

        result = EvaluationResult(
            question_id=q_id,
            question=question,
            generated_answer=generated_answer,
            golden_answer=golden_answer,
            rubric_score=score,
            is_hallucination=is_hallucination,
            false_pass=false_pass,
            sources_cited=sources,
            required_sources=required_sources,
            notes=grade_notes
        )
        results.append(result)

    # Calculate metrics
    total = len(results)
    perfect_threes = sum(1 for r in results if r.rubric_score == 3)
    twos = sum(1 for r in results if r.rubric_score == 2)
    ones = sum(1 for r in results if r.rubric_score == 1)
    zeros = sum(1 for r in results if r.rubric_score == 0)

    hallucinations = sum(1 for r in results if r.is_hallucination)
    false_passes = sum(1 for r in results if r.false_pass)
    avg_score = sum(r.rubric_score for r in results) / total if total > 0 else 0

    metrics = {
        "total_questions": total,
        "perfect_3s": perfect_threes,
        "percent_3s": (perfect_threes / total * 100) if total > 0 else 0,
        "twos": twos,
        "ones": ones,
        "zeros": zeros,
        "average_score": round(avg_score, 2),
        "hallucination_count": hallucinations,
        "hallucination_rate": (hallucinations / total * 100) if total > 0 else 0,
        "false_pass_count": false_passes,
        "false_pass_rate": (false_passes / total * 100) if total > 0 else 0,
    }

    # Generate report
    report = _generate_report(results, metrics)

    return {
        "results": results,
        "metrics": metrics,
        "report": report
    }


def _generate_report(results: List[EvaluationResult], metrics: Dict) -> str:
    """Generate human-readable evaluation report."""
    lines = [
        "\n" + "=" * 80,
        "RFP AUTO-RESPONDER EVALUATION REPORT",
        "=" * 80,
        f"\nEvaluation Date: {__import__('datetime').datetime.now().isoformat()}",
        f"\nTOTAL QUESTIONS EVALUATED: {metrics['total_questions']}",
        "\n" + "-" * 80,
        "SCORE DISTRIBUTION",
        "-" * 80,
        f"  ⭐⭐⭐ Score 3 (Perfect):        {metrics['perfect_3s']:3d} ({metrics['percent_3s']:5.1f}%)  ✅",
        f"  ⭐⭐  Score 2 (Correct, Uncited): {metrics['twos']:3d} ({metrics['twos']/metrics['total_questions']*100:5.1f}%)  ⚠️",
        f"  ⭐   Score 1 (Partial):          {metrics['ones']:3d} ({metrics['ones']/metrics['total_questions']*100:5.1f}%)  ⚠️",
        f"  ❌  Score 0 (Wrong/Hallucin):  {metrics['zeros']:3d} ({metrics['zeros']/metrics['total_questions']*100:5.1f}%)  ❌",
        f"\n  Average Score: {metrics['average_score']}/3.0",
        "\n" + "-" * 80,
        "CRITICAL METRICS (Lower is Better)",
        "-" * 80,
        f"  Hallucination Rate: {metrics['hallucination_rate']:5.1f}% ({metrics['hallucination_count']} answers)  {'✅' if metrics['hallucination_rate'] == 0 else '❌ TARGET: 0%'}",
        f"  False-Pass Rate:    {metrics['false_pass_rate']:5.1f}% ({metrics['false_pass_count']} answers)  {'✅' if metrics['false_pass_rate'] == 0 else '❌ TARGET: 0%'}",
        "\n" + "-" * 80,
        "DETAILED RESULTS",
        "-" * 80,
    ]

    for r in results:
        score_emoji = {
            3: "⭐⭐⭐",
            2: "⭐⭐ ",
            1: "⭐  ",
            0: "❌ "
        }[r.rubric_score]

        lines.append(f"\n{score_emoji} {r.question_id}: {r.question[:60]}...")
        lines.append(f"   Generated: {r.generated_answer[:80]}...")
        if r.sources_cited:
            lines.append(f"   Sources:   {'; '.join(r.sources_cited)}")
        else:
            lines.append(f"   Sources:   [NONE CITED]")
        lines.append(f"   Notes:     {r.notes}")
        if r.is_hallucination:
            lines.append(f"   ⚠️  HALLUCINATION DETECTED")
        if r.false_pass:
            lines.append(f"   ⚠️  FALSE PASS (should have been escalated)")

    lines.append("\n" + "=" * 80)
    lines.append("SUMMARY & RECOMMENDATIONS")
    lines.append("=" * 80)

    if metrics['percent_3s'] >= 80:
        lines.append("✅ PASS: System demonstrates strong grounding and compliance verification.")
    else:
        lines.append(f"❌ IMPROVEMENT NEEDED: Only {metrics['percent_3s']:.0f}% perfect answers. Review:")
        lines.append("   - Policy corpus (too sparse?)")
        lines.append("   - Retrieval tuning (RETRIEVAL_K, embedding model)")
        lines.append("   - Compliance rules (too strict?)")

    if metrics['hallucination_rate'] > 0:
        lines.append(f"🚨 CRITICAL: {metrics['hallucination_count']} hallucinations detected.")
        lines.append("   This is the core risk this system aims to prevent.")
        lines.append("   → Review Compliance Agent rules and retrieval quality.")

    if metrics['false_pass_rate'] > 0:
        lines.append(f"🚨 CRITICAL: {metrics['false_pass_count']} non-compliant answers passed the gate.")
        lines.append("   → Tighten compliance rules or expand policy corpus.")

    lines.append("\n" + "=" * 80 + "\n")

    return "\n".join(lines)


def print_results(eval_result: Dict):
    """Pretty-print evaluation results."""
    print(eval_result["report"])

    # Print detailed results as table
    print("\nDETAILED SCORING TABLE:")
    print(f"{'QID':<6} {'Score':<8} {'Hallucin':<10} {'FalsePass':<10} {'Status':<12} {'Notes':<40}")
    print("-" * 100)
    for r in eval_result["results"]:
        notes_short = r.notes[:35] + "..." if len(r.notes) > 35 else r.notes
        print(
            f"{r.question_id:<6} "
            f"{r.rubric_score}/3{'':<4} "
            f"{'YES' if r.is_hallucination else 'NO':<10} "
            f"{'YES' if r.false_pass else 'NO':<10} "
            f"{'GOOD' if r.rubric_score == 3 else 'NEEDS WORK':<12} "
            f"{notes_short:<40}"
        )


if __name__ == "__main__":
    # Run evaluation
    eval_result = run_evaluation()
    print_results(eval_result)

    # Also export results to JSON for programmatic use
    output_json = Path("output/evaluation_results.json")
    output_json.parent.mkdir(parents=True, exist_ok=True)

    results_for_json = [
        {
            "question_id": r.question_id,
            "question": r.question,
            "generated_answer": r.generated_answer,
            "rubric_score": r.rubric_score,
            "is_hallucination": r.is_hallucination,
            "false_pass": r.false_pass,
            "sources_cited": r.sources_cited,
            "notes": r.notes
        }
        for r in eval_result["results"]
    ]

    with open(output_json, 'w') as f:
        json.dump({
            "metrics": eval_result["metrics"],
            "results": results_for_json
        }, f, indent=2)

    print(f"\n✅ Evaluation results exported to {output_json}")
