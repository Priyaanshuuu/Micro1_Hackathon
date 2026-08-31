'use client';

import { useState, useEffect } from 'react';

export function LastUpdated() {
  const [timestamp, setTimestamp] = useState<string>('');

  useEffect(() => {
    setTimestamp(new Date().toLocaleString());
  }, []);

  return (
    <div className="text-sm text-gray-500 dark:text-gray-400">
      Last updated: {timestamp || 'Loading...'}
    </div>
  );
}
