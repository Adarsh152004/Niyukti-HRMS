import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';

export interface EmployeeSummary {
  employee_id: string;
  employee_code: string;
  first_name: string;
  last_name: string;
  email: string;
  department_id?: string;
  designation_id?: string;
  employment_status: string;
  location?: string;
  joining_date?: string;
}

export interface Profile {
  employee_id: string;
  employee_code: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  phone?: string;
  department_name?: string;
  designation_name?: string;
  employment_status?: string;
  employment_type?: string;
  joining_date?: string;
  location?: string;
  timezone?: string;
}

export interface AttendanceRecord {
  id: string;
  date: string;
  check_in?: string;
  check_out?: string;
  status: string;
  source?: string;
  overtime_hours?: number;
  remarks?: string;
}

export interface AttendanceData {
  employee_id: string;
  is_clocked_in: boolean;
  is_clocked_out: boolean;
  today?: AttendanceRecord;
  stats?: {
    period_days: number;
    days_present: number;
    days_absent: number;
    total_overtime_hours: number;
  };
  records?: AttendanceRecord[];
}

export interface LeaveBalances {
  annual?: { total: number; used: number; available: number };
  sick?: { total: number; used: number; available: number };
  casual?: { total: number; used: number; available: number };
}

export interface LeaveRequestItem {
  id: string;
  leave_type_id: string;
  start_date: string;
  end_date: string;
  days_count: number;
  reason: string;
  status: string;
  created_at?: string;
  approved_by?: string;
}

export interface LeaveData {
  balances?: LeaveBalances;
  requests?: LeaveRequestItem[];
}

export interface Payslip {
  id: string;
  period: string;
  gross_salary: number;
  net_salary: number;
  deductions: number;
  tax: number;
  disbursed_at: string;
  status: string;
}

export interface WorkLog {
  id: string;
  work_date: string;
  description: string;
  hours_spent: number;
  blockers?: string;
  created_at: string;
}

interface EmployeeContextType {
  actorId: string;
  setActorId: (id: string) => void;
  employeesList: EmployeeSummary[];
  profile: Profile | null;
  attendance: AttendanceData | null;
  leaveData: LeaveData | null;
  payslips: Payslip[];
  workLogs: WorkLog[];
  loading: boolean;
  refreshing: boolean;
  punching: boolean;
  feedback: { type: 'success' | 'error'; message: string } | null;
  setFeedback: React.Dispatch<React.SetStateAction<{ type: 'success' | 'error'; message: string } | null>>;
  currentTime: Date;
  shiftElapsedTime: string | null;
  totalDaysPresent: number;
  attendanceRate: number;
  totalLeaveAvailable: number;
  latestPayslip: Payslip | null;
  selectedPayslip: Payslip | null;
  setSelectedPayslip: (p: Payslip | null) => void;
  showLeaveModal: boolean;
  setShowLeaveModal: (b: boolean) => void;
  fetchData: (isManualRefresh?: boolean) => Promise<void>;
  handleSelectEmployee: (id: string) => void;
  handlePunch: (action: 'CLOCK_IN' | 'CLOCK_OUT') => Promise<void>;
  handleCreateWorkLog: (data: { category: string; title: string; desc: string; hours: string; blockers: string }) => Promise<boolean>;
  handleApplyLeave: (data: { leaveType: string; start: string; end: string; days: string; reason: string }) => Promise<boolean>;
  formatCurrency: (amount?: number) => string;
}

const EmployeeContext = createContext<EmployeeContextType | undefined>(undefined);

