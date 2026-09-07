import React from 'react';
import { CreditCard, FileText, Download, ShieldCheck } from 'lucide-react';
import { PageHeader, Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table';
import { useEmployee } from '@/context/EmployeeContext';

export const PayrollView: React.FC = () => {
  const { payslips, setSelectedPayslip, latestPayslip, formatCurrency } = useEmployee();

  return (
    <div className="space-y-6 animate-in fade-in duration-150">
      <PageHeader
        title="Payroll & Payslips"
        description="Official salary statements, direct deposit confirmations, and statutory deduction schedules."
      />

      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="p-4">
          <p className="text-xs text-text-muted font-medium">Latest Net Payout</p>
          <p className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400 mt-1">
            {latestPayslip ? formatCurrency(latestPayslip.net_salary) : '$0.00'}
          </p>
          <p className="text-xs text-text-muted mt-0.5">
            {latestPayslip ? `Disbursed on ${latestPayslip.disbursed_at}` : 'Awaiting payroll'}
          </p>
        </Card>

        <Card className="p-4">
          <p className="text-xs text-text-muted font-medium">Payment Channel</p>
          <p className="text-lg font-bold text-text-primary mt-1 flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-emerald-500" />
            <span>Direct ACH Deposit</span>
          </p>
          <p className="text-xs text-text-muted mt-0.5">Automated clearing house tier 1</p>
        </Card>

        <Card className="p-4">
          <p className="text-xs text-text-muted font-medium">Withholding &amp; Taxes</p>
          <p className="text-lg font-bold font-mono text-text-primary mt-1">
            {latestPayslip ? formatCurrency(latestPayslip.tax) : '$0.00'}
          </p>
          <p className="text-xs text-text-muted mt-0.5">Federal &amp; State tax withholding</p>
        </Card>
      </div>

      {/* Payslips Table */}
      <Card padding="none">
        <CardHeader className="px-5 pt-5 pb-3 flex flex-row items-center justify-between">
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            <CreditCard className="h-4 w-4 text-accent" />
            Earnings History &amp; Official Receipts
          </CardTitle>
          <span className="text-xs text-text-muted font-mono">
            Records: <strong className="text-text-primary">{payslips.length}</strong>
          </span>
        </CardHeader>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Pay Period</TableHead>
              <TableHead className="text-right">Gross Salary</TableHead>
              <TableHead className="text-right">Deductions</TableHead>
              <TableHead className="text-right">Tax Withholding</TableHead>
              <TableHead className="text-right">Net Take-Home</TableHead>
              <TableHead>Disbursed Date</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {payslips.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-8 text-text-muted italic">
                  No payslips found for active profile.
                </TableCell>
              </TableRow>
            ) : (
              payslips.map((ps) => (
                <TableRow key={ps.id}>
                  <TableCell className="font-semibold text-xs text-text-primary">{ps.period}</TableCell>
                  <TableCell className="text-right font-mono text-xs text-text-primary">
                    ${Number(ps.gross_salary).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </TableCell>
                  <TableCell className="text-right font-mono text-xs text-rose-600 dark:text-rose-400">
                    -${Number(ps.deductions).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </TableCell>
                  <TableCell className="text-right font-mono text-xs text-rose-600 dark:text-rose-400">
                    -${Number(ps.tax).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </TableCell>
                  <TableCell className="text-right font-mono text-xs font-bold text-emerald-600 dark:text-emerald-400">
                    ${Number(ps.net_salary).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </TableCell>
                  <TableCell className="font-mono text-xs text-text-muted">{ps.disbursed_at}</TableCell>
                  <TableCell>
                    <Badge variant="success" size="sm">
                      {ps.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => setSelectedPayslip(ps)}
                      className="gap-1 text-xs"
                    >
                      <FileText className="h-3.5 w-3.5 text-accent" />
                      <span>View Receipt</span>
                    </Button>
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
