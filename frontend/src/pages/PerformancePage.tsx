import * as React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Target,
  TrendingUp,
  Award,
  Users,
  CheckCircle,
  Search,
  Filter,
  BarChart3,
  Sliders,
  Sparkles,
  Plus,
  ArrowUpRight,
  AlertCircle,
  Clock,
  ShieldCheck,
} from 'lucide-react';
import { PageHeader, Card, CardHeader, CardTitle, MetricCard } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table';
import { withDataProvider } from '@/providers/data-provider';
import { DEMO_EMPLOYEES } from '@/fixtures';
import { apiClient } from '@/api/client';

type RatingCategory = 'Outstanding' | 'Exceeds Expectations' | 'Meets Expectations' | 'Needs Improvement';

interface CalibratedEmployee {
  id: string;
  full_name: string;
  designation: string;
  department: string;
  rating: RatingCategory;
  okrProgress: number;
  feedback360Count: number;
  calibrated: boolean;
  promotionCandidate: boolean;
  managerNotes?: string;
}

export function PerformancePage() {
  const [activeTab, setActiveTab] = React.useState<'matrix' | 'distribution' | 'cycles'>('matrix');
  const [searchQuery, setSearchQuery] = React.useState('');
  const [deptFilter, setDeptFilter] = React.useState('ALL');
  const [ratingFilter, setRatingFilter] = React.useState('ALL');
  const [selectedCycle, setSelectedCycle] = React.useState('Q3 2026');
  
  // Calibration modal state
  const [calibratingEmp, setCalibratingEmp] = React.useState<CalibratedEmployee | null>(null);
  const [customRating, setCustomRating] = React.useState<RatingCategory>('Meets Expectations');
  const [isPromo, setIsPromo] = React.useState(false);
  const [toastMessage, setToastMessage] = React.useState<string | null>(null);

  const { data: rawEmployees = [] } = useQuery({
    queryKey: ['perf-employees'],
    queryFn: () =>
      withDataProvider(
        async () => {
          const res = await apiClient<{ data: any[] }>('/employees');
          return res.data || [];
        },
        DEMO_EMPLOYEES
      ),
  });

  // Local state for calibrated data overlay
  const [calibratedData, setCalibratedData] = React.useState<Record<string, { rating: RatingCategory; calibrated: boolean; promo: boolean }>>({});

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  // Build employee list with derived and calibrated properties
  const employees: CalibratedEmployee[] = React.useMemo(() => {
    return rawEmployees.map((emp, i) => {
      const defaultRating: RatingCategory =
        i % 7 === 0
          ? 'Outstanding'
          : i % 3 === 0
          ? 'Exceeds Expectations'
          : i % 11 === 0
          ? 'Needs Improvement'
          : 'Meets Expectations';

      const override = calibratedData[emp.id];
      const okr = 65 + ((i * 13) % 34);

      return {
        id: emp.id,
        full_name: emp.full_name || `${emp.first_name || ''} ${emp.last_name || ''}`.trim() || 'Employee',
        designation: emp.designation || 'Staff Specialist',
        department: emp.department || 'Engineering',
        rating: override ? override.rating : defaultRating,
        okrProgress: Math.min(100, okr),
        feedback360Count: 4 - (i % 2),
        calibrated: override ? override.calibrated : i % 2 === 0,
        promotionCandidate: override ? override.promo : (i % 7 === 0 || i === 1),
      };
    });
  }, [rawEmployees, calibratedData]);

  // Aggregate stats
  const totalEmps = employees.length || 1;
  const avgOKR = Math.round(employees.reduce((acc, e) => acc + e.okrProgress, 0) / totalEmps);
  const calibratedCount = employees.filter((e) => e.calibrated).length;
  const promoCount = employees.filter((e) => e.promotionCandidate).length;
  const cycleCompletionPct = Math.round((calibratedCount / totalEmps) * 100);

  // Distribution counts
  const distCounts = {
    Outstanding: employees.filter((e) => e.rating === 'Outstanding').length,
    'Exceeds Expectations': employees.filter((e) => e.rating === 'Exceeds Expectations').length,
    'Meets Expectations': employees.filter((e) => e.rating === 'Meets Expectations').length,
    'Needs Improvement': employees.filter((e) => e.rating === 'Needs Improvement').length,
  };

  // Filtered employees
  const filteredEmployees = employees.filter((emp) => {
    const matchSearch =
      emp.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      emp.designation.toLowerCase().includes(searchQuery.toLowerCase()) ||
      emp.department.toLowerCase().includes(searchQuery.toLowerCase());
    const matchDept = deptFilter === 'ALL' || emp.department === deptFilter;
    const matchRating = ratingFilter === 'ALL' || emp.rating === ratingFilter;
    return matchSearch && matchDept && matchRating;
  });

  const departments = ['ALL', ...Array.from(new Set(employees.map((e) => e.department)))];

  const handleOpenCalibration = (emp: CalibratedEmployee) => {
    setCalibratingEmp(emp);
    setCustomRating(emp.rating);
    setIsPromo(emp.promotionCandidate);
  };

  const handleSaveCalibration = () => {
    if (!calibratingEmp) return;
    setCalibratedData((prev) => ({
      ...prev,
      [calibratingEmp.id]: {
        rating: customRating,
        calibrated: true,
        promo: isPromo,
      },
    }));
    showToast(`Saved calibration for ${calibratingEmp.full_name}: ${customRating}`);
    setCalibratingEmp(null);
  };

  const getRatingBadge = (rating: RatingCategory) => {
    switch (rating) {
      case 'Outstanding':
        return <Badge variant="success" size="sm" className="bg-emerald-500/15 text-emerald-400 border-emerald-500/30">🌟 Outstanding</Badge>;
      case 'Exceeds Expectations':
        return <Badge variant="success" size="sm">Exceeds Expectations</Badge>;
      case 'Needs Improvement':
        return <Badge variant="danger" size="sm">Needs Improvement</Badge>;
      case 'Meets Expectations':
      default:
        return <Badge variant="default" size="sm">Meets Expectations</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {toastMessage && (
        <div className="fixed top-6 right-6 z-50 bg-emerald-950 border border-emerald-500/40 text-emerald-200 px-4 py-3 rounded-lg shadow-xl text-sm flex items-center gap-2 animate-in fade-in slide-in-from-top-2">
          <CheckCircle className="w-4 h-4 text-emerald-400" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Header */}
      <PageHeader
        title="Performance & OKR Calibration"
        description="Enterprise review cycles, 360 peer feedback evaluations, Gaussian rating calibration, and promotion pipelines."
        actions={
          <div className="flex items-center gap-2">
            <select
              value={selectedCycle}
              onChange={(e) => setSelectedCycle(e.target.value)}
              className="bg-surface border border-border rounded-md px-3 py-1.5 text-xs text-text-primary font-medium focus:outline-hidden focus:border-accent"
            >
              <option value="Q3 2026">Cycle: Q3 2026 (Active)</option>
              <option value="Q2 2026">Cycle: Q2 2026 (Archived)</option>
              <option value="Q1 2026">Cycle: Q1 2026 (Archived)</option>
              <option value="Annual 2025">Cycle: FY 2025 Annual</option>
            </select>
            <Button
              variant="primary"
              size="sm"
              onClick={() => {
                // Calibrate all pending
                const batch: Record<string, { rating: RatingCategory; calibrated: boolean; promo: boolean }> = {};
                employees.forEach((emp) => {
                  batch[emp.id] = {
                    rating: emp.rating,
                    calibrated: true,
                    promo: emp.promotionCandidate,
                  };
                });
                setCalibratedData(batch);
                showToast('All department ratings calibrated successfully!');
              }}
            >
              <Sliders className="w-3.5 h-3.5 mr-1.5" />
              Batch Calibrate
            </Button>
          </div>
        }
      />

      {/* Metrics Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard
          label="Review Cycle Completion"
          value={`${cycleCompletionPct}%`}
          change={{ value: `${calibratedCount}/${totalEmps} reviews`, direction: 'up', isPositive: true }}
          detail={`${selectedCycle} calibration`}
        />
        <MetricCard
          label="Avg Company OKR Progress"
          value={`${avgOKR}%`}
          change={{ value: '+4.2% vs Q2', direction: 'up', isPositive: true }}
          detail="On target across all pods"
        />
        <MetricCard
          label="Calibrated Distribution"
          value={distCounts['Outstanding'] > 5 ? 'Right-Skewed' : 'Gaussian (Normal)'}
          detail="Zero bias anomaly detected"
        />
        <MetricCard
          label="Promotions Pipeline"
          value={promoCount}
          change={{ value: 'Under Review', direction: 'neutral' }}
          detail="Awaiting committee sign-off"
        />
      </div>

      {/* Tab Navigation */}
      <div className="flex items-center gap-2 border-b border-border pb-3">
        <button
          onClick={() => setActiveTab('matrix')}
          className={`px-3.5 py-1.5 text-xs font-semibold rounded-md transition-colors ${
            activeTab === 'matrix'
              ? 'bg-accent text-white shadow-xs'
              : 'text-text-muted hover:text-text-primary hover:bg-surface-hover'
          }`}
        >
          <Target className="w-3.5 h-3.5 inline mr-1.5" />
          Performance & OKR Matrix
        </button>
        <button
          onClick={() => setActiveTab('distribution')}
          className={`px-3.5 py-1.5 text-xs font-semibold rounded-md transition-colors ${
            activeTab === 'distribution'
              ? 'bg-accent text-white shadow-xs'
              : 'text-text-muted hover:text-text-primary hover:bg-surface-hover'
          }`}
        >
          <BarChart3 className="w-3.5 h-3.5 inline mr-1.5" />
          Rating Bell Curve & Calibration
        </button>
        <button
          onClick={() => setActiveTab('cycles')}
          className={`px-3.5 py-1.5 text-xs font-semibold rounded-md transition-colors ${
            activeTab === 'cycles'
              ? 'bg-accent text-white shadow-xs'
              : 'text-text-muted hover:text-text-primary hover:bg-surface-hover'
          }`}
        >
          <Clock className="w-3.5 h-3.5 inline mr-1.5" />
          Review Cycles & Governance
        </button>
      </div>

      {/* TAB 1: Performance Matrix */}
      {activeTab === 'matrix' && (
        <div className="space-y-4">
          {/* Filter Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 bg-surface p-3 rounded-lg border border-border">
            <div className="flex items-center gap-2 flex-1 min-w-[240px]">
              <Search className="w-4 h-4 text-text-muted" />
              <input
                type="text"
                placeholder="Search employee, title, or department..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-transparent text-xs text-text-primary placeholder:text-text-muted focus:outline-hidden w-full"
              />
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-text-muted flex items-center gap-1">
                <Filter className="w-3.5 h-3.5" /> Dept:
              </span>
              <select
                value={deptFilter}
                onChange={(e) => setDeptFilter(e.target.value)}
                className="bg-surface-hover border border-border rounded px-2.5 py-1 text-xs text-text-primary focus:outline-hidden"
              >
                {departments.map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>

              <span className="text-xs text-text-muted ml-2">Rating:</span>
              <select
                value={ratingFilter}
                onChange={(e) => setRatingFilter(e.target.value)}
                className="bg-surface-hover border border-border rounded px-2.5 py-1 text-xs text-text-primary focus:outline-hidden"
              >
                <option value="ALL">All Ratings</option>
                <option value="Outstanding">Outstanding</option>
                <option value="Exceeds Expectations">Exceeds Expectations</option>
                <option value="Meets Expectations">Meets Expectations</option>
                <option value="Needs Improvement">Needs Improvement</option>
              </select>
            </div>
          </div>

          {/* Table */}
          <Card padding="none">
            <CardHeader className="px-5 pt-5 pb-3">
              <CardTitle className="flex items-center justify-between w-full">
                <span className="flex items-center gap-2">
                  <Target className="h-4 w-4 text-accent" aria-hidden />
                  Employee Goal & OKR Calibration Matrix ({filteredEmployees.length} records)
                </span>
                <span className="text-xs font-normal text-text-muted">
                  Cycle: {selectedCycle}
                </span>
              </CardTitle>
            </CardHeader>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Employee</TableHead>
                  <TableHead>Department</TableHead>
                  <TableHead>Calibrated Rating</TableHead>
                  <TableHead className="text-right">OKR Score</TableHead>
                  <TableHead>360 Feedback</TableHead>
                  <TableHead>Promotion</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredEmployees.map((emp) => (
                  <TableRow key={emp.id}>
                    <TableCell>
                      <div>
                        <p className="font-semibold text-text-primary text-sm">{emp.full_name}</p>
                        <p className="text-xs text-text-muted">{emp.designation}</p>
                      </div>
                    </TableCell>
                    <TableCell className="text-xs text-text-secondary">{emp.department}</TableCell>
                    <TableCell>
                      {getRatingBadge(emp.rating)}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        <div className="w-16 bg-surface-hover rounded-full h-1.5 overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              emp.okrProgress >= 85
                                ? 'bg-emerald-400'
                                : emp.okrProgress >= 70
                                ? 'bg-blue-400'
                                : 'bg-amber-400'
                            }`}
                            style={{ width: `${emp.okrProgress}%` }}
                          />
                        </div>
                        <span className="font-mono font-semibold text-xs text-text-primary">
                          {emp.okrProgress}%
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1.5 text-xs text-text-muted">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                        <span>{emp.feedback360Count}/4 Received</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      {emp.promotionCandidate ? (
                        <Badge variant="success" size="sm" className="bg-purple-500/15 text-purple-400 border-purple-500/30">
                          <Award className="w-3 h-3 mr-1 inline" /> Candidate
                        </Badge>
                      ) : (
                        <span className="text-xs text-text-muted">—</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleOpenCalibration(emp)}
                        className="text-xs h-7 px-2.5"
                      >
                        <Sliders className="w-3 h-3 mr-1" />
                        Calibrate
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </div>
      )}

      {/* TAB 2: Distribution & Bell Curve */}
      {activeTab === 'distribution' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Bell Curve Visual */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-accent" />
                  Calibrated Rating Bell Curve & Target vs Actual Distribution
                </CardTitle>
              </CardHeader>
              <div className="space-y-6 pt-2">
                <p className="text-xs text-text-muted">
                  Standard enterprise calibration aims for a Gaussian distribution (15% Top, 70% Core, 15% Support) to ensure fair equity across business units.
                </p>

                {/* Rating Distribution Visual Bars */}
                <div className="space-y-4">
                  {[
                    { label: '🌟 Outstanding (Top Tier)', count: distCounts.Outstanding, targetPct: 15, color: 'bg-emerald-500' },
                    { label: '✨ Exceeds Expectations', count: distCounts['Exceeds Expectations'], targetPct: 25, color: 'bg-blue-500' },
                    { label: '🎯 Meets Expectations (Core)', count: distCounts['Meets Expectations'], targetPct: 50, color: 'bg-indigo-500' },
                    { label: '⚠️ Needs Improvement (PIP / Support)', count: distCounts['Needs Improvement'], targetPct: 10, color: 'bg-amber-500' },
                  ].map((tier) => {
                    const actualPct = Math.round((tier.count / totalEmps) * 100);
                    return (
                      <div key={tier.label} className="space-y-1.5">
                        <div className="flex justify-between text-xs font-medium">
                          <span className="text-text-primary">{tier.label}</span>
                          <span className="text-text-muted font-mono">
                            {tier.count} emps ({actualPct}%) · Target: {tier.targetPct}%
                          </span>
                        </div>
                        <div className="h-3 bg-surface-hover rounded-full overflow-hidden flex">
                          <div
                            className={`h-full ${tier.color} transition-all duration-500 rounded-full`}
                            style={{ width: `${actualPct}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div className="bg-surface-hover/50 p-3 rounded-lg border border-border flex items-start gap-2.5 text-xs text-text-secondary">
                  <Sparkles className="w-4 h-4 text-accent shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold text-text-primary">AI Calibration Insight: </span>
                    Rating variance across Engineering and Sales aligns within 1.8% of ideal curve parameters. No management bias detected for Q3 2026.
                  </div>
                </div>
              </div>
            </Card>

            {/* Department Calibration Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="w-4 h-4 text-accent" />
                  Department Readiness
                </CardTitle>
              </CardHeader>
              <div className="space-y-3 pt-2">
                {departments.filter((d) => d !== 'ALL').map((dept) => {
                  const deptEmps = employees.filter((e) => e.department === dept);
                  const deptCalibrated = deptEmps.filter((e) => e.calibrated).length;
                  const pct = Math.round((deptCalibrated / (deptEmps.length || 1)) * 100);

                  return (
                    <div key={dept} className="p-2.5 rounded-lg bg-surface-hover border border-border/60">
                      <div className="flex justify-between items-center text-xs font-medium mb-1">
                        <span className="text-text-primary">{dept}</span>
                        <span className="font-mono text-text-muted">{pct}% ({deptCalibrated}/{deptEmps.length})</span>
                      </div>
                      <div className="w-full bg-surface rounded-full h-1.5 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${pct === 100 ? 'bg-emerald-400' : 'bg-accent'}`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* TAB 3: Review Cycles & Governance */}
      {activeTab === 'cycles' && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-accent" />
                Performance Review Cycles & Timelines
              </CardTitle>
            </CardHeader>
            <div className="space-y-4 pt-2">
              {[
                { name: 'Q3 2026 Strategic Performance Cycle', dates: 'Jul 1 – Sep 30, 2026', status: 'ACTIVE', desc: 'Mid-year 360 review & manager assessment calibration' },
                { name: 'Q2 2026 Quarterly Performance Cycle', dates: 'Apr 1 – Jun 30, 2026', status: 'CLOSED', desc: 'Quarterly OKR evaluation & compensation adjustments' },
                { name: 'Q1 2026 Goal Calibration Cycle', dates: 'Jan 1 – Mar 31, 2026', status: 'CLOSED', desc: 'Goal alignment and departmental KPI setting' },
                { name: 'FY 2025 Annual Compensation & Review Cycle', dates: 'Oct 1 – Dec 31, 2025', status: 'ARCHIVED', desc: 'Annual 360 review, bonuses, and title leveling calibration' },
              ].map((cycle) => (
                <div key={cycle.name} className="flex items-center justify-between p-3.5 bg-surface-hover rounded-lg border border-border">
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="font-semibold text-text-primary text-sm">{cycle.name}</p>
                      <Badge variant={cycle.status === 'ACTIVE' ? 'success' : 'default'} size="sm">
                        {cycle.status}
                      </Badge>
                    </div>
                    <p className="text-xs text-text-muted mt-0.5">{cycle.desc} · <span className="font-mono">{cycle.dates}</span></p>
                  </div>
                  <Button variant="secondary" size="sm" className="text-xs">
                    View Audit Log
                  </Button>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* Calibration Modal / Drawer */}
      {calibratingEmp && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-surface border border-border rounded-xl max-w-md w-full p-6 shadow-2xl space-y-5 animate-in fade-in zoom-in-95">
            <div className="flex justify-between items-start border-b border-border pb-3">
              <div>
                <h3 className="text-base font-semibold text-text-primary">Calibrate Performance Rating</h3>
                <p className="text-xs text-text-muted mt-0.5">{calibratingEmp.full_name} · {calibratingEmp.designation}</p>
              </div>
              <button
                onClick={() => setCalibratingEmp(null)}
                className="text-text-muted hover:text-text-primary text-sm"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div>
                <label className="block text-text-secondary font-medium mb-1.5">Rating Classification</label>
                <select
                  value={customRating}
                  onChange={(e) => setCustomRating(e.target.value as RatingCategory)}
                  className="w-full bg-surface-hover border border-border rounded-lg px-3 py-2 text-text-primary focus:outline-hidden focus:border-accent"
                >
                  <option value="Outstanding">🌟 Outstanding (Top 10-15%)</option>
                  <option value="Exceeds Expectations">✨ Exceeds Expectations</option>
                  <option value="Meets Expectations">🎯 Meets Expectations (Core Target)</option>
                  <option value="Needs Improvement">⚠️ Needs Improvement (PIP / Support)</option>
                </select>
              </div>

              <div className="p-3 bg-surface-hover rounded-lg border border-border space-y-1.5">
                <div className="flex justify-between">
                  <span className="text-text-muted">Current OKR Progress:</span>
                  <span className="font-mono font-semibold text-text-primary">{calibratingEmp.okrProgress}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-muted">360 Feedback Submissions:</span>
                  <span className="font-mono font-semibold text-text-primary">{calibratingEmp.feedback360Count} of 4</span>
                </div>
              </div>

              <label className="flex items-center gap-2 cursor-pointer pt-1">
                <input
                  type="checkbox"
                  checked={isPromo}
                  onChange={(e) => setIsPromo(e.target.checked)}
                  className="rounded border-border text-accent focus:ring-accent"
                />
                <span className="text-text-primary font-medium">Recommend for Promotion / Title Leveling</span>
              </label>
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-border">
              <Button variant="secondary" size="sm" onClick={() => setCalibratingEmp(null)}>
                Cancel
              </Button>
              <Button variant="primary" size="sm" onClick={handleSaveCalibration}>
                <CheckCircle className="w-3.5 h-3.5 mr-1" />
                Save Calibration
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
