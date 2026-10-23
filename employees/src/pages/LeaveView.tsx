import React from 'react';
import { Calendar, Plus, Clock, CheckCircle2, AlertCircle } from 'lucide-react';
import { PageHeader, Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table';
import { useEmployee } from '@/context/EmployeeContext';

export const LeaveView: React.FC = () => {
  const { leaveData, totalLeaveAvailable, setShowLeaveModal } = useEmployee();

  return (
    <div className="space-y-6 animate-in fade-in duration-150">
      <PageHeader
        title="Leave & PTO Hub"
        description="Submit paid time off requests, check statutory accruals, and monitor department head approval queues."
        actions={
          <Button variant="primary" size="sm" onClick={() => setShowLeaveModal(true)} className="gap-1.5">
            <Plus className="h-3.5 w-3.5" />
            <span>Apply for Leave</span>
          </Button>
        }
      />

      {/* Balance Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Annual Leave */}
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-text-muted">Annual Vacation</span>
            <span className="text-xs font-semibold text-accent">Accrued</span>
          </div>
          <p className="text-2xl font-bold text-text-primary mt-1">
            {leaveData?.balances?.annual?.available ?? 18} <span className="text-sm font-normal text-text-muted">days</span>
          </p>
          <div className="h-2 rounded-full bg-surface-secondary overflow-hidden border border-border mt-3">
            <div
              className="h-full bg-accent rounded-full"
              style={{
                width: `${Math.min(
                  100,
                  (((leaveData?.balances?.annual?.available ?? 18) / (leaveData?.balances?.annual?.total ?? 20)) * 100)
                )}%`,
              }}
            />
          </div>
          <p className="text-2xs text-text-muted mt-2">
            Used: {leaveData?.balances?.annual?.used ?? 2}d / Total: {leaveData?.balances?.annual?.total ?? 20}d
          </p>
        </Card>

        {/* Sick Leave */}
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-text-muted">Sick & Medical</span>
            <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400">Available</span>
          </div>
          <p className="text-2xl font-bold text-text-primary mt-1">
            {leaveData?.balances?.sick?.available ?? 10} <span className="text-sm font-normal text-text-muted">days</span>
          </p>
          <div className="h-2 rounded-full bg-surface-secondary overflow-hidden border border-border mt-3">
            <div
              className="h-full bg-emerald-500 rounded-full"
              style={{
                width: `${Math.min(
                  100,
                  (((leaveData?.balances?.sick?.available ?? 10) / (leaveData?.balances?.sick?.total ?? 10)) * 100)
                )}%`,
              }}
            />
          </div>
          <p className="text-2xs text-text-muted mt-2">
            Used: {leaveData?.balances?.sick?.used ?? 0}d / Total: {leaveData?.balances?.sick?.total ?? 10}d
          </p>
        </Card>

        {/* Casual Leave */}
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-text-muted">Casual / Personal</span>
            <span className="text-xs font-semibold text-amber-600 dark:text-amber-400">Flexible</span>
          </div>
          <p className="text-2xl font-bold text-text-primary mt-1">
            {leaveData?.balances?.casual?.available ?? 6} <span className="text-sm font-normal text-text-muted">days</span>
          </p>
          <div className="h-2 rounded-full bg-surface-secondary overflow-hidden border border-border mt-3">
            <div
              className="h-full bg-amber-500 rounded-full"
              style={{
                width: `${Math.min(
                  100,
                  (((leaveData?.balances?.casual?.available ?? 6) / (leaveData?.balances?.casual?.total ?? 6)) * 100)
                )}%`,
              }}
            />
          </div>
          <p className="text-2xs text-text-muted mt-2">
            Used: {leaveData?.balances?.casual?.used ?? 0}d / Total: {leaveData?.balances?.casual?.total ?? 6}d
          </p>
        </Card>
      </div>

      {/* Requests History Table */}
      <Card padding="none">
        <CardHeader className="px-5 pt-5 pb-3 flex flex-row items-center justify-between">
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            <Calendar className="h-4 w-4 text-accent" />
            Submitted Applications &amp; Status
          </CardTitle>
          <span className="text-xs text-text-muted font-mono">
            Total Available: <strong className="text-text-primary">{totalLeaveAvailable} days</strong>
          </span>
        </CardHeader>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Type</TableHead>
              <TableHead>Dates</TableHead>
              <TableHead className="text-right">Days</TableHead>
              <TableHead>Reason</TableHead>
              <TableHead>Decision / Status</TableHead>
              <TableHead>Reviewed By</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {(leaveData?.requests || []).length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center py-8 text-text-muted italic">
                  No leave requests filed yet. Click "Apply for Leave" above.
                </TableCell>
              </TableRow>
            ) : (
              (leaveData?.requests || []).map((req) => (
                <TableRow key={req.id}>
                  <TableCell className="font-medium text-xs text-text-primary">
                    {req.leave_type_id === 'lt-annual'
                      ? 'Annual Leave'
                      : req.leave_type_id === 'lt-sick'
                      ? 'Sick Leave'
                      : req.leave_type_id === 'lt-casual'
                      ? 'Casual Leave'
                      : req.leave_type_id}
                  </TableCell>
                  <TableCell className="font-mono text-xs text-text-primary">
                    {req.start_date} → {req.end_date}
                  </TableCell>
                  <TableCell className="text-right font-mono text-xs font-semibold text-text-primary">
                    {req.days_count}d
                  </TableCell>
                  <TableCell className="text-xs text-text-muted max-w-[220px] truncate">
                    {req.reason}
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        req.status === 'APPROVED'
                          ? 'success'
                          : req.status === 'REJECTED'
                          ? 'danger'
                          : 'warning'
                      }
                      size="sm"
                    >
                      {req.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-xs text-text-muted">
                    {req.approved_by || 'Pending Manager Review'}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
};
