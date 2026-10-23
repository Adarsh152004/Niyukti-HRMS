import React from 'react';
import { X, Printer } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useEmployee } from '@/context/EmployeeContext';

export const PayslipModal: React.FC = () => {
  const { selectedPayslip, setSelectedPayslip, profile, actorId } = useEmployee();

  if (!selectedPayslip) return null;

  const employeeDisplayName = profile ? `${profile.first_name} ${profile.last_name}` : actorId;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in">
      <div className="w-full max-w-lg bg-surface border border-border rounded-2xl shadow-2xl p-6 relative">
        <button
          onClick={() => setSelectedPayslip(null)}
          className="absolute right-4 top-4 text-text-muted hover:text-text-primary transition"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="border-b border-border pb-4 mb-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-text-primary">NOVA CORP INTERNATIONAL</h3>
              <p className="text-2xs text-text-muted">Official Salary Certificate &amp; Earnings Statement</p>
            </div>
            <Badge variant="success" size="sm">
              PAID &amp; SETTLED
            </Badge>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 text-xs mb-4 p-3 rounded-xl bg-surface-secondary border border-border">
          <div>
            <p className="text-2xs text-text-muted">Employee</p>
            <p className="font-semibold text-text-primary">{employeeDisplayName}</p>
            <p className="text-2xs text-text-muted">{profile?.employee_code || actorId}</p>
          </div>
          <div>
            <p className="text-2xs text-text-muted">Pay Period</p>
            <p className="font-semibold text-text-primary">{selectedPayslip.period}</p>
            <p className="text-2xs text-text-muted">Disbursed: {selectedPayslip.disbursed_at}</p>
          </div>
        </div>

        <div className="space-y-2 text-xs border-t border-b border-border py-3 mb-4">
          <div className="flex justify-between">
            <span className="text-text-secondary">Base Gross Earnings</span>
            <span className="font-mono font-semibold text-text-primary">
              ${Number(selectedPayslip.gross_salary).toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </span>
          </div>
          <div className="flex justify-between text-rose-600 dark:text-rose-400">
            <span>Medical &amp; Benefits Deductions</span>
            <span className="font-mono font-semibold">
              -${Number(selectedPayslip.deductions).toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </span>
          </div>
          <div className="flex justify-between text-rose-600 dark:text-rose-400">
            <span>Federal &amp; State Tax Withholding</span>
            <span className="font-mono font-semibold">
              -${Number(selectedPayslip.tax).toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </span>
          </div>
        </div>

        <div className="flex items-center justify-between p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-700 dark:text-emerald-300 mb-5">
          <span className="text-xs font-bold uppercase tracking-wider">Net Direct Deposit</span>
          <span className="text-lg font-bold font-mono">
            ${Number(selectedPayslip.net_salary).toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </span>
        </div>

        <div className="flex items-center justify-end gap-2">
          <Button variant="secondary" size="sm" onClick={() => window.print()} className="gap-1.5">
            <Printer className="h-3.5 w-3.5" />
            Print Certificate
          </Button>
          <Button variant="primary" size="sm" onClick={() => setSelectedPayslip(null)}>
            Close
          </Button>
        </div>
      </div>
    </div>
  );
};
