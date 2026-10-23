import * as React from 'react';
import { useQuery } from '@tanstack/react-query';
import { ShieldCheck, Lock, AlertTriangle, Activity, Database, CheckCircle, Flame } from 'lucide-react';
import { PageHeader, Card, CardHeader, CardTitle, MetricCard } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge, RiskBadge, StatusBadge } from '@/components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table';
import { withDataProvider } from '@/providers/data-provider';
import { DEMO_GOVERNANCE } from '@/fixtures';

export function GovernancePage() {
  const { data: gov } = useQuery({
    queryKey: ['governance-data'],
    queryFn: () => withDataProvider(async () => { throw new Error(); }, DEMO_GOVERNANCE),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        title="AI Governance & Safety Center"
        description="Real-time monitoring of AI gateways, LLM token economics, data firewalls, circuit breakers, and policy compliance."
        actions={
          <div className="flex items-center gap-2">
            <Badge variant="success" size="lg">
              <CheckCircle className="h-3.5 w-3.5" aria-hidden />
              AI Gateway: {gov?.gateway_status || 'OPERATIONAL'}
            </Badge>
            <Button variant="secondary" size="sm">Audit Log</Button>
          </div>
        }
      />

      {/* Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard label="Total Requests Today" value={gov?.firewall_metrics.scanned_today.toLocaleString() || '18,240'} detail="Across 24 active agents" />
        <MetricCard label="PII Auto-Masked" value={gov?.firewall_metrics.pii_masked || '412'} change={{ value: '100% compliant', direction: 'up', isPositive: true }} detail="Zero data leakage" />
        <MetricCard label="Prompt Injections Blocked" value={gov?.firewall_metrics.prompt_injections_blocked || '3'} change={{ value: 'Safe', direction: 'neutral', isPositive: true }} detail="Sanitized at gateway" />
        <MetricCard label="Circuit Breakers Tripped" value={gov?.firewall_metrics.tool_circuit_breaks || '1'} detail="Auto-recovered" />
      </div>

      {/* Model Providers / LLM Gateway Status */}
      <Card padding="none">
        <CardHeader className="px-5 pt-5 pb-3">
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-accent" aria-hidden />
            AI Providers &amp; Execution Engines
          </CardTitle>
        </CardHeader>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Provider / Model</TableHead>
              <TableHead>Health Status</TableHead>
              <TableHead className="text-right">p95 Latency</TableHead>
              <TableHead className="text-right">Error Rate</TableHead>
              <TableHead className="text-right">Requests Today</TableHead>
              <TableHead className="text-right">Tokens Consumed</TableHead>
              <TableHead className="text-right">Estimated Cost</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {gov?.providers.map((p) => (
              <TableRow key={p.name}>
                <TableCell className="font-medium text-text-primary">{p.name}</TableCell>
                <TableCell>
                  <Badge variant="success" size="sm">
                    <span className="h-1.5 w-1.5 rounded-full bg-success inline-block mr-1" />
                    {p.status}
                  </Badge>
                </TableCell>
                <TableCell className="text-right font-mono text-xs">{p.latency_p95}</TableCell>
                <TableCell className="text-right text-xs text-success">{p.error_rate}</TableCell>
                <TableCell className="text-right font-medium">{p.requests_today.toLocaleString()}</TableCell>
                <TableCell className="text-right text-text-muted text-xs font-mono">{p.tokens_today.toLocaleString()}</TableCell>
                <TableCell className="text-right font-medium text-text-primary">${p.cost_today.toFixed(2)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      {/* Security & Policy Violation Events */}
      <Card padding="none">
        <CardHeader className="px-5 pt-5 pb-3">
          <CardTitle className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-warning" aria-hidden />
            Recent Security &amp; Policy Guardrail Events
          </CardTitle>
        </CardHeader>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Event Type</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Agent</TableHead>
              <TableHead>Risk</TableHead>
              <TableHead className="text-right">Time</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {gov?.security_events.map((ev) => (
              <TableRow key={ev.id}>
                <TableCell>
                  <code className="text-xs bg-surface-secondary px-1.5 py-0.5 rounded border border-border font-mono font-medium">
                    {ev.type}
                  </code>
                </TableCell>
                <TableCell className="text-sm text-text-secondary">{ev.description}</TableCell>
                <TableCell className="text-xs text-text-muted">{ev.agent}</TableCell>
                <TableCell>
                  <RiskBadge level={ev.risk} />
                </TableCell>
                <TableCell className="text-right text-xs text-text-muted font-mono">{ev.timestamp}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
