import * as React from 'react';
import { useQuery } from '@tanstack/react-query';
import { FolderOpen, FileText, Download, ShieldCheck, Plus, Lock } from 'lucide-react';
import { PageHeader, Card, CardHeader, CardTitle, MetricCard } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table';
import { withDataProvider } from '@/providers/data-provider';

const DEMO_DOCS = [
  { id: 'doc-01', title: 'Global Employee Code of Conduct 2026', category: 'Policy', version: 'v4.2', updated: '2026-01-15', status: 'Published', classification: 'Public Internal' },
  { id: 'doc-02', title: 'Executive Compensation & Equity Plan', category: 'Governance', version: 'v2.0', updated: '2026-06-30', status: 'Restricted', classification: 'Board Confidential' },
  { id: 'doc-03', title: 'AI & Data Privacy Governance Framework', category: 'AI Policy', version: 'v3.1', updated: '2026-08-10', status: 'Published', classification: 'Enterprise Mandate' },
  { id: 'doc-04', title: 'Standard Mutual Non-Disclosure Agreement', category: 'Legal', version: 'v5.0', updated: '2025-11-20', status: 'Published', classification: 'Standard Template' },
  { id: 'doc-05', title: 'Statutory Leave & Benefits Handbook', category: 'HR Operations', version: 'v2026.1', updated: '2026-02-01', status: 'Published', classification: 'All Employees' },
];

export function DocumentsPage() {
  const { data: docs } = useQuery({
    queryKey: ['documents-list'],
    queryFn: () => withDataProvider(async () => { throw new Error(); }, DEMO_DOCS),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        title="Document &amp; Policy Library"
        description="Encrypted enterprise documents, compliance policies, standard operating procedures, and employment agreements."
        actions={
          <Button variant="primary" size="sm">
            <Plus className="h-4 w-4" aria-hidden />
            Upload Document
          </Button>
        }
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard label="Total Documents" value="48" detail="Version controlled" />
        <MetricCard label="Compliance Policies" value="12" detail="100% acknowledged" />
        <MetricCard label="Restricted / Board" value="4" detail="Access logged" />
        <MetricCard label="Vault Encryption" value="AES-256" detail="Hardware KMS secured" />
      </div>

      <Card padding="none">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Document Title</TableHead>
              <TableHead>Category</TableHead>
              <TableHead>Version</TableHead>
              <TableHead>Classification</TableHead>
              <TableHead>Last Updated</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="w-20"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {docs?.map((d) => (
              <TableRow key={d.id}>
                <TableCell>
                  <div className="flex items-center gap-2.5">
                    <FileText className="h-4 w-4 text-accent shrink-0" aria-hidden />
                    <div>
                      <p className="font-semibold text-text-primary text-sm">{d.title}</p>
                      <p className="text-xs text-text-muted font-mono">{d.id}</p>
                    </div>
                  </div>
                </TableCell>
                <TableCell className="text-xs text-text-secondary">{d.category}</TableCell>
                <TableCell className="text-xs font-mono text-text-primary">{d.version}</TableCell>
                <TableCell>
                  <span className="text-xs text-text-muted bg-surface-secondary px-2 py-0.5 rounded border border-border">
                    {d.classification}
                  </span>
                </TableCell>
                <TableCell className="text-xs text-text-muted">{d.updated}</TableCell>
                <TableCell>
                  <Badge variant="success" size="sm">{d.status}</Badge>
                </TableCell>
                <TableCell>
                  <Button variant="ghost" size="icon-sm" aria-label="Download document">
                    <Download className="h-3.5 w-3.5" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
