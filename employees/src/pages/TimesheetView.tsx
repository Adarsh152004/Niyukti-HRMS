import React, { useState } from 'react';
import { CheckSquare, FileText, Plus, AlertCircle } from 'lucide-react';
import { PageHeader, Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table';
import { useEmployee } from '@/context/EmployeeContext';

export const TimesheetView: React.FC = () => {
  const { workLogs, handleCreateWorkLog } = useEmployee();

  const [category, setCategory] = useState('Engineering');
  const [title, setTitle] = useState('');
  const [desc, setDesc] = useState('');
  const [hours, setHours] = useState('2.0');
  const [blockers, setBlockers] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    const ok = await handleCreateWorkLog({
      category,
      title,
      desc,
      hours,
      blockers,
    });
    if (ok) {
      setTitle('');
      setDesc('');
      setBlockers('');
    }
    setSubmitting(false);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-150">
      <PageHeader
        title="Daily Tasks / Timesheet"
        description="Log engineering deliverables, client sprint updates, billable hours, and blockers."
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form Card */}
        <Card className="lg:col-span-1">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <CheckSquare className="h-4 w-4 text-accent" />
              Log Daily Deliverables
            </CardTitle>
          </CardHeader>
          <form onSubmit={handleSubmit} className="space-y-4 pt-2">
            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1">Project / Stream</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-surface-secondary border border-border text-xs text-text-primary focus:outline-none focus:ring-1 focus:ring-accent"
              >
                <option value="Engineering">Engineering / AI Core</option>
                <option value="Product">Product Architecture</option>
                <option value="Infrastructure">DevOps &amp; Infrastructure</option>
                <option value="Compliance">Security &amp; Governance</option>
                <option value="Operations">Workforce Operations</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1">Task Summary</label>
              <input
                type="text"
                placeholder="e.g. LangGraph Self-RAG Node Integration"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-surface-secondary border border-border text-xs text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-1 focus:ring-accent"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1">Hours Spent</label>
              <input
                type="number"
                step="0.5"
                min="0.5"
                max="16"
                value={hours}
                onChange={(e) => setHours(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-surface-secondary border border-border text-xs text-text-primary font-mono focus:outline-none focus:ring-1 focus:ring-accent"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1">Detailed Deliverables</label>
              <textarea
                rows={3}
                placeholder="Details of PRs merged, docs written, or bugs resolved..."
                value={desc}
                onChange={(e) => setDesc(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-surface-secondary border border-border text-xs text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-1 focus:ring-accent"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-text-secondary mb-1">Blockers / Dependencies</label>
              <input
                type="text"
                placeholder="Optional blockers..."
                value={blockers}
                onChange={(e) => setBlockers(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-surface-secondary border border-border text-xs text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-1 focus:ring-accent"
              />
            </div>

            <Button type="submit" variant="primary" size="sm" className="w-full" disabled={submitting}>
              {submitting ? 'Submitting...' : 'Submit Timesheet Entry'}
            </Button>
          </form>
        </Card>

        {/* Audit Feed */}
        <Card padding="none" className="lg:col-span-2">
          <CardHeader className="px-5 pt-5 pb-3">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <FileText className="h-4 w-4 text-accent" />
              Verified Work Logs &amp; Audit Trail
            </CardTitle>
          </CardHeader>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Deliverables &amp; Details</TableHead>
                <TableHead className="text-right">Hours</TableHead>
                <TableHead>Blockers</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {workLogs.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center py-8 text-text-muted italic">
                    No timesheet entries logged for current period.
                  </TableCell>
                </TableRow>
              ) : (
                workLogs.map((wl) => (
                  <TableRow key={wl.id}>
                    <TableCell className="font-mono text-xs text-text-primary whitespace-nowrap">
                      {wl.work_date}
                    </TableCell>
                    <TableCell className="text-xs text-text-primary">
                      <span className="font-medium">{wl.description}</span>
                    </TableCell>
                    <TableCell className="text-right font-mono text-xs font-semibold text-text-primary">
                      {wl.hours_spent}h
                    </TableCell>
                    <TableCell className="text-xs text-text-muted">
                      {wl.blockers ? (
                        <span className="text-rose-500 font-medium">{wl.blockers}</span>
                      ) : (
                        '—'
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </Card>
      </div>
    </div>
  );
};
