import React from 'react';
import { Link } from 'react-router-dom';
import {
  Clock,
  Calendar,
  CreditCard,
  CheckSquare,
  TrendingUp,
  LogIn,
  LogOut,
  ArrowUpRight,
  ShieldCheck,
  Building,
  User,
  ExternalLink,
} from 'lucide-react';
import { PageHeader, Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useEmployee } from '@/context/EmployeeContext';

export const DashboardView: React.FC = () => {
  const {
    profile,
    attendance,
    leaveData,
    payslips,
    workLogs,
    shiftElapsedTime,
    punching,
    handlePunch,
    totalDaysPresent,
    attendanceRate,
    totalLeaveAvailable,
    latestPayslip,
    setSelectedPayslip,
    setShowLeaveModal,
    formatCurrency,
  } = useEmployee();

  const isClockedIn = attendance?.is_clocked_in;
  const isClockedOut = attendance?.is_clocked_out;

  return (
    <div className="space-y-6 animate-in fade-in duration-150">
      <PageHeader
        title="Employee Dashboard & Highlights"
        description="Personal workspace summary, shift timeclock, leave entitlements, and company credentials."
        actions={
          <Button variant="primary" size="sm" onClick={() => setShowLeaveModal(true)} className="gap-1.5">
            <Calendar className="h-3.5 w-3.5" />
            <span>Apply for Leave</span>
          </Button>
        }
      />

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Shift Timeclock */}
        <Card className="flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">
                Shift Timeclock
              </span>
              <Badge variant={isClockedIn ? 'success' : isClockedOut ? 'default' : 'warning'} size="sm">
                {isClockedIn ? 'In Progress' : isClockedOut ? 'Completed' : 'Pending Punch'}
              </Badge>
            </div>
            <div className="text-2xl font-bold font-mono text-text-primary tracking-tight">
              {isClockedIn && shiftElapsedTime ? (
                <span className="text-emerald-600 dark:text-emerald-400">{shiftElapsedTime}</span>
              ) : isClockedOut ? (
                'Shift Ended'
              ) : (
                'Not Clocked In'
              )}
            </div>
            <p className="text-xs text-text-muted mt-1">
              {attendance?.today?.check_in
                ? `Check-in at ${new Date(attendance.today.check_in).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
                : 'Awaiting punch'}
            </p>
          </div>

          <div className="mt-4 pt-3 border-t border-border flex items-center gap-2">
            {!isClockedIn && !isClockedOut && (
              <Button
                variant="primary"
                size="sm"
                className="w-full gap-1.5"
                onClick={() => handlePunch('CLOCK_IN')}
                disabled={punching}
              >
                <LogIn className="h-3.5 w-3.5" />
                <span>Clock In Now</span>
              </Button>
            )}
            {isClockedIn && (
              <Button
                variant="destructive"
                size="sm"
                className="w-full gap-1.5"
                onClick={() => handlePunch('CLOCK_OUT')}
                disabled={punching}
              >
                <LogOut className="h-3.5 w-3.5" />
                <span>Clock Out Now</span>
              </Button>
            )}
            {isClockedOut && (
              <span className="text-xs text-text-muted italic py-1">Daily hours recorded</span>
            )}
          </div>
        </Card>

        {/* Attendance Score */}
        <Card className="flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">
                Monthly Attendance
              </span>
              <Badge variant="success" size="sm">
                {totalDaysPresent} Days Logged
              </Badge>
            </div>
            <div className="text-2xl font-bold text-text-primary">
              {attendanceRate}%
            </div>
            <p className="text-xs text-text-muted mt-1">
              {attendance?.stats?.days_absent || 0} absences • {attendance?.stats?.total_overtime_hours || 0}h overtime
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-border flex items-center justify-between text-xs">
            <span className="text-text-muted">Biometric Status</span>
            <span className="font-semibold text-emerald-600 dark:text-emerald-400">100% Verified</span>
          </div>
        </Card>

        {/* PTO Balance */}
        <Card className="flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">
                PTO Available
              </span>
              <span className="text-xs font-medium text-accent">Accrued</span>
            </div>
            <div className="text-2xl font-bold text-text-primary">
              {totalLeaveAvailable} <span className="text-sm font-normal text-text-muted">days</span>
            </div>
            <p className="text-xs text-text-muted mt-1">
              {leaveData?.balances?.annual?.available || 0}d Annual • {leaveData?.balances?.sick?.available || 0}d Sick • {leaveData?.balances?.casual?.available || 0}d Casual
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-border flex items-center justify-between text-xs">
            <span className="text-text-muted">Pending Requests</span>
            <span className="font-semibold text-text-primary font-mono">
              {leaveData?.requests?.filter((r) => r.status === 'PENDING').length || 0}
            </span>
          </div>
        </Card>

        {/* Latest Compensation */}
        <Card className="flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">
                Latest Payout
              </span>
              <Badge variant="success" size="sm">
                {latestPayslip?.status || 'SETTLED'}
              </Badge>
            </div>
            <div className="text-2xl font-bold font-mono text-text-primary">
              {latestPayslip ? formatCurrency(latestPayslip.net_salary) : '$0.00'}
            </div>
            <p className="text-xs text-text-muted mt-1">
              {latestPayslip ? `Period: ${latestPayslip.period}` : 'No recent payroll run'}
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-border flex items-center justify-between text-xs">
            <span className="text-text-muted">Direct Deposit</span>
            {latestPayslip ? (
              <button
                onClick={() => setSelectedPayslip(latestPayslip)}
                className="text-accent hover:underline font-medium inline-flex items-center gap-1"
              >
                <span>View Receipt</span>
                <ArrowUpRight className="h-3 w-3" />
              </button>
            ) : (
              <span className="text-text-muted">—</span>
            )}
          </div>
        </Card>
      </div>

      {/* Two Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Quick Profile & Active Entitlements */}
        <Card className="p-5 space-y-4">
          <CardHeader className="pb-3 border-b border-border">
            <CardTitle className="flex items-center gap-2">
              <User className="h-4 w-4 text-accent" />
              <span>Identity & Organization</span>
            </CardTitle>
          </CardHeader>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between py-1.5 border-b border-border">
              <span className="text-text-muted">Full Name</span>
              <span className="font-semibold text-text-primary">
                {profile ? `${profile.first_name} ${profile.last_name}` : '—'}
              </span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-border">
              <span className="text-text-muted">Employee Code</span>
              <span className="font-mono font-semibold text-accent">{profile?.employee_code || '—'}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-border">
              <span className="text-text-muted">Department</span>
              <span className="font-medium text-text-primary">{profile?.department_name || 'Engineering'}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-border">
              <span className="text-text-muted">Designation</span>
              <span className="font-medium text-text-primary">{profile?.designation_name || 'Staff Member'}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-border">
              <span className="text-text-muted">Work Location</span>
              <span className="font-medium text-text-primary">{profile?.location || 'San Francisco HQ'}</span>
            </div>
            <div className="flex justify-between py-1.5">
              <span className="text-text-muted">Employment Type</span>
              <Badge variant="outline" size="sm">{profile?.employment_type || 'FULL_TIME'}</Badge>
            </div>
          </div>
        </Card>

        {/* Center & Right: Recent Timesheet & Leave Requests */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="p-5">
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-border">
              <CardTitle className="flex items-center gap-2">
                <CheckSquare className="h-4 w-4 text-accent" />
                <span>Recent Daily Tasks & Timesheet Logs</span>
              </CardTitle>
              <Link to="/timesheet" className="text-xs text-accent hover:underline flex items-center gap-1 font-medium">
                <span>View all</span>
                <ArrowUpRight className="h-3 w-3" />
              </Link>
            </div>

            {workLogs.length === 0 ? (
              <p className="text-xs text-text-muted italic py-4 text-center">No timesheet entries logged yet.</p>
            ) : (
              <div className="space-y-2.5">
                {workLogs.slice(0, 3).map((log) => (
                  <div key={log.id} className="p-3 rounded-xl bg-surface-secondary border border-border flex items-start justify-between">
                    <div className="space-y-1">
                      <p className="text-xs font-semibold text-text-primary">{log.description}</p>
                      <p className="text-[11px] text-text-muted">Date: {log.work_date}</p>
                    </div>
                    <Badge variant="primary" size="sm">
                      {log.hours_spent} hrs
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </Card>

          <Card className="p-5">
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-border">
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-accent" />
                <span>Upcoming & Recent Leave Applications</span>
              </CardTitle>
              <Link to="/leave" className="text-xs text-accent hover:underline flex items-center gap-1 font-medium">
                <span>PTO Hub</span>
                <ArrowUpRight className="h-3 w-3" />
              </Link>
            </div>

            {(!leaveData?.requests || leaveData.requests.length === 0) ? (
              <p className="text-xs text-text-muted italic py-4 text-center">No leave requests found.</p>
            ) : (
              <div className="space-y-2.5">
                {leaveData.requests.slice(0, 3).map((req) => (
                  <div key={req.id} className="p-3 rounded-xl bg-surface-secondary border border-border flex items-center justify-between">
                    <div>
                      <p className="text-xs font-semibold text-text-primary capitalize">
                        {req.leave_type_id.replace('lt-', '')} Leave ({req.days_count} days)
                      </p>
                      <p className="text-[11px] text-text-muted">
                        {req.start_date} to {req.end_date} • {req.reason}
                      </p>
                    </div>
                    <Badge
                      variant={req.status === 'APPROVED' ? 'success' : req.status === 'REJECTED' ? 'danger' : 'warning'}
                      size="sm"
                    >
                      {req.status}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};
