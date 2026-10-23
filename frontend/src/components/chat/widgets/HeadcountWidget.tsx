import React from "react";
import { Users, Building2, Briefcase, ArrowUpRight, CheckCircle2 } from "lucide-react";
import { useNavigate } from "react-router-dom";

export interface HeadcountWidgetData {
  total_active_staff: number;
  departments: Array<{ department: string; count: number; percentage: number }>;
  employment_types: { FULL_TIME: number; CONTRACT?: number; INTERN?: number };
  last_synced?: string;
}

export const HeadcountWidget: React.FC<{ data: HeadcountWidgetData; title?: string }> = ({
  data,
  title = "Live Headcount Distribution",
}) => {
  const navigate = useNavigate();
  const total = data.total_active_staff || 0;
  const depts = data.departments || [];

  return (
    <div className="my-3 overflow-hidden rounded-2xl border border-indigo-500/20 bg-gradient-to-br from-slate-900/95 via-slate-900/90 to-indigo-950/40 p-4 text-white shadow-xl backdrop-blur-md">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-500/15 text-indigo-400 ring-1 ring-indigo-500/30">
            <Users className="h-5 w-5" />
          </div>
          <div>
            <h4 className="text-sm font-semibold tracking-tight text-slate-100">{title}</h4>
            <div className="flex items-center gap-1.5 text-[11px] text-emerald-400">
              <CheckCircle2 className="h-3 w-3" />
              <span>Real-time SQLite sync</span>
            </div>
          </div>
        </div>
        <button
          onClick={() => navigate("/employees")}
          className="flex items-center gap-1 rounded-lg bg-indigo-500/10 px-2.5 py-1 text-xs font-medium text-indigo-300 transition-all hover:bg-indigo-500/20 hover:text-white"
        >
          <span>Directory</span>
          <ArrowUpRight className="h-3.5 w-3.5" />
        </button>
      </div>

      {/* KPI Highlight */}
      <div className="mt-3.5 grid grid-cols-2 gap-3 sm:grid-cols-3">
        <div className="rounded-xl border border-slate-800 bg-slate-800/40 p-3">
          <div className="text-[11px] font-medium uppercase tracking-wider text-slate-400">Total Active Staff</div>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight text-white">{total}</span>
            <span className="text-xs text-emerald-400">100% active</span>
          </div>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-800/40 p-3">
          <div className="text-[11px] font-medium uppercase tracking-wider text-slate-400">Full-Time Staff</div>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight text-indigo-300">
              {data.employment_types?.FULL_TIME || total}
            </span>
            <span className="text-xs text-slate-400">Core</span>
          </div>
        </div>
        <div className="col-span-2 rounded-xl border border-slate-800 bg-slate-800/40 p-3 sm:col-span-1">
          <div className="text-[11px] font-medium uppercase tracking-wider text-slate-400">Departments</div>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight text-purple-300">{depts.length}</span>
            <span className="text-xs text-slate-400">Functional</span>
          </div>
        </div>
      </div>

      {/* Department Breakdown Bars */}
      <div className="mt-4">
        <div className="mb-2 flex items-center justify-between text-xs text-slate-400">
          <span className="flex items-center gap-1">
            <Building2 className="h-3.5 w-3.5" />
            <span>Allocation by Department</span>
          </span>
          <span>{depts.length} Units</span>
        </div>

        <div className="space-y-2.5">
          {depts.map((d, i) => (
            <div key={i} className="group">
              <div className="flex justify-between text-xs">
                <span className="font-medium text-slate-300 group-hover:text-white transition-colors">
                  {d.department}
                </span>
                <span className="font-semibold text-slate-400">
                  {d.count} ({d.percentage}%)
                </span>
              </div>
              <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-cyan-400 transition-all duration-500"
                  style={{ width: `${Math.max(5, d.percentage)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
