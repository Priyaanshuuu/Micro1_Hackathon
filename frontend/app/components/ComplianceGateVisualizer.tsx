'use client';

import { useState, useEffect } from 'react';

interface ComplianceCheck {
  rule_id: string;
  rule_name: string;
  status: 'passed' | 'failed' | 'checking';
  keywords_found?: string[];
  timestamp: string;
}

export function ComplianceGateVisualizer() {
  const [checks, setChecks] = useState<ComplianceCheck[]>([]);
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    // Poll for latest compliance checks
    const fetchChecks = async () => {
      try {
        const res = await fetch('/api/compliance-checks');
        const data = await res.json();
        setChecks(data.recent_checks || []);
      } catch (error) {
        console.error('Failed to fetch compliance checks:', error);
      }
    };

    fetchChecks();
    const interval = setInterval(fetchChecks, 2000); // Poll every 2s

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          🛡️ Compliance Gate (Live)
        </h3>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isLive ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {isLive ? 'Active' : 'Idle'}
          </span>
        </div>
      </div>

      <div className="space-y-3">
        {checks.length === 0 ? (
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-8">
            No recent checks. Run evaluation to see live compliance verification.
          </p>
        ) : (
          checks.map((check, idx) => (
            <div
              key={`${check.rule_id}-${idx}`}
              className={`p-4 rounded-lg border-l-4 ${
                check.status === 'passed'
                  ? 'bg-green-50 dark:bg-green-900/20 border-green-500'
                  : check.status === 'failed'
                  ? 'bg-red-50 dark:bg-red-900/20 border-red-500'
                  : 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-500'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-sm text-gray-900 dark:text-white">
                  {check.rule_name}
                </span>
                <span
                  className={`text-xs px-2 py-1 rounded ${
                    check.status === 'passed'
                      ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                      : check.status === 'failed'
                      ? 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
                      : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100'
                  }`}
                >
                  {check.status.toUpperCase()}
                </span>
              </div>
              {check.keywords_found && check.keywords_found.length > 0 && (
                <div className="text-xs text-gray-600 dark:text-gray-400">
                  Keywords detected:{' '}
                  <code className="bg-gray-100 dark:bg-gray-700 px-1 rounded">
                    {check.keywords_found.join(', ')}
                  </code>
                </div>
              )}
              <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                {new Date(check.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
