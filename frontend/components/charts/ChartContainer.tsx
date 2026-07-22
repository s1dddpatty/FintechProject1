import LoadingState from '../ui/LoadingState';
import ErrorState from '../ui/ErrorState';
import EmptyState from '../ui/EmptyState';

interface ChartContainerProps {
  title: string;
  description?: string;
  isLoading?: boolean;
  isError?: boolean;
  isEmpty?: boolean;
  onRetry?: () => void;
  children: React.ReactNode;
}

export default function ChartContainer({
  title,
  description,
  isLoading,
  isError,
  isEmpty,
  onRetry,
  children
}: ChartContainerProps) {
  return (
    <div className="rounded-xl border bg-card text-card-foreground shadow">
      <div className="flex flex-col space-y-1.5 p-6">
        <h3 className="font-semibold leading-none tracking-tight">{title}</h3>
        {description && (
          <p className="text-sm text-muted-foreground">{description}</p>
        )}
      </div>
      <div className="p-6 pt-0">
        {isLoading && <div className="h-[300px] w-full flex items-center justify-center"><LoadingState /></div>}
        {isError && !isLoading && <div className="h-[300px] w-full flex items-center justify-center"><ErrorState onRetry={onRetry} /></div>}
        {isEmpty && !isLoading && !isError && <div className="h-[300px] w-full flex items-center justify-center"><EmptyState /></div>}
        {!isLoading && !isError && !isEmpty && (
          <div className="h-[300px] w-full">
            {children}
          </div>
        )}
      </div>
    </div>
  );
}
