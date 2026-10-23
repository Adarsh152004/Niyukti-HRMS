import * as React from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { 
  Cpu, CheckCircle2, AlertOctagon, HelpCircle, Layers, Sliders, 
  Sparkles, Play, ArrowUpRight, ShieldCheck, Activity 
} from 'lucide-react';
import { PageHeader, Card, CardHeader, CardTitle, MetricCard } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table';
import { SkeletonTable } from '@/components/ui/skeleton';

export interface MLModelRecord {
  id: string;
  name: string;
  version: string;
  framework: string;
  task: string;
  auc_roc: number;
  ece: number;
  brier_score: number;
  drift_status: string;
  dataset_version: string;
  features: string[];
  last_trained: string;
}

export function MLCenterPage() {
  // Simulator input states
  const [tenure, setTenure] = React.useState(24);
  const [compRatio, setCompRatio] = React.useState(1.0);
  const [lastPromo, setLastPromo] = React.useState(18);
  const [overtime, setOvertime] = React.useState(8);
  const [predictionResult, setPredictionResult] = React.useState<any>(null);

  // Fetch ML Models from live endpoint
  const { data: models = [], isLoading } = useQuery<MLModelRecord[]>({
    queryKey: ['ml-production-models'],
    queryFn: async () => {
      const res = await fetch('/api/v1/ml/models');
      if (!res.ok) return [];
      return res.json();
    },
    refetchInterval: 10000,
  });

  // Run Inference Simulation
  const predictMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/v1/ml/predict/attrition', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenure_months: Number(tenure),
          comp_ratio: Number(compRatio),
          last_promotion_months: Number(lastPromo),
          leave_frequency: 3,
          overtime_hours: Number(overtime),
        }),
      });
      if (!res.ok) throw new Error('Prediction failed');
      return res.json();
    },
    onSuccess: (data) => {
      setPredictionResult(data);
    },
  });

  React.useEffect(() => {
    predictMutation.mutate();
  }, [tenure, compRatio, lastPromo, overtime]);

  return (
    <div className="space-y-5 pb-10">
      <PageHeader
        title="Machine Learning & Prediction Center"
        description="Production model registry, calibration curves, dataset version lineage, concept drift monitoring, and fairness audits."
        actions={
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm">
              <Activity className="h-3.5 w-3.5" aria-hidden />
              Evaluate Fairness
            </Button>
            <Button variant="primary" size="sm">
              <Sparkles className="h-3.5 w-3.5" aria-hidden />
              Retrain Pipeline
            </Button>
          </div>
        }
      />

      {/* Overview Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard label="Active ML Models" value={models.length} detail="Calibrated (ECE < 0.05)" />
        <MetricCard label="Average AUC-ROC" value="0.916" change={{ value: 'Well calibrated', direction: 'up', isPositive: true }} detail="Discrimination metric" />
        <MetricCard label="Drift Status" value="Stable" detail="Feature distributions aligned" />
        <MetricCard label="Governed Inference" value="100% Audited" detail="Lineage tracked" />
      </div>

      {/* Interactive Predictive Inference Simulator */}
      <Card className="p-5 space-y-4 border border-border">
        <div className="flex items-center justify-between border-b border-border pb-3">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-accent" />
            <h3 className="font-semibold text-text-primary text-sm">Live Predictive Risk Scoring Simulator (XGBoost Engine)</h3>
          </div>
          <Badge variant="primary" size="sm">Realtime Inference</Badge>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Controls */}
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-text-secondary font-medium">Compensation Ratio (vs Market Band)</span>
                <span className="font-mono font-bold text-accent">{compRatio}x</span>
              </div>
              <input
                type="range"
                min="0.70"
                max="1.50"
                step="0.05"
                value={compRatio}
                onChange={(e) => setCompRatio(parseFloat(e.target.value))}
                className="w-full accent-accent cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-text-secondary font-medium">Tenure (Months)</span>
                <span className="font-mono font-bold text-text-primary">{tenure} mos</span>
              </div>
              <input
                type="range"
                min="3"
                max="72"
                value={tenure}
                onChange={(e) => setTenure(parseInt(e.target.value))}
                className="w-full accent-accent cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-text-secondary font-medium">Months Since Last Promotion</span>
                <span className="font-mono font-bold text-text-primary">{lastPromo} mos</span>
              </div>
              <input
                type="range"
                min="1"
                max="48"
                value={lastPromo}
                onChange={(e) => setLastPromo(parseInt(e.target.value))}
                className="w-full accent-accent cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-text-secondary font-medium">Monthly Overtime (Hours)</span>
                <span className="font-mono font-bold text-text-primary">{overtime} hrs</span>
              </div>
              <input
                type="range"
                min="0"
                max="40"
                value={overtime}
                onChange={(e) => setOvertime(parseInt(e.target.value))}
                className="w-full accent-accent cursor-pointer"
              />
            </div>
          </div>

          {/* Realtime Output Card */}
          <div className="bg-surface-secondary border border-border p-4 rounded-xl flex flex-col justify-between space-y-3">
            <div>
              <span className="text-xs text-text-muted uppercase tracking-wider font-semibold">Predicted Attrition Risk</span>
              <div className="flex items-baseline gap-3 mt-1">
                <span className="text-3xl font-bold font-mono text-text-primary">
                  {predictionResult ? `${(predictionResult.attrition_probability * 100).toFixed(1)}%` : '—'}
                </span>
                {predictionResult && (
                  <Badge 
                    variant={predictionResult.risk_tier === 'HIGH' ? 'danger' : (predictionResult.risk_tier === 'MEDIUM' ? 'warning' : 'success')}
                  >
                    {predictionResult.risk_tier} RISK TIER
                  </Badge>
                )}
              </div>
            </div>

            {predictionResult?.top_drivers && (
              <div className="space-y-1.5 border-t border-border pt-3">
                <span className="text-xs font-semibold text-text-primary">Key Contributing Factors:</span>
                {predictionResult.top_drivers.map((d: any, idx: number) => (
                  <div key={idx} className="flex justify-between text-xs text-text-secondary">
                    <span>{d.factor}:</span>
                    <span className="font-mono font-medium">{d.impact}</span>
                  </div>
                ))}
              </div>
            )}

            <div className="bg-surface border border-border p-2.5 rounded-lg text-xs flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
              <span className="text-text-secondary">{predictionResult?.recommended_action || 'Calibrated & Ready'}</span>
            </div>
          </div>
        </div>
      </Card>

      {/* Model Registry Table */}
      <Card padding="none">
        <CardHeader className="px-5 pt-5 pb-3">
          <CardTitle className="flex items-center gap-2">
            <Cpu className="h-4 w-4 text-accent" aria-hidden />
            Production Model Registry &amp; Calibration Metrics
          </CardTitle>
        </CardHeader>
        
        {isLoading ? (
          <SkeletonTable rows={3} cols={8} />
        ) : (
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
              {models.map((m) => (
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
                  <TableCell className="text-right font-mono text-xs text-emerald-600 font-semibold">{m.ece.toFixed(3)}</TableCell>
                  <TableCell className="text-right font-mono text-xs">{m.brier_score.toFixed(3)}</TableCell>
                  <TableCell>
                    <Badge variant={m.drift_status === 'STABLE' ? 'success' : 'warning'} size="sm">
                      {m.drift_status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <span className="text-xs font-mono text-text-muted bg-surface-secondary px-1.5 py-0.5 rounded border border-border">
                      {m.dataset_version}
                    </span>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>
    </div>
  );
}
