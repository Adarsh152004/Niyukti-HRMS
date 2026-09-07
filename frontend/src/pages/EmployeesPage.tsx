import * as React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Filter, Plus, MoreHorizontal } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { StatusBadge } from '@/components/ui/badge';
import { Avatar } from '@/components/ui/avatar';
import {
  Table, TableHeader, TableBody, TableRow, TableHead, TableCell, Pagination,
} from '@/components/ui/table';
import { SkeletonTable, EmptyState } from '@/components/ui/skeleton';
import { withDataProvider } from '@/providers/data-provider';
import { DEMO_EMPLOYEES } from '@/fixtures';
import { apiClient } from '@/api/client';

export function EmployeesPage() {
  const navigate = useNavigate();
  const [page, setPage] = React.useState(1);
  const [search, setSearch] = React.useState('');
  const [statusFilter, setStatusFilter] = React.useState<string>('all');

  const { data: employees, isLoading } = useQuery({
    queryKey: ['employees', page, search, statusFilter],
    queryFn: () =>
      withDataProvider(
        async () => {
          const res = await apiClient<{ data: any[] }>('/employees');
          return res.data || [];
        },
        DEMO_EMPLOYEES
      ),
  });

  const filtered = React.useMemo(() => {
    if (!employees) return [];
    return employees.filter((e) => {
      const matchSearch =
        !search ||
        e.full_name.toLowerCase().includes(search.toLowerCase()) ||
        e.email.toLowerCase().includes(search.toLowerCase()) ||
        e.department.toLowerCase().includes(search.toLowerCase());
      const matchStatus = statusFilter === 'all' || e.status === statusFilter;
      return matchSearch && matchStatus;
    });
  }, [employees, search, statusFilter]);

  return (
    <div className="space-y-4">
      <PageHeader
        title="Employees"
        description={`${employees?.length ?? 0} employees across the organization.`}
        actions={
          <Button variant="primary" size="md">
            <Plus className="h-4 w-4" aria-hidden />
            Add Employee
          </Button>
        }
      />

      {/* Filters */}
      <div className="flex items-center gap-2 flex-wrap">
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-text-muted" aria-hidden />
          <input
            type="search"
            placeholder="Search employees..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="h-8 pl-8 pr-3 text-sm bg-surface border border-border rounded-md w-64 placeholder:text-text-muted text-text-primary focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent transition-colors"
            aria-label="Search employees"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="h-8 px-2.5 text-sm bg-surface border border-border rounded-md text-text-secondary focus:outline-none focus:ring-2 focus:ring-accent"
          aria-label="Filter by status"
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
        <Button variant="secondary" size="sm">
          <Filter className="h-3.5 w-3.5" aria-hidden />
          More Filters
        </Button>
        {(search || statusFilter !== 'all') && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => { setSearch(''); setStatusFilter('all'); }}
          >
            Clear filters
          </Button>
        )}
      </div>

      {/* Table */}
      <div className="border border-border rounded-lg overflow-hidden bg-surface">
        {isLoading ? (
          <SkeletonTable rows={6} cols={5} />
        ) : filtered.length === 0 ? (
          <EmptyState
            title="No employees found"
            description="Try adjusting your filters or search query."
          />
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-10">
                    <input type="checkbox" aria-label="Select all" className="rounded border-border-strong" />
                  </TableHead>
                  <TableHead>Employee</TableHead>
                  <TableHead>Department</TableHead>
                  <TableHead>Designation</TableHead>
                  <TableHead>Location</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="w-12"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filtered.map((emp) => (
                  <TableRow
                    key={emp.id}
                    className="cursor-pointer"
                    onClick={() => navigate(`/employees/${emp.id}`)}
                  >
                    <TableCell onClick={(e) => e.stopPropagation()}>
                      <input type="checkbox" aria-label={`Select ${emp.full_name}`} className="rounded border-border-strong" />
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <Avatar name={emp.full_name} size="sm" />
                        <div className="min-w-0">
                          <p className="font-medium text-text-primary truncate">{emp.full_name}</p>
                          <p className="text-xs text-text-muted truncate">{emp.email}</p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="text-text-secondary">{emp.department}</TableCell>
                    <TableCell className="text-text-secondary">{emp.designation}</TableCell>
                    <TableCell className="text-text-muted text-xs">{emp.location}</TableCell>
                    <TableCell>
                      <StatusBadge status={emp.status} />
                    </TableCell>
                    <TableCell onClick={(e) => e.stopPropagation()}>
                      <Button variant="ghost" size="icon-sm" aria-label={`More actions for ${emp.full_name}`}>
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <Pagination
              page={page}
              totalPages={Math.ceil(filtered.length / 20)}
              total={filtered.length}
              pageSize={20}
              onPageChange={setPage}
            />
          </>
        )}
      </div>
    </div>
  );
}
