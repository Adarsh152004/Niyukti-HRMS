import * as React from 'react';
import { Outlet } from 'react-router-dom';
import { Topbar } from '@/components/layout/Topbar';
import { Sidebar } from '@/components/layout/Sidebar';
import { CommandPalette } from '@/components/layout/CommandPalette';
import { cn } from '@/lib/utils';

interface AppShellProps {
  isDark: boolean;
  onToggleDark: () => void;
}

export function AppShell({ isDark, onToggleDark }: AppShellProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false);
  const [commandOpen, setCommandOpen] = React.useState(false);

  // Ctrl+K / Cmd+K to open command palette
  React.useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setCommandOpen((open) => !open);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  return (
    <div className={cn('h-screen flex flex-col bg-background overflow-hidden', isDark && 'dark')}>
      {/* Top Bar */}
      <Topbar
        onOpenSearch={() => setCommandOpen(true)}
        onToggleDark={onToggleDark}
        isDark={isDark}
      />

      {/* Body: Sidebar + Main */}
      <div className="flex flex-1 overflow-hidden min-h-0">
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed((c) => !c)}
        />

        {/* Main Content */}
        <main
          className="flex-1 overflow-y-auto bg-background"
          id="main-content"
          tabIndex={-1}
        >
          <div className="max-w-[1440px] mx-auto px-6 py-6">
            <Outlet />
          </div>
        </main>
      </div>

      {/* Command Palette */}
      <CommandPalette open={commandOpen} onClose={() => setCommandOpen(false)} />
    </div>
  );
}
