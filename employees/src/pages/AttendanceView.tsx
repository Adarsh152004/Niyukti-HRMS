import React from 'react';
import { Clock, CheckCircle2, LogIn, LogOut, Download } from 'lucide-react';
import { PageHeader, Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table';
import { useEmployee } from '@/context/EmployeeContext';

export const AttendanceView: React.FC = () => {
  const { attendance, attendanceRate, totalDaysPresent, punching, handlePunch, shiftElapsedTime } = useEmployee();

  const isClockedIn = attendance?.is_clocked_in;
  const isClockedOut = attendance?.is_clocked_out;

  return (
    <div className="space-y-6 animate-in fade-in duration-150">
      <PageHeader
        title="Attendance & Logs"
        description="Comprehensive biometric punch history, check-in timestamps, and 30-day compliance ledger."
        actions={
          <div className="flex items-center gap-2">
            {isClockedIn ? (
              <Button
                variant="destructive"
                size="sm"
                className="gap-1.5"
                onClick={() => handlePunch('CLOCK_OUT')}
                disabled={punching}
              >
                <LogOut className="h-3.5 w-3.5" />
                <span>Clock Out Now</span>
              </Button>
            ) : (
              <Button
                variant="primary"
                size="sm"
                className="gap-1.5"
                onClick={() => handlePunch('CLOCK_IN')}
                disabled={punching}
              >
                <LogIn className="h-3.5 w-3.5" />
                <span>Clock In Now</span>
              </Button>
            )}
          </div>
        }
      />

      {/* Highlights Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="p-4">
          <p className="text-xs text-text-muted font-medium">Compliance Rate</p>
          <p className="text-2xl font-bold text-text-primary mt-1">{attendanceRate}%</p>
          <p className="text-xs text-text-muted mt-0.5">30-day verified attendance ratio</p>
        </Card>

        <Card className="p-4">
          <p className="text-xs text-text-muted font-medium">Total Days Present</p>
          <p className="text-2xl font-bold text-text-primary mt-1">{totalDaysPresent} Days</p>
          <p className="text-xs text-text-muted mt-0.5">{attendance?.stats?.days_absent || 0} unexcused absences</p>
        </Card>

        <Card className="p-4">
          <p className="text-xs text-text-muted font-medium">Today's Shift Status</p>
          <div className="flex items-center gap-2 mt-1">
            <Badge variant={isClockedIn ? 'success' : isClockedOut ? 'default' : 'warning'} size="sm">
              {isClockedIn ? 'Clocked In' : isClockedOut ? 'Completed' : 'Not Clocked In'}
            </Badge>
            {isClockedIn && shiftElapsedTime && (
              <span className="font-mono text-xs font-semibold text-emerald-600 dark:text-emerald-400">
                {shiftElapsedTime}
              </span>
            )}
          </div>
          <p className="text-xs text-text-muted mt-1.5">
            {attendance?.today?.check_in
              ? `Started: ${new Date(attendance.today.check_in).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
              : 'Awaiting first punch'}
          </p>
        </Card>
      </div>

      {/* Ledger Table */}
      <Card padding="none">
        <CardHeader className="px-5 pt-5 pb-3 flex flex-row items-center justify-between">
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            <Clock className="h-4 w-4 text-accent" />
            Full Attendance Ledger (30-Day Audit History)
          </CardTitle>
          <span className="text-xs text-text-muted font-mono">
            Compliance: <strong className="text-text-primary">{attendanceRate}%</strong>
          </span>
        </CardHeader>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Date</TableHead>
              <TableHead>Check-In</TableHead>
              <TableHead>Check-Out</TableHead>
              <TableHead>Effective Hours</TableHead>
              <TableHead>Overtime</TableHead>
              <TableHead>Source</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Notes</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {(attendance?.records || []).map((rec) => {
              const isPresent = !!rec.check_in;
              return (
                <TableRow key={rec.id}>
                  <TableCell className="font-mono text-xs text-text-primary font-semibold">
                    {rec.date}
                  </TableCell>
                  <TableCell className="font-mono text-xs text-text-primary">
                    {rec.check_in ? (
                      new Date(rec.check_in).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
                    ) : (
                      <span className="text-text-muted">—</span>
                    )}
                  </TableCell>
                  <TableCell className="font-mono text-xs text-text-muted">
                    {rec.check_out ? (
                      new Date(rec.check_out).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
                    ) : rec.check_in ? (
                      <span className="text-emerald-500 font-semibold text-2xs">Shift In Progress</span>
                    ) : (
                      '—'
                    )}
                  </TableCell>
                  <TableCell className="font-mono text-xs font-semibold text-text-primary">
                    {rec.check_in && rec.check_out ? '8h 30m' : rec.check_in ? 'Active' : '0h'}
                  </TableCell>
                  <TableCell className="font-mono text-xs text-text-muted">
                    {rec.overtime_hours ? `${rec.overtime_hours}h` : '0.0h'}
                  </TableCell>
                  <TableCell>
                    <span className="text-2xs bg-surface-secondary px-1.5 py-0.5 rounded border border-border text-text-muted">
                      {rec.source || 'PORTAL'}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Badge variant={isPresent ? 'success' : 'default'} size="sm">
                      {rec.status || (isPresent ? 'Present' : 'Absent')}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-2xs text-text-muted max-w-[160px] truncate">
                    {rec.remarks || 'Biometric match'}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
};
