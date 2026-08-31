'use client';

import { useState, useEffect } from 'react';

interface RetryAttempt {
  attempt_number: number;
  search_query: string;
  answer: string;
  verdict: string;
  feedback?: string;
}

interface RetryFlow {
  question_id: string;
  question: string;
  attempts: RetryAttempt[];
  final_status: 'approved' | 'escalated';
}

export function RetryFlowVisualizer() {
  const [retryFlows, setRetryFlows] = useState<RetryFlow[]>([]);
  const [selectedFlow, setSelectedFlow] = useState<RetryFlow | null>(null);

  useEffect(() => {
    const fetchRetryFlows = async () => {
      try {
        const res = await fetch('/api/retry-flows');
        const data = await res.json();
        setRetryFlows(data.flows || []);
      } catch (error) {
        console.error('Failed to fetch retry flows:', error);
      }
    };

    fetchRetryFlows();
  }, []);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        🔄 Self-Correction Flow
      </h3>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
        Watch how the system refines its search and answers based on compliance feedback
      </p>

      {retryFlows.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-8">
          No retry flows recorded yet. Questions with compliance issues will show here.
        </p>
      ) : (
        <div className="space-y-4">
          {retryFlows.map((flow) => (
            <div key={flow.question_id} className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
              <button
                onClick={() => setSelectedFlow(selectedFlow?.question_id === flow.question_id ? null : flow)}
                className="w-full p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <span className="font-medium text-sm text-gray-900 dark:text-white">
                      {flow.question_id}
                    </span>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {flow.question}
                    </p>
                  </div>
                  <div className="flex items-center gap-3 ml-4">
                    <span className="text-xs px-2 py-1 rounded bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100">
                      {flow.attempts.length} attempts
                    </span>
                    <span
                      className={`text-xs px-2 py-1 rounded ${
                        flow.final_status === 'approved'
                          ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                          : 'bg-amber-100 text-amber-800 dark:bg-amber-800 dark:text-amber-100'
                      }`}
                    >
                      {flow.final_status}
                    </span>
                  </div>
                </div>
              </button>

              {selectedFlow?.question_id === flow.question_id && (
                <div className="p-4 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700">
                  <div className="space-y-4">
                    {flow.attempts.map((attempt, idx) => (
                      <div key={idx} className="relative pl-8">
                        <div className="absolute left-0 top-0 w-6 h-6 rounded-full bg-blue-500 text-white text-xs flex items-center justify-center font-bold">
                          {attempt.attempt_number}
                        </div>

                        {idx < flow.attempts.length - 1 && (
                          <div className="absolute left-3 top-6 w-0.5 h-full bg-blue-300 dark:bg-blue-700" />
                        )}

                        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                          <div className="mb-2">
                            <span className="text-xs font-semibold text-gray-700 dark:text-gray-300">
                              Search Query:
                            </span>
                            <p className="text-sm text-gray-900 dark:text-white mt-1">
                              {attempt.search_query}
                            </p>
                          </div>

                          <div className="mb-2">
                            <span className="text-xs font-semibold text-gray-700 dark:text-gray-300">
                              Generated Answer:
                            </span>
                            <p className="text-sm text-gray-900 dark:text-white mt-1">
                              {attempt.answer}
                            </p>
                          </div>

                          <div className="flex items-center justify-between pt-2 border-t border-gray-100 dark:border-gray-700">
                            <span
                              className={`text-xs px-2 py-1 rounded ${
                                attempt.verdict === 'PASSED'
                                  ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                                  : 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
                              }`}
                            >
                              {attempt.verdict}
                            </span>
                            {attempt.feedback && (
                              <span className="text-xs text-gray-600 dark:text-gray-400 max-w-md">
                                {attempt.feedback}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
