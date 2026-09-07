import React from 'react';
import {
  Clock,
  Calendar,
  LogIn,
  LogOut,
  RefreshCw,
  Sun,
  Moon,
  ShieldCheck,
  ChevronDown,
  UserCheck,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useEmployee } from '@/context/EmployeeContext';

export const EmployeeTopbar: React.FC = () => {
  const {
    profile,
    actorId,
    setActorId,
    employeesList,
    attendance,
    currentTime,
    shiftElapsedTime,
    punching,
    refreshing,
    fetchData,
    handlePunch,
    setShowLeaveModal,
  } = useEmployee();

  const isClockedIn = attendance?.is_clocked_in;
  const isClockedOut = attendance?.is_clocked_out;

  const toggleTheme = () => {
    const isDark = document.documentElement.classList.contains('dark');
    if (isDark) {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    } else {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    }
  };

  const displayName = profile ? `${profile.first_name} ${profile.last_name}` : actorId;

  return (
    <header className="h-14 border-b border-border bg-surface px-4 flex items-center justify-between z-10 shrink-0 select-none">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-accent/10 border border-accent/20 flex items-center justify-center text-accent font-bold text-xs shrink-0">
            {profile?.first_name ? profile.first_name[0] : 'E'}
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <label htmlFor="employee-switcher" className="sr-only">Switch Employee Profile</label>
              <div className="relative">
                <select
                  id="employee-switcher"
                  value={actorId}
                  onChange={(e) => setActorId(e.target.value)}
                  className="h-7 pl-2 pr-6 text-xs font-bold bg-surface-secondary hover:bg-surface-secondary/80 border border-border hover:border-accent/40 rounded-md text-text-primary focus:outline-none focus:ring-1 focus:ring-accent cursor-pointer appearance-none transition-colors"
                  title="Switch logged-in employee profile"
                >
                  {employeesList && employeesList.length > 0 ? (
                    employeesList.map((emp) => (
                      <option key={emp.employee_id} value={emp.employee_id}>
                        {emp.first_name} {emp.last_name} ({emp.employee_code})
                      </option>
                    ))
                  ) : (
                    <option value={actorId}>{displayName}</option>
                  )}
                </select>
                <ChevronDown className="w-3 h-3 text-text-muted absolute right-1.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              </div>
              <span className="hidden lg:inline-flex px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-surface-secondary border border-border text-text-muted">
                {profile?.department_name || 'Department'}
              </span>
            </div>
            <p className="text-[10px] text-text-muted hidden sm:block mt-0.5">
              {profile?.designation_name || 'Active Employee'} • {profile?.location || 'Bangalore HQ'}
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2.5">
        {/* Live Clock & Shift timer */}
        <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-lg bg-surface-secondary border border-border">
          <Clock className="w-3.5 h-3.5 text-text-muted" />
          <span className="font-mono text-xs text-text-primary font-semibold">
            {currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
          </span>
          {isClockedIn && shiftElapsedTime && (
            <span className="text-[11px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-mono font-medium border border-emerald-500/20">
              {shiftElapsedTime}
            </span>
          )}
        </div>

        {/* 1-Tap Biometric Punch Button */}
        {isClockedIn ? (
          <Button
            size="sm"
            variant="destructive"
            loading={punching}
            onClick={() => handlePunch('CLOCK_OUT')}
            className="gap-1 text-xs h-8"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Clock Out</span>
          </Button>
        ) : (
          <Button
            size="sm"
            variant="primary"
            loading={punching}
            onClick={() => handlePunch('CLOCK_IN')}
            className="gap-1 text-xs h-8"
          >
            <LogIn className="w-3.5 h-3.5" />
            <span>Clock In</span>
          </Button>
        )}

        {/* Apply Leave CTA */}
        <Button
          size="sm"
          variant="secondary"
          onClick={() => setShowLeaveModal(true)}
          className="gap-1 text-xs h-8 hidden md:inline-flex"
        >
          <Calendar className="w-3.5 h-3.5 text-accent" />
          <span>Apply Leave</span>
        </Button>

        {/* Refresh button */}
        <Button
          size="icon-sm"
          variant="ghost"
          onClick={() => fetchData(true)}
          disabled={refreshing}
          title="Refresh Data"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin text-accent' : 'text-text-muted'}`} />
        </Button>

        {/* Dark / Light theme toggle */}
        <Button
          size="icon-sm"
          variant="ghost"
          onClick={toggleTheme}
          title="Toggle Theme"
        >
          <Sun className="w-3.5 h-3.5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0 text-text-muted" />
          <Moon className="absolute w-3.5 h-3.5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100 text-text-muted" />
        </Button>
      </div>
    </header>
  );
};
