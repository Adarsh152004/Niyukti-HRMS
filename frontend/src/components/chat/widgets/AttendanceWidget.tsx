import React from "react";
import { Clock, CheckCircle2, XCircle, Calendar, ArrowUpRight, ShieldCheck } from "lucide-react";
import { useNavigate } from "react-router-dom";

export interface AttendanceWidgetData {
  date: string;
  total_staff: number;
  present_count: number;
  absent_count: number;
  attendance_rate: number;
  source?: string;
}

export const AttendanceWidget: React.FC<{ data: AttendanceWidgetData; title?: string }> = ({
  data,
  title = "Attendance Overview",
}) => {
  const navigate = useNavigate();
  const rate = data.attendance_rate || 0;

  return (
    <div className="my-3 overflow-hidden rounded-2xl border border-emerald-500/20 bg-gradient-to-br from-slate-900/95 via-slate-900/90 to-emerald-950/40 p-4 text-white shadow-xl backdrop-blur-md">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-500/15 text-emerald-400 ring-1 ring-emerald-500/30">
            <Clock className="h-5 w-5" />
          </div>
          <div>
            <h4 className="text-sm font-semibold tracking-tight text-slate-100">{title}</h4>
            <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
              <Calendar className="h-3 w-3" />
              <span>{data.date || "Today"}</span>
            </div>
          </div>
        </div>
        <button
          onClick={() => navigate("/attendance")}
          className="flex items-center gap-1 rounded-lg bg-emerald-500/10 px-2.5 py-1 text-xs font-medium text-emerald-300 transition-all hover:bg-emerald-500/20 hover:text-white"
        >
          <span>Register</span>
          <ArrowUpRight className="h-3.5 w-3.5" />
        </button>
      </div>

      {/* Metrics Row */}
      <div className="mt-3.5 grid grid-cols-3 gap-2.5">
        <div className="rounded-xl border border-slate-800 bg-slate-800/40 p-3 text-center">
          <div className="text-[11px] font-medium uppercase tracking-wider text-emerald-400 flex items-center justify-center gap-1">
            <CheckCircle2 className="h-3.5 w-3.5" />
            <span>Present</span>
          </div>
          <div className="mt-1 text-2xl font-bold text-white">{data.present_count}</div>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-800/40 p-3 text-center">
          <div className="text-[11px] font-medium uppercase tracking-wider text-rose-400 flex items-center justify-center gap-1">
            <XCircle className="h-3.5 w-3.5" />
            <span>Absent</span>
          </div>
          <div className="mt-1 text-2xl font-bold text-white">{data.absent_count}</div>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-800/40 p-3 text-center">
          <div className="text-[11px] font-medium uppercase tracking-wider text-cyan-400 flex items-center justify-center gap-1">
            <ShieldCheck className="h-3.5 w-3.5" />
            <span>Rate</span>
          </div>
          <div className="mt-1 text-2xl font-bold text-white">{rate}%</div>
        </div>
      </div>

      {/* Attendance Bar */}
      <div className="mt-3.5">
        <div className="h-2 w-full overflow-hidden rounded-full bg-slate-800">
          <div
            className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-500"
            style={{ width: `${Math.min(100, Math.max(5, rate))}%` }}
          />
        </div>
        <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400">
          <span>Source: {data.source || "Biometric & Self-Service"}</span>
          <span className="text-emerald-400 font-medium">{rate}% Active Attendance</span>
        </div>
      </div>
    </div>
  );
};
