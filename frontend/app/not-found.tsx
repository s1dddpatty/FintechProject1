import Link from 'next/link';
import { FileQuestion } from 'lucide-react';
import EmptyState from '@/components/ui/EmptyState';

export default function NotFound() {
  return (
    <div className="flex h-full w-full items-center justify-center p-8">
      <div className="text-center">
        <EmptyState 
          title="404 - Page Not Found"
          description="The page you are looking for does not exist or has been moved."
          icon={<FileQuestion className="mx-auto h-16 w-16 text-muted-foreground" />}
        />
        <div className="mt-6">
          <Link 
            href="/dashboard"
            className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow hover:bg-primary/90 transition-colors"
          >
            Return to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}
