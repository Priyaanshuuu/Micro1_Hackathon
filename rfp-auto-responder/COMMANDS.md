# 🚀 RFP Auto-Responder - Commands Guide

Complete guide for running and testing the RFP Auto-Responder system.

---

## **Prerequisites**

- Python 3.8+
- Node.js 16+ (for dashboard)
- pip and npm installed
- Git installed

---

## **1. Initial Setup**

### Clone and Navigate
```bash
cd rfp-auto-responder
```

### Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Configure Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys
# Required: GROQ_API_KEY
```

---

## **2. Build Vector Store**

Build the local vector store from policy documents:

```bash
python -m src.ingest
```

**Expected Output:**
```
Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
Found 4 policy files
  data_security_and_hosting.md: 12 chunks
  compilance_certificates.md: 8 chunks
  access_control_and_incident_response.md: 15 chunks
  data_retention_and_deletion.md: 10 chunks

Total chunks: 45
Embedding chunks (using local HuggingFace model)...
Vector store saved to data/vector_store.json
```

**Generated Files:**
- `data/vector_store.json` (~200KB)

---

## **3. Run Single Question Test**

Test the system with a single RFP question:

```bash
python -c "
from src.graph.orchestrator import build_graph
from src.types import RFPState

graph = build_graph()
state = {
    'question_id': 'TEST001',
    'question': 'What encryption standard do you use for data at rest?',
    'search_query': '',
    'retrieved_chunks': [],
    'answer': '',
    'verdict': None,
    'retry_count': 0,
    'status': 'pending',
    'attempts': []
}

result = graph.invoke(state)

print('Question:', result['question'])
print('\nAnswer:', result['answer'])
print('\nStatus:', result['status'])
print('Retries:', result['retry_count'])
print('Sources:', set([c.source for c in result['retrieved_chunks']]))
"
```

---

## **4. Run Baseline Comparison**

Compare naive LLM vs full system on 10 golden questions:

```bash
python baseline_comparison.py
```

**Duration:** 5-10 minutes (makes multiple LLM calls)

**Expected Output:**
```
======================================================================
RFP AUTO-RESPONDER: BASELINE COMPARISON
======================================================================

Comparing:
  [BASELINE] Naive LLM (no RAG, no compliance gate)
  [SYSTEM]   RFP Auto-Responder (full pipeline)

Running comparison on 10 questions...

[1/10] Q001: What encryption standard do you use for data at re...
  -> Naive LLM... Done (2.3s, score=0)
  -> System... Done (15.8s, score=3, status=approved)

...

SUMMARY
======================================================================
Naive Hallucination Rate:  60.0%
System Hallucination Rate: 0.0%

Naive False-Pass Rate:     0.0%
System False-Pass Rate:    0.0%

Average Score Improvement: +1.7 (0.5 → 2.2)

✓ Results saved to:
  - output/baseline_comparison.json
  - output/baseline_report.txt
```

**Generated Files:**
- `output/baseline_comparison.json` (~40KB)
- `output/baseline_report.txt` (detailed report)

---

## **5. Generate Dashboard Data**

Create compliance checks and retry flows for dashboard:

```bash
python generate_compliance_log.py
python generate_retry_flows.py
```

**Expected Output:**
```
Generated 20 compliance checks
Saved to: output/compliance_checks.json

Generated 7 retry flows
Saved to: output/retry_flows.json
```

**Generated Files:**
- `output/compliance_checks.json`
- `output/retry_flows.json`

---

## **6. Run Evaluation Suite**

Run full evaluation against golden answers:

```bash
python tests/evaluation.py
```

**Expected Output:**
```
Running evaluation on 10 golden questions...

Results saved to: output/evaluation_results.json
Average Score: 2.2/3.0
Hallucination Rate: 0%
```

**Generated Files:**
- `output/evaluation_results.json`

---

## **7. Start Dashboard**

### Install Frontend Dependencies (First Time Only)
```bash
cd ../frontend
npm install
```

### Start Development Server
```bash
npm run dev
```

**Expected Output:**
```
✓ Ready on http://localhost:3000
```

**Open in Browser:**
```
http://localhost:3000
```

---

## **8. Process CSV Input (Batch Mode)**

Process a CSV file with multiple RFP questions:

```bash
python -m src.main --input samples/sample_rfp.csv --output output/responses.csv
```

**Expected Output:**
```
Processing 15 questions from samples/sample_rfp.csv...
[1/15] Q001: What encryption standard...
[2/15] Q002: Do you support on-premise...
...
✓ Responses saved to: output/responses.csv
✓ Human review queue saved to: output/human_review_queue.csv
```

**Generated Files:**
- `output/responses.csv` (all answers)
- `output/human_review_queue.csv` (escalated questions)

---

## **9. Naive LLM Demo (For Video)**

### Quick Single Question
```bash
python quick_naive_demo.py "Are you FedRAMP authorized?"
```

### Interactive Multi-Question Demo
```bash
python naive_llm_demo.py
```

---

## **10. View Results**

### View Baseline Comparison Summary
```bash
cat output/baseline_report.txt | head -50
```

### View JSON Results
```bash
# Pretty print baseline comparison
python -c "import json; print(json.dumps(json.load(open('output/baseline_comparison.json')), indent=2))" | head -100

