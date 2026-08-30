"""
Compliance Agent: Verifies answers against hard rules + LLM groundedness check.

Hard rules derived from policy documents:
- Never confirm on-premise/self-hosted/single-tenant deployment
- Never confirm customer-managed encryption keys (BYOK/CMEK)
- Never confirm FedRAMP, HITRUST, or HIPAA compliance
- Answer must be grounded in retrieved chunks
"""

import json
import os
import re
from typing import Dict

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from src.types import ComplianceVerdict, RFPState

load_dotenv()


def compliance_node(state: RFPState) -> Dict:
    """
    Check the drafted answer against compliance rules.

    Returns 'verdict' field with ComplianceVerdict.
    """
    answer = state["answer"]
    retrieved_chunks = state["retrieved_chunks"]
    question = state["question"]

    # Fast deterministic keyword checks for prohibited claims
    answer_lower = answer.lower()

    # Rule 1: No on-premise/self-hosted/single-tenant claims
    if any(
        term in answer_lower
        for term in [
            "on-premise",
            "on premise",
            "self-hosted",
            "self hosted",
            "single-tenant",
            "single tenant",
            "dedicated environment",
            "private cloud",
        ]
    ):
        # Check if it's a denial vs confirmation
        denial_indicators = [
            "do not offer",
            "not support",
            "not available",
            "not provide",
            "exclusively",
            "multi-tenant only",
        ]
        if not any(indicator in answer_lower for indicator in denial_indicators):
            return {
                "verdict": ComplianceVerdict(
                    passed=False,
                    violated_rule="no on-premise deployment claims",
                    feedback="The answer suggests on-premise/self-hosted deployment support. Our platform is multi-tenant SaaS only - we do not offer on-premise, self-hosted, or single-tenant deployments.",
                )
            }

    # Rule 2: No customer-managed encryption key claims
    if any(
        term in answer_lower
        for term in [
            "byok",
            "bring your own key",
            "cmek",
            "customer-managed key",
            "customer managed key",
            "customer-provided key",
        ]
    ):
        denial_indicators = [
            "do not support",
            "not support",
            "not available",
            "aws-managed",
            "provider-managed",
        ]
        if not any(indicator in answer_lower for indicator in denial_indicators):
            return {
                "verdict": ComplianceVerdict(
                    passed=False,
                    violated_rule="no BYOK/CMEK support claims",
                    feedback="The answer suggests customer-managed encryption key support. We use AWS-managed KMS keys only - customer-managed keys (BYOK/CMEK) are not supported.",
                )
            }

    # Rule 3: No unauthorized certifications
    prohibited_certs = ["fedramp", "hitrust", "hipaa"]
    for cert in prohibited_certs:
        if cert in answer_lower:
            # Check if it's explicitly denied
            denial_indicators = [
                "not certified",
                "do not hold",
                "not currently certified",
                "not hipaa compliant",
            ]
            if not any(indicator in answer_lower for indicator in denial_indicators):
                return {
                    "verdict": ComplianceVerdict(
                        passed=False,
                        violated_rule=f"no {cert.upper()} certification claims",
                        feedback=f"The answer suggests {cert.upper()} certification. We are NOT certified for {cert.upper()}. Only claim certifications we actually hold: SOC 2 Type II and ISO 27001.",
                    )
                }

    # LLM-based groundedness check
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
