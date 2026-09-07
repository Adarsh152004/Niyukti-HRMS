import React from "react";
import { DollarSign, CheckCircle2, Calendar, ArrowUpRight, TrendingUp } from "lucide-react";
import { useNavigate } from "react-router-dom";

export interface PayrollWidgetData {
  period: string;
  total_gross: number;
  total_deductions: number;
  total_net: number;
  employee_count: number;
  status: string;
  currency?: string;
}

export const PayrollWidget: React.FC<{ data: PayrollWidgetData; title?: string }> = ({
  data,
  title = "Executive Payroll Summary",
}) => {
  const navigate = useNavigate();
  const formatCur = (val: number) => `$${Number(val || 0).toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;

  return (
    <div className="my-3 overflow-hidden rounded-2xl border border-amber-500/20 bg-gradient-to-br from-slate-900/95 via-slate-900/90 to-amber-950/40 p-4 text-white shadow-xl backdrop-blur-md">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-500/15 text-amber-400 ring-1 ring-amber-500/30">
            <DollarSign className="h-5 w-5" />
          </div>
          <div>
            <h4 className="text-sm font-semibold tracking-tight text-slate-100">{title}</h4>
            <div className="flex items-center gap-1.5 text-[11px] text-emerald-400">
              <CheckCircle2 className="h-3 w-3" />
              <span>Status: {data.status || "COMPLETED"}</span>
            </div>
          </div>
        </div>
        <button
          onClick={() => navigate("/payroll")}
          className="flex items-center gap-1 rounded-lg bg-amber-500/10 px-2.5 py-1 text-xs font-medium text-amber-300 transition-all hover:bg-amber-500/20 hover:text-white"
        >
          <span>Payroll Tab</span>
          <ArrowUpRight className="h-3.5 w-3.5" />
        </button>
      </div>

      {/* Figures */}
      <div className="mt-3.5 grid grid-cols-2 gap-3">
        <div className="rounded-xl border border-slate-800 bg-slate-800/40 p-3">
          <div className="text-[11px] font-medium uppercase tracking-wider text-slate-400">Net Disbursed</div>
          <div className="mt-1 text-2xl font-bold text-emerald-400">{formatCur(data.total_net)}</div>
          <div className="mt-1 text-[11px] text-slate-400">{data.employee_count} Payees Included</div>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-800/40 p-3">
          <div className="text-[11px] font-medium uppercase tracking-wider text-slate-400">Gross Payroll</div>
          <div className="mt-1 text-2xl font-bold text-slate-100">{formatCur(data.total_gross)}</div>
          <div className="mt-1 text-[11px] text-rose-400">Deductions: {formatCur(data.total_deductions)}</div>
        </div>
      </div>
    </div>
  );
};
