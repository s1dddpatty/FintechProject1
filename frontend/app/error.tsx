'use client';

import { useEffect } from 'react';
import ErrorState from '@/components/ui/ErrorState';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service if configured
    console.error(error);
  }, [error]);

  return (
    <div className="flex h-full w-full items-center justify-center p-8">
      <ErrorState 
        title="Application Error" 
        message={error.message || "An unexpected error occurred in the application."}
        onRetry={reset} 
      />
    </div>
  );
}
