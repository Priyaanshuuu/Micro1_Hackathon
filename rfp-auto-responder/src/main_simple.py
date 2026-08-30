"""
Simplified main CLI that uses CSV module instead of pandas.

Usage:
    python -m src.main_simple --input samples/sample_rfp.csv --output output/responses.csv
"""

import argparse
import csv
from pathlib import Path

from dotenv import load_dotenv

from src.graph.orchestrator import build_graph
from src.types import RFPState

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="RFP Auto-Responder")
    parser.add_argument("--input", required=True, help="Input CSV path (RFP questions)")
    parser.add_argument("--output", required=True, help="Output CSV path (responses)")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load input questions
    print(f"Loading questions from {input_path}")
    questions = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            questions.append({
                'question_id': row['question_id'],
                'question': row['question']
            })

    print(f"Processing {len(questions)} questions...\n")

    # Build the graph
    graph = build_graph()

    # Process each question
    responses = []
    escalated_rows = []

    for i, q in enumerate(questions, 1):
        print(f"[{i}/{len(questions)}] {q['question_id']}: {q['question'][:60]}...")

        # Initialize state
        initial_state: RFPState = {
            "question_id": q['question_id'],
            "question": q['question'],
            "search_query": "",
            "retrieved_chunks": [],
            "answer": "",
            "verdict": None,
            "retry_count": 0,
            "status": "pending",
            "attempts": [],
        }

        # Run the graph
        final_state = graph.invoke(initial_state)

        # Extract response data
        status = final_state["status"]
        answer = final_state["answer"]
        attempts = final_state["attempts"]

        # Get unique source citations
        sources = set()
        for attempt in attempts:
            for chunk in attempt.retrieved_chunks:
                sources.add(chunk.source)
        source_citations = "; ".join(sorted(sources))

        response_row = {
            'question_id': q['question_id'],
            'question': q['question'],
            'answer': answer,
            'status': status,
            'source_citations': source_citations,
            'retries': final_state["retry_count"]
        }
        responses.append(response_row)

        # Track escalated questions
        if status == "escalated":
            escalated_data = {
                "question_id": q['question_id'],
                "question": q['question'],
                "final_answer": answer,
                "attempts": len(attempts),
                "retries": final_state["retry_count"],
            }

            # Add attempt details
            for idx, attempt in enumerate(attempts, 1):
                escalated_data[f"attempt_{idx}_query"] = attempt.search_query
                escalated_data[f"attempt_{idx}_answer"] = attempt.answer
                escalated_data[f"attempt_{idx}_verdict"] = (
                    "PASSED" if attempt.verdict.passed else f"FAILED: {attempt.verdict.feedback}"
                )

            escalated_rows.append(escalated_data)

        print(f"  → {status.upper()} (retries: {final_state['retry_count']})")

    # Write output responses
    print(f"\nWriting {len(responses)} responses to {output_path}")
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['question_id', 'question', 'answer', 'status', 'source_citations', 'retries']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(responses)

    # Write human review queue if any escalations
    if escalated_rows:
        review_queue_path = output_path.parent / "human_review_queue.csv"
        print(f"Writing {len(escalated_rows)} escalated questions to {review_queue_path}")

        # Get all fieldnames dynamically
        all_fields = set()
        for row in escalated_rows:
            all_fields.update(row.keys())
        fieldnames = sorted(all_fields)

        with open(review_queue_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(escalated_rows)

    # Summary
    approved = sum(1 for r in responses if r['status'] == "approved")
    escalated = sum(1 for r in responses if r['status'] == "escalated")
    total_retries = sum(r['retries'] for r in responses)

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Total questions: {len(responses)}")
    print(f"Approved: {approved} ({approved/len(responses)*100:.1f}%)")
    print(f"Escalated: {escalated} ({escalated/len(responses)*100:.1f}%)")
    print(f"Total retries: {total_retries}")
    print(f"Avg retries per question: {total_retries/len(responses):.2f}")


if __name__ == "__main__":
    main()
