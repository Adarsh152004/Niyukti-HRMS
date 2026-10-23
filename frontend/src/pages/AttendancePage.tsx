import * as React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Clock, RefreshCw } from 'lucide-react';
import { PageHeader, Card, CardHeader, CardTitle, MetricCard } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table';

interface AttendanceRecord {
  employee_id: string;
  employee_code: string;
  first_name: string;
  last_name: string;
  email: string;
  location?: string;
  department_name?: string;
  designation_title?: string;
  attendance_id?: string;
  record_date?: string;
  check_in?: string;
  check_out?: string;
  status?: string;
  source?: string;
  overtime_hours?: number;
  remarks?: string;
}

export function AttendancePage() {
  const { data: records, isLoading, refetch } = useQuery<AttendanceRecord[]>({
    queryKey: ['attendance-list'],
    queryFn: async () => {
      const res = await fetch('/api/v1/attendance');
      if (!res.ok) throw new Error('Failed to fetch attendance records');
      const json = await res.json();
      return json.data || [];
    },
    refetchInterval: 10000,
  });

  const totalEmployees = records?.length || 0;
  const presentCount = records?.filter((r) => !!r.check_in).length || 0;
  const remoteCount = records?.filter((r) => (r.location || '').toLowerCase().includes('remote')).length || 0;
  const attendanceRate = totalEmployees > 0 ? Math.round((presentCount / totalEmployees) * 100) : 0;

  const todayStr = new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

  return (
    <div className="space-y-5">
      <PageHeader
        title="Attendance & Time Management"
        description="Daily check-ins, biometric sync, remote verification, and anomaly detection."
        actions={
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm" onClick={() => refetch()}>
              <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
              Today: {todayStr}
            </Button>
            <Button variant="primary" size="sm">Export Timesheet</Button>
          </div>
        }
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard
          label="Present Today"
          value={`${presentCount} / ${totalEmployees}`}
          change={{ value: `${attendanceRate}%`, direction: 'up', isPositive: true }}
          detail="Workforce logged in"
        />
        <MetricCard label="Remote / Hybrid" value={String(remoteCount)} detail="Flexible location staff" />
        <MetricCard label="On Approved Leave" value="0" detail="Vacation, sick, parental" />
        <MetricCard label="Attendance Anomalies" value="0" change={{ value: 'Resolved', direction: 'neutral', isPositive: true }} detail="Zero missed clock-outs" />
      </div>

      <Card padding="none">
        <CardHeader className="px-5 pt-5 pb-3">
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-accent" aria-hidden />
            Today's Attendance &amp; Check-in Log
          </CardTitle>
        </CardHeader>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Employee</TableHead>
              <TableHead>Work Mode / Location</TableHead>
              <TableHead>Check-In Time</TableHead>
              <TableHead>Check-Out Time</TableHead>
              <TableHead>Effective Hours</TableHead>
              <TableHead>Verification Method</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8 text-text-muted">
                  Loading real-time attendance records...
                </TableCell>
              </TableRow>
            ) : records?.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8 text-text-muted">
                  No attendance records found for today.
                </TableCell>
              </TableRow>
            ) : (
              records?.map((rec) => {
                const formatTime = (tStr?: string) => {
                  if (!tStr) return null;
                  try {
                    const d = new Date(tStr.includes(' ') && !tStr.includes('T') ? tStr.replace(' ', 'T') : tStr);
                    if (isNaN(d.getTime())) return tStr;
                    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
                  } catch {
                    return tStr;
                  }
                };

                const calcEffectiveHours = (ci?: string, co?: string) => {
                  if (!ci) return '—';
                  const d1 = new Date(ci.includes(' ') && !ci.includes('T') ? ci.replace(' ', 'T') : ci);
                  const d2 = co ? new Date(co.includes(' ') && !co.includes('T') ? co.replace(' ', 'T') : co) : new Date();
                  if (isNaN(d1.getTime()) || isNaN(d2.getTime())) return '—';
                  const diffMs = Math.max(0, d2.getTime() - d1.getTime());
                  const hrs = Math.floor(diffMs / (1000 * 60 * 60));
                  const mins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
                  return `${hrs}h ${mins}m`;
                };

                const isPresent = !!rec.check_in;
                const isClockedOut = !!rec.check_out;

                return (
                  <TableRow key={rec.employee_id}>
                    <TableCell>
                      <div>
                        <p className="font-semibold text-text-primary text-sm">{rec.first_name} {rec.last_name}</p>
                        <p className="text-xs text-text-muted">{rec.employee_code} • {rec.department_name || 'General'}</p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className="text-xs text-text-secondary">{rec.location || 'HQ Office'}</span>
                    </TableCell>
                    <TableCell className="font-mono text-xs text-text-primary">
                      {rec.check_in ? formatTime(rec.check_in) : <span className="text-text-muted">—</span>}
                    </TableCell>
                    <TableCell className="font-mono text-xs text-text-muted">
                      {rec.check_out ? (
                        formatTime(rec.check_out)
                      ) : isPresent ? (
                        <span className="text-emerald-500 font-semibold flex items-center gap-1">
                          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                          In Progress
                        </span>
                      ) : (
                        '—'
                      )}
                    </TableCell>
                    <TableCell className="font-mono text-xs font-semibold text-text-primary">
                      {calcEffectiveHours(rec.check_in, rec.check_out)}
                    </TableCell>
                    <TableCell>
                      <span className="text-2xs bg-surface-secondary px-1.5 py-0.5 rounded border border-border text-text-muted">
                        {rec.source === 'PORTAL' ? 'Employee Portal' : rec.source === 'BIOMETRIC' ? 'Biometric Gate' : (rec.location || '').toLowerCase().includes('remote') ? 'Remote SSO' : 'Office Biometric'}
                      </span>
                    </TableCell>
                    <TableCell>
                      <Badge variant={isPresent ? 'success' : 'default'} size="sm">
                        {isClockedOut ? 'Completed' : isPresent ? 'Present' : 'Not Checked In'}
                      </Badge>
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