export const EmployeeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [actorId, setActorId] = useState<string>(() => {
    return localStorage.getItem('hrms_active_employee_id') || 'emp-001';
  });

  const [employeesList, setEmployeesList] = useState<EmployeeSummary[]>([]);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [attendance, setAttendance] = useState<AttendanceData | null>(null);
  const [leaveData, setLeaveData] = useState<LeaveData | null>(null);
  const [payslips, setPayslips] = useState<Payslip[]>([]);
  const [workLogs, setWorkLogs] = useState<WorkLog[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [punching, setPunching] = useState<boolean>(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [selectedPayslip, setSelectedPayslip] = useState<Payslip | null>(null);
  const [showLeaveModal, setShowLeaveModal] = useState<boolean>(false);

  // Real-time ticking clock
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Fetch all employees for switcher
  useEffect(() => {
    const loadEmployees = async () => {
      try {
        const res = await fetch('/api/v1/employees/', {
          headers: { 'X-Tenant-ID': 'org-nova-01' },
        });
        if (res.ok) {
          const data = await res.json();
          const list = Array.isArray(data) ? data : data.data || [];
          setEmployeesList(list);
        }
      } catch (e) {
        console.error('Failed to load employees list:', e);
      }
    };
    loadEmployees();
  }, []);

  // Fetch employee specific data
  const fetchData = async (isManualRefresh = false) => {
    if (isManualRefresh) setRefreshing(true);
    else setLoading(true);

    const headers = {
      'X-Actor-ID': actorId,
      'X-Tenant-ID': 'org-nova-01',
    };

    try {
      const [pRes, aRes, lRes, psRes, wlRes] = await Promise.all([
        fetch('/api/v1/me', { headers }),
        fetch('/api/v1/me/attendance', { headers }),
        fetch('/api/v1/me/leave', { headers }),
        fetch('/api/v1/me/payslips', { headers }),
        fetch('/api/v1/me/work-logs', { headers }),
      ]);

      if (pRes.ok) {
        const pData = await pRes.json();
        setProfile(pData);
      }
      if (aRes.ok) {
        const aData = await aRes.json();
        setAttendance(aData);
      }
      if (lRes.ok) {
        const lData = await lRes.json();
        setLeaveData(lData);
      }
      if (psRes.ok) {
        const psJson = await psRes.json();
        setPayslips(Array.isArray(psJson) ? psJson : psJson.payslips || []);
      }
      if (wlRes.ok) {
        const wlJson = await wlRes.json();
        setWorkLogs(Array.isArray(wlJson) ? wlJson : wlJson.work_logs || []);
      }
    } catch (err) {
      console.error('Error fetching employee portal data:', err);
      setFeedback({ type: 'error', message: 'Failed to load employee records from backend.' });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [actorId]);

  const handleSelectEmployee = (empId: string) => {
    setActorId(empId);
    localStorage.setItem('hrms_active_employee_id', empId);
    setFeedback({ type: 'success', message: `Switched identity to ${empId}` });
  };

  const handlePunch = async (action: 'CLOCK_IN' | 'CLOCK_OUT') => {
    setPunching(true);
    setFeedback(null);
    try {
      const res = await fetch('/api/v1/me/attendance/punch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Actor-ID': actorId,
          'X-Tenant-ID': 'org-nova-01',
        },
        body: JSON.stringify({
          action,
          notes: action === 'CLOCK_IN' ? 'Clocked in via Employee Portal' : 'Clocked out via Employee Portal',
        }),
      });

      const data = await res.json();
      if (res.ok) {
        setFeedback({
          type: 'success',
          message: data.message || `Biometric punch ${action === 'CLOCK_IN' ? 'Check-in' : 'Check-out'} recorded!`,
        });
        await fetchData(true);
      } else {
        setFeedback({ type: 'error', message: data.detail || 'Punch action failed.' });
      }
    } catch (err) {
      setFeedback({ type: 'error', message: 'Network error recording punch.' });
    } finally {
      setPunching(false);
    }
  };

  const handleCreateWorkLog = async (data: { category: string; title: string; desc: string; hours: string; blockers: string }) => {
    if (!data.title.trim()) {
      setFeedback({ type: 'error', message: 'Please enter a task summary.' });
      return false;
    }
    setFeedback(null);
    try {
      const fullDesc = `[${data.category}] ${data.title.trim()}${data.desc.trim() ? ' — ' + data.desc.trim() : ''}`;
      const res = await fetch('/api/v1/me/work-logs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Actor-ID': actorId,
          'X-Tenant-ID': 'org-nova-01',
        },
        body: JSON.stringify({
          description: fullDesc,
          hours_spent: parseFloat(data.hours) || 1.0,
          blockers: data.blockers.trim() || undefined,
        }),
      });

      if (res.ok) {
        setFeedback({ type: 'success', message: 'Daily timesheet entry logged successfully!' });
        await fetchData(true);
        return true;
      } else {
        const d = await res.json();
        setFeedback({ type: 'error', message: d.detail || 'Failed to save work log.' });
        return false;
      }
    } catch (err) {
      setFeedback({ type: 'error', message: 'Network error saving work log.' });
      return false;
    }
  };

  const handleApplyLeave = async (data: { leaveType: string; start: string; end: string; days: string; reason: string }) => {
    setFeedback(null);
    try {
      const res = await fetch('/api/v1/me/leave', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Actor-ID': actorId,
          'X-Tenant-ID': 'org-nova-01',
        },
        body: JSON.stringify({
          leave_type_id: data.leaveType,
          start_date: data.start,
          end_date: data.end,
          days_count: parseFloat(data.days) || 1.0,
          reason: data.reason,
        }),
      });

      if (res.ok) {
        setShowLeaveModal(false);
        setFeedback({ type: 'success', message: 'Leave request submitted to People Operations & HR approval queue.' });
        await fetchData(true);
        return true;
      } else {
        const d = await res.json();
        setFeedback({ type: 'error', message: d.detail || 'Leave application failed.' });
        return false;
      }
    } catch (err) {
      setFeedback({ type: 'error', message: 'Network error submitting leave application.' });
      return false;
    }
  };

  const shiftElapsedTime = useMemo(() => {
    if (!attendance?.is_clocked_in || !attendance?.today?.check_in) return null;
    const checkInStr = attendance.today.check_in;
    const checkInDate = new Date(checkInStr.includes(' ') && !checkInStr.includes('T') ? checkInStr.replace(' ', 'T') : checkInStr);
    if (isNaN(checkInDate.getTime())) return null;

    const diffMs = Math.max(0, currentTime.getTime() - checkInDate.getTime());
    const hours = Math.floor(diffMs / (1000 * 60 * 60));
    const mins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    const secs = Math.floor((diffMs % (1000 * 60)) / 1000);
    return `${String(hours).padStart(2, '0')}h ${String(mins).padStart(2, '0')}m ${String(secs).padStart(2, '0')}s`;
  }, [attendance, currentTime]);

  const totalDaysPresent = attendance?.stats?.days_present ?? 0;
  const periodDays = attendance?.stats?.period_days ?? 30;
  const attendanceRate = periodDays > 0 ? Math.round((totalDaysPresent / Math.max(1, totalDaysPresent + (attendance?.stats?.days_absent || 0))) * 100) : 100;
  const totalLeaveAvailable = (leaveData?.balances?.annual?.available || 0) + (leaveData?.balances?.sick?.available || 0) + (leaveData?.balances?.casual?.available || 0);
  const latestPayslip = payslips.length > 0 ? payslips[0] : null;

  const formatCurrency = (amount?: number) => {
    if (amount === undefined || amount === null) return '$0.00';
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
  };

  return (
    <EmployeeContext.Provider
      value={{
        actorId,
        setActorId,
        employeesList,
        profile,
        attendance,
        leaveData,
        payslips,
        workLogs,
        loading,
        refreshing,
        punching,
        feedback,
        setFeedback,
        currentTime,
        shiftElapsedTime,
        totalDaysPresent,
        attendanceRate,
        totalLeaveAvailable,
        latestPayslip,
        selectedPayslip,
        setSelectedPayslip,
        showLeaveModal,
        setShowLeaveModal,
        fetchData,
        handleSelectEmployee,
        handlePunch,
        handleCreateWorkLog,
        handleApplyLeave,
        formatCurrency,
      }}
    >
      {children}
    </EmployeeContext.Provider>
  );
};

export const useEmployee = () => {
  const context = useContext(EmployeeContext);
  if (!context) throw new Error('useEmployee must be used within an EmployeeProvider');
  return context;
};
