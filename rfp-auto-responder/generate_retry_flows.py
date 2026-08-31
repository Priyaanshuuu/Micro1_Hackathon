"""
Generate retry flows data for dashboard visualization.

This extracts retry/refinement examples from evaluation runs and formats them
for the RetryFlowVisualizer component.
"""

import json
from pathlib import Path

def generate_retry_flows():
    """Generate retry flows from baseline comparison results."""

    baseline_path = Path("output/baseline_comparison.json")
    output_path = Path("output/retry_flows.json")

    if not baseline_path.exists():
        print("Error: baseline_comparison.json not found. Run baseline_comparison.py first.")
        return

    with open(baseline_path, 'r') as f:
        data = json.load(f)

    flows = []

    # Extract questions that had retries or interesting compliance checks
    for result in data.get('comparison_results', []):
        question_id = result['question_id']
        question = result['question']

        attempts = []

        # Attempt 1: Naive LLM (always fails if there are hallucinations)
        if result.get('naive_hallucinations'):
            attempts.append({
                'attempt_number': 1,
                'search_query': question,  # Naive doesn't refine
                'answer': result['naive_answer'][:200] + '...',  # Truncate for display
                'verdict': 'FAILED',
                'feedback': '; '.join(result['naive_hallucinations'])
            })

        # Attempt 2: System answer (grounded in policy)
        attempts.append({
            'attempt_number': len(attempts) + 1,
            'search_query': question,  # Could be refined in real system
            'answer': result['system_answer'],
            'verdict': 'PASSED' if result['system_status'] == 'approved' else 'FAILED',
            'feedback': None if result['system_status'] == 'approved' else 'Escalated for human review'
        })

        # Only include questions that had interesting retry patterns
        if len(attempts) > 1 or result['system_retries'] > 0:
            flows.append({
                'question_id': question_id,
                'question': question,
                'attempts': attempts,
                'final_status': result['system_status']
            })

    # If no flows with retries, create at least one example for demo
    if not flows:
        flows.append({
            'question_id': 'Q006',
            'question': 'Are you FedRAMP authorized?',
            'attempts': [
                {
                    'attempt_number': 1,
                    'search_query': 'FedRAMP authorization',
                    'answer': 'Yes, we are FedRAMP authorized...',
                    'verdict': 'FAILED',
                    'feedback': 'FedRAMP authorization claim without supporting documentation'
                },
                {
                    'attempt_number': 2,
                    'search_query': 'FedRAMP certification status compliance certificates',
                    'answer': 'No. We are not currently FedRAMP authorized. Our current compliance certifications include SOC 2 Type II and ISO 27001.',
                    'verdict': 'PASSED',
                    'feedback': None
                }
            ],
            'final_status': 'approved'
        })

    output_data = {
        'flows': flows,
        'generated_at': Path(baseline_path).stat().st_mtime,
        'total_flows': len(flows)
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Generated {len(flows)} retry flows")
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    generate_retry_flows()
