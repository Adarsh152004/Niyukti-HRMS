import * as React from 'react';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Pause, Play, Power, MoreHorizontal, ChevronRight, Zap, RefreshCw,
  CheckCircle2, Clock, Bot, Activity, Layers, ArrowRight, ShieldCheck,
  Check, ArrowUpRight, Cpu
} from 'lucide-react';
import { PageHeader, Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { StatusBadge, Badge, type StatusVariant } from '@/components/ui/badge';
import {
  Table, TableHeader, TableBody, TableRow, TableHead, TableCell,
} from '@/components/ui/table';

interface ActiveWorkflowRun {
  run_id: string;
  workflow_status: string;
  decision: string;
  provider_used: string;
  collaboration_chain: string[];
  markdown_answer: string;
  approval_request?: any;
  artifact?: any;
  nodes?: any[];
}

interface FleetAgent {
  id: string;
  name: string;
  role: string;
  status: StatusVariant;
  tasks_today: number;
  success_rate: number;
  avg_latency_ms: number;
  autonomy_mode: string;
  primary_domain: string;
}

const FLEET_AGENTS: FleetAgent[] = [
  {
    id: 'agent-nova',
    name: 'Executive Partner (Nova)',
    role: 'Autonomous Coordinator & Domain Classifier',
    status: 'active',
    tasks_today: 42,
    success_rate: 99.8,
    avg_latency_ms: 45,
    autonomy_mode: 'AUTONOMOUS_LOW_RISK',
    primary_domain: 'Executive Strategy & Intent Routing'
  },
  {
    id: 'agent-payroll',
    name: 'Deterministic Payroll Agent',
    role: 'Statutory Tax, Salary Run & Audit Ledger',
    status: 'active',
    tasks_today: 18,
    success_rate: 100.0,
    avg_latency_ms: 72,
    autonomy_mode: 'AUTONOMOUS_WITH_APPROVAL',
    primary_domain: 'Compensation & Financial Compliance'
  },
  {
    id: 'agent-recruitment',
    name: 'Talent Acquisition & JD Builder',
    role: 'Candidate Matching, Offer Letters & JDs',
    status: 'active',
    tasks_today: 27,
    success_rate: 98.5,
    avg_latency_ms: 120,
    autonomy_mode: 'AUTONOMOUS_WITH_APPROVAL',
    primary_domain: 'Talent & Open Requisitions'
  },
  {
    id: 'agent-attendance',
    name: 'Workforce Attendance Auditor',
    role: 'Biometric & Portal Punch Compliance',
    status: 'active',
    tasks_today: 64,
    success_rate: 99.4,
    avg_latency_ms: 38,
    autonomy_mode: 'AUTONOMOUS_LOW_RISK',
    primary_domain: 'Time Management & Compliance'
  },
  {
    id: 'agent-leave',
    name: 'Leave Policy & Entitlement Agent',
    role: 'Balance Verification & Approval Orchestrator',
    status: 'active',
    tasks_today: 31,
    success_rate: 100.0,
    avg_latency_ms: 48,
    autonomy_mode: 'AUTONOMOUS_WITH_APPROVAL',
    primary_domain: 'PTO & Statutory Leaves'
  },
  {
    id: 'agent-self-rag',
    name: 'Self-RAG Grounded Intelligence Engine',
    role: 'Live SQLite Ingestion & Fact Verification',
    status: 'active',
    tasks_today: 89,
    success_rate: 99.9,
    avg_latency_ms: 110,
    autonomy_mode: 'ADVISORY',
    primary_domain: 'Enterprise Grounded Knowledge'
  },
];

export function AgentsPage() {
  const navigate = useNavigate();
  const [activeRun, setActiveRun] = useState<ActiveWorkflowRun | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [approving, setApproving] = useState(false);

  // Trigger autonomous workflow
  const triggerWorkflow = async (queryText: string) => {
    setIsExecuting(true);
    setActiveRun(null);
    try {
      const res = await fetch('/api/v1/orchestration/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: queryText,
          initiator: 'CEO / Fleet Director',
          channel: 'AI_WORKSPACE'
        })
      });

      if (res.ok) {
        const data = await res.json();
        const structured = data.structured_response || {};
        setActiveRun({
          run_id: data.run_id,
          workflow_status: data.workflow_status,
          decision: data.decision,
          provider_used: data.provider_used,
          collaboration_chain: structured.collaboration_chain || ['Executive Partner (Nova)', 'Database Facts Engine', 'Synthesis Agent'],
          markdown_answer: structured.markdown_answer || data.envelope?.text || 'Workflow completed successfully.',
          approval_request: structured.approval_request,
          artifact: structured.artifact,
        });
      }
    } catch (err) {
      console.error('Failed to execute workflow:', err);
    } finally {
      setIsExecuting(false);
    }
  };

  // Sign off on pending approval gate
  const approveRun = async () => {
    if (!activeRun?.run_id) return;
    setApproving(true);
    try {
      const res = await fetch(`/api/v1/orchestration/workflows/${activeRun.run_id}/approve`, {
        method: 'POST'
      });
      if (res.ok) {
        setActiveRun(prev => prev ? {
          ...prev,
          workflow_status: 'COMPLETED',
          approval_request: { ...prev.approval_request, status: 'APPROVED' },
        } : null);
      }
    } catch (e) {
      console.error('Approval failed:', e);
    } finally {
      setApproving(false);
    }
  };

  return (
    <div className="space-y-4">
      <PageHeader
        title="AI Agent Fleet & Multi-Agent Orchestration"
        description="Autonomous HR agents with live SQLite data verification, delegation chains, and human approval gates."
        actions={
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm" onClick={() => navigate('/orchestration')}>
              <Activity className="h-3.5 w-3.5 mr-1.5 text-indigo-500" />
              Open DAG Explorer
            </Button>
            <Button variant="primary" size="sm" onClick={() => navigate('/ai')}>
              <Bot className="h-3.5 w-3.5 mr-1.5" />
              AI Workspace Chat
            </Button>
          </div>
        }
      />

      {/* Fleet Summary KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {[
          { label: 'Active Autonomous Agents', count: '6 / 6', variant: 'success' as const, sub: '100% Operational' },
          { label: 'Agent Tasks Dispatched Today', count: '271', variant: 'primary' as const, sub: '+34 from yesterday' },
          { label: 'Grounded Execution Accuracy', count: '99.6%', variant: 'default' as const, sub: 'Zero hallucinations (Self-RAG)' },
          { label: 'Human-in-the-Loop Gates', count: activeRun?.workflow_status === 'WAITING_FOR_APPROVAL' ? '1 PENDING' : '0 PENDING', variant: activeRun?.workflow_status === 'WAITING_FOR_APPROVAL' ? ('warning' as const) : ('success' as const), sub: 'Executive sign-off' },
        ].map(({ label, count, sub }) => (
          <Card key={label} className="p-4">
            <p className="text-2xl font-bold text-text-primary tracking-tight">{count}</p>
            <p className="text-xs font-semibold text-text-muted mt-0.5">{label}</p>
            <p className="text-[11px] text-text-muted/70 mt-1 font-mono">{sub}</p>
          </Card>
        ))}
      </div>

      {/* Instant Multi-Agent Autonomous Launcher */}
      <div className="p-4 bg-surface border border-border rounded-xl shadow-xs space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-500">
              <Zap className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-text-primary">Autonomous Multi-Agent Triggers</h3>
              <p className="text-xs text-text-muted">Launch orchestrated agent chains with live DAG progression and human sign-offs.</p>
            </div>
          </div>
          {isExecuting && (
            <div className="flex items-center gap-1.5 text-xs text-indigo-500 font-semibold animate-pulse">
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              <span>Running delegation graph...</span>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2.5">
          {[
            {
              title: 'Deterministic Payroll Run',
              desc: '5-node audit, statutory taxes & CEO disbursement approval gate',
              icon: Activity,
              query: 'Run monthly payroll for all employees',
              accent: 'border-l-emerald-500',
            },
            {
              title: 'Recruitment & Job Description',
              desc: 'Draft requisition, role specs, and candidate matcher pipeline',
              icon: Bot,
              query: 'Create job description for senior platform engineer',
              accent: 'border-l-indigo-500',
            },
            {
              title: 'Attendance Compliance Audit',
              desc: 'Scan punch timestamps, remote checks, and anomaly detection',
              icon: Clock,
              query: 'Run attendance compliance audit',
              accent: 'border-l-sky-500',
            },
            {
              title: 'Executive Headcount Breakdown',
              desc: 'Compute active headcount & departmental density from SQLite',
              icon: Layers,
              query: 'Check active headcount breakdown',
              accent: 'border-l-purple-500',
            },
          ].map((action, i) => {
            const Icon = action.icon;
            return (
              <button
                key={i}
                disabled={isExecuting}
                onClick={() => triggerWorkflow(action.query)}
                className={`p-3 rounded-lg bg-surface-secondary/70 hover:bg-surface-secondary border border-border hover:border-indigo-500/50 border-l-3 ${action.accent} text-left transition group disabled:opacity-50 cursor-pointer shadow-2xs`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2">
                    <Icon className="w-3.5 h-3.5 text-text-muted group-hover:text-indigo-500 transition-colors" />
                    <span className="text-xs font-bold text-text-primary group-hover:text-indigo-500 transition-colors">{action.title}</span>
                  </div>
                  <ArrowRight className="w-3 h-3 text-text-muted group-hover:text-indigo-500 transition-colors" />
                </div>
                <p className="text-[11px] text-text-muted leading-relaxed">{action.desc}</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Live Active Workflow Result & Approval Card */}
      {activeRun && (
        <div className="p-4 rounded-xl border border-indigo-500/40 bg-indigo-500/5 space-y-3.5 shadow-sm">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-surface border border-border text-text-muted">
                RUN: {activeRun.run_id}
              </span>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                activeRun.workflow_status === 'WAITING_FOR_APPROVAL'
                  ? 'bg-amber-500/15 text-amber-500 border border-amber-500/30 animate-pulse'
                  : 'bg-emerald-500/15 text-emerald-500 border border-emerald-500/30'
              }`}>
                {activeRun.workflow_status.replace(/_/g, ' ')}
              </span>
              <span className="text-xs text-text-muted">
                via <strong className="text-text-primary font-medium">{activeRun.provider_used}</strong>
              </span>
            </div>

            <Button variant="secondary" size="sm" onClick={() => navigate('/orchestration')}>
              <span>View Full DAG Graph</span>
              <ArrowUpRight className="w-3.5 h-3.5 ml-1" />
            </Button>
          </div>

          {/* Multi-Agent Delegation Chain */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
            <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider mr-1">Chain:</span>
            {activeRun.collaboration_chain.map((ag, idx) => (
              <React.Fragment key={idx}>
                <span className="px-2 py-1 rounded bg-surface border border-border text-xs font-semibold text-text-primary whitespace-nowrap flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                  <span>{ag}</span>
                </span>
                {idx < activeRun.collaboration_chain.length - 1 && (
                  <ArrowRight className="w-3 h-3 text-text-muted shrink-0" />
                )}
              </React.Fragment>
            ))}
          </div>

          {/* Human Review Approval Gate Action Banner */}
          {activeRun.workflow_status === 'WAITING_FOR_APPROVAL' && (
            <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-amber-500 animate-pulse shrink-0" />
                <div>
                  <p className="text-xs font-bold text-amber-500">Executive Approval Required</p>
                  <p className="text-[11px] text-text-muted">
                    {activeRun.approval_request?.action_required || 'Review artifact output and sign-off to disburse funds / publish requisition.'}
                  </p>
                </div>
              </div>
              <Button
                variant="primary"
                size="sm"
                disabled={approving}
                onClick={approveRun}
                className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold"
              >
                <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                <span>{approving ? 'Signing Off...' : 'Sign-Off & Authorize'}</span>
              </Button>
            </div>
          )}

          {/* Markdown Output Snippet */}
          <div className="p-3 rounded-lg bg-surface border border-border text-xs text-text-secondary whitespace-pre-wrap max-h-48 overflow-y-auto leading-relaxed">
            {activeRun.markdown_answer}
          </div>
        </div>
      )}

      {/* Fleet Agents Table */}
      <div className="border border-border rounded-lg overflow-hidden bg-surface">
        <div className="p-3 bg-surface-secondary/60 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="w-4 h-4 text-indigo-500" />
            <span className="text-xs font-bold text-text-primary">Operational Agent Roster</span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-surface border border-border text-text-muted font-mono">
              6 Online
            </span>
          </div>
          <span className="text-[11px] text-text-muted">
            All agents connected to core SQLite & Supabase event bus
          </span>
        </div>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Agent</TableHead>
              <TableHead>Core Role & Capabilities</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Tasks Today</TableHead>
              <TableHead className="text-right">Accuracy Rate</TableHead>
              <TableHead className="text-right">Avg Latency</TableHead>
              <TableHead>Autonomy Policy</TableHead>
              <TableHead className="text-right">Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {FLEET_AGENTS.map((agent) => (
              <TableRow key={agent.id}>
                <TableCell>
                  <div className="flex items-center gap-2.5">
                    <div className="h-8 w-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center shrink-0">
                      <Bot className="w-4 h-4 text-indigo-500" />
                    </div>
                    <div>
                      <p className="font-bold text-text-primary text-sm">{agent.name}</p>
                      <p className="text-[11px] text-text-muted font-mono">{agent.primary_domain}</p>
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <code className="text-xs text-text-muted bg-surface-secondary px-1.5 py-0.5 rounded border border-border font-mono">
                    {agent.role}
                  </code>
                </TableCell>
                <TableCell>
                  <StatusBadge status={agent.status} />
                </TableCell>
                <TableCell className="text-right font-medium text-text-primary font-mono">
                  {agent.tasks_today}
                </TableCell>
                <TableCell className="text-right">
                  <span className="text-emerald-500 font-bold font-mono">
                    {agent.success_rate}%
                  </span>
                </TableCell>
                <TableCell className="text-right text-text-secondary font-mono">
                  {agent.avg_latency_ms}ms
                </TableCell>
                <TableCell>
                  <Badge variant={
                    agent.autonomy_mode === 'AUTONOMOUS_LOW_RISK' ? 'success' :
                    agent.autonomy_mode === 'AUTONOMOUS_WITH_APPROVAL' ? 'warning' : 'default'
                  } size="sm">
                    {agent.autonomy_mode.replace(/_/g, ' ')}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => triggerWorkflow(`Execute audit for ${agent.name}`)}
                    className="text-xs text-indigo-500 hover:text-indigo-400"
                  >
                    Run Audit
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
