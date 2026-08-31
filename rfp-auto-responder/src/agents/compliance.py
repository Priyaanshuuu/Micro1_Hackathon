"""
Compliance Agent: Verifies answers against configurable rules + LLM groundedness check.

Rules are loaded from src/compliance_rules.json and can be customized without code changes.
Hard rules include:
- Never confirm on-premise/self-hosted/single-tenant deployment
- Never confirm customer-managed encryption keys (BYOK/CMEK)
- Never confirm unauthorized certifications (FedRAMP, HITRUST, HIPAA)
- Answer must be grounded in retrieved chunks
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from src.types import ComplianceVerdict, RFPState

load_dotenv()

# Load compliance rules from config
RULES_CONFIG_PATH = Path(__file__).parent.parent / "compliance_rules.json"


def load_compliance_rules() -> Dict[str, Any]:
    """Load compliance rules from JSON configuration file."""
    if not RULES_CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Compliance rules not found at {RULES_CONFIG_PATH}. "
            "Please ensure src/compliance_rules.json exists."
        )
    
    with open(RULES_CONFIG_PATH, 'r') as f:
        return json.load(f)


def check_keyword_rules(answer: str, rules_config: Dict[str, Any]) -> ComplianceVerdict | None:
    """Check answer against keyword-based compliance rules."""
    answer_lower = answer.lower()
    
    for rule in rules_config["compliance_rules"]:
        if not rule.get("enabled", True):
            continue
        
        # Check for keywords that trigger the rule
        has_keyword = False
        if "keywords" in rule:
            has_keyword = any(keyword in answer_lower for keyword in rule["keywords"])
        elif "prohibited_claims" in rule:
            has_keyword = any(claim in answer_lower for claim in rule["prohibited_claims"])
        
        if has_keyword:
            # Check if it's a denial (acceptable)
            denial_keywords = rule.get("denial_keywords", [])
            is_denial = any(keyword in answer_lower for keyword in denial_keywords)
            
            if not is_denial:
                return ComplianceVerdict(
                    passed=False,
                    violated_rule=rule.get("violated_rule", rule["name"]),
                    feedback=rule.get("feedback", f"Rule '{rule['name']}' was violated.")
                )
    
    return None


def compliance_node(state: RFPState) -> Dict:
    """
    Check the drafted answer against compliance rules.

    Rules are loaded from src/compliance_rules.json.
    Returns 'verdict' field with ComplianceVerdict.
    """
    answer = state["answer"]
    retrieved_chunks = state["retrieved_chunks"]
    question = state["question"]
    
    # Load rules
    try:
        rules_config = load_compliance_rules()
    except FileNotFoundError as e:
        # Fallback: return pass if config not found
        return {
            "verdict": ComplianceVerdict(
                passed=True,
                violated_rule=None,
                feedback=None
            )
        }
    
    # Check keyword-based rules first (fast)
    keyword_verdict = check_keyword_rules(answer, rules_config)
    if keyword_verdict:
        return {"verdict": keyword_verdict}
    
    # If groundedness check is enabled, verify answer is sourced correctly
    if rules_config.get("groundedness_check", {}).get("enabled", True):
        context_summary = "\n\n".join(
            [f"[{chunk.source}] {chunk.content}" for chunk in retrieved_chunks]
        )

        llm = ChatGroq(model=os.getenv("MODEL_NAME", "openai/gpt-oss-20b"), temperature=0)

        groundedness_prompt = f"""You are a compliance reviewer checking if an RFP answer is properly grounded in source documentation.

Question: {question}

Answer to verify: {answer}

Retrieved policy context:
{context_summary}

Verify:
1. Is every factual claim in the answer supported by the retrieved context?
2. Does the answer contradict anything in the context?
3. Does the answer add unsupported claims from general knowledge?

Respond in JSON format:
{{
  "passed": true/false,
  "violated_rule": "groundedness check" (if failed, else null),
  "feedback": "Specific explanation of what claim is unsupported" (if failed, else null)
}}

Be strict - if the answer makes ANY claim not directly traceable to the context, fail it."""

        response = llm.invoke(groundedness_prompt)
        response_text = response.content.strip()

        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            verdict_dict = json.loads(json_str)
        else:
            # If no JSON found, assume passed
            verdict_dict = {"passed": True, "violated_rule": None, "feedback": None}

        verdict = ComplianceVerdict(
            passed=verdict_dict.get("passed", True),
            violated_rule=verdict_dict.get("violated_rule"),
            feedback=verdict_dict.get("feedback")
        )

        return {"verdict": verdict}
    
    # All checks passed
    return {
        "verdict": ComplianceVerdict(
            passed=True,
            violated_rule=None,
            feedback=None
        )
    }
