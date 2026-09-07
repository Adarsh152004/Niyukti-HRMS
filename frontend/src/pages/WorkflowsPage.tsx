import * as React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Workflow as WorkflowIcon, CheckCircle2, Clock, PlayCircle, AlertCircle,
  Plus, ShieldCheck, ArrowRight, Loader2, RefreshCw
} from 'lucide-react';
import { PageHeader, Card, CardHeader, CardTitle, MetricCard } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge, StatusBadge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';

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

export function WorkflowsPage() {
  const queryClient = useQueryClient();
  const [isTriggerModalOpen, setIsTriggerModalOpen] = React.useState(false);
  const [newWfName, setNewWfName] = React.useState('');
  const [newWfCategory, setNewWfCategory] = React.useState('Workforce');

  // Fetch dynamic workflows from backend API
  const { data: workflows, isLoading, refetch } = useQuery<EnterpriseWorkflow[]>({
    queryKey: ['enterprise-workflows-list'],
    queryFn: async () => {
      const res = await fetch('/api/v1/enterprise-workflows');
      if (!res.ok) throw new Error('Failed to fetch workflows');
      return res.json();
    },
    refetchInterval: 3000, // Live auto-poll every 3s
  });

  // Trigger New Workflow Mutation
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

  // Approve HITL Step Mutation
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

  const handleTriggerSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newWfName.trim()) return;
    triggerMutation.mutate({ name: newWfName.trim(), category: newWfCategory });
  };

  const activeWorkflowsCount = workflows?.filter((w) => w.status !== 'completed').length || 0;
  const waitingOnHumanCount =
    workflows?.filter((w) =>
      w.steps.some((s) => s.agent === 'Human-in-the-Loop' && s.status === 'running')
    ).length || 0;

  return (
    <div className="space-y-5 pb-10">
      <PageHeader
        title="Automated Workflow Operations"
        description="State machine executions, multi-agent delegations, and standing enterprise background DAGs."
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => refetch()}
              className="flex items-center gap-1.5"
            >
              <RefreshCw className="h-3.5 w-3.5" /> Refresh
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={() => setIsTriggerModalOpen(true)}
              className="flex items-center gap-1.5"
            >
              <Plus className="h-4 w-4" /> Trigger Workflow
            </Button>
          </div>
        }
      />

      {/* Metrics Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard label="Active Workflows" value={activeWorkflowsCount} detail="Running &amp; pending" />
        <MetricCard label="Average Completion Time" value="4.2h" detail="Onboarding SLA" />
        <MetricCard
          label="Automation Rate"
          value="91.4%"
          change={{ value: '+2.1%', direction: 'up', isPositive: true }}
          detail="Zero-touch steps"
        />
        <MetricCard label="Waiting on Human" value={waitingOnHumanCount} detail="Executive sign-off required" />
      </div>

      {/* Workflows List */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="h-48 flex items-center justify-center bg-surface rounded-xl border border-border">
            <Loader2 className="h-6 w-6 text-accent animate-spin" />
          </div>
        ) : workflows && workflows.length > 0 ? (
          workflows.map((wf) => (
            <Card key={wf.id} padding="none" className="overflow-hidden shadow-sm">
              <div className="px-5 py-4 bg-surface-secondary border-b border-border flex items-center justify-between flex-wrap gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-text-primary text-base">{wf.name}</h3>
                    <Badge variant="default" size="sm">
                      {wf.category}
                    </Badge>
                    <StatusBadge status={wf.status === 'completed' ? 'active' : wf.status} />
                  </div>
                  <p className="text-xs text-text-muted mt-1">
                    Current Step: <strong className="text-text-primary">{wf.currentStep}</strong> • Started at{' '}
                    {new Date(wf.startedAt).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>

                <div className="flex items-center gap-4">
                  {/* Approve HITL Button if waiting on Human */}
                  {wf.steps.some((s) => s.agent === 'Human-in-the-Loop' && s.status === 'running') && (
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => approveMutation.mutate(wf.id)}
                      disabled={approveMutation.isPending}
                      className="bg-amber-600 hover:bg-amber-500 text-white flex items-center gap-1.5"
                    >
                      <ShieldCheck className="h-4 w-4" /> Approve &amp; Advance Step
                    </Button>
                  )}

                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <p className="text-xs text-text-muted">Progress</p>
                      <p className="text-sm font-bold text-text-primary">{wf.progress}%</p>
                    </div>
                    <div className="w-24 h-2 rounded-full bg-border overflow-hidden">
                      <div
                        className="h-full rounded-full bg-accent transition-all duration-300"
                        style={{ width: `${wf.progress}%` }}
                        role="progressbar"
                        aria-valuenow={wf.progress}
                        aria-valuemin={0}
                        aria-valuemax={100}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Workflow Step Progression Bar */}
              <div className="p-5 overflow-x-auto">
                <div className="flex items-center gap-3 min-w-[650px]">
                  {wf.steps.map((step, idx) => (
                    <React.Fragment key={step.id}>
                      <div className="flex flex-col items-center text-center space-y-1.5 flex-1 min-w-[130px]">
                        <div className="relative">
                          {step.status === 'completed' ? (
                            <div className="w-7 h-7 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 flex items-center justify-center">
                              <CheckCircle2 className="h-4 w-4" />
                            </div>
                          ) : step.status === 'running' ? (
                            <div className="w-7 h-7 rounded-full bg-accent-soft text-accent border border-accent/40 flex items-center justify-center animate-pulse">
                              <PlayCircle className="h-4 w-4" />
                            </div>
                          ) : (
                            <div className="w-7 h-7 rounded-full bg-surface-secondary text-text-muted border border-border flex items-center justify-center">
                              <Clock className="h-4 w-4" />
                            </div>
                          )}
                        </div>
                        <p className="text-xs font-medium text-text-primary line-clamp-2 leading-tight">
                          {step.label}
                        </p>
                        <p className="text-2xs font-semibold text-text-muted">{step.agent}</p>
                        {step.duration && (
                          <span className="text-2xs text-text-muted bg-surface-secondary px-1.5 py-0.5 rounded border border-border">
                            {step.duration}
                          </span>
                        )}
                      </div>
                      {idx < wf.steps.length - 1 && (
                        <div className="w-6 h-0.5 bg-border shrink-0 self-center -mt-6" />
                      )}
                    </React.Fragment>
                  ))}
                </div>
              </div>
            </Card>
          ))
        ) : (
          <div className="p-8 text-center text-text-muted text-sm bg-surface rounded-xl border border-border">
            No active standing enterprise workflows. Click "Trigger Workflow" to launch a new background DAG.
          </div>
        )}
      </div>

      {/* Trigger Workflow Modal */}
      {isTriggerModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-surface border border-border rounded-xl p-6 w-full max-w-md space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-base font-bold text-text-primary">Trigger Standing Enterprise Workflow</h3>
              <button
                onClick={() => setIsTriggerModalOpen(false)}
                className="text-text-muted hover:text-text-primary text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleTriggerSubmit} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-text-muted block mb-1">
                  Workflow Name
                </label>
                <input
                  type="text"
                  value={newWfName}
                  onChange={(e) => setNewWfName(e.target.value)}
                  placeholder="e.g. New Hire Onboarding - Elena Rostova"
                  className="w-full px-3 py-2 text-sm bg-surface border border-border rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-accent"
                  required
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-text-muted block mb-1">Category</label>
                <select
                  value={newWfCategory}
                  onChange={(e) => setNewWfCategory(e.target.value)}
                  className="w-full px-3 py-2 text-sm bg-surface border border-border rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-accent"
                >
                  <option value="Workforce">Workforce &amp; Onboarding</option>
                  <option value="Payroll & Finance">Payroll &amp; Finance</option>
                  <option value="Talent & Compensation">Talent &amp; Compensation</option>
                  <option value="SLA Maintenance">SLA &amp; Operations Maintenance</option>
                </select>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  onClick={() => setIsTriggerModalOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  size="sm"
                  disabled={triggerMutation.isPending || !newWfName.trim()}
                >
                  {triggerMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Launch DAG'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
