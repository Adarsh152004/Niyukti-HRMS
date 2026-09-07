import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Clock,
  Calendar,
  CreditCard,
  CheckSquare,
  ShieldCheck,
  User,
  ChevronDown,
  Sparkles,
  PanelLeftClose,
  PanelLeftOpen,
  Search,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { useEmployee } from '@/context/EmployeeContext';

interface EmployeeSidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export const EmployeeSidebar: React.FC<EmployeeSidebarProps> = ({ collapsed, onToggle }) => {
  const { actorId, profile, employeesList, handleSelectEmployee } = useEmployee();
  const [isSwitcherOpen, setIsSwitcherOpen] = useState(false);
  const [search, setSearch] = useState('');

  const employeeDisplayName = profile ? `${profile.first_name} ${profile.last_name}` : actorId;
  const employeeRole = profile?.designation_name || 'Staff Member';
  const employeeDept = profile?.department_name || 'Nova Team';

  const navItems = [
    { label: 'Dashboard & Highlights', to: '/', icon: LayoutDashboard },
    { label: 'Attendance & Logs', to: '/attendance', icon: Clock },
    { label: 'Leave & PTO Hub', to: '/leave', icon: Calendar },
    { label: 'Payroll & Payslips', to: '/payroll', icon: CreditCard },
    { label: 'Daily Tasks / Timesheet', to: '/timesheet', icon: CheckSquare },
    { label: 'Credentials', to: '/credentials', icon: ShieldCheck },
  ];

  const filteredEmployees = employeesList.filter((e) => {
    const q = search.toLowerCase();
    return (
      e.first_name.toLowerCase().includes(q) ||
      e.last_name.toLowerCase().includes(q) ||
      e.employee_code.toLowerCase().includes(q)
    );
  });

  return (
    <aside
      className={cn(
        'flex flex-col h-full border-r border-border bg-surface transition-all duration-200 ease-in-out shrink-0 select-none z-20',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Brand Header */}
      <div className="flex items-center justify-between h-14 px-3 border-b border-border">
        {!collapsed ? (
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-lg bg-accent/10 border border-accent/20 flex items-center justify-center shrink-0">
              <Sparkles className="w-4 h-4 text-accent" />
            </div>
            <div className="min-w-0">
              <span className="font-semibold text-sm text-text-primary tracking-tight block truncate">
                HRMS Employees
              </span>
              <span className="text-[10px] text-accent uppercase tracking-wider font-semibold block">
                Self-Service Portal
              </span>
            </div>
          </div>
        ) : (
          <div className="w-8 h-8 rounded-lg bg-accent/10 border border-accent/20 flex items-center justify-center mx-auto">
            <Sparkles className="w-4 h-4 text-accent" />
          </div>
        )}

        <button
          onClick={onToggle}
          className="p-1.5 rounded text-text-muted hover:text-text-primary hover:bg-surface-secondary transition shrink-0"
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <PanelLeftOpen className="w-4 h-4" /> : <PanelLeftClose className="w-4 h-4" />}
        </button>
      </div>

      {/* Identity Switcher Bar */}
      {!collapsed && (
        <div className="p-3 border-b border-border bg-surface-secondary/40 relative">
          <button
            onClick={() => setIsSwitcherOpen(!isSwitcherOpen)}
            className="w-full flex items-center justify-between p-2 rounded-xl bg-surface border border-border hover:border-accent/40 text-left transition shadow-2xs"
          >
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="w-8 h-8 rounded-full bg-accent/10 text-accent font-bold text-xs flex items-center justify-center shrink-0 border border-accent/20">
                {profile ? `${profile.first_name[0]}${profile.last_name[0]}` : 'EM'}
              </div>
              <div className="min-w-0">
                <p className="text-xs font-semibold text-text-primary truncate">{employeeDisplayName}</p>
                <p className="text-[11px] text-text-muted truncate">{employeeRole}</p>
              </div>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-text-muted shrink-0" />
          </button>

          {isSwitcherOpen && (
            <div className="absolute left-3 right-3 top-16 z-30 bg-surface border border-border rounded-xl shadow-xl p-2 animate-in fade-in">
              <div className="relative mb-2">
                <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-text-muted" />
                <input
                  type="text"
                  placeholder="Switch identity..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full pl-8 pr-2.5 py-1.5 text-xs bg-surface-secondary border border-border rounded-lg text-text-primary focus:outline-none focus:ring-1 focus:ring-accent"
                />
              </div>
              <div className="max-h-48 overflow-y-auto space-y-1">
                {filteredEmployees.map((emp) => (
                  <button
                    key={emp.employee_id}
                    onClick={() => {
                      handleSelectEmployee(emp.employee_id);
                      setIsSwitcherOpen(false);
                    }}
                    className={cn(
                      'w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-left text-xs transition',
                      emp.employee_id === actorId
                        ? 'bg-accent/10 text-accent font-semibold'
                        : 'hover:bg-surface-secondary text-text-primary'
                    )}
                  >
                    <span className="truncate">{emp.first_name} {emp.last_name}</span>
                    <span className="text-[10px] text-text-muted font-mono">{emp.employee_code}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Navigation Group */}
      <div className="flex-1 overflow-y-auto px-2 py-3 space-y-1">
        {!collapsed && (
          <p className="px-2 pb-1 text-[11px] font-semibold text-text-muted uppercase tracking-wider">
            Employee Workspace
          </p>
        )}

        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-xs font-medium transition group',
                  isActive
                    ? 'bg-accent text-accent-foreground font-semibold shadow-xs'
                    : 'text-text-secondary hover:text-text-primary hover:bg-surface-secondary'
                )
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              {!collapsed && <span className="truncate">{item.label}</span>}
            </NavLink>
          );
        })}
      </div>

      {/* Footer Info */}
      {!collapsed && (
        <div className="p-3 border-t border-border bg-surface-secondary/30">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-[11px] text-text-muted">Live HRMS Database Sync</span>
          </div>
        </div>
      )}
    </aside>
  );
};
