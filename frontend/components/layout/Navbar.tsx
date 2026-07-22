'use client';

import { Moon, Sun, User } from 'lucide-react';
import { useTheme } from 'next-themes';
import Breadcrumbs from './Breadcrumbs';

export default function Navbar() {
  const { theme, setTheme } = useTheme();

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b bg-background px-4 sm:px-6">
      <div className="flex items-center">
        <Breadcrumbs />
      </div>

      <div className="flex items-center space-x-4">
        {/* Placeholder Search */}
        <div className="hidden md:block">
          <input
            type="text"
            placeholder="Search..."
            className="h-9 w-64 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            disabled
          />
        </div>

        {/* Theme Toggle */}
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="inline-flex items-center justify-center rounded-md w-9 h-9 border border-input bg-transparent hover:bg-accent hover:text-accent-foreground"
        >
          <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </button>

        {/* User Avatar Placeholder */}
        <div className="h-9 w-9 rounded-full bg-muted flex items-center justify-center border">
          <User className="h-5 w-5 text-muted-foreground" />
        </div>
      </div>
    </header>
  );
}
