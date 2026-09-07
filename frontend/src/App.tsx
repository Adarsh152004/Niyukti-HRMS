import { EmployeePortalPage } from '@/pages/EmployeePortalPage';
import * as React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppShell } from '@/layouts/AppShell';
import { DashboardPage } from '@/pages/DashboardPage';
import { EmployeesPage } from '@/pages/EmployeesPage';
import { Employee360Page } from '@/pages/Employee360Page';
import { AttendancePage } from '@/pages/AttendancePage';
import { LeavePage } from '@/pages/LeavePage';
import { PerformancePage } from '@/pages/PerformancePage';
import { RecruitmentPage } from '@/pages/RecruitmentPage';
import { PayrollPage } from '@/pages/PayrollPage';
import { DocumentsPage } from '@/pages/DocumentsPage';
import { CommandCenterPage } from '@/pages/CommandCenterPage';
import { AIAssistantPage } from '@/pages/AIAssistantPage';
import { AgentsPage } from '@/pages/AgentsPage';
import { WorkflowsPage } from '@/pages/WorkflowsPage';
import { OrchestrationPage } from '@/pages/OrchestrationPage';
import { AnalyticsPage } from '@/pages/AnalyticsPage';
import { MLCenterPage } from '@/pages/MLCenterPage';
import { GovernancePage } from '@/pages/GovernancePage';
import { AuditPage } from '@/pages/AuditPage';
import { SettingsPage } from '@/pages/SettingsPage';
import { GenericPage } from '@/pages/GenericPage';
import { CEOMobileChatPage } from '@/pages/CEOMobileChatPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 60_000,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  const [isDark, setIsDark] = React.useState(() => {
    if (typeof window === 'undefined') return false;
    const stored = localStorage.getItem('hrms-theme');
    if (stored) return stored === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  const toggleDark = () => {
    setIsDark((d) => {
      const next = !d;
      localStorage.setItem('hrms-theme', next ? 'dark' : 'light');
      return next;
    });
  };

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Standalone CEO Mobile App Routes (completely independent from AppShell/Sidebar) */}
          <Route path="mobile-chat" element={<CEOMobileChatPage />} />
          <Route path="ceo-mobile" element={<CEOMobileChatPage />} />

          {/* App Shell — all authenticated enterprise routes */}
          <Route element={<AppShell isDark={isDark} onToggleDark={toggleDark} />}>
            {/* Overview */}
            <Route index element={<DashboardPage />} />

            {/* Workforce */}
            <Route path="employee-portal" element={<EmployeePortalPage />} />
            <Route path="portal" element={<EmployeePortalPage />} />
            <Route path="employees" element={<EmployeesPage />} />
            <Route path="employees/:id" element={<Employee360Page />} />
            <Route path="attendance" element={<AttendancePage />} />
            <Route path="leave" element={<LeavePage />} />
            <Route path="performance" element={<PerformancePage />} />
            <Route path="learning" element={<GenericPage title="Learning & Development" description="Course certifications, compliance modules, and learning paths." />} />

            {/* Talent & Compensation */}
            <Route path="recruitment" element={<RecruitmentPage />} />
            <Route path="recruitment/jobs" element={<RecruitmentPage />} />
            <Route path="recruitment/candidates" element={<RecruitmentPage />} />
            <Route path="candidates" element={<RecruitmentPage />} />
            <Route path="payroll" element={<PayrollPage />} />

            {/* Operations & Documents */}
            <Route path="documents" element={<DocumentsPage />} />
            <Route path="policies" element={<DocumentsPage />} />

            {/* AI & Automation */}
            <Route path="command" element={<CommandCenterPage />} />
            <Route path="ai" element={<AIAssistantPage />} />
            <Route path="ai/assistant" element={<AIAssistantPage />} />
            <Route path="agents" element={<AgentsPage />} />
            <Route path="agents/:id" element={<AgentsPage />} />
            <Route path="ai/agents" element={<AgentsPage />} />
            <Route path="orchestration" element={<OrchestrationPage />} />
            <Route path="workflows" element={<WorkflowsPage />} />
            <Route path="workflows/:id" element={<WorkflowsPage />} />
            <Route path="ai/workflows" element={<WorkflowsPage />} />

            {/* Intelligence & ML */}
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="analytics/hr" element={<AnalyticsPage />} />
            <Route path="analytics/predictions" element={<MLCenterPage />} />
            <Route path="analytics/workforce" element={<AnalyticsPage />} />
            <Route path="ml" element={<MLCenterPage />} />
            <Route path="ml/models" element={<MLCenterPage />} />
            <Route path="ml/predictions" element={<MLCenterPage />} />
            <Route path="ml/lineage" element={<MLCenterPage />} />
            <Route path="ml/drift" element={<MLCenterPage />} />
            <Route path="ml/fairness" element={<MLCenterPage />} />

            {/* Administration, Governance & Safety */}
            <Route path="governance" element={<GovernancePage />} />
            <Route path="governance/overview" element={<GovernancePage />} />
            <Route path="governance/models" element={<MLCenterPage />} />
            <Route path="governance/llm" element={<GovernancePage />} />
            <Route path="governance/security" element={<GovernancePage />} />
            <Route path="governance/audit" element={<AuditPage />} />
            <Route path="audit" element={<AuditPage />} />
            <Route path="settings" element={<SettingsPage />} />

            {/* 404 fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;