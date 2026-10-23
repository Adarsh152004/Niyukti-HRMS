import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2, Info, Lightbulb } from 'lucide-react';

export type CalloutType = 'note' | 'tip' | 'info' | 'warning' | 'important' | 'success';

interface CalloutProps {
  type: CalloutType;
  title?: string;
  children: React.ReactNode;
}

const config: Record<
  CalloutType,
  { icon: React.FC<{ className?: string }>; border: string; bg: string; text: string; defaultTitle: string }
> = {
  note: {
    icon: Info,
    border: 'border-blue-500/30',
    bg: 'bg-blue-500/10',
    text: 'text-blue-400',
    defaultTitle: 'Note',
  },
  info: {
    icon: Info,
    border: 'border-cyan-500/30',
    bg: 'bg-cyan-500/10',
    text: 'text-cyan-400',
    defaultTitle: 'Information',
  },
  tip: {
    icon: Lightbulb,
    border: 'border-emerald-500/30',
    bg: 'bg-emerald-500/10',
    text: 'text-emerald-400',
    defaultTitle: 'Tip',
  },
  warning: {
    icon: AlertTriangle,
    border: 'border-amber-500/30',
    bg: 'bg-amber-500/10',
    text: 'text-amber-400',
    defaultTitle: 'Warning',
  },
  important: {
    icon: AlertCircle,
    border: 'border-purple-500/30',
    bg: 'bg-purple-500/10',
    text: 'text-purple-400',
    defaultTitle: 'Important',
  },
  success: {
    icon: CheckCircle2,
    border: 'border-emerald-500/30',
    bg: 'bg-emerald-500/10',
    text: 'text-emerald-400',
    defaultTitle: 'Success',
  },
};

export const Callout: React.FC<CalloutProps> = ({ type, title, children }) => {
  const c = config[type] || config.note;
  const Icon = c.icon;

  return (
    <div className={`my-3.5 flex gap-3 rounded-xl border ${c.border} ${c.bg} p-3.5 text-xs shadow-sm`}>
      <Icon className={`h-4 w-4 shrink-0 mt-0.5 ${c.text}`} />
      <div className="flex-1 space-y-1">
        <p className={`font-semibold tracking-wide ${c.text}`}>
          {title || c.defaultTitle}
        </p>
        <div className="text-zinc-300 leading-relaxed">{children}</div>
      </div>
    </div>
  );
};
