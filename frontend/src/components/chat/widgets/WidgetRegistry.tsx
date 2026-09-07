import React from "react";
import { HeadcountWidget } from "./HeadcountWidget";
import { AttendanceWidget } from "./AttendanceWidget";
import { PayrollWidget } from "./PayrollWidget";
import { RecruitmentWidget } from "./RecruitmentWidget";

export interface WidgetPayload {
  widget_type: string;
  version: number;
  title: string;
  data: any;
}

export const WidgetRegistry: React.FC<{ widget: WidgetPayload }> = ({ widget }) => {
  if (!widget || !widget.widget_type) return null;

  try {
    switch (widget.widget_type) {
      case "HEADCOUNT":
        return <HeadcountWidget data={widget.data} title={widget.title} />;
      case "ATTENDANCE":
        return <AttendanceWidget data={widget.data} title={widget.title} />;
      case "PAYROLL_SUMMARY":
        return <PayrollWidget data={widget.data} title={widget.title} />;
      case "RECRUITMENT_PIPELINE":
        return <RecruitmentWidget data={widget.data} title={widget.title} />;
      default:
        return (
          <div className="my-2 rounded-xl border border-slate-800 bg-slate-900/60 p-3 text-xs text-slate-300">
            <div className="font-medium text-slate-200">{widget.title}</div>
            <pre className="mt-1 overflow-x-auto text-[11px] text-slate-400">
              {JSON.stringify(widget.data, null, 2)}
            </pre>
          </div>
        );
    }
  } catch (err) {
    console.error("Failed to render widget:", widget, err);
    return null;
  }
};
