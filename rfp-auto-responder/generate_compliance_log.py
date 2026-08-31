"""
Generate compliance checks log for dashboard visualization.

This extracts compliance check results from evaluation runs and formats them
for the ComplianceGateVisualizer component.
"""

import json
from pathlib import Path
from datetime import datetime

def generate_compliance_checks_log():
    """Generate compliance checks from baseline comparison results."""

    baseline_path = Path("output/baseline_comparison.json")
    output_path = Path("output/compliance_checks.json")

    if not baseline_path.exists():
        print("Error: baseline_comparison.json not found. Run baseline_comparison.py first.")
        return

    with open(baseline_path, 'r') as f:
        data = json.load(f)

    checks = []

    # Extract compliance checks from comparison results
    for result in data.get('comparison_results', []):
        question_id = result['question_id']
        timestamp = datetime.now().isoformat()

        # Check for naive LLM hallucinations (simulating what compliance gate would catch)
        for hallucination in result.get('naive_hallucinations', []):
            rule_id = 'unknown'
            rule_name = hallucination
            keywords = []

            if 'FedRAMP' in hallucination:
                rule_id = 'no_fedramp'
                rule_name = 'No FedRAMP Certification Claims'
                keywords = ['fedramp']
            elif 'HIPAA' in hallucination:
                rule_id = 'no_hipaa'
                rule_name = 'No HIPAA Compliance Claims'
                keywords = ['hipaa']
            elif 'HITRUST' in hallucination:
                rule_id = 'no_hitrust'
                rule_name = 'No HITRUST Certification Claims'
                keywords = ['hitrust']
            elif 'BYOK' in hallucination or 'CMEK' in hallucination:
                rule_id = 'no_byok'
                rule_name = 'No Customer-Managed Encryption Keys'
                keywords = ['byok', 'cmek']
            elif 'on-premise' in hallucination or 'self-hosted' in hallucination:
                rule_id = 'no_on_premise'
                rule_name = 'No On-Premise Deployment Claims'
                keywords = ['on-premise', 'self-hosted']

            checks.append({
                'rule_id': rule_id,
                'rule_name': rule_name,
                'status': 'failed',
                'keywords_found': keywords,
                'timestamp': timestamp,
                'question_id': question_id
            })

        # System checks (all passed since system_hallucinations is empty)
        if result['system_status'] == 'approved':
            checks.append({
                'rule_id': 'groundedness_check',
                'rule_name': 'Groundedness Verification',
                'status': 'passed',
                'keywords_found': [],
                'timestamp': timestamp,
                'question_id': question_id
            })

    output_data = {
        'checks': checks,
        'generated_at': datetime.now().isoformat(),
        'total_checks': len(checks)
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Generated {len(checks)} compliance checks")
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    generate_compliance_checks_log()
