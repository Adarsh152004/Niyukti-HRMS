import * as React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Workflow as WorkflowIcon, CheckCircle2, Clock, PlayCircle, AlertCircle,
  Plus, ShieldCheck, ArrowRight, Loader2, RefreshCw, Trash2, Sparkles, X
} from 'lucide-react';
import { PageHeader, Card, CardHeader, CardTitle, MetricCard } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge, StatusBadge } from '@/components/ui/badge';

export interface WorkflowStep {
  id: string;
  label: string;
  agent: string;
  status: 'completed' | 'running' | 'pending';
  duration?: string;
}

export interface EnterpriseWorkflow {
  id: string;
  name: string;
  category: string;
  status: 'running' | 'pending' | 'completed';
  currentStep: string;
  progress: number;
  startedAt: string;
  steps: WorkflowStep[];
}

const TEMPLATE_PRESETS = [
  { name: 'New Hire Onboarding & Provisioning', category: 'Workforce' },
  { name: 'Statutory Payroll Verification Cycle', category: 'Payroll' },
  { name: 'Automated Candidate Screening & Ranking', category: 'Recruitment' },
  { name: 'Security & KMS Policy Audit', category: 'Compliance' }
];

export function WorkflowsPage() {
  const queryClient = useQueryClient();
  const [isTriggerModalOpen, setIsTriggerModalOpen] = React.useState(false);
  const [newWfName, setNewWfName] = React.useState('');
  const [newWfCategory, setNewWfCategory] = React.useState('Workforce');

  // Fetch live workflows
  const { data: workflows = [], isLoading, refetch } = useQuery<EnterpriseWorkflow[]>({
    queryKey: ['enterprise-workflows-list'],
    queryFn: async () => {
      const res = await fetch('/api/v1/enterprise-workflows');
      if (!res.ok) return [];
      return res.json();
    },
    refetchInterval: 3000,
  });

  // Trigger Mutation
  const triggerMutation = useMutation({
    mutationFn: async (payload: { name: string; category: string }) => {
      const res = await fetch('/api/v1/enterprise-workflows/trigger', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error('Failed to trigger workflow');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['enterprise-workflows-list'] });
      setIsTriggerModalOpen(false);
      setNewWfName('');
    },
  });

  // Approve Step Mutation
  const approveMutation = useMutation({
    mutationFn: async (workflowId: string) => {
      const res = await fetch(`/api/v1/enterprise-workflows/${workflowId}/approve`, {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to approve step');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['enterprise-workflows-list'] });
    },
  });

  // Delete Workflow Mutation
  const deleteMutation = useMutation({
    mutationFn: async (workflowId: string) => {
      const res = await fetch(`/api/v1/enterprise-workflows/${workflowId}`, {
        method: 'DELETE',
      });
      if (!res.ok) throw new Error('Failed to delete workflow');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['enterprise-workflows-list'] });
    },
  });

  const activeCount = workflows.filter((w) => w.status === 'running').length;
  const completedCount = workflows.filter((w) => w.status === 'completed').length;
  const pendingHitlCount = workflows.filter((w) =>
    w.steps.some((s) => s.agent === 'Human-in-the-Loop' && s.status === 'running')
  ).length;

  return (
    <div className="space-y-5 pb-10">
      <PageHeader
        title="Automated Workflow Operations"
        description="State machine executions, multi-agent delegations, and standing enterprise background DAGs."
        actions={
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm" onClick={() => refetch()}>
              <RefreshCw className="h-3.5 w-3.5" aria-hidden />
              Sync
            </Button>
            <Button variant="primary" size="sm" onClick={() => setIsTriggerModalOpen(true)}>
              <PlayCircle className="h-3.5 w-3.5" aria-hidden />
              Trigger Workflow DAG
            </Button>
          </div>
        }
      />

      {/* Quick Launch Preset Buttons */}
      <div className="flex items-center gap-2 overflow-x-auto py-1 scrollbar-none">
        <span className="text-[10px] font-semibold text-text-muted uppercase tracking-wider whitespace-nowrap flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-accent" /> One-Click Launch:
        </span>
        {TEMPLATE_PRESETS.map((t, idx) => (
          <button
            key={idx}
            onClick={() => triggerMutation.mutate(t)}
            disabled={triggerMutation.isPending}
            className="text-xs whitespace-nowrap bg-surface hover:bg-surface-secondary border border-border hover:border-accent/50 text-text-primary rounded-full px-3 py-1.5 transition shadow-xs flex items-center gap-1"
          >
            <PlayCircle className="w-3 h-3 text-accent" />
            <span>{t.name}</span>
          </button>
        ))}
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard label="Active DAGs" value={activeCount} detail="Autonomous execution" />
        <MetricCard label="HITL Gates Waiting" value={pendingHitlCount} detail="Executive action required" />
        <MetricCard label="Completed Operations" value={completedCount} detail="All steps verified" />
        <MetricCard label="System Concurrency" value="Infinite Scale" detail="Event-driven state machine" />
      </div>

      {/* Workflows List */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="py-12 text-center text-text-muted">Loading workflow instances...</div>
        ) : workflows.length === 0 ? (
          <Card className="p-8 text-center space-y-3">
            <WorkflowIcon className="w-8 h-8 text-text-muted mx-auto" />
            <h3 className="font-semibold text-text-primary text-base">No active workflows</h3>
            <p className="text-xs text-text-muted max-w-sm mx-auto">
              Launch one of the preset workflows above or click "Trigger Workflow DAG" to initiate a background operation.
            </p>
          </Card>
        ) : (
          workflows.map((wf) => {
            const isHitlWaiting = wf.steps.some(
              (s) => s.agent === 'Human-in-the-Loop' && s.status === 'running'
            );

            return (
              <Card key={wf.id} className="p-5 space-y-4 border border-border hover:border-accent/40 transition">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border pb-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-text-primary text-base">{wf.name}</span>
                      <Badge variant={wf.status === 'completed' ? 'success' : 'primary'} size="sm">
                        {wf.status === 'completed' ? 'Completed' : 'Running'}
                      </Badge>
                      <span className="text-xs text-text-muted bg-surface-secondary px-2 py-0.5 rounded border border-border">
                        {wf.category}
                      </span>
                    </div>
                    <p className="text-xs text-text-muted mt-1 font-mono">{wf.id} · Started {new Date(wf.startedAt).toLocaleTimeString()}</p>
                  </div>

                  <div className="flex items-center gap-2">
                    {isHitlWaiting && (
                      <Button
                        size="sm"
                        variant="primary"
                        onClick={() => approveMutation.mutate(wf.id)}
                        disabled={approveMutation.isPending}
                        className="text-xs gap-1.5"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        Approve HITL Gate
                      </Button>
                    )}
                    <button
                      onClick={() => deleteMutation.mutate(wf.id)}
                      className="p-1.5 text-text-muted hover:text-danger rounded-lg transition"
                      title="Delete workflow"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs text-text-muted">
                    <span>Current: <strong className="text-text-primary">{wf.currentStep}</strong></span>
                    <span className="font-mono font-medium">{wf.progress}%</span>
                  </div>
                  <div className="w-full bg-surface-secondary rounded-full h-2 overflow-hidden border border-border">
                    <div
                      className={`h-full transition-all duration-500 ${
                        wf.status === 'completed' ? 'bg-emerald-500' : 'bg-accent'
                      }`}
                      style={{ width: `${wf.progress}%` }}
                    />
                  </div>
                </div>

                {/* DAG Steps timeline */}
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-2 pt-2">
                  {wf.steps.map((st, idx) => {
                    const isCompleted = st.status === 'completed';
                    const isRunning = st.status === 'running';

                    return (
                      <div
                        key={st.id || idx}
                        className={`p-2.5 rounded-lg border text-xs space-y-1 ${
                          isCompleted
                            ? 'bg-emerald-50/40 border-emerald-200 text-emerald-900'
                            : isRunning
                            ? 'bg-accent/10 border-accent/40 text-text-primary ring-1 ring-accent/30'
                            : 'bg-surface-secondary border-border text-text-muted'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-mono text-[10px] text-text-muted">0{idx + 1}</span>
                          {isCompleted ? (
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                          ) : isRunning ? (
                            <Loader2 className="w-3.5 h-3.5 text-accent animate-spin" />
                          ) : (
                            <Clock className="w-3.5 h-3.5 text-text-muted" />
                          )}
                        </div>
                        <p className="font-medium text-[11px] line-clamp-2 leading-tight">{st.label}</p>
                        <p className="text-[10px] opacity-75">{st.agent}</p>
                      </div>
                    );
                  })}
                </div>
              </Card>
            );
          })
        )}
      </div>

      {/* Custom Trigger Modal */}
      {isTriggerModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-surface border border-border rounded-xl max-w-md w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="font-semibold text-text-primary text-base flex items-center gap-2">
                <PlayCircle className="w-4 h-4 text-accent" /> Launch Workflow DAG
              </h3>
              <button onClick={() => setIsTriggerModalOpen(false)} className="text-text-muted hover:text-text-primary">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (newWfName.trim()) {
                  triggerMutation.mutate({ name: newWfName.trim(), category: newWfCategory });
                }
              }}
              className="space-y-3.5"
            >
              <div>
                <label className="text-xs font-medium text-text-secondary">Workflow Operation Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Q3 Compensation Equity Rebalancing"
                  value={newWfName}
                  onChange={(e) => setNewWfName(e.target.value)}
                  className="w-full h-8 px-3 text-xs bg-surface border border-border rounded-lg text-text-primary focus:outline-none focus:ring-1 focus:ring-accent mt-1"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-text-secondary">Category</label>
                <select
                  value={newWfCategory}
                  onChange={(e) => setNewWfCategory(e.target.value)}
                  className="w-full h-8 px-2 text-xs bg-surface border border-border rounded-lg text-text-primary mt-1"
                >
                  <option value="Workforce">Workforce Operations</option>
                  <option value="Payroll">Payroll & Compliance</option>
                  <option value="Recruitment">Recruitment & Sourcing</option>
                  <option value="Compliance">Security & Governance</option>
                </select>
              </div>

              <div className="flex gap-2 justify-end pt-2">
                <Button variant="secondary" size="sm" type="button" onClick={() => setIsTriggerModalOpen(false)}>
                  Cancel
                </Button>
                <Button variant="primary" size="sm" type="submit" disabled={triggerMutation.isPending}>
                  {triggerMutation.isPending ? 'Launching...' : 'Start Execution'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
