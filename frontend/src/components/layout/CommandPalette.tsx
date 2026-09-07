import * as React from 'react';
import { Command } from 'cmdk';
import { useNavigate } from 'react-router-dom';
import {
  Search, Users, Bot, Workflow, CheckSquare,
  BarChart3, Settings, FileText, LayoutDashboard,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface CommandPaletteProps {
  open: boolean;
  onClose: () => void;
}

const quickActions = [
  { label: 'Dashboard', icon: LayoutDashboard, to: '/' },
  { label: 'Employees', icon: Users, to: '/employees' },
  { label: 'Approvals', icon: CheckSquare, to: '/approvals' },
  { label: 'AI Agents', icon: Bot, to: '/agents' },
  { label: 'Workflows', icon: Workflow, to: '/workflows' },
  { label: 'Analytics', icon: BarChart3, to: '/analytics' },
  { label: 'Policies', icon: FileText, to: '/policies' },
  { label: 'Settings', icon: Settings, to: '/settings' },
];

export function CommandPalette({ open, onClose }: CommandPaletteProps) {
  const navigate = useNavigate();

  const handleSelect = (to: string) => {
    navigate(to);
    onClose();
  };

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        if (!open) onClose(); // parent toggles open
      }
      if (e.key === 'Escape' && open) onClose();
    };
    window.addEventListener('keydown', down);
    return () => window.removeEventListener('keydown', down);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 bg-black/40 backdrop-blur-[2px] flex items-start justify-center pt-[15vh]"
      onClick={(e) => e.target === e.currentTarget && onClose()}
      role="dialog"
      aria-modal
      aria-label="Command palette"
    >
      <Command
        className={cn(
          'w-full max-w-xl bg-surface border border-border rounded-xl shadow-xl',
          'overflow-hidden animate-slide-in-up'
        )}
      >
        <div className="flex items-center gap-2 px-4 py-3 border-b border-border">
          <Search className="h-4 w-4 text-text-muted shrink-0" aria-hidden />
          <Command.Input
            placeholder="Search employees, reports, commands..."
            className="flex-1 bg-transparent text-sm text-text-primary placeholder:text-text-muted focus:outline-none"
            autoFocus
          />
          <kbd className="text-2xs text-text-muted bg-surface-secondary px-1.5 py-0.5 rounded border border-border font-mono">
            ESC
          </kbd>
        </div>

        <Command.List className="max-h-96 overflow-y-auto py-2">
          <Command.Empty className="flex items-center justify-center py-8 text-sm text-text-muted">
            No results found.
          </Command.Empty>

          <Command.Group
            heading="Quick Actions"
            className="[&_[cmdk-group-heading]]:px-4 [&_[cmdk-group-heading]]:py-1.5 [&_[cmdk-group-heading]]:text-2xs [&_[cmdk-group-heading]]:font-semibold [&_[cmdk-group-heading]]:text-text-muted [&_[cmdk-group-heading]]:uppercase [&_[cmdk-group-heading]]:tracking-wide"
          >
            {quickActions.map((action) => {
              const Icon = action.icon;
              return (
                <Command.Item
                  key={action.to}
                  value={action.label}
                  onSelect={() => handleSelect(action.to)}
                  className={cn(
                    'flex items-center gap-3 px-4 py-2 text-sm text-text-secondary cursor-pointer',
                    'hover:bg-surface-secondary hover:text-text-primary',
                    'data-[selected=true]:bg-accent-soft data-[selected=true]:text-accent',
                    'transition-colors focus:outline-none'
                  )}
                >
                  <Icon className="h-4 w-4 shrink-0" aria-hidden />
                  {action.label}
                </Command.Item>
              );
            })}
          </Command.Group>
        </Command.List>
      </Command>
    </div>
  );
}
