import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { EmployeeProvider } from '@/context/EmployeeContext';
import { EmployeeShell } from '@/components/layout/EmployeeShell';
import { DashboardView } from '@/pages/DashboardView';
import { AttendanceView } from '@/pages/AttendanceView';
import { LeaveView } from '@/pages/LeaveView';
import { PayrollView } from '@/pages/PayrollView';
import { TimesheetView } from '@/pages/TimesheetView';
import { CredentialsView } from '@/pages/CredentialsView';

export function App() {
  return (
    <EmployeeProvider>
      <Routes>
        <Route path="/" element={<EmployeeShell />}>
          <Route index element={<DashboardView />} />
          <Route path="attendance" element={<AttendanceView />} />
          <Route path="leave" element={<LeaveView />} />
          <Route path="payroll" element={<PayrollView />} />
          <Route path="timesheet" element={<TimesheetView />} />
          <Route path="credentials" element={<CredentialsView />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </EmployeeProvider>
  );
}

export default App;
