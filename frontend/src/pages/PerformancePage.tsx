import * as React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Target, TrendingUp, Award, Users, CheckCircle } from 'lucide-react';
import { PageHeader, Card, CardHeader, CardTitle, MetricCard } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table';
import { withDataProvider } from '@/providers/data-provider';
import { DEMO_EMPLOYEES } from '@/fixtures';
import { apiClient } from '@/api/client';

export function PerformancePage() {
  const { data: employees } = useQuery({
    queryKey: ['perf-employees'],
    queryFn: () =>
      withDataProvider(
        async () => {
          const res = await apiClient<{ data: any[] }>('/employees');
          return res.data || [];
        },
        DEMO_EMPLOYEES
      ),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        title="Performance &amp; OKR Calibration"
        description="Review cycles, 360 peer evaluations, calibrated rating distributions, and goal tracking."
        actions={
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm">Cycle: Q3 2026</Button>
            <Button variant="primary" size="sm">Calibrate Ratings</Button>
          </div>
        }
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard label="Review Cycle Completion" value="84.2%" change={{ value: '+12%', direction: 'up', isPositive: true }} detail="Q3 2026 cycle" />
        <MetricCard label="Company OKR Progress" value="78.5%" detail="On track for Q3" />
        <MetricCard label="Calibrated Rating Distribution" value="Normal" detail="Zero skew detected" />
        <MetricCard label="Promotions Recommended" value="14" detail="Awaiting calibration" />
      </div>

      <Card padding="none">
        <CardHeader className="px-5 pt-5 pb-3">
          <CardTitle className="flex items-center gap-2">
            <Target className="h-4 w-4 text-accent" aria-hidden />
            Employee Performance &amp; Goal Progress Overview
          </CardTitle>
        </CardHeader>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Employee</TableHead>
              <TableHead>Department</TableHead>
              <TableHead>Current Rating</TableHead>
              <TableHead className="text-right">OKR Progress</TableHead>
              <TableHead>360 Feedback Status</TableHead>
              <TableHead>Calibration Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {employees?.map((emp, i) => {
              const rating = i === 0 ? 'Exceeds Expectations' : i === 1 ? 'Exceeds Expectations' : i === 7 ? 'Needs Improvement' : 'Meets Expectations';
              const ratingVariant = rating === 'Exceeds Expectations' ? 'success' : rating === 'Needs Improvement' ? 'danger' : 'default';
              const okr = 75 + ((i * 7) % 24);

              return (
                <TableRow key={emp.id}>
                  <TableCell>
                    <div>
                      <p className="font-semibold text-text-primary text-sm">{emp.full_name}</p>
                      <p className="text-xs text-text-muted">{emp.designation}</p>
                    </div>
                  </TableCell>
                  <TableCell className="text-xs text-text-secondary">{emp.department}</TableCell>
                  <TableCell>
                    <Badge variant={ratingVariant} size="sm">{rating}</Badge>
                  </TableCell>
                  <TableCell className="text-right font-mono font-semibold text-xs text-text-primary">
                    {okr}%
                  </TableCell>
                  <TableCell>
                    <span className="text-xs text-text-muted">4/4 Received</span>
                  </TableCell>
                  <TableCell>
                    <Badge variant="default" size="sm">Calibrated</Badge>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
