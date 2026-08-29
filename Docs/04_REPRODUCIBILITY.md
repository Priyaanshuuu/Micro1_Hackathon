# Reproducibility — Environment Setup & Running the Demo

## Prerequisites
- **Node.js** ≥ 18.x and **npm** ≥ 9.x — check with `node -v` and `npm -v`.
- An **OpenAI API key** with access to a chat-completions-capable model.
- No external database or paid vector store required — everything runs against an in-process local vector store, so there's nothing else to provision.

## Key Dependencies
| Package | Role |
|---|---|
| `@langchain/langgraph` | Defines the agent state graph — nodes, edges, and the retry/escalation routing logic. |
| `@langchain/openai` | LLM calls (drafting, compliance checks) and embeddings (indexing + retrieval). |
| `MemoryVectorStore` / `HNSWLib` | Local vector store holding the synthetic SOC2/InfoSec policy corpus — no external service needed. |
| `papaparse` | Parses the input RFP CSV and writes the output response CSV. |

## Project Structure (Target Layout)
```
rfp-auto-responder/
├── docs/                        # This documentation set
├── data/
│   └── policies/                # Synthetic SOC2 / InfoSec policy source documents
├── samples/
│   └── sample_rfp.csv           # Small synthetic RFP question set for demo/testing
├── src/
│   ├── agents/
│   │   ├── searcher.ts
│   │   ├── drafter.ts
│   │   └── compliance.ts
│   ├── graph/
│   │   └── orchestrator.ts      # LangGraph state graph wiring the agents together
│   ├── ingest/
│   │   └── buildVectorStore.ts  # One-time script to embed data/policies into the vector store
│   ├── types.ts
│   └── index.ts                 # CLI entrypoint
├── output/                      # Generated at runtime: responses + human review queue
├── .env.example
├── package.json
└── tsconfig.json
```
*This is the target structure we'll build toward file-by-file in Step 2 — exact filenames may be refined slightly as we go, and this doc will be kept in sync.*

## Environment Variables
Copy `.env.example` to `.env` and fill in your key:
```
OPENAI_API_KEY=sk-...
MODEL_NAME=gpt-4o-mini
MAX_COMPLIANCE_RETRIES=2
```

## Install
```bash
git clone <this-repo>
cd rfp-auto-responder
npm install
cp .env.example .env   # then paste in your OPENAI_API_KEY
```

## Step 1 — Build the Vector Store
Embeds the synthetic policy documents in `data/policies/` into a local vector index:
```bash
npm run ingest
```
**Expected output:** a log line confirming how many policy chunks were embedded and indexed.

## Step 2 — Run the Pipeline Against a Sample RFP
```bash
npm run start -- --input samples/sample_rfp.csv --output output/responses.csv
```
**Expected output:**
- `output/responses.csv` — one row per input question, with columns: `question`, `answer`, `status` (`approved` / `escalated`), `source_citations`, `retries`.
- `output/human_review_queue.csv` — present only if at least one question escalated; contains the question, both drafted attempts, and the specific compliance objection for each.
- A console trace showing each question moving through **Searcher → Drafter → Compliance Agent**, including any retry loops and the feedback that triggered them.

## Verifying Success
- Every row in `samples/sample_rfp.csv` should appear exactly once in `output/responses.csv`.
- `npm test` runs the rubric-graded eval set described in `03_AGENT_EVALUATION.md` against the sample corpus and prints the score distribution and false-pass rate.

## Troubleshooting
| Symptom | Likely Cause |
|---|---|
| `OPENAI_API_KEY is not set` | `.env` wasn't created, or isn't in the project root. |
| Empty or irrelevant retrievals | `npm run ingest` wasn't (re-)run after changing files in `data/policies/`. |
| Every question escalates | `MAX_COMPLIANCE_RETRIES` is too low, or the Compliance Agent's rules are stricter than the synthetic policy corpus can satisfy. |
| Rate-limit errors on a large CSV | Reduce the batch size or add a small delay between requests — configurable in the CLI entrypoint once we build it in Step 2. |

---
**Related:** `01_USER_AND_PROBLEM.md` · `02_BOTTLENECK.md` · `03_AGENT_EVALUATION.md`
