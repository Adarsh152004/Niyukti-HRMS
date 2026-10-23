import * as React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Calendar, Plus, CheckCircle, XCircle, RefreshCw, Clock, 
  X, User, ArrowUpRight, Check, AlertCircle, Filter
} from 'lucide-react';
import { PageHeader, Card, CardHeader, CardTitle, MetricCard } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table';

interface LeaveRecord {
  id: string;
  organization_id: string;
  employee_id: string;
  leave_type_id: string;
  start_date: string;
  end_date: string;
  days_count: number;
  is_half_day: boolean;
  reason: string;
  status: string;
  applied_on?: string;
  approved_by?: string;
  approved_on?: string;
  created_at?: string;
  employee_code?: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  department_name?: string;
}

interface EmployeeOption {
  id: string;
  first_name: string;
  last_name: string;
  employee_code: string;
  department_name?: string;
}

export function LeavePage() {
  const queryClient = useQueryClient();
  const [filterTab, setFilterTab] = React.useState<'ALL' | 'PENDING' | 'APPROVED' | 'REJECTED'>('ALL');

  // Modal State
  const [isApplyModalOpen, setIsApplyModalOpen] = React.useState(false);
  const [selectedEmpId, setSelectedEmpId] = React.useState('emp-001');
  const [leaveType, setLeaveType] = React.useState('lt-annual');
  const [startDate, setStartDate] = React.useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 2);
    return d.toISOString().split('T')[0];
  });
  const [endDate, setEndDate] = React.useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 4);
    return d.toISOString().split('T')[0];
  });
  const [isHalfDay, setIsHalfDay] = React.useState(false);
  const [reason, setReason] = React.useState('');
  const [formFeedback, setFormFeedback] = React.useState<{ type: 'error' | 'success'; text: string } | null>(null);

  // Fetch live leave requests
  const { data: leaves = [], isLoading, refetch } = useQuery<LeaveRecord[]>({
    queryKey: ['leave-requests'],
    queryFn: async () => {
      const res = await fetch('/api/v1/leaves');
      if (!res.ok) throw new Error('Failed to fetch leave requests');
      const json = await res.json();
      return json.data || [];
    },
    refetchInterval: 5000,
  });

  // Fetch employees list for dropdown
  const { data: employees = [] } = useQuery<EmployeeOption[]>({
    queryKey: ['employees-leave-picker'],
    queryFn: async () => {
      const res = await fetch('/api/v1/employees?limit=100');
      if (!res.ok) return [];
      const json = await res.json();
      return (json.data || []).map((e: any) => ({
        id: e.id,
        first_name: e.first_name,
        last_name: e.last_name,
        employee_code: e.employee_code,
        department_name: e.department_name,
      }));
    },
  });

  // Decision Mutation (Approve / Reject)
  const decisionMutation = useMutation({
    mutationFn: async ({ id, status }: { id: string; status: string }) => {
      const res = await fetch(`/api/v1/leaves/${id}/decision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      });
      if (!res.ok) throw new Error('Failed to update leave status');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leave-requests'] });
    },
  });

  // Apply Leave Mutation
  const applyLeaveMutation = useMutation({
    mutationFn: async () => {
      setFormFeedback(null);
      const res = await fetch('/api/v1/leaves/apply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Actor-ID': 'hr-manager',
          'X-Tenant-ID': 'org-nova-01',
        },
        body: JSON.stringify({
          employee_id: selectedEmpId,
          leave_type: leaveType,
          start_date: startDate,
          end_date: endDate,
          is_half_day: isHalfDay,
          reason: reason.trim() || 'Personal Leave / PTO',
        }),
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || errJson.message || 'Failed to submit leave request');
      }
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leave-requests'] });
      setIsApplyModalOpen(false);
      setReason('');
      setFormFeedback(null);
    },
    onError: (err: any) => {
      setFormFeedback({ type: 'error', text: err.message || 'Submission failed' });
    },
  });

  const totalRequests = leaves?.length || 0;
  const pendingCount = leaves?.filter((l) => (l.status || '').toUpperCase() === 'PENDING').length || 0;
  const approvedCount = leaves?.filter((l) => (l.status || '').toUpperCase() === 'APPROVED').length || 0;
  const totalDays = leaves?.reduce((acc, l) => acc + (l.days_count || 0), 0) || 0;

  const formatLeaveType = (typeId: string) => {
    if (typeId === 'lt-annual') return 'Annual Leave';
    if (typeId === 'lt-sick') return 'Sick Leave';
    if (typeId === 'lt-casual') return 'Casual Leave';
    if (typeId === 'lt-maternity') return 'Maternity Leave';
    return typeId.replace('lt-', '').replace(/^[a-z]/, (c) => c.toUpperCase()) + ' Leave';
  };

  const filteredLeaves = React.useMemo(() => {
    if (filterTab === 'ALL') return leaves;
    return leaves.filter((l) => (l.status || '').toUpperCase() === filterTab);
  }, [leaves, filterTab]);

  return (
    <div className="space-y-5">
      <PageHeader
        title="Leave Management"
        description="Leave policies, automated accruals, balance tracking, and manager approval queues."
        actions={
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm" onClick={() => refetch()}>
              <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
              Refresh
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={() => setIsApplyModalOpen(true)}
              className="bg-accent text-white hover:bg-accent/90"
            >
              <Plus className="h-4 w-4 mr-1" aria-hidden />
              Apply for Leave
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => (window.location.href = '/employee-portal')}
            >
              <ArrowUpRight className="h-3.5 w-3.5 mr-1 text-text-muted" />
              Employee Portal
            </Button>
          </div>
        }
      />

      {/* Metrics Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard label="Total Requests" value={String(totalRequests)} detail="Recorded in audit ledger" />
        <MetricCard
          label="Pending Review"
          value={String(pendingCount)}
          change={{
            value: pendingCount > 0 ? 'Requires Action' : 'All Clear',
            direction: pendingCount > 0 ? 'neutral' : 'up',
            isPositive: pendingCount === 0,
          }}
          detail="Manager decision queue"
        />
        <MetricCard label="Approved Requests" value={String(approvedCount)} detail="Entitlement granted" />
        <MetricCard label="Total Days Requested" value={`${totalDays.toFixed(1)}d`} detail="Across all departments" />
      </div>

      {/* Main Leave Table Card */}
      <Card padding="none">
        <div className="px-5 pt-5 pb-3 border-b border-border flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-accent" aria-hidden />
            Organization Leave Applications &amp; Approval Status
          </CardTitle>

          {/* Filter Tabs */}
          <div className="flex items-center gap-1 bg-surface-secondary p-1 rounded-lg border border-border text-xs">
            {(['ALL', 'PENDING', 'APPROVED', 'REJECTED'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setFilterTab(tab)}
                className={`px-2.5 py-1 rounded-md font-medium transition ${
                  filterTab === tab
                    ? 'bg-surface text-text-primary shadow-xs'
                    : 'text-text-muted hover:text-text-primary'
                }`}
              >
                {tab === 'ALL' ? 'All' : tab.charAt(0) + tab.slice(1).toLowerCase()}
                {tab === 'PENDING' && pendingCount > 0 && (
                  <span className="ml-1 px-1.5 py-0.2 rounded-full bg-warning/20 text-warning text-2xs font-bold">
                    {pendingCount}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Employee</TableHead>
              <TableHead>Department</TableHead>
              <TableHead>Leave Type</TableHead>
              <TableHead>Dates</TableHead>
              <TableHead className="text-right">Duration</TableHead>
              <TableHead>Reason</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-8 text-text-muted">
                  Loading real-time leave requests...
                </TableCell>
              </TableRow>
            ) : filteredLeaves.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-8 text-text-muted">
                  No leave applications found for this filter.
                </TableCell>
              </TableRow>
            ) : (
              filteredLeaves.map((lv) => {
                const statusUpper = (lv.status || 'PENDING').toUpperCase();
                const isPending = statusUpper === 'PENDING';
                const empName = lv.first_name
                  ? `${lv.first_name} ${lv.last_name || ''}`.trim()
                  : lv.employee_id;

                return (
                  <TableRow key={lv.id}>
                    <TableCell className="font-medium text-text-primary">
                      <div>
                        <div>{empName}</div>
                        {lv.employee_code && (
                          <div className="text-2xs text-text-muted font-mono">{lv.employee_code}</div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="text-text-muted text-xs">
                      {lv.department_name || 'Engineering'}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" size="sm">
                        {formatLeaveType(lv.leave_type_id)}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-mono text-xs text-text-secondary whitespace-nowrap">
                      {lv.start_date} → {lv.end_date}
                    </TableCell>
                    <TableCell className="text-right font-mono text-xs font-semibold text-text-primary">
                      {lv.days_count}d {lv.is_half_day ? '(Half Day)' : ''}
                    </TableCell>
                    <TableCell className="text-text-secondary text-xs max-w-xs truncate" title={lv.reason}>
                      {lv.reason || 'Personal leave'}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          statusUpper === 'APPROVED'
                            ? 'success'
                            : statusUpper === 'REJECTED'
                            ? 'danger'
                            : 'warning'
                        }
                        size="sm"
                      >
                        {statusUpper}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      {isPending ? (
                        <div className="flex items-center justify-end gap-1.5">
                          <button
                            onClick={() => decisionMutation.mutate({ id: lv.id, status: 'APPROVED' })}
                            disabled={decisionMutation.isPending}
                            className="inline-flex items-center gap-1 text-2xs font-semibold px-2 py-1 rounded bg-emerald-500/10 text-emerald-600 hover:bg-emerald-500/20 border border-emerald-500/30 transition"
                          >
                            <CheckCircle className="h-3 w-3" />
                            Approve
                          </button>
                          <button
                            onClick={() => decisionMutation.mutate({ id: lv.id, status: 'REJECTED' })}
                            disabled={decisionMutation.isPending}
                            className="inline-flex items-center gap-1 text-2xs font-semibold px-2 py-1 rounded bg-rose-500/10 text-rose-600 hover:bg-rose-500/20 border border-rose-500/30 transition"
                          >
                            <XCircle className="h-3 w-3" />
                            Reject
                          </button>
                        </div>
                      ) : (
                        <span className="text-2xs text-text-muted">
                          {lv.approved_by ? `By ${lv.approved_by}` : 'Decided'}
                        </span>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </Card>

      {/* Apply for Leave Modal */}
      {isApplyModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-surface border border-border rounded-xl max-w-md w-full p-6 shadow-2xl space-y-4 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-accent/10 text-accent flex items-center justify-center">
                  <Calendar className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-semibold text-text-primary text-base">Apply for Leave</h3>
                  <p className="text-2xs text-text-muted">Direct SQLite core ledger submission</p>
                </div>
              </div>
              <button
                onClick={() => setIsApplyModalOpen(false)}
                className="text-text-muted hover:text-text-primary transition"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {formFeedback && (
              <div className="p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-600 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{formFeedback.text}</span>
              </div>
            )}

            <form
              onSubmit={(e) => {
                e.preventDefault();
                applyLeaveMutation.mutate();
              }}
              className="space-y-3.5"
            >
              {/* Employee Selector */}
              <div>
                <label className="text-xs font-medium text-text-secondary">Employee</label>
                <select
                  value={selectedEmpId}
                  onChange={(e) => setSelectedEmpId(e.target.value)}
                  className="w-full h-8 px-2.5 text-xs bg-surface border border-border rounded-lg text-text-primary focus:outline-none focus:ring-1 focus:ring-accent mt-1"
                >
                  {employees.length === 0 ? (
                    <option value="emp-001">Vikram Aditya (EMP-001)</option>
                  ) : (
                    employees.map((emp) => (
                      <option key={emp.id} value={emp.id}>
                        {emp.first_name} {emp.last_name} ({emp.employee_code})
                      </option>
                    ))
                  )}
                </select>
              </div>

              {/* Leave Type */}
              <div>
                <label className="text-xs font-medium text-text-secondary">Leave Type</label>
                <select
                  value={leaveType}
                  onChange={(e) => setLeaveType(e.target.value)}
                  className="w-full h-8 px-2.5 text-xs bg-surface border border-border rounded-lg text-text-primary focus:outline-none focus:ring-1 focus:ring-accent mt-1"
                >
                  <option value="lt-annual">Annual Leave (PTO)</option>
                  <option value="lt-sick">Sick Leave</option>
                  <option value="lt-casual">Casual Leave</option>
                  <option value="lt-maternity">Maternity Leave</option>
                </select>
              </div>

              {/* Dates */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-text-secondary">Start Date</label>
                  <input
                    type="date"
                    required
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full h-8 px-2.5 text-xs bg-surface border border-border rounded-lg text-text-primary focus:outline-none focus:ring-1 focus:ring-accent mt-1"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-text-secondary">End Date</label>
                  <input
                    type="date"
                    required
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full h-8 px-2.5 text-xs bg-surface border border-border rounded-lg text-text-primary focus:outline-none focus:ring-1 focus:ring-accent mt-1"
                  />
                </div>
              </div>

              {/* Half Day Toggle */}
              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="half-day-check"
                  checked={isHalfDay}
                  onChange={(e) => setIsHalfDay(e.target.checked)}
                  className="rounded border-border text-accent focus:ring-accent"
                />
                <label htmlFor="half-day-check" className="text-xs text-text-secondary cursor-pointer">
                  Half-day leave (0.5 days count)
                </label>
              </div>

              {/* Reason */}
              <div>
                <label className="text-xs font-medium text-text-secondary">Reason / Notes</label>
                <textarea
                  rows={2}
                  placeholder="e.g. Annual family vacation, medical appointment..."
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  className="w-full p-2.5 text-xs bg-surface border border-border rounded-lg text-text-primary focus:outline-none focus:ring-1 focus:ring-accent mt-1 resize-none"
                />
              </div>

              {/* Submit Buttons */}
              <div className="flex items-center justify-end gap-2 pt-2 border-t border-border">
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  onClick={() => setIsApplyModalOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  size="sm"
                  disabled={applyLeaveMutation.isPending}
                  className="bg-accent text-white"
                >
                  {applyLeaveMutation.isPending ? 'Submitting...' : 'Submit Leave Request'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
