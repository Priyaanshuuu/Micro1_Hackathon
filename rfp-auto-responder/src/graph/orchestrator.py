"""
LangGraph Orchestrator: Wires agents into a state graph with retry logic.

Flow:
    Searcher → Drafter → Compliance → Router

Router decisions:
    - verdict.passed → status="approved", END
    - verdict failed + retry_count < MAX → increment retry, back to Searcher
    - verdict failed + retry_count >= MAX → status="escalated", END
"""

import os
from typing import Literal

from dotenv import load_dotenv
from langgraph.graph import END, StateGraph

from src.agents.compliance import compliance_node
from src.agents.drafter import drafter_node
from src.agents.searcher import searcher_node
from src.types import Attempt, RFPState

load_dotenv()


def record_attempt_node(state: RFPState) -> dict:
    """
    Record the current attempt in the history before routing.

    This runs after compliance check and captures the full attempt.
    """
    attempt = Attempt(
        attempt_number=state["retry_count"] + 1,
        search_query=state["search_query"],
        retrieved_chunks=state["retrieved_chunks"],
        answer=state["answer"],
        verdict=state["verdict"],
    )

    return {"attempts": [attempt]}


def router_node(state: RFPState) -> dict:
    """
    Routing logic: approve, retry, or escalate.

    Returns updated retry_count and status.
    """
    verdict = state["verdict"]
    retry_count = state["retry_count"]
    max_retries = int(os.getenv("MAX_COMPLIANCE_RETRIES", "2"))

    if verdict.passed:
        # Success - approve and end
        return {"status": "approved"}

    # Failed compliance check
    if retry_count < max_retries:
        # Retry with feedback
        return {"retry_count": retry_count + 1}
    else:
        # Exhausted retries - escalate to human
        return {"status": "escalated"}


def should_retry(state: RFPState) -> Literal["retry", "end"]:
    """
    Conditional edge: determine if we retry or end.
    """
    status = state["status"]

    if status in ["approved", "escalated"]:
        return "end"
    else:
        return "retry"


def build_graph():
    """
    Build and compile the RFP processing graph.
    """
    workflow = StateGraph(RFPState)

    # Add nodes
    workflow.add_node("searcher", searcher_node)
    workflow.add_node("drafter", drafter_node)
    workflow.add_node("compliance", compliance_node)
    workflow.add_node("record_attempt", record_attempt_node)
    workflow.add_node("router", router_node)

    # Linear flow through agents
    workflow.set_entry_point("searcher")
    workflow.add_edge("searcher", "drafter")
    workflow.add_edge("drafter", "compliance")
    workflow.add_edge("compliance", "record_attempt")
    workflow.add_edge("record_attempt", "router")

    # Conditional edge from router
    workflow.add_conditional_edges(
        "router",
        should_retry,
        {
            "retry": "searcher",  # Loop back for retry
            "end": END,
        },
    )

    return workflow.compile()
