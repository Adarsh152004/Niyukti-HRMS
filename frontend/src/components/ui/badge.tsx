import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const badgeVariants = cva(
  'inline-flex items-center gap-1 whitespace-nowrap font-medium border transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-surface-secondary text-text-secondary border-border',
        primary: 'bg-accent-soft text-accent border-accent/20',
        success: 'bg-success-soft text-success border-success/20',
        warning: 'bg-warning-soft text-warning border-warning/20',
        danger: 'bg-danger-soft text-danger border-danger/20',
        info: 'bg-info-soft text-info border-info/20',
        ai: 'bg-ai-soft text-ai border-ai/20',
        outline: 'bg-transparent text-text-secondary border-border',
      },
      size: {
        sm: 'h-4 px-1.5 text-2xs rounded',
        md: 'h-5 px-2 text-xs rounded',
        lg: 'h-6 px-2.5 text-sm rounded-md',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, size, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant, size }), className)} {...props} />
  );
}

// ── Risk badge — maps risk levels to semantic colors ───────────────────────
type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

const riskVariantMap: Record<RiskLevel, BadgeProps['variant']> = {
  LOW: 'success',
  MEDIUM: 'warning',
  HIGH: 'danger',
  CRITICAL: 'danger',
};

function RiskBadge({ level, className }: { level: RiskLevel; className?: string }) {
  return (
    <Badge
      variant={riskVariantMap[level]}
      className={cn(level === 'CRITICAL' && 'font-bold', className)}
    >
      {level === 'CRITICAL' && (
        <span className="w-1.5 h-1.5 rounded-full bg-current inline-block" aria-hidden />
      )}
      {level}
    </Badge>
  );
}

// ── Status badge — employee/workflow/agent statuses ────────────────────────
type StatusVariant = 'active' | 'inactive' | 'pending' | 'running' | 'failed' | 'suspended' | 'on_leave' | 'resigned' | 'terminated' | string;

const statusConfig: Record<string, { label: string; variant: BadgeProps['variant'] }> = {
  active: { label: 'Active', variant: 'success' },
  inactive: { label: 'Inactive', variant: 'default' },
  pending: { label: 'Pending', variant: 'warning' },
  running: { label: 'Running', variant: 'primary' },
  failed: { label: 'Failed', variant: 'danger' },
  suspended: { label: 'Suspended', variant: 'danger' },
  on_leave: { label: 'On Leave', variant: 'warning' },
  resigned: { label: 'Resigned', variant: 'default' },
  terminated: { label: 'Terminated', variant: 'danger' },
};

function StatusBadge({ status, className }: { status: StatusVariant; className?: string }) {
  const normalizedKey = (status || 'active').toLowerCase();
  const config = statusConfig[normalizedKey] || {
    label: (status || 'Unknown').charAt(0).toUpperCase() + (status || 'Unknown').slice(1).toLowerCase(),
    variant: 'default'
  };
  return (
    <Badge variant={config.variant} className={className}>
      <span className="w-1.5 h-1.5 rounded-full bg-current inline-block" aria-hidden />
      {config.label}
    </Badge>
  );
}

export { Badge, badgeVariants, RiskBadge, StatusBadge };
export type { RiskLevel, StatusVariant };
