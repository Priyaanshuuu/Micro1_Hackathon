"""
Shared type definitions for the RFP Auto-Responder agent graph.

Every agent (Searcher, Drafter, Compliance) and the LangGraph orchestrator
read from and write to a single shared `RFPState`. Keeping every field
definition in one place means they all agree on the same shape, and
extending a node later doesn't risk silently drifting the schema.
"""

from __future__ import annotations

import operator
from typing import Annotated, List, Literal, Optional, TypedDict

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------
# Structured sub-objects
# --------------------------------------------------------------------------


class RetrievedChunk(BaseModel):
    """A single chunk of policy text returned by the vector store."""

    content: str = Field(..., description="The raw policy text for this chunk.")
    source: str = Field(..., description="Filename or identifier of the source policy document.")
    score: float = Field(..., description="Similarity score from the vector store (higher is more relevant).")


class ComplianceVerdict(BaseModel):
    """Structured output produced by the Compliance Agent's verification call."""

    passed: bool = Field(..., description="True if the answer violates no compliance rule.")
    violated_rule: Optional[str] = Field(
        default=None,
        description="The specific rule that was violated, if any (e.g. 'no on-premise hosting claims').",
    )
    feedback: Optional[str] = Field(
        default=None,
        description=(
            "Actionable feedback explaining the violation, folded into the next "
            "Searcher query on retry. None when passed is True."
        ),
    )


class Attempt(BaseModel):
    """One complete draft-and-check attempt for a question, kept for audit history."""

    attempt_number: int = Field(..., description="1 for the first try, 2+ for each retry.")
    search_query: str
    retrieved_chunks: List[RetrievedChunk] = Field(default_factory=list)
    answer: str
    verdict: ComplianceVerdict


# --------------------------------------------------------------------------
# Graph state
# --------------------------------------------------------------------------

QuestionStatus = Literal["pending", "approved", "escalated"]


class RFPState(TypedDict):
    """
    The state object threaded through every node in the LangGraph graph.

    Each node returns only the fields it updates; LangGraph merges that into
    the running state. `attempts` uses an `operator.add` reducer so every
    retry appends to the history instead of overwriting the previous one.
    """

    # Set once when the graph run starts; never mutated afterward.
    question_id: str
    question: str

    # Rewritten by the Searcher on every attempt — on retries, this reflects
    # the prior compliance feedback rather than repeating the original query.
    search_query: str
    retrieved_chunks: List[RetrievedChunk]

    # Rewritten by the Drafter on every attempt.
    answer: str

    # Rewritten by the Compliance Agent on every attempt. None until the
    # first check has run.
    verdict: Optional[ComplianceVerdict]

    # Owned by the router: retries used so far, and the question's terminal
    # state once the graph finishes.
    retry_count: int
    status: QuestionStatus

    # Full history of every attempt — most useful once a question escalates
    # to the Human Review Queue.
    attempts: Annotated[List[Attempt], operator.add]


# --------------------------------------------------------------------------
# CSV row shapes, used by main.py to read input and write output
# --------------------------------------------------------------------------


class RFPQuestionRow(BaseModel):
    """One row of the input RFP spreadsheet."""

    question_id: str
    question: str


class RFPResponseRow(BaseModel):
    """One row of the output responses CSV."""

    question_id: str
    question: str
    answer: str
    status: QuestionStatus
    source_citations: str = Field(..., description="Semicolon-separated source policy filenames cited.")
    retries: int