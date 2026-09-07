import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { CheckCircle2, AlertCircle, X } from 'lucide-react';
import { EmployeeSidebar } from './EmployeeSidebar';
import { EmployeeTopbar } from './EmployeeTopbar';
import { ApplyLeaveModal } from '@/components/modals/ApplyLeaveModal';
import { PayslipModal } from '@/components/modals/PayslipModal';
import { useEmployee } from '@/context/EmployeeContext';

export const EmployeeShell: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { feedback, setFeedback } = useEmployee();

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar */}
      <EmployeeSidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />

      {/* Main Column */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <EmployeeTopbar />

        {/* Feedback Alert Banner */}
        {feedback && (
          <div
            className={`px-4 py-2 text-xs flex items-center justify-between border-b ${
              feedback.type === 'success'
                ? 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border-emerald-500/20'
                : 'bg-rose-500/10 text-rose-700 dark:text-rose-300 border-rose-500/20'
            }`}
          >
            <div className="flex items-center gap-2">
              {feedback.type === 'success' ? (
                <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
              ) : (
                <AlertCircle className="w-3.5 h-3.5 shrink-0" />
              )}
              <span className="font-medium">{feedback.message}</span>
            </div>
            <button
              onClick={() => setFeedback(null)}
              className="text-text-muted hover:text-text-primary transition"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* Tab Page Outlet */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>

      {/* Global Modals */}
      <ApplyLeaveModal />
      <PayslipModal />
    </div>
  );
};
