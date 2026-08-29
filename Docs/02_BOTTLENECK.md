# What Bottleneck Makes This Worth Solving?

## The Manual Process Today
1. An RFP arrives as a spreadsheet — anywhere from 50 to 300+ rows, mixing commercial, technical, and security questions.
2. A Proposal Manager triages it and forwards batches of rows to whichever Sales Engineer or SME "probably knows this."
3. Each SME searches their own scattered sources: old proposals, an internal wiki, Slack history, the actual SOC2 report PDF, or their own memory of what was true six months ago.
4. Answers get pasted back into the spreadsheet with no consistent format, no citation, and no re-check against current policy.
5. A reviewer, if there's time, skims the completed sheet before it goes out.

## Three Concrete Bottlenecks

### 1. Manual Search Over Tribal Knowledge
The correct answer to "Do you support on-premise deployment?" or "What's your data retention policy for deleted accounts?" is almost always already written down — in a policy doc, a past RFP, or a SOC2 report. The bottleneck isn't knowledge creation, it's **finding the right paragraph fast**, and that currently depends on one person's memory of where things live.

### 2. Risk of Wrong Compliance Promises
Because answers are hand-written under deadline pressure, it's easy to accidentally:
- Promise a capability the product doesn't have (e.g., confirming on-premise hosting for a cloud-only product).
- Cite an expired or incorrect certification.
- Contradict what a different SME told a different prospect last month.

A wrong answer here is worse than a slow one: it can become a **contractual commitment**, and discovering the contradiction during a security audit or breach investigation is far more expensive than the extra hour it would have taken to verify the answer up front.

### 3. Slow Turnaround Against Fixed Deadlines
RFP response windows are typically fixed by the prospect (3–10 business days) and non-negotiable. Time lost to internal routing and SME availability directly limits how many deals a team can respond to in parallel, and a late or incomplete response can eliminate a vendor from consideration regardless of the answers' quality.

## Why Naive Automation Doesn't Fix This
Pasting each question into a generic chat LLM is faster than manual search, but reintroduces the exact risk this workflow can't afford:
- No grounding in a current policy source → confident-sounding hallucinations.
- No verification step → nothing catches an answer that contradicts policy before a human sees it.
- No audit trail → a reviewer can't tell *why* the model said what it said, so they end up re-verifying everything anyway — which erases the time savings.

## The Asymmetry That Justifies This Project
| | Slow, correct answer | Fast, wrong answer |
|---|---|---|
| **Cost** | A missed deadline — bad, but recoverable | Contractual or legal exposure, lost trust — bad, sometimes unrecoverable |

Because the downside of a wrong answer is structurally worse than the downside of a slow one, automation here is only worth shipping if it has a **verification gate** and a **safe escalation path** — the core design bet of this project.

---
**Related:** `01_USER_AND_PROBLEM.md` · `03_AGENT_EVALUATION.md` · `04_REPRODUCIBILITY.md`
