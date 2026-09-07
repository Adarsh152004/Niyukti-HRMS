import React from "react";
import { UserPlus, Briefcase, CheckCircle2, ArrowUpRight } from "lucide-react";
import { useNavigate } from "react-router-dom";

export interface RecruitmentWidgetData {
  active_requisitions: number;
  total_candidates: number;
  recent_positions: Array<{ title: string; openings_count: number; status: string }>;
  stages?: Array<{ stage: string; count: number }>;
}

export const RecruitmentWidget: React.FC<{ data: RecruitmentWidgetData; title?: string }> = ({
  data,
  title = "Recruitment Pipeline",
}) => {
  const navigate = useNavigate();

  return (
    <div className="my-3 overflow-hidden rounded-2xl border border-cyan-500/20 bg-gradient-to-br from-slate-900/95 via-slate-900/90 to-cyan-950/40 p-4 text-white shadow-xl backdrop-blur-md">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-cyan-500/15 text-cyan-400 ring-1 ring-cyan-500/30">
            <UserPlus className="h-5 w-5" />
          </div>
          <div>
            <h4 className="text-sm font-semibold tracking-tight text-slate-100">{title}</h4>
            <div className="flex items-center gap-1.5 text-[11px] text-cyan-300">
              <span>{data.active_requisitions} Active Job Requisitions</span>
            </div>
          </div>
        </div>
        <button
          onClick={() => navigate("/recruitment")}
          className="flex items-center gap-1 rounded-lg bg-cyan-500/10 px-2.5 py-1 text-xs font-medium text-cyan-300 transition-all hover:bg-cyan-500/20 hover:text-white"
        >
          <span>Hiring Hub</span>
          <ArrowUpRight className="h-3.5 w-3.5" />
        </button>
      </div>

      {/* Summary Chips */}
      <div className="mt-3.5 grid grid-cols-2 gap-3">
        <div className="rounded-xl border border-slate-800 bg-slate-800/40 p-3">
          <div className="text-[11px] font-medium uppercase tracking-wider text-slate-400">Open Requisitions</div>
          <div className="mt-1 text-2xl font-bold text-cyan-300">{data.active_requisitions}</div>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-800/40 p-3">
          <div className="text-[11px] font-medium uppercase tracking-wider text-slate-400">Candidate Pool</div>
          <div className="mt-1 text-2xl font-bold text-purple-300">{data.total_candidates}</div>
        </div>
      </div>

      {/* Recent Positions */}
      {data.recent_positions && data.recent_positions.length > 0 && (
        <div className="mt-3.5 space-y-1.5">
          <div className="text-[11px] font-medium uppercase tracking-wider text-slate-400">Recent Postings</div>
          {data.recent_positions.slice(0, 3).map((p, i) => (
            <div key={i} className="flex items-center justify-between rounded-lg bg-slate-800/30 px-2.5 py-1.5 text-xs">
              <span className="font-medium text-slate-200">{p.title}</span>
              <span className="rounded bg-cyan-500/15 px-1.5 py-0.5 text-[10px] font-medium text-cyan-300">
                {p.status} ({p.openings_count})
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
