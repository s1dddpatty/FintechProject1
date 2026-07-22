import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  text?: string;
}

export default function LoadingState({ text = "Loading..." }: LoadingStateProps) {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center p-8">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
      <p className="mt-4 text-sm text-muted-foreground">{text}</p>
    </div>
  );
}
