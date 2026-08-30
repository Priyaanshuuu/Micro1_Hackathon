'use client';

import { useEffect, useState } from 'react';

interface ScoreDistribution {
  label: string;
  count: number;
  percentage: number;
  color: string;
}

interface MetricsData {
  perfect_3s: number;
  twos: number;
  ones: number;
  zeros: number;
  total_questions: number;
}

export function ScoreDistributionChart() {
  const [distribution, setDistribution] = useState<ScoreDistribution[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/metrics')
      .then(res => res.json())
      .then(data => {
        if (data.metrics) {
          const m = data.metrics as MetricsData;
          setDistribution([
            {
              label: 'Score 3 (Perfect)',
              count: m.perfect_3s,
              percentage: m.total_questions > 0 ? (m.perfect_3s / m.total_questions * 100) : 0,
              color: '#10b981' // green
            },
            {
              label: 'Score 2 (Correct)',
              count: m.twos,
              percentage: m.total_questions > 0 ? (m.twos / m.total_questions * 100) : 0,
              color: '#3b82f6' // blue
            },
            {
              label: 'Score 1 (Partial)',
              count: m.ones,
              percentage: m.total_questions > 0 ? (m.ones / m.total_questions * 100) : 0,
              color: '#f59e0b' // amber
            },
            {
              label: 'Score 0 (Wrong)',
              count: m.zeros,
              percentage: m.total_questions > 0 ? (m.zeros / m.total_questions * 100) : 0,
              color: '#ef4444' // red
            }
          ]);
        }
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-gray-500">Loading chart...</div>;

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Score Distribution</h3>
      <div className="space-y-3">
        {distribution.map(item => (
          <div key={item.label}>
            <div className="flex justify-between mb-1">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{item.label}</span>
              <span className="text-sm font-semibold text-gray-900 dark:text-white">
                {item.count} ({item.percentage.toFixed(1)}%)
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${item.percentage}%`,
                  backgroundColor: item.color
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
