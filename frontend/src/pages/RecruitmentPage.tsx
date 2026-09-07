import * as React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Filter, Plus, ChevronDown, MoreHorizontal } from 'lucide-react';
import { PageHeader, Card, CardHeader, CardTitle, MetricCard } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge, RiskBadge, StatusBadge } from '@/components/ui/badge';
import {
  Table, TableHeader, TableBody, TableRow, TableHead, TableCell,
} from '@/components/ui/table';
import { SkeletonTable, EmptyState } from '@/components/ui/skeleton';
import { withDataProvider } from '@/providers/data-provider';

const DEMO_CANDIDATES = [
  {
    id: 'cand-001',
    name: 'Alice Lin',
    role: 'Principal AI Architect',
    department: 'AI Research Lab',
    stage: 'Offer',
    source: 'LinkedIn',
    score: 94,
    applied: '2026-08-15',
    lastActivity: '2026-08-29',
    aiScreening: { summary: 'Exceptional match. 14/14 required competencies. Strong publication record.', confidence: 96, flag: null },
  },
  {
    id: 'cand-002',
    name: 'David Park',
    role: 'Staff Software Engineer',
    department: 'Engineering Platform',
    stage: 'Interview',
    source: 'Referral',
    score: 88,
    applied: '2026-08-18',
    lastActivity: '2026-08-28',
    aiScreening: { summary: 'Strong candidate. System design round scheduled. Minor gap in distributed storage experience.', confidence: 88, flag: null },
  },
  {
    id: 'cand-003',
    name: 'Nina Osei',
    role: 'Senior Compliance Counsel',
    department: 'Legal & Compliance',
    stage: 'Screening',
    source: 'Agency',
    score: 72,
    applied: '2026-08-22',
    lastActivity: '2026-08-27',
    aiScreening: { summary: 'Good legal background. Missing fintech regulatory experience specified in JD.', confidence: 72, flag: 'Gap in required domain' },
  },
  {
    id: 'cand-004',
    name: 'James Wu',
    role: 'Financial Analyst II',
    department: 'Finance Operations',
    stage: 'Applied',
    source: 'Job Board',
    score: 65,
    applied: '2026-08-25',
    lastActivity: '2026-08-25',
    aiScreening: { summary: 'Meets baseline requirements. Resume screening passed.', confidence: 65, flag: null },
  },
  {
    id: 'cand-005',
    name: 'Fatima Al-Rashid',
    role: 'Product Designer',
    department: 'Product Design',
    stage: 'Shortlisted',
    source: 'Direct Application',
    score: 91,
    applied: '2026-08-20',
    lastActivity: '2026-08-29',
    aiScreening: { summary: 'Excellent portfolio. Strong B2B SaaS experience. Design system expertise confirmed.', confidence: 91, flag: null },
  },
];

const PIPELINE_STAGES = ['Applied', 'Screening', 'Shortlisted', 'Interview', 'Offer', 'Hired', 'Rejected'];

const stageCounts = PIPELINE_STAGES.reduce((acc, stage) => {
  acc[stage] = DEMO_CANDIDATES.filter((c) => c.stage === stage).length;
  return acc;
}, {} as Record<string, number>);

const stageColor: Record<string, string> = {
  Applied: 'bg-surface-secondary',
  Screening: 'bg-info-soft',
  Shortlisted: 'bg-accent-soft',
  Interview: 'bg-warning-soft',
  Offer: 'bg-ai-soft',
  Hired: 'bg-success-soft',
  Rejected: 'bg-danger-soft',
};

const stageBadge: Record<string, 'default' | 'info' | 'primary' | 'warning' | 'ai' | 'success' | 'danger'> = {
  Applied: 'default',
  Screening: 'info',
  Shortlisted: 'primary',
  Interview: 'warning',
  Offer: 'ai',
  Hired: 'success',
  Rejected: 'danger',
};

export function RecruitmentPage() {
  const { data: candidates, isLoading } = useQuery({
    queryKey: ['candidates'],
    queryFn: () => withDataProvider(
      async () => { throw new Error('API not connected'); },
      DEMO_CANDIDATES
    ),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        title="Recruitment"
        description="Talent pipeline, candidate tracking, and AI-assisted screening."
        actions={
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm">Export</Button>
            <Button variant="primary" size="sm">
              <Plus className="h-4 w-4" aria-hidden />
              Post Job
            </Button>
          </div>
        }
      />

      {/* Pipeline Summary */}
      <div className="grid grid-cols-4 lg:grid-cols-7 gap-2">
        {PIPELINE_STAGES.map((stage) => (
          <div key={stage} className={`${stageColor[stage]} border border-border rounded-lg px-3 py-2.5 text-center`}>
            <p className="text-xl font-bold text-text-primary">{stageCounts[stage] ?? 0}</p>
            <p className="text-xs text-text-muted mt-0.5 truncate">{stage}</p>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2 flex-wrap">
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-text-muted" aria-hidden />
          <input
            type="search"
            placeholder="Search candidates..."
            className="h-8 pl-8 pr-3 text-sm bg-surface border border-border rounded-md w-56 placeholder:text-text-muted text-text-primary focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent"
            aria-label="Search candidates"
          />
        </div>
        <select
          className="h-8 px-2.5 text-sm bg-surface border border-border rounded-md text-text-secondary focus:outline-none focus:ring-2 focus:ring-accent"
          aria-label="Filter by stage"
        >
          <option value="">All Stages</option>
          {PIPELINE_STAGES.map((s) => <option key={s}>{s}</option>)}
        </select>
        <Button variant="secondary" size="sm">
          <Filter className="h-3.5 w-3.5" aria-hidden />
          Filters
        </Button>
      </div>

      {/* Candidate Table */}
      <div className="border border-border rounded-lg overflow-hidden bg-surface">
        {isLoading ? (
          <SkeletonTable rows={5} cols={6} />
        ) : !candidates?.length ? (
          <EmptyState title="No candidates" description="Post a job to start receiving applications." />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Candidate</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Stage</TableHead>
                <TableHead className="text-right">AI Score</TableHead>
                <TableHead>Source</TableHead>
                <TableHead>AI Screening</TableHead>
                <TableHead className="w-10"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {candidates?.map((c) => (
                <TableRow key={c.id}>
                  <TableCell>
                    <div>
                      <p className="font-medium text-text-primary">{c.name}</p>
                      <p className="text-xs text-text-muted">{c.department}</p>
                    </div>
                  </TableCell>
                  <TableCell className="text-text-secondary text-sm">{c.role}</TableCell>
                  <TableCell>
                    <Badge variant={stageBadge[c.stage]} size="sm">{c.stage}</Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <span className={
                      c.score >= 90 ? 'text-success font-semibold' :
                      c.score >= 75 ? 'text-text-primary font-medium' :
                      'text-warning'
                    }>
                      {c.score}
                    </span>
                  </TableCell>
                  <TableCell>
                    <span className="text-xs text-text-muted">{c.source}</span>
                  </TableCell>
                  <TableCell>
                    <div className="max-w-xs">
                      <p className="text-xs text-text-secondary line-clamp-1">{c.aiScreening.summary}</p>
                      {c.aiScreening.flag && (
                        <p className="text-2xs text-warning mt-0.5">⚠ {c.aiScreening.flag}</p>
                      )}
                      <p className="text-2xs text-text-muted mt-0.5">
                        AI screening · {c.aiScreening.confidence}% confidence
                      </p>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Button variant="ghost" size="icon-xs" aria-label="More actions">
                      <MoreHorizontal className="h-3.5 w-3.5" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
}
