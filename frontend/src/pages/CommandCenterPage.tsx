import * as React from 'react';
import { useQuery } from '@tanstack/react-query';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { ArrowRight, CheckSquare, Bot, TrendingUp, Sparkles, Clock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { PageHeader, Card, CardHeader, CardTitle, MetricCard } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RiskBadge, StatusBadge } from '@/components/ui/badge';
import { ToolExecution } from '@/components/ai/ai-primitives';
import { withDataProvider } from '@/providers/data-provider';
import { DEMO_KPIS, DEMO_HEADCOUNT_TREND, DEMO_APPROVALS, DEMO_AGENTS } from '@/fixtures';

const DEMO_ACTIVE_AUTOMATIONS = [
  { name: 'August Payroll Processing', status: 'running' as const, step: 'Calculating statutory deductions', progress: 78 },
  { name: 'Q3 Performance Review Cycle', status: 'pending' as const, step: 'Waiting for manager sign-off', progress: 42 },
  { name: 'New Hire Onboarding - Alice Lin', status: 'running' as const, step: 'Provisioning system access', progress: 65 },
];

export function CommandCenterPage() {
  const navigate = useNavigate();
  const [queryInput, setQueryInput] = React.useState('');

  const { data: suggestionsData } = useQuery({
    queryKey: ['command-center-dynamic-suggestions'],
    queryFn: async () => {
      const res = await fetch('/api/v1/orchestration/suggestions');
      if (!res.ok) return null;
      return res.json();
    },
    staleTime: 60_000,
  });

  const { data: kpis } = useQuery({
    queryKey: ['dashboard-kpis'],
    queryFn: () => withDataProvider(async () => { throw new Error(); }, DEMO_KPIS),
  });
  const { data: trend } = useQuery({
    queryKey: ['headcount-trend'],
    queryFn: () => withDataProvider(async () => { throw new Error(); }, DEMO_HEADCOUNT_TREND),
  });
  const { data: approvals } = useQuery({
    queryKey: ['pending-approvals'],
    queryFn: () => withDataProvider(async () => { throw new Error(); }, DEMO_APPROVALS),
  });
  const { data: agents } = useQuery({
    queryKey: ['agents'],
    queryFn: () => withDataProvider(async () => { throw new Error(); }, DEMO_AGENTS),
  });

  const suggestedPrompts = suggestionsData?.suggested_prompts || [
    'Check headcount distribution across all departments',
    'Show attendance of Priya',
    'Recruit a new senior backend engineer for HealthPulse',
    'List all employees in our company',
  ];

  return (
    <div className="space-y-5">
      <PageHeader
        title="Executive Command Center"
        description="Organization intelligence, active automation, and decisions requiring your attention."
      />

      {/* Natural language query surface */}
      <Card className="border-border-strong">
        <div className="flex items-center justify-between mb-2">
          <p className="text-xs font-semibold text-text-muted uppercase tracking-wide flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-accent" />
            Ask your organization
          </p>
          {suggestionsData?.time_context && (
            <span className="text-2xs text-text-muted flex items-center gap-1">
              <Clock className="w-3 h-3 text-accent" />
              <span className="capitalize">{suggestionsData.time_context.period} focus</span>: {suggestionsData.time_context.time}
            </span>
          )}
        </div>

        <div className="flex gap-2">
          <input
            type="text"
            value={queryInput}
            onChange={(e) => setQueryInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && navigate('/ai', { state: { query: queryInput } })}
            placeholder="What needs executive attention today?"
            className="flex-1 h-9 px-3 text-sm bg-surface-secondary border border-border rounded-md text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent"
            aria-label="Ask the AI about the organization"
          />
          <Button variant="primary" size="md" onClick={() => navigate('/ai', { state: { query: queryInput } })}>
            Ask <ArrowRight className="h-3.5 w-3.5" aria-hidden />
          </Button>
        </div>

        <div className="flex flex-wrap gap-2 mt-2.5">
          {suggestedPrompts.map((q: string) => (
            <button
              key={q}
              onClick={() => navigate('/ai', { state: { query: q } })}
              className="text-2xs px-2.5 py-1 rounded-full bg-surface-secondary hover:bg-surface-secondary/80 border border-border text-text-muted hover:text-text-primary transition"
            >
              {q}
            </button>
          ))}
        </div>
      </Card>

      {/* Primary KPI strip */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard label="Headcount" value={(kpis as any)?.total_headcount?.value ?? (kpis as any)?.headcount?.value ?? 11} subtext="vs last quarter" />
        <MetricCard label="Attrition Rate" value={(kpis as any)?.attrition_rate?.value ?? (kpis as any)?.attrition?.value ?? '0.0%'} subtext="annualized" />
        <MetricCard label="Open Requisitions" value={(kpis as any)?.open_positions?.value ?? (kpis as any)?.openRequisitions?.value ?? 7} subtext="active openings" />
        <MetricCard label="Active AI Agents" value={(kpis as any)?.active_ai_agents?.value ?? 8} subtext="autonomous agents" />
      </div>

      {/* Headcount vs Attrition */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Workforce Growth & Attrition Trend</CardTitle>
          </CardHeader>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trend ?? []}>
                <defs>
                  <linearGradient id="colorHeadcount" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--color-accent, #3b82f6)" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="var(--color-accent, #3b82f6)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border, #e5e7eb)" />
                <XAxis dataKey="month" tick={{ fontSize: 11, fill: 'var(--color-text-muted, #9ca3af)' }} />
                <YAxis tick={{ fontSize: 11, fill: 'var(--color-text-muted, #9ca3af)' }} />
                <Tooltip />
                <Area type="monotone" dataKey="headcount" stroke="var(--color-accent, #3b82f6)" fill="url(#colorHeadcount)" name="Headcount" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Decisions needing CEO attention */}
        <Card>
          <CardHeader>
            <CardTitle>Requires Your Attention</CardTitle>
          </CardHeader>
          <div className="space-y-3">
            {approvals?.slice(0, 3).map((a) => (
              <div key={a.id} className="p-2.5 rounded-lg bg-surface-secondary border border-border text-xs space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-text-primary">{a.title}</span>
                  <RiskBadge level={a.riskLevel as any} />
                </div>
                <p className="text-text-muted">{(a as any).summary || a.reason}</p>
                <div className="flex gap-2 pt-1">
                  <Button variant="primary" size="sm" onClick={() => navigate('/approvals')}>Review</Button>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