# View aggregate metrics only
python -c "import json; data=json.load(open('output/baseline_comparison.json')); print('Metrics:', json.dumps(data['aggregate_metrics'], indent=2))"
```

### View Generated Responses
```bash
cat output/responses.csv
```

### View Human Review Queue
```bash
cat output/human_review_queue.csv
```

---

## **Testing Checklist**

Run these commands in order to verify everything works:

```bash
# ✅ 1. Build vector store
python -m src.ingest

# ✅ 2. Run baseline comparison
python baseline_comparison.py

# ✅ 3. Generate dashboard data
python generate_compliance_log.py
python generate_retry_flows.py

# ✅ 4. Run evaluation
python tests/evaluation.py

# ✅ 5. Test batch processing
python -m src.main --input samples/sample_rfp.csv --output output/responses.csv

# ✅ 6. Start dashboard
cd ../frontend && npm run dev
# Open http://localhost:3000 in browser

# ✅ 7. Test naive LLM (demo)
python quick_naive_demo.py "Are you FedRAMP authorized?"
```

---

## **Troubleshooting**

### Vector Store Not Found
```bash
# Error: "Vector store not found at data/vector_store.json"
# Solution: Run ingestion first
python -m src.ingest
```

### API Key Issues
```bash
# Error: "GROQ_API_KEY not set"
# Solution: Check .env file
cat .env | grep GROQ_API_KEY

# Make sure it's not the placeholder
# Should be: GROQ_API_KEY=gsk_actual_key_here
```

### Dashboard Not Loading Data
```bash
# Solution: Generate data files first
python baseline_comparison.py
python generate_compliance_log.py
python generate_retry_flows.py
```

### Import Errors
```bash
# Error: "ModuleNotFoundError: No module named 'langchain_groq'"
# Solution: Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Port Already in Use
```bash
# Error: "Port 3000 already in use"
# Solution: Kill existing process or use different port
npm run dev -- -p 3001
```

---

## **Quick Test (30 seconds)**

Verify system is working:

```bash
# 1. Check vector store exists
ls -lh data/vector_store.json

# 2. Test single question
python quick_naive_demo.py "What is your SOC 2 status?"

# 3. Check if baseline data exists
ls -lh output/baseline_comparison.json
```

---

## **Full System Test (10 minutes)**

Complete end-to-end test:

```bash
# Clean previous outputs
rm -rf output/*.json output/*.csv output/*.txt

# Run full pipeline
python -m src.ingest
python baseline_comparison.py
python generate_compliance_log.py
python generate_retry_flows.py
python tests/evaluation.py

# Verify outputs
ls -lh output/

# Expected files:
# - baseline_comparison.json
# - baseline_report.txt
# - compliance_checks.json
# - retry_flows.json
# - evaluation_results.json
```

---

## **Development Commands**

### Run Linter
```bash
# If you have flake8 installed
flake8 src/ tests/
```

### Run Type Checker
```bash
# If you have mypy installed
mypy src/
```

### Clean Generated Files
```bash
# Remove all output files
rm -rf output/*.json output/*.csv output/*.txt

# Remove vector store
rm -rf data/vector_store.json

# Remove Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

---

## **Command Reference Quick Sheet**

| Task | Command |
|------|---------|
| Install dependencies | `pip install -r requirements.txt` |
| Build vector store | `python -m src.ingest` |
| Run baseline comparison | `python baseline_comparison.py` |
| Run evaluation | `python tests/evaluation.py` |
| Process CSV | `python -m src.main --input file.csv --output out.csv` |
| Start dashboard | `cd ../frontend && npm run dev` |
| Naive LLM demo | `python quick_naive_demo.py "question"` |
| View results | `cat output/baseline_report.txt` |

---

## **Performance Benchmarks**

Expected timing for each command:

| Command | Duration | Notes |
|---------|----------|-------|
| `python -m src.ingest` | ~30s | First run downloads embedding model |
| `python baseline_comparison.py` | 5-10min | 10 questions × 2 approaches |
| `python tests/evaluation.py` | 3-5min | 10 questions through full pipeline |
| `python -m src.main` (15 questions) | 3-5min | Depends on retries needed |
| `npm run dev` (startup) | 5-10s | Dashboard compile time |

---

## **System Requirements Check**

```bash
# Check Python version (need 3.8+)
python --version

# Check Node version (need 16+)
node --version

# Check disk space (need ~500MB for models)
df -h .

# Check memory (recommend 4GB+)
free -h  # Linux
vm_stat  # Mac
```

---

Good luck testing! 🚀
