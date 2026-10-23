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

export { Badge, badgeVariants };
