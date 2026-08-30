'use client';

import { useEffect, useState } from 'react';

interface MetricsData {
  total_questions: number;
  perfect_3s: number;
  percent_3s: number;
  twos: number;
  ones: number;
  zeros: number;
  average_score: number;
  hallucination_count: number;
  hallucination_rate: number;
  false_pass_count: number;
  false_pass_rate: number;
}

export function MetricsCard() {
  const [metrics, setMetrics] = useState<MetricsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/metrics')
      .then(res => res.json())
      .then(data => {
        if (data.metrics) {
          setMetrics(data.metrics);
        }
      })
      .catch(err => setError(String(err)))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-gray-500">Loading metrics...</div>;
  if (error) return <div className="text-red-500">Error: {error}</div>;
  if (!metrics) return <div className="text-gray-500">No evaluation results found</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {/* Perfect Answers Card */}
      <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900 dark:to-green-800 p-6 rounded-lg border border-green-200 dark:border-green-700">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-sm font-medium text-green-600 dark:text-green-400">Perfect (3s)</p>
            <p className="text-3xl font-bold text-green-900 dark:text-green-100 mt-2">
              {metrics.perfect_3s}
            </p>
            <p className="text-xs text-green-600 dark:text-green-400 mt-1">
              {metrics.percent_3s.toFixed(1)}% of all answers
            </p>
          </div>
          <div className="text-3xl">⭐⭐⭐</div>
        </div>
      </div>

      {/* Average Score Card */}
      <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900 dark:to-blue-800 p-6 rounded-lg border border-blue-200 dark:border-blue-700">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-sm font-medium text-blue-600 dark:text-blue-400">Average Score</p>
            <p className="text-3xl font-bold text-blue-900 dark:text-blue-100 mt-2">
              {metrics.average_score}/3.0
            </p>
            <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
              {metrics.total_questions} questions evaluated
            </p>
          </div>
          <div className="text-3xl">📊</div>
        </div>
      </div>

      {/* Hallucination Rate Card */}
      <div className={`bg-gradient-to-br ${metrics.hallucination_rate === 0 ? 'from-emerald-50 to-emerald-100 dark:from-emerald-900 dark:to-emerald-800' : 'from-red-50 to-red-100 dark:from-red-900 dark:to-red-800'} p-6 rounded-lg border ${metrics.hallucination_rate === 0 ? 'border-emerald-200 dark:border-emerald-700' : 'border-red-200 dark:border-red-700'}`}>
        <div className="flex justify-between items-start">
          <div>
            <p className={`text-sm font-medium ${metrics.hallucination_rate === 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'}`}>
              Hallucination Rate
            </p>
            <p className={`text-3xl font-bold mt-2 ${metrics.hallucination_rate === 0 ? 'text-emerald-900 dark:text-emerald-100' : 'text-red-900 dark:text-red-100'}`}>
              {metrics.hallucination_rate.toFixed(1)}%
            </p>
            <p className={`text-xs mt-1 ${metrics.hallucination_rate === 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'}`}>
              {metrics.hallucination_count} hallucinations {metrics.hallucination_rate === 0 ? '✅' : '❌'}
            </p>
          </div>
          <div className="text-3xl">{metrics.hallucination_rate === 0 ? '🛡️' : '🚨'}</div>
        </div>
      </div>
    </div>
  );
}
