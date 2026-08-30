'use client';

import { useEffect, useState } from 'react';

interface ResponsesData {
  total: number;
  approved: number;
  escalated: number;
  approved_percentage: string;
  escalation_percentage: string;
  avg_retries: string;
  total_retries: number;
}

export function ResponsesSummary() {
  const [data, setData] = useState<ResponsesData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/responses')
      .then(res => res.json())
      .then(data => {
        if (data.total !== undefined) {
          setData(data);
        } else if (data.error) {
          setError(data.error);
        }
      })
      .catch(err => setError(String(err)))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-gray-500">Loading responses...</div>;
  if (error) return <div className="text-yellow-600 bg-yellow-50 dark:bg-yellow-900 p-3 rounded">{error}</div>;
  if (!data) return <div className="text-gray-500">No responses found</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Approved Summary */}
      <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900 dark:to-green-800 p-6 rounded-lg border border-green-200 dark:border-green-700">
        <div className="flex justify-between items-center">
          <div>
            <p className="text-sm text-green-600 dark:text-green-400">Approved Responses</p>
            <p className="text-3xl font-bold text-green-900 dark:text-green-100 mt-1">
              {data.approved}/{data.total}
            </p>
            <p className="text-sm text-green-600 dark:text-green-400 mt-1">
              {data.approved_percentage}% ready to send
            </p>
          </div>
          <div className="text-5xl">✅</div>
        </div>
      </div>

      {/* Escalated Summary */}
      <div className="bg-gradient-to-br from-amber-50 to-amber-100 dark:from-amber-900 dark:to-amber-800 p-6 rounded-lg border border-amber-200 dark:border-amber-700">
        <div className="flex justify-between items-center">
          <div>
            <p className="text-sm text-amber-600 dark:text-amber-400">Escalated to Review</p>
            <p className="text-3xl font-bold text-amber-900 dark:text-amber-100 mt-1">
              {data.escalated}/{data.total}
            </p>
            <p className="text-sm text-amber-600 dark:text-amber-400 mt-1">
              {data.escalation_percentage}% need human review
            </p>
          </div>
          <div className="text-5xl">⚠️</div>
        </div>
      </div>

      {/* Retry Stats */}
      <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900 dark:to-blue-800 p-6 rounded-lg border border-blue-200 dark:border-blue-700 md:col-span-2">
        <div className="flex justify-between items-center">
          <div>
            <p className="text-sm text-blue-600 dark:text-blue-400">Retry Statistics</p>
            <div className="flex gap-6 mt-2">
              <div>
                <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">{data.total_retries}</p>
                <p className="text-xs text-blue-600 dark:text-blue-400">total retries</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">{data.avg_retries}</p>
                <p className="text-xs text-blue-600 dark:text-blue-400">average per question</p>
              </div>
            </div>
          </div>
          <div className="text-5xl">🔄</div>
        </div>
      </div>
    </div>
  );
}
