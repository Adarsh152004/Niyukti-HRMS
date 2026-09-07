import * as React from 'react';
import { cn } from '@/lib/utils';
import { Badge, type RiskLevel } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { CheckCircle, XCircle, RotateCcw, ChevronDown } from 'lucide-react';

// ── AI Recommendation Card ─────────────────────────────────────────────────
interface AIRecommendationProps {
  title: string;
  recommendation: string;
  evidence: string[];
  confidence: number; // 0–100
  riskLevel: RiskLevel;
  sources?: { label: string; count: number }[];
  onApprove?: () => void;
  onModify?: () => void;
  onReject?: () => void;
  className?: string;
}

function AIRecommendation({
  title,
  recommendation,
  evidence,
  confidence,
  riskLevel,
  sources = [],
  onApprove,
  onModify,
  onReject,
  className,
}: AIRecommendationProps) {
  const [expanded, setExpanded] = React.useState(false);

  const riskColors: Record<RiskLevel, 'success' | 'warning' | 'danger'> = {
    LOW: 'success',
    MEDIUM: 'warning',
    HIGH: 'danger',
    CRITICAL: 'danger',
  };

  const confidenceColor =
    confidence >= 80 ? 'text-success' : confidence >= 60 ? 'text-warning' : 'text-danger';

  return (
    <div
      className={cn(
        'border border-border rounded-lg bg-surface overflow-hidden',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-ai-soft border-b border-ai/20">
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-ai" aria-hidden />
          <span className="text-xs font-semibold text-ai">AI Recommendation</span>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={riskColors[riskLevel]} size="sm">
            {riskLevel} risk
          </Badge>
          <span className={cn('text-xs font-bold', confidenceColor)}>
            {confidence}% confidence
          </span>
        </div>
      </div>

      {/* Body */}
      <div className="px-4 py-3 space-y-3">
        <div>
          <p className="text-sm font-semibold text-text-primary">{title}</p>
          <p className="text-sm text-text-secondary mt-1 leading-relaxed">{recommendation}</p>
        </div>

        {/* Evidence */}
        <button
          type="button"
          className="flex items-center gap-1.5 text-xs text-text-muted hover:text-text-primary transition-colors"
          onClick={() => setExpanded(!expanded)}
          aria-expanded={expanded}
        >
          <ChevronDown
            className={cn('h-3.5 w-3.5 transition-transform', expanded && 'rotate-180')}
            aria-hidden
          />
          Evidence &amp; sources
        </button>

        {expanded && (
          <div className="space-y-2 pl-3 border-l border-border">
            <ul className="space-y-1">
              {evidence.map((item, i) => (
                <li key={i} className="text-xs text-text-secondary flex items-start gap-2">
                  <span className="text-text-muted mt-0.5">•</span>
                  {item}
                </li>
              ))}
            </ul>
            {sources.length > 0 && (
              <div className="flex flex-wrap gap-2 pt-1">
                {sources.map((s, i) => (
                  <span key={i} className="text-2xs text-text-muted bg-surface-secondary px-2 py-0.5 rounded border border-border">
                    {s.count} {s.label}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        {(onApprove || onModify || onReject) && (
          <div className="flex items-center gap-2 pt-1">
            {onApprove && (
              <Button size="sm" variant="primary" onClick={onApprove}>
                <CheckCircle className="h-3.5 w-3.5" aria-hidden />
                Approve
              </Button>
            )}
            {onModify && (
              <Button size="sm" variant="secondary" onClick={onModify}>
                <RotateCcw className="h-3.5 w-3.5" aria-hidden />
                Modify
              </Button>
            )}
            {onReject && (
              <Button size="sm" variant="destructive-ghost" onClick={onReject}>
                <XCircle className="h-3.5 w-3.5" aria-hidden />
                Reject
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ── Tool Execution Progress ────────────────────────────────────────────────
type ToolStepStatus = 'pending' | 'running' | 'completed' | 'failed';

interface ToolStep {
  id: string;
  label: string;
  status: ToolStepStatus;
  timestamp?: string;
}

function ToolExecution({ steps, className }: { steps: ToolStep[]; className?: string }) {
  return (
    <div className={cn('space-y-1.5', className)} role="status" aria-label="Automation progress">
      {steps.map((step) => {
        const icon =
          step.status === 'completed' ? (
            <CheckCircle className="h-3.5 w-3.5 text-success shrink-0" aria-label="Completed" />
          ) : step.status === 'failed' ? (
            <XCircle className="h-3.5 w-3.5 text-danger shrink-0" aria-label="Failed" />
          ) : step.status === 'running' ? (
            <svg className="h-3.5 w-3.5 text-accent shrink-0 animate-spin" fill="none" viewBox="0 0 24 24" aria-label="Running">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          ) : (
            <span className="h-3.5 w-3.5 shrink-0 rounded-full border border-border-strong" aria-label="Pending" />
          );

        return (
          <div
            key={step.id}
            className={cn(
              'flex items-center gap-2 text-xs',
              step.status === 'pending' && 'text-text-muted',
              step.status === 'running' && 'text-text-primary font-medium',
              step.status === 'completed' && 'text-text-secondary',
              step.status === 'failed' && 'text-danger'
            )}
          >
            {icon}
            <span className="flex-1">{step.label}</span>
            {step.timestamp && (
              <span className="text-text-muted shrink-0">{step.timestamp}</span>
            )}
          </div>
        );
      })}
    </div>
  );
}

export { AIRecommendation, ToolExecution };
export type { AIRecommendationProps, ToolStep, ToolStepStatus };
