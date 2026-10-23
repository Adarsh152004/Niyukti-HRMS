import React, { useState } from 'react';
import { X, Calendar } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useEmployee } from '@/context/EmployeeContext';

export const ApplyLeaveModal: React.FC = () => {
  const { showLeaveModal, setShowLeaveModal, leaveData, handleApplyLeave } = useEmployee();

  const [leaveType, setLeaveType] = useState('lt-annual');
  const [leaveStart, setLeaveStart] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 1);
    return d.toISOString().split('T')[0];
  });
  const [leaveEnd, setLeaveEnd] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 2);
    return d.toISOString().split('T')[0];
  });
  const [leaveDays, setLeaveDays] = useState('2.0');
  const [leaveReason, setLeaveReason] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (!showLeaveModal) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    await handleApplyLeave({
      leaveType,
      start: leaveStart,
      end: leaveEnd,
      days: leaveDays,
      reason: leaveReason,
    });
    setSubmitting(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in">
      <div className="w-full max-w-md bg-surface border border-border rounded-2xl shadow-2xl p-6 relative">
        <button
          onClick={() => setShowLeaveModal(false)}
          className="absolute right-4 top-4 text-text-muted hover:text-text-primary transition"
        >
          <X className="h-5 w-5" />
        </button>

        <h3 className="text-base font-bold text-text-primary flex items-center gap-2">
          <Calendar className="h-5 w-5 text-accent" />
          Apply for Paid Time Off
        </h3>
        <p className="text-xs text-text-muted mt-1">Submit request to People Ops &amp; Department Manager.</p>

        <form onSubmit={handleSubmit} className="space-y-4 mt-5">
          <div>
            <label className="block text-xs font-semibold text-text-secondary mb-1">Leave Type</label>
            <select
              value={leaveType}
              onChange={(e) => setLeaveType(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-surface-secondary border border-border text-xs text-text-primary focus:outline-none focus:ring-1 focus:ring-accent"
            >
              <option value="lt-annual">Annual Leave ({leaveData?.balances?.annual?.available || 0}d available)</option>
              <option value="lt-sick">Sick Leave ({leaveData?.balances?.sick?.available || 0}d available)</option>
              <option value="lt-casual">Casual Leave ({leaveData?.balances?.casual?.available || 0}d available)</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-text-secondary mb-1">Start Date</label>
              <input
                type="date"
                value={leaveStart}
                onChange={(e) => setLeaveStart(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-surface-secondary border border-border text-xs text-text-primary focus:outline-none focus:ring-1 focus:ring-accent"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-text-secondary mb-1">End Date</label>
              <input
                type="date"
                value={leaveEnd}
                onChange={(e) => setLeaveEnd(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-surface-secondary border border-border text-xs text-text-primary focus:outline-none focus:ring-1 focus:ring-accent"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-text-secondary mb-1">Total Days</label>
            <input
              type="number"
              step="0.5"
              min="0.5"
              value={leaveDays}
              onChange={(e) => setLeaveDays(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-surface-secondary border border-border text-xs text-text-primary font-mono focus:outline-none focus:ring-1 focus:ring-accent"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-text-secondary mb-1">Reason / Notes</label>
            <textarea
              rows={3}
              placeholder="Please describe reason for leave..."
              value={leaveReason}
              onChange={(e) => setLeaveReason(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-surface-secondary border border-border text-xs text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-1 focus:ring-accent"
              required
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <Button type="button" variant="secondary" size="sm" onClick={() => setShowLeaveModal(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" disabled={submitting}>
              {submitting ? 'Submitting...' : 'Submit Application'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
