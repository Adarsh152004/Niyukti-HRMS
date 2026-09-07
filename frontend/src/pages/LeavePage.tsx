import * as React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Calendar, Plus, CheckCircle, XCircle, RefreshCw, Clock } from 'lucide-react';
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

export function LeavePage() {
  const queryClient = useQueryClient();

  const { data: leaves, isLoading, refetch } = useQuery<LeaveRecord[]>({
    queryKey: ['leave-requests'],
    queryFn: async () => {
      const res = await fetch('/api/v1/leaves');
      if (!res.ok) throw new Error('Failed to fetch leave requests');
      const json = await res.json();
      return json.data || [];
    },
    refetchInterval: 10000,
  });

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
            <Button variant="primary" size="sm" onClick={() => window.location.href = '/employee-portal'}>
              <Plus className="h-4 w-4 mr-1" aria-hidden />
              Employee Portal Request
            </Button>
          </div>
        }
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard label="Total Requests" value={String(totalRequests)} detail="Recorded in audit ledger" />
        <MetricCard
          label="Pending Review"
          value={String(pendingCount)}
          change={{ value: pendingCount > 0 ? 'Requires Action' : 'All Clear', direction: pendingCount > 0 ? 'neutral' : 'up', isPositive: pendingCount === 0 }}
          detail="Manager decision queue"
        />
        <MetricCard label="Approved Requests" value={String(approvedCount)} detail="Entitlement granted" />
        <MetricCard label="Total Days Requested" value={`${totalDays}d`} detail="Across all departments" />
      </div>

      <Card padding="none">
        <CardHeader className="px-5 pt-5 pb-3">
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-accent" aria-hidden />
            Organization Leave Applications &amp; Approval Status
          </CardTitle>
        </CardHeader>
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
            ) : leaves?.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-8 text-text-muted">
                  No leave applications recorded in database.
                </TableCell>
              </TableRow>
            ) : (
              leaves?.map((lv) => {
                const statusUpper = (lv.status || 'PENDING').toUpperCase();
                const isPending = statusUpper === 'PENDING';

                return (
                  <TableRow key={lv.id}>
                    <TableCell>
                      <div>
                        <p className="font-semibold text-text-primary text-sm">
                          {lv.first_name ? `${lv.first_name} ${lv.last_name}` : lv.employee_id}
                        </p>
                        <p className="text-xs text-text-muted">{lv.employee_code || lv.employee_id}</p>
                      </div>
                    </TableCell>
                    <TableCell className="text-xs text-text-secondary">
                      {lv.department_name || 'Engineering'}
                    </TableCell>
                    <TableCell>
                      <Badge variant="default" size="sm">
                        {formatLeaveType(lv.leave_type_id)}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-xs font-mono text-text-primary">
                      {lv.start_date} → {lv.end_date}
                    </TableCell>
                    <TableCell className="text-right text-xs font-semibold text-text-primary">
                      {lv.days_count}d
                    </TableCell>
                    <TableCell className="text-xs text-text-muted max-w-[200px] truncate" title={lv.reason}>
                      {lv.reason}
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
    </div>
  );
}
