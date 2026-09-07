import * as React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Users, Building2, Clock, Calendar,
  Briefcase, UserCheck, CreditCard, Target, GraduationCap,
  FolderOpen, FileText, Bot, Workflow, CheckSquare,
  BarChart3, TrendingDown, ShieldCheck, FileSearch, Settings,
  Cpu, Activity, PanelLeftClose, PanelLeftOpen,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface NavItem {
  label: string;
  to: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string | number;
}

interface NavGroup {
  label: string;
  items: NavItem[];
}

const navGroups: NavGroup[] = [
  {
    label: 'Overview',
    items: [
      { label: 'Executive Dashboard', to: '/', icon: LayoutDashboard },
    ],
  },
  {
    label: 'Workforce',
    items: [
      { label: 'Employees', to: '/employees', icon: Users },
      { label: 'Attendance', to: '/attendance', icon: Clock },
      { label: 'Leave', to: '/leave', icon: Calendar },
      { label: 'Performance & OKRs', to: '/performance', icon: Target },
    ],
  },
  {
    label: 'Talent & Compensation',
    items: [
      { label: 'Recruitment Pipeline', to: '/recruitment', icon: Briefcase },
      { label: 'Deterministic Payroll', to: '/payroll', icon: CreditCard },
    ],
  },
  {
    label: 'Operations & Documents',
    items: [
      { label: 'Documents & Policies', to: '/documents', icon: FolderOpen },
    ],
  },
  {
    label: 'AI & Automation',
    items: [
      { label: 'Agent Orchestration', to: '/orchestration', icon: Activity },
      { label: 'CEO Command Center', to: '/command', icon: LayoutDashboard },
      { label: 'AI Workspace Chat', to: '/ai', icon: Bot },
      { label: 'Agent Fleet Center', to: '/agents', icon: Bot },
      { label: 'Workflows & DAGs', to: '/workflows', icon: Workflow },
      
    ],
  },
  {
    label: 'Intelligence & ML',
    items: [
      { label: 'Workforce Analytics', to: '/analytics', icon: BarChart3 },
      { label: 'ML & Calibration Center', to: '/ml', icon: Cpu },
    ],
  },
  {
    label: 'Administration & Safety',
    items: [
      { label: 'AI Governance & Safety', to: '/governance', icon: ShieldCheck },
      { label: 'Audit & Lineage Explorer', to: '/audit', icon: FileSearch },
      { label: 'System Settings', to: '/settings', icon: Settings },
    ],
  },
];

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const location = useLocation();

  return (
    <aside
      className={cn(
        'flex flex-col h-full',
        'border-r border-border bg-surface',
        'transition-all duration-200 ease-in-out shrink-0 select-none z-20',
        collapsed ? 'w-16' : 'w-64'
      )}
      aria-label="Main navigation"
    >
      {/* Collapse toggle header */}
      <div
        className={cn(
          'h-11 border-b border-border flex items-center shrink-0 px-3',
          collapsed ? 'justify-center px-0' : 'justify-between'
        )}
      >
        {!collapsed && (
          <span className="text-2xs font-bold text-text-muted uppercase tracking-wider pl-1">
            Navigation
          </span>
        )}
        <button
          type="button"
          onClick={onToggle}
          className={cn(
            'flex items-center justify-center h-7 w-7 rounded-md text-text-muted hover:text-text-primary hover:bg-surface-secondary',
            'transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent'
          )}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed
            ? <PanelLeftOpen className="h-4 w-4 shrink-0" />
            : <PanelLeftClose className="h-4 w-4 shrink-0" />
          }
        </button>
      </div>

      {/* Nav items */}
      <nav className="flex-1 overflow-y-auto px-2 py-3 space-y-4">
        {navGroups.map((group) => (
          <div key={group.label}>
            {!collapsed && (
              <p className="px-2 mb-1 text-2xs font-semibold text-text-muted tracking-wider uppercase">
                {group.label}
              </p>
            )}
            <ul className="space-y-0.5" role="list">
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive =
                  item.to === '/'
                    ? location.pathname === '/'
                    : location.pathname.startsWith(item.to);

                return (
                  <li key={item.to}>
                    <NavLink
                      to={item.to}
                      className={cn(
                        'flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-sm',
                        'transition-colors duration-100',
                        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent',
                        isActive
                          ? 'bg-accent-soft text-accent font-semibold'
                          : 'text-text-secondary hover:text-text-primary hover:bg-surface-secondary',
                        collapsed && 'justify-center px-0'
                      )}
                      title={collapsed ? item.label : undefined}
                      aria-current={isActive ? 'page' : undefined}
                    >
                      <Icon
                        className={cn(
                          'h-4 w-4 shrink-0',
                          isActive ? 'text-accent' : 'text-text-muted'
                        )}
                        aria-hidden
                      />
                      {!collapsed && (
                        <span className="flex-1 truncate">{item.label}</span>
                      )}
                      {!collapsed && item.badge !== undefined && (
                        <span className="h-4 min-w-4 px-1 text-2xs font-semibold rounded-full bg-accent text-white flex items-center justify-center">
                          {item.badge}
                        </span>
                      )}
                    </NavLink>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>
    </aside>
  );
}