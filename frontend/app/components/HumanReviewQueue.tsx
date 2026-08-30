'use client';

import { useEffect, useState } from 'react';

interface EscalatedQuestion {
  [key: string]: string;
}

export function HumanReviewQueue() {
  const [questions, setQuestions] = useState<EscalatedQuestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  useEffect(() => {
    fetch('/api/review-queue')
      .then(res => res.json())
      .then(data => {
        setQuestions(data.escalated_questions || []);
      })
      .catch(err => setError(String(err)))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-gray-500">Loading escalated questions...</div>;
  if (error) return <div className="text-red-500">Error: {error}</div>;
  
  if (questions.length === 0) {
    return (
      <div className="bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-700 rounded-lg p-6 text-center">
        <p className="text-green-800 dark:text-green-200 font-semibold text-lg">✅ No Escalations!</p>
        <p className="text-green-700 dark:text-green-300 text-sm mt-2">
          All questions passed compliance checks. No human review needed.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {questions.map((q, idx) => (
        <div key={idx} className="border border-amber-200 dark:border-amber-700 rounded-lg overflow-hidden bg-white dark:bg-gray-800">
          {/* Header (clickable) */}
          <button
            onClick={() => setExpandedId(expandedId === idx ? null : idx)}
            className="w-full px-6 py-4 hover:bg-amber-50 dark:hover:bg-gray-700 transition-colors flex justify-between items-start text-left"
          >
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-amber-100 dark:bg-amber-900 text-amber-800 dark:text-amber-200">
                  ⚠️ Escalated
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  ID: {q.question_id || `Q${idx + 1}`}
                </span>
              </div>
              <p className="text-sm font-medium text-gray-900 dark:text-white truncate max-w-2xl">
                {q.question}
              </p>
            </div>
            <div className={`ml-4 transform transition-transform ${expandedId === idx ? 'rotate-180' : ''}`}>
              ▼
            </div>
          </button>

          {/* Expanded Details */}
          {expandedId === idx && (
            <div className="border-t border-amber-200 dark:border-amber-700 bg-amber-50 dark:bg-gray-700 px-6 py-4 space-y-4">
              {/* Reason for Escalation */}
              <div>
                <h4 className="text-sm font-semibold text-amber-900 dark:text-amber-100 mb-2">
                  🚨 Reason for Escalation
                </h4>
                <p className="text-sm text-amber-800 dark:text-amber-200 bg-white dark:bg-gray-800 p-3 rounded">
                  {q.escalation_reason || 'Max retries exceeded without passing compliance check'}
                </p>
              </div>

              {/* Attempts */}
              <div>
                <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                  🔄 Attempted Answers ({Object.keys(q).filter(k => k.startsWith('attempt_')).length / 3})
                </h4>
                <div className="space-y-3">
                  {[1, 2, 3].map(attemptNum => {
                    const attempt = {
                      answer: q[`attempt_${attemptNum}_answer`],
                      verdict: q[`attempt_${attemptNum}_verdict`]
                    };
                    if (!attempt.answer) return null;
                    
                    return (
                      <div key={attemptNum} className="bg-white dark:bg-gray-800 p-3 rounded border border-gray-200 dark:border-gray-600">
                        <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">
                          Attempt {attemptNum}
                        </p>
                        <p className="text-sm text-gray-900 dark:text-gray-100 mb-2">
                          {attempt.answer}
                        </p>
                        <p className="text-xs text-red-600 dark:text-red-400">
                          ❌ {attempt.verdict || 'Compliance check failed'}
                        </p>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-2">
                <button className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded transition-colors">
                  ✅ Approve & Send
                </button>
                <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded transition-colors">
                  ✏️ Edit & Send
                </button>
                <button className="px-4 py-2 bg-gray-400 hover:bg-gray-500 text-white text-sm font-medium rounded transition-colors">
                  ⏸️ Defer
                </button>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
