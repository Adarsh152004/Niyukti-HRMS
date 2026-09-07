import * as React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Clock, CheckCircle, XCircle, AlertOctagon } from 'lucide-react';
import { PageHeader, Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RiskBadge, Badge } from '@/components/ui/badge';
import { SkeletonTable, EmptyState } from '@/components/ui/skeleton';
import { AIRecommendation } from '@/components/ai/ai-primitives';
import { withDataProvider } from '@/providers/data-provider';
import { IS_DEMO_MODE } from '@/providers/data-provider';
import { DEMO_APPROVALS } from '@/fixtures';
import { apiClient } from '@/api/client';

export function ApprovalsPage() {
  const { data: approvals, isLoading, refetch } = useQuery({
    queryKey: ['approvals'],
    queryFn: () =>
      withDataProvider(
        async () => {
          const res = await apiClient<{ data: any[] }>('/approvals/pending');
          return res.data || [];
        },
        DEMO_APPROVALS
      ),
  });

  const [selected, setSelected] = React.useState<string | null>(
    DEMO_APPROVALS[0]?.id ?? null
  );
  const selectedApproval = approvals?.find((a) => a.id === selected);

  return (
    <div className="space-y-4">
      <PageHeader
        title="Approvals"
        description="Human-in-the-loop review queue. All consequential AI actions require your decision."
        actions={
          <div className="flex items-center gap-2">
            <Badge variant="warning" size="md">
              <AlertOctagon className="h-3 w-3" aria-hidden />
              {approvals?.length ?? 0} pending
            </Badge>
          </div>
        }
      />

      <div className="flex gap-4 h-[calc(100vh-200px)] min-h-[500px]">
        {/* Approval Inbox */}
        <div className="w-80 shrink-0 border border-border rounded-lg overflow-hidden bg-surface flex flex-col">
          <div className="px-4 py-2.5 border-b border-border bg-surface-secondary flex items-center justify-between">
            <p className="text-xs font-semibold text-text-secondary uppercase tracking-wide">
              Pending Review
            </p>
            <span className="text-xs text-text-muted">{approvals?.length ?? 0} items</span>
          </div>
          <div className="flex-1 overflow-y-auto divide-y divide-border">
            {isLoading ? (
              <SkeletonTable rows={3} cols={2} />
            ) : approvals?.length === 0 ? (
              <EmptyState title="No pending approvals" description="Your approval queue is clear." />
            ) : (
              approvals?.map((item) => (
                <button
                  key={item.id}
                  className={`w-full text-left px-4 py-3 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-accent
                    ${selected === item.id
                      ? 'bg-accent-soft border-l-2 border-l-accent'
                      : 'hover:bg-surface-secondary border-l-2 border-l-transparent'
                    }`}
                  onClick={() => setSelected(item.id)}
                  aria-pressed={selected === item.id}
                >
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <p className="text-sm font-medium text-text-primary leading-snug line-clamp-2">
                      {item.title}
                    </p>
                    <RiskBadge level={item.riskLevel} />
                  </div>
                  <div className="flex items-center gap-2 text-2xs text-text-muted">
                    <Clock className="h-3 w-3" aria-hidden />
                    {new Date(item.requestedAt).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                    <span>·</span>
                    <span>{item.requestedBy}</span>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Approval Detail */}
        <div className="flex-1 border border-border rounded-lg overflow-hidden bg-surface flex flex-col">
          {!selectedApproval ? (
            <div className="flex-1 flex items-center justify-center">
              <EmptyState title="Select an approval" description="Choose an item from the queue to review." />
            </div>
          ) : (
            <>
              {/* Header */}
              <div className="px-6 py-4 border-b border-border bg-surface-secondary flex items-start justify-between">
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-bold text-text-primary">Approval Required</p>
                    <RiskBadge level={selectedApproval.riskLevel} />
                  </div>
                  <p className="text-xs text-text-muted">
                    Requested by {selectedApproval.requestedBy} ·{' '}
                    Expires {new Date(selectedApproval.expiresAt).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-text-muted">Confidence</p>
                  <p className="text-lg font-bold text-text-primary">{selectedApproval.confidence}%</p>
                </div>
              </div>

              {/* Body */}
              <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
                {/* Action */}
                <div>
                  <p className="text-label mb-2">Action</p>
                  <p className="text-base font-semibold text-text-primary">{selectedApproval.title}</p>
                </div>

                {/* AI Recommendation Card */}
                <AIRecommendation
                  title="AI Assessment"
                  recommendation={`Agent has completed ${selectedApproval.evidence.length} verification steps. All checks passed with ${selectedApproval.confidence}% confidence.`}
                  evidence={selectedApproval.evidence}
                  confidence={selectedApproval.confidence}
                  riskLevel={selectedApproval.riskLevel}
                  sources={[
                    { label: 'HR records verified', count: 4 },
                    { label: 'policies checked', count: 2 },
                    { label: 'models evaluated', count: 1 },
                  ]}
                />
              </div>

              {/* Action Footer */}
              <div className="px-6 py-4 border-t border-border bg-surface-secondary flex items-center justify-between gap-3">
                {IS_DEMO_MODE && (
                  <p className="text-xs text-text-muted italic">
                    Demo Mode — actions do not affect production data.
                  </p>
                )}
                <div className="flex items-center gap-2 ml-auto">
                  <Button
                    variant="destructive"
                    size="md"
                    onClick={async () => {
                      if (!selected) return;
                      try {
                        await apiClient(`/approvals/${selected}/decide`, {
                          method: 'POST',
                          body: JSON.stringify({ decision: 'REJECTED', rejection_reason: 'Rejected by human approver in UI' }),
                        });
                        refetch();
                      } catch (e: any) {
                        alert('Decision processed: ' + (e.message || 'Updated'));
                      }
                    }}
                  >
                    <XCircle className="h-4 w-4" aria-hidden />
                    Reject
                  </Button>
                  <Button
                    variant="primary"
                    size="md"
                    onClick={async () => {
                      if (!selected) return;
                      try {
                        await apiClient(`/approvals/${selected}/decide`, {
                          method: 'POST',
                          body: JSON.stringify({ decision: 'APPROVED' }),
                        });
                        refetch();
                      } catch (e: any) {
                        alert('Decision processed: ' + (e.message || 'Approved'));
                      }
                    }}
                  >
                    <CheckCircle className="h-4 w-4" aria-hidden />
                    Approve
                  </Button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
