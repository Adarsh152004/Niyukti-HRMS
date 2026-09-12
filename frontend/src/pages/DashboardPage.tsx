import * as React from 'react';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { useQuery } from '@tanstack/react-query';
import { AlertTriangle, ArrowRight, Bot, CheckSquare } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { PageHeader, MetricCard, Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { StatusBadge } from '@/components/ui/badge';
import { SkeletonTable } from '@/components/ui/skeleton';
import { withDataProvider } from '@/providers/data-provider';
import { apiClient } from '@/api/client';
import {
  DEMO_KPIS, DEMO_HEADCOUNT_TREND, DEMO_ATTRITION_TREND,
  DEMO_APPROVALS, DEMO_AGENTS,
} from '@/fixtures';

export function DashboardPage() {
  const navigate = useNavigate();

  const { data: dashboardData, isLoading: kpiLoading } = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: async () => {
      try {
        const res = await apiClient<{ summary: any; departments: any[]; ai_operations: any }>('/analytics/dashboard');
        return res;
      } catch {
        return null;
      }
    },
  });

  const { data: pendingApprovalsList } = useQuery({
    queryKey: ['pending-approvals'],
    queryFn: async () => {
      try {
        const res = await apiClient<any[]>('/approvals');
        return res;
      } catch {
        return [];
      }
    },
  });

  const kpis = React.useMemo(() => {
    const s = dashboardData?.summary;
    if (!s) return DEMO_KPIS;
    return {
      total_headcount: { value: s.total_headcount || 12, change: 4.2, period: 'Active Staff' },
      attrition_rate: { value: s.attrition_risk_rate || 3.8, change: -1.2, period: 'vs Prior Year' },
      open_positions: { value: s.active_job_openings || 4, change: 2, period: 'Open Roles' },
      absenteeism_rate: { value: Math.max(0, 100 - (s.overall_attendance_rate || 95.4)).toFixed(1), change: 0.3, period: 'This Month' },
      pending_approvals: { value: s.pending_hitl_approvals || 2, change: 0, period: 'Action Required' },
      active_ai_agents: { value: dashboardData?.ai_operations?.active_agents || 8, change: 0, period: 'Fleet Active' },
    };
  }, [dashboardData]);

  const headcountTrend = React.useMemo(() => {
    const depts = dashboardData?.departments;
    if (depts && depts.length > 0) {
      return depts.map((d: any) => ({
        month: d.department.slice(0, 7),
        headcount: d.headcount || 4,
      }));
    }
    return DEMO_HEADCOUNT_TREND;
  }, [dashboardData]);

  const attritionTrend = DEMO_ATTRITION_TREND;
  const approvals = pendingApprovalsList && pendingApprovalsList.length > 0 ? pendingApprovalsList : DEMO_APPROVALS;
  const agents = DEMO_AGENTS;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Workforce Overview"
        description="Organization health, workforce metrics, and AI automation status."
        actions={
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm">This Month</Button>
            <Button variant="secondary" size="sm">Export</Button>
          </div>
        }
      />

      {/* ── KPI Row ────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4">
        {kpis && (
          <>
            <MetricCard
              label="Total Headcount"
              value={kpis.total_headcount.value}
              change={{ value: `${Math.abs(kpis.total_headcount.change)}%`, direction: 'up', isPositive: true }}
              detail={kpis.total_headcount.period}
            />
            <MetricCard
              label="Attrition Rate"
              value={`${kpis.attrition_rate.value}%`}
              change={{ value: `${Math.abs(kpis.attrition_rate.change)}%`, direction: 'down', isPositive: true }}
              detail="vs Prior Year"
            />
            <MetricCard
              label="Open Positions"
              value={kpis.open_positions.value}
              change={{ value: `+${kpis.open_positions.change}`, direction: 'up', isPositive: false }}
              detail={kpis.open_positions.period}
            />
            <MetricCard
              label="Absenteeism"
              value={`${kpis.absenteeism_rate.value}%`}
              change={{ value: `+${kpis.absenteeism_rate.change}%`, direction: 'up', isPositive: false }}
              detail={kpis.absenteeism_rate.period}
            />
            <MetricCard
              label="Pending Approvals"
              value={kpis.pending_approvals.value}
              detail="Require your decision"
            />
            <MetricCard
              label="Active AI Agents"
              value={`${kpis.active_ai_agents.value} / 24`}
              detail="Fleet operational"
            />
          </>
        )}
      </div>

      {/* ── Main Charts Row ───────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Headcount Trend */}
        <Card>
          <CardHeader>
            <CardTitle>Workforce Headcount — 8 Month Trend</CardTitle>
          </CardHeader>
          <div className="h-52">
            {headcountTrend ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={headcountTrend} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--tw-border)" className="stroke-border" />
                  <XAxis dataKey="month" tick={{ fontSize: 11, fill: 'var(--text-muted, #6B7280)' }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: 'var(--text-muted, #6B7280)' }} axisLine={false} tickLine={false} domain={['dataMin - 10', 'dataMax + 10']} />
                  <Tooltip
                    contentStyle={{
                      fontSize: 12,
                      border: '1px solid hsl(220 13% 90%)',
                      borderRadius: 8,
                      background: 'hsl(0 0% 100%)',
                      color: 'hsl(220 26% 10%)',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="headcount"
                    stroke="#2563EB"
                    strokeWidth={2}
                    fill="#EFF6FF"
                    dot={false}
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full bg-surface-secondary rounded animate-skeleton-pulse" />
            )}
          </div>
        </Card>

        {/* Attrition Trend */}
        <Card>
          <CardHeader>
            <CardTitle>Attrition Rate — YTD Trajectory</CardTitle>
          </CardHeader>
          <div className="h-52">
            {attritionTrend ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={attritionTrend} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(220 13% 90%)" />
                  <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#6B7280' }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: '#6B7280' }} axisLine={false} tickLine={false} unit="%" />
                  <Tooltip
                    formatter={(v: number) => [`${v}%`, 'Attrition']}
                    contentStyle={{ fontSize: 12, border: '1px solid #E5E7EB', borderRadius: 8, background: '#fff' }}
                  />
                  <Bar dataKey="rate" fill="#2563EB" radius={[3, 3, 0, 0]} maxBarSize={36} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full bg-surface-secondary rounded animate-skeleton-pulse" />
            )}
          </div>
        </Card>
      </div>

      {/* ── Bottom Row: Attention Required + Agent Fleet ──────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        {/* Pending Approvals */}
        <Card className="lg:col-span-3" padding="none">
          <CardHeader className="px-5 pt-5 pb-4">
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-warning" aria-hidden />
              Attention Required
            </CardTitle>
            <Button
              variant="ghost"
              size="xs"
              onClick={() => navigate('/approvals')}
              className="text-accent"
            >
              View all <ArrowRight className="h-3 w-3" aria-hidden />
            </Button>
          </CardHeader>
          <div className="divide-y divide-border px-5 pb-4 space-y-0">
            {approvals?.map((item) => (
              <div key={item.id} className="py-3 flex items-center gap-3">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-text-primary truncate">{item.title}</p>
                  <p className="text-xs text-text-muted mt-0.5">{item.requestedBy} · {item.riskLevel} risk · {item.confidence}% confidence</p>
                </div>
                <Button
                  size="xs"
                  variant="primary"
                  onClick={() => navigate('/approvals')}
                >
                  Review
                </Button>
              </div>
            ))}
          </div>
        </Card>

        {/* AI Agent Status */}
        <Card className="lg:col-span-2" padding="none">
          <CardHeader className="px-5 pt-5 pb-4">
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-4 w-4 text-accent" aria-hidden />
              AI Agent Fleet
            </CardTitle>
            <Button variant="ghost" size="xs" onClick={() => navigate('/agents')} className="text-accent">
              View all <ArrowRight className="h-3 w-3" aria-hidden />
            </Button>
          </CardHeader>
          <div className="divide-y divide-border px-5 pb-4">
            {agents?.slice(0, 5).map((agent) => (
              <div key={agent.id} className="py-2.5 flex items-center gap-3">
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-text-primary truncate">{agent.name}</p>
                  <p className="text-xs text-text-muted">{agent.tasks_today} tasks · {agent.avg_latency_ms}ms avg</p>
                </div>
                <StatusBadge status={agent.status} />
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
