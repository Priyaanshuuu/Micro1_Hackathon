# Does the Agent Solve It Well? — Evaluation Methodology

## Evaluation Goals
In order of importance:
1. Does the pipeline ever let a **non-compliant answer through** the gate? This is the metric that matters most — a single miss here is worse than many escalations.
2. Of the answers it approves without escalation, how many are actually **correct and well-supported**?
3. How much manual work does it actually remove — what fraction of rows reach a human queue versus resolve automatically?

## Baseline for Comparison
**Baseline:** a single LLM call per question, no retrieval and no verification — the "paste the question into a chat model" approach most teams reach for first.

**Our system:** Orchestrator → Searcher (vector retrieval over the synthetic SOC2/InfoSec policy corpus) → Drafter (answers strictly from retrieved context) → Compliance Agent (rule-based + LLM verification gate) → Routing (approve / retry with feedback / escalate after 2 retries).

The baseline is expected to produce fluent, confident answers with no way to tell which ones are actually grounded in current policy — that gap is exactly what this project measures.

## Grading Rubric (0–3 per Answer)

| Score | Label | Definition |
|---|---|---|
| **0** | Incorrect / Unsupported | Wrong, contradicts policy, or fabricated with no basis in retrieved context. |
| **1** | Partially Correct | Directionally right but missing a material detail, hedged into uselessness, or answers a slightly different question than asked. |
| **2** | Correct, Uncited | Factually correct and compliant, but doesn't reference which policy it's grounded in — a reviewer would still have to go verify it. |
| **3** | Correct, Cited, Compliant | Correct, references the specific source passage, and passes the Compliance Agent's gate. |

Scores are assigned per-question against a hand-written golden answer set. We report the **distribution**, not just the average — a system that scores mostly 3s with a couple of 0s hiding inside a good average is exactly the failure mode this project exists to prevent.

## Metrics We Report
- **Average rubric score** and **% of answers scoring 3**.
- **Hallucination rate** — answers not traceable to any retrieved passage.
- **False-pass rate** — non-compliant answers the gate incorrectly approved. Target: 0 on the synthetic eval set; this is the single most important number in the project.
- **Escalation rate** — % of questions that exhaust retries and reach the Human Review Queue.
- **Average retries per resolved question.**
- **Latency and token cost per question** — a pipeline that's accurate but too slow or expensive to run on a 300-row RFP isn't a practical win.

## Failure Handling, Step by Step
1. **Drafter** produces an answer strictly from what the **Searcher** retrieved.
2. **Compliance Agent** checks it against hard rules (e.g., "never confirm on-premise hosting," "never cite a certification not on the approved list") plus a general groundedness check.
3. **On failure:** the specific rule violated and a reason are attached to the graph state as feedback, and routing sends the question back to the **Searcher** with that feedback folded into the next retrieval query — so a second attempt is a narrower, informed search, not a blind repeat of the first.
4. **After 2 failed retries**, the question, both prior attempts, and the compliance feedback are pushed to the **Human Review Queue** instead of being forced through or silently dropped.

## The Human Review Queue Is a Success Path, Not a Failure State
An escalation is the system correctly recognizing the limits of its own retrieved context — the intended behavior for a question the policy corpus genuinely doesn't answer well, not a bug. We evaluate the queue itself on whether it carries enough context (both failed drafts plus the specific compliance objection) for a human to resolve the row quickly, rather than starting from zero.

## Illustrative Example
- **Question:** "Do you support customer-managed encryption keys (BYOK) for data at rest?"
- **Baseline (naive LLM):** Answers confidently in the affirmative — plausible-sounding, ungrounded, and wrong if BYOK isn't actually supported. **Rubric score: 0.**
- **Our pipeline:** Searcher retrieves the encryption-at-rest policy section stating AES-256 with provider-managed keys only; Drafter answers accordingly and cites the section; Compliance Agent confirms no prohibited claim was made. **Rubric score: 3.**

---
**Related:** `01_USER_AND_PROBLEM.md` · `02_BOTTLENECK.md` · `04_REPRODUCIBILITY.md`
