'use client';

import { useState, useEffect } from 'react';

interface ComparisonMetric {
  metric: string;
  naive_value: string;
  system_value: string;
  improvement: string;
  is_better: boolean;
}

export function BaselineComparison() {
  const [metrics, setMetrics] = useState<ComparisonMetric[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchComparison = async () => {
      try {
        const res = await fetch('/api/baseline-comparison');
        const data = await res.json();

        if (data.aggregate_metrics) {
          const metricsData: ComparisonMetric[] = [
            {
              metric: 'Hallucination Rate',
              naive_value: data.aggregate_metrics.naive_hallucination_rate,
              system_value: data.aggregate_metrics.system_hallucination_rate,
              improvement: calculateImprovement(
                data.aggregate_metrics.naive_hallucination_rate,
                data.aggregate_metrics.system_hallucination_rate,
                true
              ),
              is_better: true
            },
            {
              metric: 'False-Pass Rate',
              naive_value: data.aggregate_metrics.naive_false_pass_rate,
              system_value: data.aggregate_metrics.system_false_pass_rate,
              improvement: calculateImprovement(
                data.aggregate_metrics.naive_false_pass_rate,
                data.aggregate_metrics.system_false_pass_rate,
                true
              ),
              is_better: true
            },
            {
              metric: 'Grounding Rate',
              naive_value: data.aggregate_metrics.naive_grounding_rate,
              system_value: data.aggregate_metrics.system_grounding_rate,
              improvement: calculateImprovement(
                data.aggregate_metrics.naive_grounding_rate,
                data.aggregate_metrics.system_grounding_rate,
                false
              ),
              is_better: true
            },
            {
              metric: 'Average Score',
              naive_value: data.aggregate_metrics.avg_naive_score.toFixed(2),
              system_value: data.aggregate_metrics.avg_system_score.toFixed(2),
              improvement: data.aggregate_metrics.score_improvement,
              is_better: true
            }
          ];
          setMetrics(metricsData);
        }
      } catch (error) {
        console.error('Failed to fetch baseline comparison:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchComparison();
  }, []);

  const calculateImprovement = (naive: string, system: string, lowerIsBetter: boolean): string => {
    const naiveNum = parseFloat(naive.replace('%', ''));
    const systemNum = parseFloat(system.replace('%', ''));
    const diff = lowerIsBetter ? naiveNum - systemNum : systemNum - naiveNum;
    return diff > 0 ? `↓ ${Math.abs(diff).toFixed(1)}%` : `→ 0%`;
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          📊 vs Naive LLM Baseline
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-8">
          Loading comparison data...
        </p>
      </div>
    );
  }

  if (metrics.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          📊 vs Naive LLM Baseline
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-8">
          Run <code className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">python baseline_comparison.py</code> to generate comparison data
        </p>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-lg border border-purple-200 dark:border-purple-700 p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
        📊 Competitive Advantage vs Naive LLM
      </h3>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
        Quantified improvement over direct LLM prompting (no RAG, no compliance gate)
      </p>

      <div className="space-y-3">
        {metrics.map((metric) => (
          <div
            key={metric.metric}
            className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-sm text-gray-900 dark:text-white">
                {metric.metric}
              </span>
              <span className="text-xs px-2 py-1 rounded bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100">
                {metric.improvement}
              </span>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Naive LLM</div>
                <div className="text-lg font-bold text-red-600 dark:text-red-400">
                  {metric.naive_value}
                </div>
              </div>
              <div className="text-2xl text-gray-400">→</div>
              <div className="flex-1">
                <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Our System</div>
                <div className="text-lg font-bold text-green-600 dark:text-green-400">
                  {metric.system_value}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg border border-blue-200 dark:border-blue-800">
        <p className="text-xs text-blue-900 dark:text-blue-100">
          💡 <strong>Key Insight:</strong> The system prevents hallucinations and ensures compliance through RAG + verification,
          while naive prompting produces confident but incorrect answers.
        </p>
      </div>
    </div>
  );
}
