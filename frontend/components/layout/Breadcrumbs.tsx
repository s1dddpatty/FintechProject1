'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { ChevronRight } from 'lucide-react';

export default function Breadcrumbs() {
  const pathname = usePathname();
  const paths = pathname.split('/').filter(Boolean);

  if (paths.length === 0) {
    return (
      <div className="flex items-center text-sm text-muted-foreground">
        <span className="text-foreground font-medium">Dashboard</span>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-1 text-sm text-muted-foreground">
      <Link href="/dashboard" className="hover:text-foreground transition-colors">
        Home
      </Link>
      {paths.map((path, index) => {
        const href = `/${paths.slice(0, index + 1).join('/')}`;
        const isLast = index === paths.length - 1;
        const formattedPath = path.charAt(0).toUpperCase() + path.slice(1).replace('-', ' ');

        return (
          <div key={path} className="flex items-center space-x-1">
            <ChevronRight className="w-4 h-4" />
            {isLast ? (
              <span className="text-foreground font-medium">{formattedPath}</span>
            ) : (
              <Link href={href} className="hover:text-foreground transition-colors">
                {formattedPath}
              </Link>
            )}
          </div>
        );
      })}
    </div>
  );
}
