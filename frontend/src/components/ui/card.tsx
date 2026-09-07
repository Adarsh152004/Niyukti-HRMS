import * as React from 'react';
import { cn } from '@/lib/utils';

// ── Card ─────────────────────────────────────────────────────────────────
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, padding = 'md', ...props }, ref) => {
    const padClass = { none: '', sm: 'p-4', md: 'p-5', lg: 'p-6' }[padding];
    return (
      <div
        ref={ref}
        className={cn(
          'bg-surface border border-border rounded-lg shadow-xs',
          padClass,
          className
        )}
        {...props}
      />
    );
  }
);
Card.displayName = 'Card';

const CardHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('flex items-center justify-between pb-3 mb-3 border-b border-border', className)}
      {...props}
    />
  )
);
CardHeader.displayName = 'CardHeader';

const CardTitle = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3
      ref={ref}
      className={cn('text-sm font-semibold text-text-primary leading-none', className)}
      {...props}
    />
  )
);
CardTitle.displayName = 'CardTitle';

// ── Metric Card ───────────────────────────────────────────────────────────
interface MetricCardProps {
  label: string;
  value: string | number;
  change?: { value: string; direction: 'up' | 'down' | 'neutral'; isPositive?: boolean };
  detail?: string;
  subtext?: string;
  className?: string;
}

function MetricCard({ label, value, change, detail, subtext, className }: MetricCardProps) {
  const displayDetail = detail || subtext;
  return (
    <Card className={className}>
      <div className="flex items-start justify-between">
        <p className="text-xs font-medium text-text-muted">{label}</p>
        {change && (
          <span
            className={cn(
              'text-xs font-medium px-1.5 py-0.5 rounded',
              change.isPositive !== false
                ? 'text-success bg-success-soft'
                : 'text-danger bg-danger-soft'
            )}
          >
            {change.direction === 'up' ? '↑' : change.direction === 'down' ? '↓' : '—'}{' '}
            {change.value}
          </span>
        )}
      </div>
      <p className="text-2xl font-bold text-text-primary mt-2 leading-none">
        {typeof value === 'number' ? value.toLocaleString() : value}
      </p>
      {detail && <p className="text-xs text-text-muted mt-1.5">{detail}</p>}
    </Card>
  );
}

// ── Page Header ───────────────────────────────────────────────────────────
interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: React.ReactNode;
  breadcrumb?: React.ReactNode;
  className?: string;
}

function PageHeader({ title, description, actions, breadcrumb, className }: PageHeaderProps) {
  return (
    <div className={cn('flex items-start justify-between gap-4 mb-6', className)}>
      <div className="space-y-0.5 min-w-0">
        {breadcrumb && <div className="mb-1">{breadcrumb}</div>}
        <h1 className="text-2xl font-bold text-text-primary tracking-tight leading-tight">
          {title}
        </h1>
        {description && (
          <p className="text-sm text-text-muted leading-relaxed">{description}</p>
        )}
      </div>
      {actions && (
        <div className="flex items-center gap-2 shrink-0">{actions}</div>
      )}
    </div>
  );
}

// ── Separator ─────────────────────────────────────────────────────────────
function Separator({ className, orientation = 'horizontal' }: { className?: string; orientation?: 'horizontal' | 'vertical' }) {
  return (
    <div
      role="separator"
      aria-orientation={orientation}
      className={cn(
        'bg-border shrink-0',
        orientation === 'horizontal' ? 'h-px w-full' : 'h-full w-px',
        className
      )}
    />
  );
}

export { Card, CardHeader, CardTitle, MetricCard, PageHeader, Separator };
