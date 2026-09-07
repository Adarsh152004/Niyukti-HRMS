import * as React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { BarChart3, TrendingUp, Users, Download } from 'lucide-react';
import { PageHeader, Card, CardHeader, CardTitle, MetricCard } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { withDataProvider } from '@/providers/data-provider';
import { DEMO_HEADCOUNT_TREND, DEMO_DEPARTMENTS } from '@/fixtures';

export function AnalyticsPage() {
  const { data: trend } = useQuery({
    queryKey: ['headcount-trend-analytics'],
    queryFn: () => withDataProvider(async () => { throw new Error(); }, DEMO_HEADCOUNT_TREND),
  });

  const { data: departments } = useQuery({
    queryKey: ['departments-analytics'],
    queryFn: () => withDataProvider(async () => { throw new Error(); }, DEMO_DEPARTMENTS),
  });

  return (
    <div className="space-y-5">
      <PageHeader
        title="Workforce &amp; Operational Analytics"
        description="Comprehensive workforce composition, attrition trajectory, talent acquisition pipeline velocity, and budget utilization."
        actions={
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm">YTD 2026</Button>
            <Button variant="primary" size="sm">
              <Download className="h-3.5 w-3.5" aria-hidden />
              Export Executive Report
            </Button>
          </div>
        }
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard label="Total Workforce" value="936" change={{ value: '+8.3% YTD', direction: 'up', isPositive: true }} detail="Full-time equivalent" />
        <MetricCard label="Annualized Attrition" value="4.1%" change={{ value: '-1.1pp', direction: 'down', isPositive: true }} detail="Below 6% benchmark" />
        <MetricCard label="Average Time to Hire" value="26 Days" change={{ value: '-8 Days', direction: 'down', isPositive: true }} detail="AI screening assisted" />
        <MetricCard label="Total Annualized Payroll" value="$41.0M" detail="Within board budget" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Headcount by Function Stacked Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Workforce Composition by Function (8-Month Growth)</CardTitle>
          </CardHeader>
          <div className="h-64">
            {trend && (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#6B7280' }} />
                  <YAxis tick={{ fontSize: 11, fill: '#6B7280' }} />
                  <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E5E7EB' }} />
                  <Legend iconType="circle" wrapperStyle={{ fontSize: 11, paddingTop: 8 }} />
                  <Area type="monotone" dataKey="engineering" name="Engineering" stackId="1" stroke="#2563EB" fill="#2563EB" />
                  <Area type="monotone" dataKey="gtm" name="Sales / GTM" stackId="1" stroke="#0891B2" fill="#0891B2" />
                  <Area type="monotone" dataKey="product" name="Product & Design" stackId="1" stroke="#7C3AED" fill="#7C3AED" />
                  <Area type="monotone" dataKey="operations" name="Operations & Legal" stackId="1" stroke="#6B7280" fill="#9CA3AF" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </Card>

        {/* Headcount by Department Bar Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Departmental Headcount &amp; Budget Allocation</CardTitle>
          </CardHeader>
          <div className="h-64">
            {departments && (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={departments} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="name" tick={{ fontSize: 9, fill: '#6B7280' }} angle={-20} textAnchor="end" />
                  <YAxis tick={{ fontSize: 11, fill: '#6B7280' }} />
                  <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E5E7EB' }} />
                  <Bar dataKey="headcount" name="Headcount" fill="#2563EB" radius={[4, 4, 0, 0]} maxBarSize={40} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
