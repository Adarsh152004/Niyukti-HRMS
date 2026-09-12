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

export interface EmployeeRecord {
  id: string;
  full_name: string;
  email: string;
  department: string;
  designation: string;
  location: string;
  status: string;
  employee_code?: string;
}

function normalizeEmployee(e: any): EmployeeRecord {
  const firstName = e.first_name || '';
  const lastName = e.last_name || '';
  const fullName = e.full_name || (firstName || lastName ? `${firstName} ${lastName}`.trim() : '') || e.preferred_name || 'Staff Member';
  const rawStatus = e.status || e.employment_status || 'active';
  
  return {
    id: String(e.id || e.employee_id || e.employee_code || `emp-${Math.random()}`),
    full_name: fullName,
    email: e.email || '',
    department: e.department || e.department_id || 'General',
    designation: e.designation || e.designation_id || 'Employee',
    location: e.location || 'HQ',
    status: typeof rawStatus === 'string' ? rawStatus.toLowerCase() : 'active',
    employee_code: e.employee_code || e.employee_id || '',
  };
}

export function EmployeesPage() {
  const navigate = useNavigate();
  const [page, setPage] = React.useState(1);
  const [search, setSearch] = React.useState('');
  const [statusFilter, setStatusFilter] = React.useState<string>('all');

  const { data: employees = [], isLoading } = useQuery<EmployeeRecord[]>({
    queryKey: ['employees', page, search, statusFilter],
    queryFn: () =>
      withDataProvider(
        async () => {
          const res = await apiClient<{ data: any[] }>('/employees');
          const list = Array.isArray(res?.data) ? res.data : (Array.isArray(res) ? res : []);
          return list.map(normalizeEmployee);
        },
        DEMO_EMPLOYEES.map(normalizeEmployee)
      ),
  });

  const filtered = React.useMemo(() => {
    if (!employees || !Array.isArray(employees)) return [];
    return employees.filter((e) => {
      const name = (e.full_name || '').toLowerCase();
      const email = (e.email || '').toLowerCase();
      const dept = (e.department || '').toLowerCase();
      const desig = (e.designation || '').toLowerCase();
      const sQuery = search.toLowerCase();

      const matchSearch = !search || name.includes(sQuery) || email.includes(sQuery) || dept.includes(sQuery) || desig.includes(sQuery);
      const matchStatus = statusFilter === 'all' || e.status === statusFilter.toLowerCase();
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
          <option value="on_leave">On Leave</option>
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
              totalPages={Math.max(1, Math.ceil(filtered.length / 20))}
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
