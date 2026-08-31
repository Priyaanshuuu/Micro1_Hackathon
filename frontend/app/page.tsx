'use client';

import { MetricsCard } from './components/MetricsCard';
import { ScoreDistributionChart } from './components/ScoreDistributionChart';
import { ResponsesSummary } from './components/ResponsesSummary';
import { HumanReviewQueue } from './components/HumanReviewQueue';
import { LastUpdated } from './components/LastUpdated';
import { ComplianceGateVisualizer } from './components/ComplianceGateVisualizer';
import { RetryFlowVisualizer } from './components/RetryFlowVisualizer';
import { BaselineComparison } from './components/BaselineComparison';

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                📊 RFP Auto-Responder Dashboard
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Real-time evaluation metrics and compliance monitoring
              </p>
            </div>
            <LastUpdated />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Baseline Comparison - Show competitive advantage first */}
        <section className="mb-8">
          <BaselineComparison />
        </section>

        {/* Critical Metrics Section */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">🎯 Critical Metrics</h2>
          <MetricsCard />
        </section>

        {/* Live Compliance Gate Visualization */}
        <section className="mb-8">
          <ComplianceGateVisualizer />
        </section>

        {/* Self-Correction Flow */}
        <section className="mb-8">
          <RetryFlowVisualizer />
        </section>

        {/* Response Summary Section */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">📈 Response Summary</h2>
          <ResponsesSummary />
        </section>

        {/* Human Review Queue Section */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">👥 Human Review Queue</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Questions requiring human review after failing compliance checks or exceeding retry limits
          </p>
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
            <HumanReviewQueue />
          </div>
        </section>

        {/* Score Distribution Section */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
            <ScoreDistributionChart />
          </div>

          {/* Key Insights */}
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">💡 Key Insights</h3>
            <ul className="space-y-3 text-sm text-gray-700 dark:text-gray-300">
              <li className="flex items-start gap-3">
                <span className="text-green-500 font-bold">✓</span>
                <span><strong>Grounding:</strong> Every answer is sourced from policy documents with citation</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-green-500 font-bold">✓</span>
                <span><strong>Compliance Verification:</strong> Hard rules + LLM fact-check before approval</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-green-500 font-bold">✓</span>
                <span><strong>Audit Trail:</strong> Full history of retrieved context and reasoning for each answer</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-green-500 font-bold">✓</span>
                <span><strong>Smart Escalation:</strong> Ambiguous questions go to human review with full context</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-amber-500 font-bold">→</span>
                <span><strong>False-Pass Prevention:</strong> Target = 0% false passes (no non-compliant answers slip through)</span>
              </li>
            </ul>
          </div>
        </section>

        {/* Info Section */}
        <section className="bg-blue-50 dark:bg-blue-900 border border-blue-200 dark:border-blue-700 rounded-lg p-6 mb-8">
          <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-2">ℹ️ About This Dashboard</h3>
          <p className="text-blue-800 dark:text-blue-200 text-sm mb-3">
            This dashboard displays real-time evaluation metrics from the RFP Auto-Responder system. Metrics include scoring rubrics (0-3 scale), hallucination detection, and compliance verification results.
          </p>
          <p className="text-blue-800 dark:text-blue-200 text-sm">
            <strong>To run evaluation:</strong> <code className="bg-blue-100 dark:bg-blue-800 px-2 py-1 rounded">python tests/evaluation.py</code>
          </p>
        </section>

        {/* Footer */}
        <footer className="text-center py-8 text-gray-600 dark:text-gray-400 border-t border-gray-200 dark:border-gray-700">
          <p>Built for Micro1 Hackathon 🚀</p>
          <p className="text-sm mt-2">RFP Auto-Responder with Compliance Verification</p>
        </footer>
      </main>
    </div>
  );
}
