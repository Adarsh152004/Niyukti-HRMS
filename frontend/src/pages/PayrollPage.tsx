import * as React from 'react';
import { useQuery } from '@tanstack/react-query';
import { CreditCard, Download, CheckCircle, AlertCircle, FileCheck, ShieldAlert } from 'lucide-react';
import { PageHeader, Card, CardHeader, CardTitle, MetricCard } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge, StatusBadge } from '@/components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table';
import { withDataProvider } from '@/providers/data-provider';
import { DEMO_EMPLOYEES } from '@/fixtures';

export function PayrollPage() {
  const { data: employees } = useQuery({
    queryKey: ['payroll-employees'],
    queryFn: () => withDataProvider(async () => { throw new Error(); }, DEMO_EMPLOYEES),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        title="Payroll & Compensation Management"
        description="Deterministic calculation engine, statutory withholding (EPF/TDS/ESI), anomaly verification, and direct disbursement."
        actions={
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm">
              <Download className="h-3.5 w-3.5" aria-hidden />
              Download Bank File
            </Button>
            <Button variant="primary" size="sm">
              Run Batch Verification
            </Button>
          </div>
        }
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard label="August 2026 Payroll Total" value="$3,420,500" detail="936 active personnel" />
        <MetricCard label="Statutory Deductions" value="$684,100" detail="Tax, EPF, Health fund" />
        <MetricCard label="Deterministic Engine" value="100% Match" change={{ value: '0 variances', direction: 'up', isPositive: true }} detail="Rule engine audited" />
        <MetricCard label="Wire Approval State" value="Pending Gate" detail="Awaiting executive sign-off" />
      </div>

      <Card padding="none">
        <CardHeader className="px-5 pt-5 pb-3">
          <CardTitle className="flex items-center gap-2">
            <FileCheck className="h-4 w-4 text-accent" aria-hidden />
            Current Period Employee Compensation Breakdown (Deterministic Engine)
          </CardTitle>
        </CardHeader>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Employee</TableHead>
              <TableHead>Band / Dept</TableHead>
              <TableHead className="text-right">Monthly Base</TableHead>
              <TableHead className="text-right">Statutory EPF / PF</TableHead>
              <TableHead className="text-right">Tax Withholding</TableHead>
              <TableHead className="text-right">Net Payable</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="w-20"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {employees?.map((emp) => {
              const monthlyBase = Math.round(emp.salary / 12);
              const epf = Math.round(monthlyBase * 0.12);
              const tax = Math.round(monthlyBase * 0.18);
              const net = monthlyBase - epf - tax;

              return (
                <TableRow key={emp.id}>
                  <TableCell>
                    <div>
                      <p className="font-semibold text-text-primary text-sm">{emp.full_name}</p>
                      <p className="text-xs text-text-muted">{emp.employee_number}</p>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-xs">
                      <span className="font-semibold text-text-primary">{emp.band}</span> · {emp.department}
                    </div>
                  </TableCell>
                  <TableCell className="text-right font-mono text-sm">${monthlyBase.toLocaleString()}</TableCell>
                  <TableCell className="text-right font-mono text-xs text-text-muted">${epf.toLocaleString()}</TableCell>
                  <TableCell className="text-right font-mono text-xs text-text-muted">${tax.toLocaleString()}</TableCell>
                  <TableCell className="text-right font-mono font-semibold text-sm text-text-primary">
                    ${net.toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <Badge variant="success" size="sm">Calculated</Badge>
                  </TableCell>
                  <TableCell>
                    <Button variant="ghost" size="xs" className="text-accent">
                      Payslip
                    </Button>
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
