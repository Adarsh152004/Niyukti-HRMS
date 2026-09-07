import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  [
    'inline-flex items-center justify-center gap-2 whitespace-nowrap',
    'font-medium text-sm leading-none',
    'border transition-colors duration-150',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-background',
    'disabled:pointer-events-none disabled:opacity-40',
    'select-none',
  ].join(' '),
  {
    variants: {
      variant: {
        primary: [
          'bg-accent text-white border-accent',
          'hover:bg-accent-hover hover:border-accent-hover',
          'active:opacity-90',
        ].join(' '),
        secondary: [
          'bg-surface text-text-primary border-border-strong',
          'hover:bg-surface-secondary',
          'active:bg-surface-tertiary',
        ].join(' '),
        ghost: [
          'bg-transparent text-text-secondary border-transparent',
          'hover:bg-surface-secondary hover:text-text-primary',
        ].join(' '),
        destructive: [
          'bg-danger text-white border-danger',
          'hover:opacity-90',
        ].join(' '),
        'destructive-ghost': [
          'bg-transparent text-danger border-transparent',
          'hover:bg-danger-soft',
        ].join(' '),
        ai: [
          'bg-ai-soft text-ai border border-ai/20',
          'hover:bg-ai/10',
        ].join(' '),
        link: [
          'bg-transparent text-accent border-transparent underline-offset-4',
          'hover:underline',
          'h-auto p-0',
        ].join(' '),
      },
      size: {
        xs: 'h-6 px-2 text-xs rounded',
        sm: 'h-7 px-3 text-sm rounded',
        md: 'h-8 px-3.5 text-sm rounded-md',
        lg: 'h-9 px-4 text-base rounded-md',
        xl: 'h-10 px-5 text-base rounded-md',
        icon: 'h-8 w-8 rounded-md',
        'icon-sm': 'h-7 w-7 rounded',
        'icon-xs': 'h-6 w-6 rounded',
      },
    },
    defaultVariants: {
      variant: 'secondary',
      size: 'md',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, loading, children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(buttonVariants({ variant, size }), className)}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <svg
            className="h-3.5 w-3.5 animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            aria-hidden
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
        )}
        {children}
      </button>
    );
  }
);
Button.displayName = 'Button';

export { Button, buttonVariants };
