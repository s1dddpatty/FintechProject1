import { AlertTriangle } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export default function ErrorState({ 
  title = "Something went wrong", 
  message = "An error occurred while fetching data. Please try again later.",
  onRetry 
}: ErrorStateProps) {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center rounded-md border border-destructive/50 bg-destructive/5 p-8 text-center animate-in fade-in-50">
      <AlertTriangle className="mx-auto h-12 w-12 text-destructive" />
      <h3 className="mt-4 text-lg font-semibold text-destructive">{title}</h3>
      <p className="mb-4 mt-2 text-sm text-muted-foreground max-w-md">
        {message}
      </p>
      {onRetry && (
        <button 
          onClick={onRetry}
          className="inline-flex h-9 items-center justify-center rounded-md bg-destructive px-4 py-2 text-sm font-medium text-destructive-foreground shadow hover:bg-destructive/90 transition-colors"
        >
          Try Again
        </button>
      )}
    </div>
  );
}
