import * as React from 'react';
import { cn } from '@/lib/utils';

// ── Table ─────────────────────────────────────────────────────────────────
const Table = React.forwardRef<HTMLTableElement, React.HTMLAttributes<HTMLTableElement>>(
  ({ className, ...props }, ref) => (
    <div className="w-full overflow-auto">
      <table
        ref={ref}
        className={cn('w-full caption-bottom text-sm border-collapse', className)}
        {...props}
      />
    </div>
  )
);
Table.displayName = 'Table';

const TableHeader = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <thead
    ref={ref}
    className={cn('border-b border-border bg-surface-secondary sticky top-0 z-10', className)}
    {...props}
  />
));
TableHeader.displayName = 'TableHeader';

const TableBody = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <tbody
    ref={ref}
    className={cn('divide-y divide-border [&_tr:last-child]:border-0', className)}
    {...props}
  />
));
TableBody.displayName = 'TableBody';

const TableFooter = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <tfoot
    ref={ref}
    className={cn('border-t border-border bg-surface-secondary font-medium', className)}
    {...props}
  />
));
TableFooter.displayName = 'TableFooter';

const TableRow = React.forwardRef<HTMLTableRowElement, React.HTMLAttributes<HTMLTableRowElement>>(
  ({ className, ...props }, ref) => (
    <tr
      ref={ref}
      className={cn(
        'border-b border-border transition-colors',
        'hover:bg-surface-secondary/60',
        'data-[selected=true]:bg-accent-soft',
        className
      )}
      {...props}
    />
  )
);
TableRow.displayName = 'TableRow';

const TableHead = React.forwardRef<
  HTMLTableCellElement,
  React.ThHTMLAttributes<HTMLTableCellElement>
>(({ className, ...props }, ref) => (
  <th
    ref={ref}
    className={cn(
      'h-9 px-4 text-left text-xs font-semibold text-text-muted',
      'whitespace-nowrap select-none',
      className
    )}
    {...props}
  />
));
TableHead.displayName = 'TableHead';

const TableCell = React.forwardRef<
  HTMLTableCellElement,
  React.TdHTMLAttributes<HTMLTableCellElement>
>(({ className, ...props }, ref) => (
  <td
    ref={ref}
    className={cn('h-10 px-4 py-2 text-sm text-text-primary align-middle', className)}
    {...props}
  />
));
TableCell.displayName = 'TableCell';

// ── Pagination ─────────────────────────────────────────────────────────────
interface PaginationProps {
  page: number;
  totalPages: number;
  total: number;
  pageSize: number;
  onPageChange: (page: number) => void;
}

function Pagination({ page, totalPages, total, pageSize, onPageChange }: PaginationProps) {
  const start = (page - 1) * pageSize + 1;
  const end = Math.min(page * pageSize, total);

  return (
    <div className="flex items-center justify-between px-4 py-3 border-t border-border">
      <p className="text-xs text-text-muted">
        Showing <span className="font-medium text-text-primary">{start}–{end}</span> of{' '}
        <span className="font-medium text-text-primary">{total.toLocaleString()}</span>
      </p>
      <div className="flex items-center gap-1">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
          className={cn(
            'h-7 px-2.5 text-xs rounded border border-border bg-surface',
            'text-text-secondary hover:bg-surface-secondary',
            'disabled:opacity-40 disabled:pointer-events-none transition-colors'
          )}
        >
          Previous
        </button>
        {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
          const p = i + 1;
          return (
            <button
              key={p}
              onClick={() => onPageChange(p)}
              className={cn(
                'h-7 w-7 text-xs rounded border transition-colors',
                p === page
                  ? 'bg-accent text-white border-accent font-semibold'
                  : 'border-border bg-surface text-text-secondary hover:bg-surface-secondary'
              )}
            >
              {p}
            </button>
          );
        })}
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages}
          className={cn(
            'h-7 px-2.5 text-xs rounded border border-border bg-surface',
            'text-text-secondary hover:bg-surface-secondary',
            'disabled:opacity-40 disabled:pointer-events-none transition-colors'
          )}
        >
          Next
        </button>
      </div>
    </div>
  );
}

export {
  Table, TableHeader, TableBody, TableFooter, TableRow, TableHead, TableCell, Pagination,
};
