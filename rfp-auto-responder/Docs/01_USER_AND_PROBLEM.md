# Who Has This Problem? — Users & Problem Statement

## Executive Summary
Enterprise B2B sales cycles increasingly gate on security and compliance questionnaires — RFPs, RFIs, and vendor due-diligence (DDQ) forms — before a deal can move forward. Answering these accurately, consistently, and quickly is a distinct, high-stakes workflow that sits at the intersection of sales, security, and legal. The **Enterprise RFP Auto-Responder** targets the people who own that workflow today.

## Primary Personas

### 1. Sales Engineer / Solutions Consultant — Primary User
- **Role:** Owns the technical sections of inbound RFPs; is the first person handed a 50–300 row spreadsheet with a hard deadline.
- **Pain today:** Spends hours per RFP hunting through old proposals, internal wikis, Slack threads, and SOC2 reports for an answer that was "already written somewhere."
- **What they need:** A drafted, source-grounded first-pass answer for every question, with a clear flag on anything that isn't safe to send without a second look.

### 2. Security & Compliance (InfoSec) Reviewer
- **Role:** The final check on any answer touching certifications, data residency, encryption, subprocessors, or hosting model.
- **Pain today:** Gets pulled into deals reactively, often reviewing under deadline pressure, with no easy way to see *why* an answer was written the way it was.
- **What they need:** An audit trail — which policy an answer is grounded in — plus a gate that already rejected anything contradicting stated policy before it reaches them.

### 3. RevOps / Proposal Manager
- **Role:** Owns the end-to-end RFP process across several simultaneous deals.
- **Pain today:** Manually routes questions to subject-matter experts across teams and chases answers down before the deadline.
- **What they need:** Throughput — most of the spreadsheet answered automatically and correctly, with only the genuinely ambiguous or high-risk rows needing a human.

### Secondary Stakeholder: Legal / Contracts
Not a direct user of the tool, but a downstream consumer of its output — a wrong compliance claim in an RFP response can become a contractual commitment. This is why the verification gate and human-escalation path exist at all.

## Core Problem Statement
> Technical and security teams at B2B software companies repeatedly answer the same category of high-stakes questions — under time pressure, from scattered sources, with no consistent verification step — and a wrong answer can create real legal and commercial risk.

## Why Now
- Security questionnaires have grown in length and frequency as SOC2 / ISO 27001 / data-residency requirements have become standard procurement gates rather than exceptions.
- The underlying knowledge (policies, past answers) is usually already written down — the bottleneck is **retrieval and verification**, not knowledge creation, which is exactly the shape of problem a multi-agent RAG pipeline is suited to.

## Out of Scope (Non-Goals)
- Negotiating commercial or legal contract terms.
- Replacing a human compliance sign-off on the final submission — the goal is to shrink the number of rows that need one.
- General-purpose document Q&A — this is scoped to structured RFP question lists against a defined policy corpus.

---
**Related:** `02_BOTTLENECK.md` · `03_AGENT_EVALUATION.md` · `04_REPRODUCIBILITY.md`
