import * as React from 'react';
import * as DialogPrimitive from '@radix-ui/react-dialog';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';

const Dialog = DialogPrimitive.Root;
const DialogTrigger = DialogPrimitive.Trigger;
const DialogPortal = DialogPrimitive.Portal;
const DialogClose = DialogPrimitive.Close;

const DialogOverlay = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Overlay>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Overlay
    ref={ref}
    className={cn(
      'fixed inset-0 z-50 bg-black/40 backdrop-blur-[2px]',
      'data-[state=open]:animate-in data-[state=closed]:animate-out',
      'data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
      className
    )}
    {...props}
  />
));
DialogOverlay.displayName = 'DialogOverlay';

const DialogContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content> & {
    size?: 'sm' | 'md' | 'lg' | 'xl';
  }
>(({ className, size = 'md', children, ...props }, ref) => {
  const sizeClass = {
    sm: 'max-w-sm',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  }[size];

  return (
    <DialogPortal>
      <DialogOverlay />
      <DialogPrimitive.Content
        ref={ref}
        className={cn(
          'fixed left-1/2 top-1/2 z-50 -translate-x-1/2 -translate-y-1/2',
          'w-full bg-surface border border-border rounded-xl shadow-xl',
          'focus:outline-none',
          'data-[state=open]:animate-in data-[state=closed]:animate-out',
          'data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
          'data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95',
          'data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%]',
          'data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%]',
          sizeClass,
          className
        )}
        {...props}
      >
        {children}
        <DialogPrimitive.Close className={cn(
          'absolute right-4 top-4 rounded-md p-1',
          'text-text-muted hover:text-text-primary hover:bg-surface-secondary',
          'transition-colors focus:outline-none focus:ring-2 focus:ring-accent'
        )}>
          <X className="h-4 w-4" />
          <span className="sr-only">Close</span>
        </DialogPrimitive.Close>
      </DialogPrimitive.Content>
    </DialogPortal>
  );
});
DialogContent.displayName = 'DialogContent';

const DialogHeader = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('px-6 pt-6 pb-4 border-b border-border', className)} {...props} />
);

const DialogBody = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('px-6 py-4', className)} {...props} />
);

const DialogFooter = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      'px-6 py-4 border-t border-border bg-surface-secondary rounded-b-xl',
      'flex flex-row justify-end gap-2',
      className
    )}
    {...props}
  />
);

const DialogTitle = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Title>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Title>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Title
    ref={ref}
    className={cn('text-lg font-semibold text-text-primary leading-tight', className)}
    {...props}
  />
));
DialogTitle.displayName = 'DialogTitle';

const DialogDescription = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Description>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Description>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Description
    ref={ref}
    className={cn('text-sm text-text-muted mt-1', className)}
    {...props}
  />
));
DialogDescription.displayName = 'DialogDescription';

// ── Drawer (side panel) ──────────────────────────────────────────────────
const Drawer = DialogPrimitive.Root;
const DrawerTrigger = DialogPrimitive.Trigger;
const DrawerClose = DialogPrimitive.Close;

const DrawerContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content> & {
    side?: 'left' | 'right';
    width?: string;
  }
>(({ className, side = 'right', width = 'w-[480px]', children, ...props }, ref) => (
  <DialogPortal>
    <DialogOverlay />
    <DialogPrimitive.Content
      ref={ref}
      className={cn(
        'fixed top-0 z-50 h-full bg-surface border-border shadow-xl',
        'flex flex-col focus:outline-none',
        'data-[state=open]:animate-in data-[state=closed]:animate-out',
        side === 'right'
          ? [
              'right-0 border-l',
              'data-[state=closed]:slide-out-to-right',
              'data-[state=open]:slide-in-from-right',
            ]
          : [
              'left-0 border-r',
              'data-[state=closed]:slide-out-to-left',
              'data-[state=open]:slide-in-from-left',
            ],
        width,
        className
      )}
      {...props}
    >
      {children}
      <DialogPrimitive.Close className={cn(
        'absolute right-4 top-4 rounded-md p-1',
        'text-text-muted hover:text-text-primary hover:bg-surface-secondary',
        'transition-colors focus:outline-none focus:ring-2 focus:ring-accent'
      )}>
        <X className="h-4 w-4" />
        <span className="sr-only">Close</span>
      </DialogPrimitive.Close>
    </DialogPrimitive.Content>
  </DialogPortal>
));
DrawerContent.displayName = 'DrawerContent';

export {
  Dialog, DialogTrigger, DialogPortal, DialogOverlay, DialogClose,
  DialogContent, DialogHeader, DialogBody, DialogFooter, DialogTitle, DialogDescription,
  Drawer, DrawerTrigger, DrawerClose, DrawerContent,
};
