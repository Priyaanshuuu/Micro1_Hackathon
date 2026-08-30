# RFP Auto-Responder Dashboard (Frontend)

Real-time metrics dashboard displaying evaluation results and compliance verification metrics.

## 🚀 Quick Start

### 1. Install Dependencies (first time only)
```bash
npm install
```

### 2. Run the Dashboard
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 📊 What This Dashboard Shows

- **Critical Metrics**: Perfect answers (3/3 score), average score, hallucination rate
- **Response Summary**: Approved vs escalated, retry statistics
- **Score Distribution**: Visual breakdown of answer quality (0-3 scale)
- **Key Insights**: System capabilities and compliance verification details

## 🔗 How It Works

1. **Backend Pipeline**: Runs in `rfp-auto-responder/`
   ```bash
   python -m src.main --input samples/sample_rfp.csv --output output/responses.csv
   python tests/evaluation.py  # Generates evaluation_results.json
   ```

2. **API Routes** (in this Next.js app):
   - `/api/metrics` — Returns evaluation rubric scores
   - `/api/responses` — Returns response summary stats

3. **Components**:
   - `MetricsCard` — Displays perfect answers, avg score, hallucination rate
   - `ScoreDistributionChart` — Shows 0-3 score breakdown
   - `ResponsesSummary` — Approved/escalated split and retries

## 🔄 Data Flow

```
Backend (Python)
├── python tests/evaluation.py
└── Generates: output/evaluation_results.json
       ↓
Frontend API Routes
├── /api/metrics → reads evaluation_results.json
└── /api/responses → reads responses.csv
       ↓
Dashboard Components
└── Display live metrics
```

## 🛠️ Development

### Add a New Metric Card

1. Create a component in `app/components/YourCard.tsx`:
```tsx
export function YourCard() {
  const [data, setData] = useState(null);
  useEffect(() => {
    fetch('/api/metrics')
      .then(r => r.json())
      .then(d => setData(d.metrics));
  }, []);
  return <div>{/* Your card */}</div>;
}
```

2. Import and use in `app/page.tsx`:
```tsx
<YourCard />
```

### Build for Production

```bash
npm run build
npm run start
```

## 🔐 Notes

- Dashboard reads from backend output files. Ensure backend has been run first.
- No sensitive data is exposed (API keys stay in `.env`)
- Works offline once data is generated

## 📈 Metrics Explained

| Metric | Meaning |
|--------|---------|
| **Score 3** | Perfect: Correct, cited, compliant ✅ |
| **Score 2** | Correct but no source citation |
| **Score 1** | Partially correct, missing details |
| **Score 0** | Wrong, hallucinated, unsupported ❌ |
| **Hallucination Rate** | % of answers with unsupported claims (target: 0%) |
| **False-Pass Rate** | % of non-compliant answers that passed gate (target: 0%) |
| **Approved** | Ready to send without human review |
| **Escalated** | Needs human review (ambiguous or failed compliance) |

---

**Built for Micro1 Hackathon** 🚀
