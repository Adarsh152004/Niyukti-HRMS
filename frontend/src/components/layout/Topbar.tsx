import * as React from 'react';
import { Bell, Search, Sun, Moon, HelpCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { IS_DEMO_MODE } from '@/providers/data-provider';
import { Avatar } from '@/components/ui/avatar';

interface TopbarProps {
  onOpenSearch: () => void;
  onToggleDark: () => void;
  isDark: boolean;
}

export function Topbar({ onOpenSearch, onToggleDark, isDark }: TopbarProps) {
  return (
    <header
      className="h-14 border-b border-border bg-surface flex items-center px-4 gap-3 sticky top-0 z-30 shrink-0"
      role="banner"
    >
      {/* Brand */}
      <a
        href="/"
        className="flex items-center gap-2.5 shrink-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent rounded-md"
        aria-label="HRMS Intelligence OS — home"
      >
        <div className="h-7 w-7 rounded-md bg-accent flex items-center justify-center">
          <span className="text-white font-bold text-sm leading-none select-none" aria-hidden>H</span>
        </div>
        <span className="font-semibold text-base text-text-primary hidden sm:block">
          HRMS
        </span>
        <span className="text-xs text-text-muted hidden md:block">Intelligence OS</span>
      </a>

      {/* Demo Mode Banner */}
      {IS_DEMO_MODE && (
        <span
          className="hidden sm:inline-flex items-center gap-1.5 px-2 py-0.5 rounded border border-warning/40 bg-warning-soft text-warning text-xs font-semibold"
          role="status"
          aria-label="Demo mode active — no real data is shown"
        >
          <span className="h-1.5 w-1.5 rounded-full bg-warning" aria-hidden />
          Demo Mode
        </span>
      )}

      {/* Search trigger */}
      <button
        onClick={onOpenSearch}
        className={cn(
          'hidden md:flex flex-1 max-w-sm items-center gap-2 h-8',
          'px-3 rounded-md border border-border bg-surface-secondary',
          'text-sm text-text-muted hover:bg-surface hover:border-border-strong',
          'transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent'
        )}
        aria-label="Search — press Ctrl+K"
      >
        <Search className="h-3.5 w-3.5 shrink-0" aria-hidden />
        <span className="flex-1 text-left text-sm">Search...</span>
        <kbd className="ml-auto font-mono text-2xs text-text-muted bg-border px-1.5 py-0.5 rounded border border-border-strong hidden lg:block">
          ⌘K
        </kbd>
      </button>

      <div className="flex-1" aria-hidden />

      {/* Right controls */}
      <div className="flex items-center gap-1">
        {/* Search icon (mobile) */}
        <button
          onClick={onOpenSearch}
          className="md:hidden p-1.5 rounded-md text-text-muted hover:text-text-primary hover:bg-surface-secondary transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
          aria-label="Open search"
        >
          <Search className="h-4 w-4" />
        </button>

        {/* Dark mode toggle */}
        <button
          onClick={onToggleDark}
          className="p-1.5 rounded-md text-text-muted hover:text-text-primary hover:bg-surface-secondary transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
          aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </button>

        {/* Notifications */}
        <button
          className="relative p-1.5 rounded-md text-text-muted hover:text-text-primary hover:bg-surface-secondary transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
          aria-label="Notifications — 3 unread"
        >
          <Bell className="h-4 w-4" />
          <span
            className="absolute top-1 right-1 h-2 w-2 rounded-full bg-accent border border-surface"
            aria-hidden
          />
        </button>

        {/* Help */}
        <button
          className="p-1.5 rounded-md text-text-muted hover:text-text-primary hover:bg-surface-secondary transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
          aria-label="Help and documentation"
        >
          <HelpCircle className="h-4 w-4" />
        </button>

        {/* User menu & Active Role Badge */}
        <div className="flex items-center gap-2.5 ml-1 pl-2 border-l border-border">
          <Avatar name="Alex Rivera" size="sm" />
          <div className="hidden md:flex flex-col leading-tight">
            <div className="flex items-center gap-1.5">
              <p className="text-xs font-semibold text-text-primary">Alex Rivera</p>
              <span className="inline-flex items-center gap-1 px-1.5 py-0.2 rounded bg-accent/10 border border-accent/25 text-accent text-[10px] font-bold uppercase tracking-wider">
                <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
                Superadmin
              </span>
            </div>
            <p className="text-2xs text-text-muted">CEO · Full RBAC Access</p>
          </div>
        </div>
      </div>
    </header>
  );
}
