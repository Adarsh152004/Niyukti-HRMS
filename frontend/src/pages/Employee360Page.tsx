import * as React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Edit, MoreHorizontal, MapPin, Mail, Calendar } from 'lucide-react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { StatusBadge, Badge } from '@/components/ui/badge';
import { Avatar } from '@/components/ui/avatar';
import { Card, CardHeader, CardTitle, Separator } from '@/components/ui/card';
import { withDataProvider } from '@/providers/data-provider';
import { DEMO_EMPLOYEES } from '@/fixtures';

function EmployeeOverviewTab({ employee }: { employee: (typeof DEMO_EMPLOYEES)[0] }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      {/* Employment Details */}
      <Card className="lg:col-span-2 space-y-4">
        <div>
          <p className="text-label mb-3">Employment</p>
          <dl className="grid grid-cols-2 gap-x-6 gap-y-3">
            {[
              { label: 'Employee Number', value: employee.employee_number },
              { label: 'Hire Date', value: new Date(employee.hire_date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) },
              { label: 'Department', value: employee.department },
              { label: 'Designation', value: employee.designation },
              { label: 'Manager', value: employee.manager_name },
              { label: 'Location', value: employee.location },
            ].map(({ label, value }) => (
              <div key={label}>
                <dt className="text-xs text-text-muted">{label}</dt>
                <dd className="text-sm font-medium text-text-primary mt-0.5">{value}</dd>
              </div>
            ))}
          </dl>
        </div>
        <Separator />
        <div>
          <p className="text-label mb-3">Contact</p>
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm text-text-secondary">
              <Mail className="h-3.5 w-3.5 text-text-muted" aria-hidden />
              {employee.email}
            </div>
            <div className="flex items-center gap-2 text-sm text-text-secondary">
              <MapPin className="h-3.5 w-3.5 text-text-muted" aria-hidden />
              {employee.location}
            </div>
          </div>
        </div>
      </Card>

      {/* Right panel — quick stats */}
      <div className="space-y-3">
        <Card>
          <p className="text-label mb-3">Leave Balance</p>
          <div className="space-y-2">
            {[
              { label: 'Annual Leave', remaining: 12, total: 21 },
              { label: 'Sick Leave', remaining: 8, total: 10 },
              { label: 'Casual Leave', remaining: 3, total: 5 },
            ].map((leave) => (
              <div key={leave.label}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-text-secondary">{leave.label}</span>
                  <span className="font-medium text-text-primary">{leave.remaining}/{leave.total} days</span>
                </div>
                <div className="h-1.5 rounded-full bg-surface-secondary overflow-hidden">
                  <div
                    className="h-full rounded-full bg-accent"
                    style={{ width: `${(leave.remaining / leave.total) * 100}%` }}
                    role="progressbar"
                    aria-valuenow={leave.remaining}
                    aria-valuemin={0}
                    aria-valuemax={leave.total}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <p className="text-label mb-3">Performance</p>
          <div className="space-y-1.5">
            <div className="flex justify-between">
              <span className="text-xs text-text-secondary">Last Rating</span>
              <Badge variant="success" size="sm">Exceeds Expectations</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-xs text-text-secondary">OKR Completion</span>
              <span className="text-xs font-medium text-text-primary">87%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-xs text-text-secondary">Goals Active</span>
              <span className="text-xs font-medium text-text-primary">4</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

export function Employee360Page() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: employees } = useQuery({
    queryKey: ['employees'],
    queryFn: () => withDataProvider(
      async () => { throw new Error('API not connected'); },
      DEMO_EMPLOYEES
    ),
  });

  const employee = employees?.find((e) => e.id === id) ?? employees?.[0];

  if (!employee) return null;

  return (
    <div className="space-y-4">
      {/* Breadcrumb */}
      <button
        onClick={() => navigate('/employees')}
        className="flex items-center gap-1.5 text-sm text-text-muted hover:text-text-primary transition-colors"
      >
        <ArrowLeft className="h-3.5 w-3.5" aria-hidden />
        Employees
      </button>

      {/* Employee Header Card */}
      <div className="bg-surface border border-border rounded-lg p-6">
        <div className="flex items-start gap-5">
          <Avatar name={employee.full_name} size="xl" />
          <div className="flex-1 min-w-0 space-y-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-xl font-bold text-text-primary">{employee.full_name}</h1>
              <StatusBadge status={employee.status} />
            </div>
            <p className="text-sm text-text-secondary">{employee.designation}</p>
            <p className="text-xs text-text-muted">{employee.department}</p>
            <div className="flex items-center gap-1.5 text-xs text-text-muted mt-1">
              <Calendar className="h-3 w-3" aria-hidden />
              Since {new Date(employee.hire_date).toLocaleDateString('en-US', { year: 'numeric', month: 'long' })}
              <span className="mx-1">·</span>
              <MapPin className="h-3 w-3" aria-hidden />
              {employee.location}
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <Button variant="secondary" size="sm">
              <Edit className="h-3.5 w-3.5" aria-hidden />
              Edit
            </Button>
            <Button variant="secondary" size="sm">
              Request Action
            </Button>
            <Button variant="ghost" size="icon-sm" aria-label="More actions">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview">
        <TabsList>
          {['Overview', 'Employment', 'Attendance', 'Leave', 'Performance', 'Learning', 'Documents', 'Compensation', 'Activity'].map((tab) => (
            <TabsTrigger key={tab} value={tab.toLowerCase()}>
              {tab}
            </TabsTrigger>
          ))}
        </TabsList>
        <TabsContent value="overview">
          <EmployeeOverviewTab employee={employee} />
        </TabsContent>
        {['employment', 'attendance', 'leave', 'performance', 'learning', 'documents', 'compensation', 'activity'].map((tab) => (
          <TabsContent key={tab} value={tab}>
            <div className="border border-border rounded-lg p-8 text-center text-text-muted text-sm">
              {tab.charAt(0).toUpperCase() + tab.slice(1)} tab — data loaded from backend API.
            </div>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}
