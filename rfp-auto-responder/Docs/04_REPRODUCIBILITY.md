# Reproducibility — Environment Setup & Running the Demo

## Prerequisites
- **Python** ≥ 3.10 — check with `python --version`.
- An **OpenAI API key** with access to a chat-completions-capable model.
- No external database or paid vector store required — everything runs against an in-process local vector store, so there's nothing else to provision.

## Key Dependencies
| Package | Role |
|---|---|
| `langgraph` | Defines the agent state graph — nodes, edges, and the retry/escalation routing logic. |
| `langchain-openai` | LLM calls (drafting, compliance checks) and embeddings (indexing + retrieval). |
| `langchain-core` | Core LangChain primitives for RAG and vector stores. |
| `pandas` | Parses the input RFP CSV and writes the output response CSV. |
| `pydantic` | Type validation and structured output parsing. |

## Project Structure (Target Layout)
```
rfp-auto-responder/
├── Docs/                        # This documentation set
├── data/
│   └── policies/                # Synthetic SOC2 / InfoSec policy source documents
├── samples/
│   └── sample_rfp.csv           # Small synthetic RFP question set for demo/testing
├── src/
│   ├── agents/
│   │   ├── searcher.py
│   │   ├── drafter.py
│   │   └── compliance.py
│   ├── graph/
│   │   └── orchestrator.py      # LangGraph state graph wiring the agents together
│   ├── ingest/
│   │   └── build_vector_store.py  # One-time script to embed data/policies into the vector store
│   ├── types.py
│   └── main.py                  # CLI entrypoint
├── output/                      # Generated at runtime: responses + human review queue
├── .env
├── requirements.txt
└── README.md
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
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
# Create .env and add your OPENAI_API_KEY
```

## Step 1 — Build the Vector Store
Embeds the synthetic policy documents in `data/policies/` into a local vector index:
```bash
python -m src.ingest.build_vector_store
```
**Expected output:** a log line confirming how many policy chunks were embedded and indexed.

## Step 2 — Run the Pipeline Against a Sample RFP
```bash
python -m src.main --input samples/sample_rfp.csv --output output/responses.csv
```
**Expected output:**
- `output/responses.csv` — one row per input question, with columns: `question`, `answer`, `status` (`approved` / `escalated`), `source_citations`, `retries`.
- `output/human_review_queue.csv` — present only if at least one question escalated; contains the question, both drafted attempts, and the specific compliance objection for each.
- A console trace showing each question moving through **Searcher → Drafter → Compliance Agent**, including any retry loops and the feedback that triggered them.

## Verifying Success
- Every row in `samples/sample_rfp.csv` should appear exactly once in `output/responses.csv`.
- `python -m pytest tests/` runs the rubric-graded eval set described in `03_AGENT_EVALUATION.md` against the sample corpus and prints the score distribution and false-pass rate.

## Troubleshooting
| Symptom | Likely Cause |
|---|---|
| `OPENAI_API_KEY is not set` | `.env` wasn't created, or isn't in the project root. |
| Empty or irrelevant retrievals | `python -m src.ingest.build_vector_store` wasn't (re-)run after changing files in `data/policies/`. |
| Every question escalates | `MAX_COMPLIANCE_RETRIES` is too low, or the Compliance Agent's rules are stricter than the synthetic policy corpus can satisfy. |
| Rate-limit errors on a large CSV | Reduce the batch size or add a small delay between requests — configurable in the CLI entrypoint once we build it in Step 2. |
| Import errors | Ensure virtual environment is activated and all dependencies installed. |

---
**Related:** `01_USER_AND_PROBLEM.md` · `02_BOTTLENECK.md` · `03_AGENT_EVALUATION.md`
