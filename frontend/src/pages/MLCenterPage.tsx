import * as React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Cpu, CheckCircle2, AlertOctagon, HelpCircle, Layers, Sliders } from 'lucide-react';
import { PageHeader, Card, CardHeader, CardTitle, MetricCard } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table';
import { withDataProvider } from '@/providers/data-provider';
import { DEMO_ML_REGISTRY } from '@/fixtures';

export function MLCenterPage() {
  const { data: models } = useQuery({
    queryKey: ['ml-models'],
    queryFn: () => withDataProvider(async () => { throw new Error(); }, DEMO_ML_REGISTRY),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        title="Machine Learning & Prediction Center"
        description="Production model registry, calibration curves, dataset version lineage, concept drift monitoring, and fairness audits."
        actions={
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm">Evaluate Fairness</Button>
            <Button variant="primary" size="sm">Register Model</Button>
          </div>
        }
      />

      {/* Overview Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard label="Active ML Models" value={models?.length || 3} detail="All calibrated (ECE < 0.05)" />
        <MetricCard label="Average AUC-ROC" value="0.916" change={{ value: 'Well calibrated', direction: 'up', isPositive: true }} detail="Discrimination metric" />
        <MetricCard label="Governed Abstentions" value="104" detail="Valid uncertainty outcomes" />
        <MetricCard label="Drift Status" value="Stable" detail="Feature distributions aligned" />
      </div>

      {/* Model Registry Table */}
      <Card padding="none">
        <CardHeader className="px-5 pt-5 pb-3">
          <CardTitle className="flex items-center gap-2">
            <Cpu className="h-4 w-4 text-accent" aria-hidden />
            Production Model Registry &amp; Calibration Metrics
          </CardTitle>
        </CardHeader>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Model Name</TableHead>
              <TableHead>Version</TableHead>
              <TableHead>Architecture</TableHead>
              <TableHead className="text-right">AUC-ROC</TableHead>
              <TableHead className="text-right">ECE (Calib Error)</TableHead>
              <TableHead className="text-right">Brier Score</TableHead>
              <TableHead>Drift Status</TableHead>
              <TableHead>Dataset Lineage</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {models?.map((m) => (
              <TableRow key={m.id}>
                <TableCell>
                  <div>
                    <p className="font-semibold text-text-primary text-sm">{m.name}</p>
                    <p className="text-xs text-text-muted font-mono">{m.id}</p>
                  </div>
                </TableCell>
                <TableCell>
                  <code className="text-xs bg-surface-secondary px-1.5 py-0.5 rounded border border-border font-mono">
                    v{m.version}
                  </code>
                </TableCell>
                <TableCell className="text-xs text-text-secondary">{m.framework}</TableCell>
                <TableCell className="text-right font-medium text-text-primary">{m.auc_roc.toFixed(3)}</TableCell>
                <TableCell className="text-right font-mono text-xs text-success">{m.ece.toFixed(3)}</TableCell>
                <TableCell className="text-right font-mono text-xs">{m.brier_score.toFixed(3)}</TableCell>
                <TableCell>
                  <Badge variant={m.drift_status === 'STABLE' ? 'success' : 'warning'} size="sm">
                    {m.drift_status}
                  </Badge>
                </TableCell>
                <TableCell>
                  <span className="text-xs font-mono text-text-muted bg-surface-secondary px-1.5 py-0.5 rounded">
                    {m.dataset_version}
                  </span>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      {/* Governed Prediction Outcome Distribution */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Layers className="h-4 w-4 text-text-muted" aria-hidden />
            Governed Decision Distribution (24h)
          </CardTitle>
        </CardHeader>
        <div className="space-y-4">
          <p className="text-xs text-text-muted">
            In our enterprise architecture, <strong className="text-text-primary">ABSTAIN</strong> and <strong className="text-text-primary">INSUFFICIENT_DATA</strong> are treated as first-class governed decisions to safeguard human decision-making when predictive confidence falls below calibrated thresholds.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {models?.map((m) => (
              <div key={m.id} className="border border-border rounded-lg p-3 bg-surface-secondary">
                <p className="text-xs font-semibold text-text-primary mb-2 truncate">{m.name}</p>
                <div className="space-y-1.5 text-xs">
                  <div className="flex justify-between">
                    <span className="text-text-secondary">PREDICT (Confident)</span>
                    <span className="font-semibold text-success">{m.outcomes.predict}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-secondary">ABSTAIN (Uncertain)</span>
                    <span className="font-semibold text-warning">{m.outcomes.abstain}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-secondary">INSUFFICIENT DATA</span>
                    <span className="font-semibold text-text-muted">{m.outcomes.insufficient_data}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
}
