import * as React from 'react';
import { useQuery } from '@tanstack/react-query';
import { FileSearch, Filter, ShieldCheck, Download, Search } from 'lucide-react';
import { PageHeader, Card, CardHeader, CardTitle, MetricCard } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge, RiskBadge } from '@/components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table';
import { withDataProvider } from '@/providers/data-provider';
import { DEMO_AUDIT_LOGS } from '@/fixtures';

export function AuditPage() {
  const [search, setSearch] = React.useState('');
  const { data: logs } = useQuery({
    queryKey: ['audit-logs'],
    queryFn: () => withDataProvider(async () => { throw new Error(); }, DEMO_AUDIT_LOGS),
  });

  const filtered = logs?.filter((l) =>
    !search ||
    l.actor.toLowerCase().includes(search.toLowerCase()) ||
    l.action.toLowerCase().includes(search.toLowerCase()) ||
    l.target.toLowerCase().includes(search.toLowerCase()) ||
    l.correlation_id.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-5">
      <PageHeader
        title="Enterprise Audit &amp; Lineage Explorer"
        description="Immutable audit trail of all AI autonomous operations, human approvals, compensation alterations, and security events."
        actions={
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm">
              <Download className="h-3.5 w-3.5" aria-hidden />
              Export Signed Log
            </Button>
          </div>
        }
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard label="Audit Events (24h)" value={logs?.length || 5} detail="Cryptographically signed" />
        <MetricCard label="High-Risk Actions" value="2" detail="Approved with HITL" />
        <MetricCard label="Policy Enforcement" value="100%" detail="Zero non-compliant events" />
        <MetricCard label="Tamper Verification" value="Valid" change={{ value: 'Hash chain verified', direction: 'up', isPositive: true }} detail="SHA-256 state root" />
      </div>

      <div className="flex items-center gap-2">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-text-muted" aria-hidden />
          <input
            type="search"
            placeholder="Search by actor, action, correlation ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full h-8 pl-8 pr-3 text-sm bg-surface border border-border rounded-md text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent"
          />
        </div>
      </div>

      <Card padding="none">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Timestamp</TableHead>
              <TableHead>Actor / Principal</TableHead>
              <TableHead>Action</TableHead>
              <TableHead>Target Entity</TableHead>
              <TableHead>Risk</TableHead>
              <TableHead>Governing Policy</TableHead>
              <TableHead>Correlation ID</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered?.map((log) => (
              <TableRow key={log.id}>
                <TableCell className="text-xs font-mono text-text-muted whitespace-nowrap">
                  {new Date(log.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                </TableCell>
                <TableCell className="font-semibold text-text-primary text-sm">{log.actor}</TableCell>
                <TableCell>
                  <code className="text-xs bg-surface-secondary px-1.5 py-0.5 rounded border border-border font-mono">
                    {log.action}
                  </code>
                </TableCell>
                <TableCell className="text-sm text-text-secondary">{log.target}</TableCell>
                <TableCell>
                  <RiskBadge level={log.risk} />
                </TableCell>
                <TableCell className="text-xs text-text-muted font-mono">{log.policy}</TableCell>
                <TableCell className="text-xs font-mono text-text-muted">{log.correlation_id}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
