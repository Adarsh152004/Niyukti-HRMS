import * as React from "react";
import { useState, useEffect, useMemo } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Clock,
  Calendar,
  DollarSign,
  FileText,
  User,
  CheckCircle2,
  AlertCircle,
  Plus,
  Send,
  Building,
  Briefcase,
  MapPin,
  TrendingUp,
  ExternalLink,
  ShieldCheck,
  Download,
  Timer,
  LogOut,
  LogIn,
  Search,
  RefreshCw,
  X,
  Mail,
  Phone,
  LayoutDashboard,
  CheckSquare,
  CreditCard,
  ChevronDown,
  Printer,
  Sparkles,
} from "lucide-react";
import { PageHeader, Card, CardHeader, CardTitle, MetricCard } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { cn } from "@/lib/utils";

interface EmployeeSummary {
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

interface Profile {
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

interface AttendanceRecord {
  id: string;
  date: string;
  check_in?: string;
  check_out?: string;
  status: string;
  source?: string;
  overtime_hours?: number;
  remarks?: string;
}

interface AttendanceData {
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

interface LeaveBalances {
  annual?: { total: number; used: number; available: number };
  sick?: { total: number; used: number; available: number };
  casual?: { total: number; used: number; available: number };
}

interface LeaveRequestItem {
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

interface LeaveData {
  balances?: LeaveBalances;
  requests?: LeaveRequestItem[];
}

interface Payslip {
  id: string;
  period: string;
  gross_salary: number;
  net_salary: number;
  deductions: number;
  tax: number;
  disbursed_at: string;
  status: string;
}

interface WorkLog {
  id: string;
  work_date: string;
  description: string;
  hours_spent: number;
  blockers?: string;
  created_at: string;
}

export function EmployeePortalPage() {
  const navigate = useNavigate();

  // Active Employee Actor Context
  const [actorId, setActorId] = useState<string>(() => {
    return localStorage.getItem("hrms_active_employee_id") || "emp-001";
  });

  // State
  const [employeesList, setEmployeesList] = useState<EmployeeSummary[]>([]);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [attendance, setAttendance] = useState<AttendanceData | null>(null);
  const [leaveData, setLeaveData] = useState<LeaveData | null>(null);
  const [payslips, setPayslips] = useState<Payslip[]>([]);
  const [workLogs, setWorkLogs] = useState<WorkLog[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [punching, setPunching] = useState<boolean>(false);
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; message: string } | null>(null);
  const [activeTab, setActiveTab] = useState<"overview" | "attendance" | "leave" | "payslip" | "timesheet" | "profile">("overview");

  // Real-time ticking clock
  const [currentTime, setCurrentTime] = useState(new Date());

  // Search filter for employee switcher
  const [employeeSearch, setEmployeeSearch] = useState("");
  const [isSwitcherOpen, setIsSwitcherOpen] = useState(false);

  // New Work Log State
  const [logCategory, setLogCategory] = useState("Engineering");
  const [logTitle, setLogTitle] = useState("");
  const [logDesc, setLogDesc] = useState("");
  const [logHours, setLogHours] = useState("2.0");
  const [logBlockers, setLogBlockers] = useState("");
  const [submittingLog, setSubmittingLog] = useState(false);

  // Leave Modal State
  const [showLeaveModal, setShowLeaveModal] = useState(false);
  const [leaveType, setLeaveType] = useState("lt-annual");
  const [leaveStart, setLeaveStart] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 1);
    return d.toISOString().split("T")[0];
  });
  const [leaveEnd, setLeaveEnd] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 2);
    return d.toISOString().split("T")[0];
  });
  const [leaveDays, setLeaveDays] = useState("2.0");
  const [leaveReason, setLeaveReason] = useState("");
  const [submittingLeave, setSubmittingLeave] = useState(false);

  // Payslip Receipt Modal
  const [selectedPayslip, setSelectedPayslip] = useState<Payslip | null>(null);

  // Clock interval
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Fetch all employees for switcher
  useEffect(() => {
    const loadEmployees = async () => {
      try {
        const res = await fetch("/api/v1/employees/", {
          headers: { "X-Tenant-ID": "org-nova-01" },
        });
        if (res.ok) {
          const data = await res.json();
          const list = Array.isArray(data) ? data : data.data || [];
          setEmployeesList(list);
        }
      } catch (e) {
        console.error("Failed to load employees list:", e);
      }
    };
    loadEmployees();
  }, []);

  // Fetch employee specific data
  const fetchData = async (isManualRefresh = false) => {
    if (isManualRefresh) setRefreshing(true);
    else setLoading(true);

    const headers = {
      "X-Actor-ID": actorId,
      "X-Tenant-ID": "org-nova-01",
    };

    try {
      const [pRes, aRes, lRes, psRes, wlRes] = await Promise.all([
        fetch("/api/v1/me", { headers }),
        fetch("/api/v1/me/attendance", { headers }),
        fetch("/api/v1/me/leave", { headers }),
        fetch("/api/v1/me/payslips", { headers }),
        fetch("/api/v1/me/work-logs", { headers }),
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
      console.error("Error fetching employee portal data:", err);
      setFeedback({ type: "error", message: "Failed to load employee records from backend." });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [actorId]);

  // Handle Employee Switching
  const handleSelectEmployee = (empId: string) => {
    setActorId(empId);
    localStorage.setItem("hrms_active_employee_id", empId);
    setIsSwitcherOpen(false);
    setFeedback({ type: "success", message: `Switched identity to ${empId}` });
  };

  // 1-Tap Biometric Punch In / Out
  const handlePunch = async (action: "CLOCK_IN" | "CLOCK_OUT") => {
    setPunching(true);
    setFeedback(null);
    try {
      const res = await fetch("/api/v1/me/attendance/punch", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Actor-ID": actorId,
          "X-Tenant-ID": "org-nova-01",
        },
        body: JSON.stringify({
          action,
          notes: action === "CLOCK_IN" ? "Clocked in via Employee Self-Service" : "Clocked out via Employee Self-Service",
        }),
      });

      const data = await res.json();
      if (res.ok) {
        setFeedback({
          type: "success",
          message: data.message || `Biometric punch ${action === "CLOCK_IN" ? "Check-in" : "Check-out"} recorded!`,
        });
        await fetchData(true);
      } else {
        setFeedback({ type: "error", message: data.detail || "Punch action failed." });
      }
    } catch (err) {
      setFeedback({ type: "error", message: "Network error recording punch." });
    } finally {
      setPunching(false);
    }
  };

  // Submit Work Log
  const handleCreateWorkLog = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!logTitle.trim()) {
      setFeedback({ type: "error", message: "Please enter a task summary." });
      return;
    }
    setSubmittingLog(true);
    setFeedback(null);
    try {
      const fullDesc = `[${logCategory}] ${logTitle.trim()}${logDesc.trim() ? " — " + logDesc.trim() : ""}`;
      const res = await fetch("/api/v1/me/work-logs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Actor-ID": actorId,
          "X-Tenant-ID": "org-nova-01",
        },
        body: JSON.stringify({
          description: fullDesc,
          hours_spent: parseFloat(logHours) || 1.0,
          blockers: logBlockers.trim() || undefined,
        }),
      });

      if (res.ok) {
        setLogTitle("");
        setLogDesc("");
        setLogBlockers("");
        setFeedback({ type: "success", message: "Daily timesheet entry logged successfully!" });
        await fetchData(true);
      } else {
        const d = await res.json();
        setFeedback({ type: "error", message: d.detail || "Failed to save work log." });
      }
    } catch (err) {
      setFeedback({ type: "error", message: "Network error saving work log." });
    } finally {
      setSubmittingLog(false);
    }
  };

  // Submit Leave Application
  const handleApplyLeave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittingLeave(true);
    setFeedback(null);
    try {
      const res = await fetch("/api/v1/me/leave", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Actor-ID": actorId,
          "X-Tenant-ID": "org-nova-01",
        },
        body: JSON.stringify({
          leave_type_id: leaveType,
          start_date: leaveStart,
          end_date: leaveEnd,
          days_count: parseFloat(leaveDays) || 1.0,
          reason: leaveReason,
        }),
      });

      if (res.ok) {
        setShowLeaveModal(false);
        setLeaveReason("");
        setFeedback({ type: "success", message: "Leave request submitted to People Operations & HR approval queue." });
        await fetchData(true);
      } else {
        const d = await res.json();
        setFeedback({ type: "error", message: d.detail || "Leave application failed." });
      }
    } catch (err) {
      setFeedback({ type: "error", message: "Network error submitting leave application." });
    } finally {
      setSubmittingLeave(false);
    }
  };

  // Calculate live shift elapsed time
  const shiftElapsedTime = useMemo(() => {
    if (!attendance?.is_clocked_in || !attendance?.today?.check_in) return null;
    const checkInStr = attendance.today.check_in;
    const checkInDate = new Date(checkInStr.includes(" ") && !checkInStr.includes("T") ? checkInStr.replace(" ", "T") : checkInStr);
    if (isNaN(checkInDate.getTime())) return null;

    const diffMs = Math.max(0, currentTime.getTime() - checkInDate.getTime());
    const hours = Math.floor(diffMs / (1000 * 60 * 60));
    const mins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    const secs = Math.floor((diffMs % (1000 * 60)) / 1000);
    return `${String(hours).padStart(2, "0")}h ${String(mins).padStart(2, "0")}m ${String(secs).padStart(2, "0")}s`;
  }, [attendance, currentTime]);

  const isClockedIn = attendance?.is_clocked_in;
  const isClockedOut = attendance?.is_clocked_out;

  // Stats calculations
  const totalDaysPresent = attendance?.stats?.days_present ?? 0;
  const periodDays = attendance?.stats?.period_days ?? 30;
  const attendanceRate = periodDays > 0 ? Math.round((totalDaysPresent / Math.max(1, totalDaysPresent + (attendance?.stats?.days_absent || 0))) * 100) : 100;
  const totalLeaveAvailable = (leaveData?.balances?.annual?.available || 0) + (leaveData?.balances?.sick?.available || 0) + (leaveData?.balances?.casual?.available || 0);
  const latestPayslip = payslips.length > 0 ? payslips[0] : null;

  // Filtered employees for switcher
  const filteredEmployees = useMemo(() => {
    if (!employeeSearch.trim()) return employeesList;
    const q = employeeSearch.toLowerCase();
    return employeesList.filter(
      (e) =>
        e.first_name.toLowerCase().includes(q) ||
        e.last_name.toLowerCase().includes(q) ||
        e.employee_code.toLowerCase().includes(q) ||
        e.email.toLowerCase().includes(q)
    );
  }, [employeesList, employeeSearch]);

  const activeEmployeeObj = employeesList.find((e) => e.employee_id === actorId);
  const employeeDisplayName = profile?.full_name || (activeEmployeeObj ? `${activeEmployeeObj.first_name} ${activeEmployeeObj.last_name}` : actorId);

  return (
    <div className="space-y-6">
      {/* Enterprise Page Header with Actions & Switcher */}
      <PageHeader
        title="Employee Self-Service (ESS)"
        description="Personal workforce portal for timeclock, leave entitlements, verified payroll, and daily timesheets."
        actions={
          <div className="flex flex-wrap items-center gap-3">
            {/* Live Clock Badge */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-secondary border border-border text-xs font-mono text-text-secondary shadow-sm">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>
                {currentTime.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" })} •{" "}
                {currentTime.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
              </span>
            </div>

            {/* Employee Switcher Dropdown */}
            <div className="relative">
              <button
                type="button"
                onClick={() => setIsSwitcherOpen(!isSwitcherOpen)}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface border border-border hover:bg-surface-secondary text-text-primary text-xs font-medium transition shadow-sm"
              >
                <div className="h-5 w-5 rounded-full bg-accent/20 text-accent font-bold text-2xs flex items-center justify-center">
                  {employeeDisplayName.charAt(0)}
                </div>
                <div className="text-left">
                  <span className="font-semibold">{employeeDisplayName}</span>
                  <span className="text-text-muted ml-1.5 text-2xs">({profile?.employee_code || actorId})</span>
                </div>
                <ChevronDown className="h-3.5 w-3.5 text-text-muted ml-1" />
              </button>

              {isSwitcherOpen && (
                <div className="absolute right-0 mt-2 w-72 bg-surface border border-border rounded-xl shadow-xl z-50 p-2 animate-in fade-in slide-in-from-top-2 duration-150">
                  <div className="p-2 border-b border-border">
                    <p className="text-xs font-semibold text-text-primary mb-1.5">Switch Active Identity</p>
                    <div className="relative">
                      <Search className="h-3.5 w-3.5 absolute left-2.5 top-2.5 text-text-muted" />
                      <input
                        type="text"
                        placeholder="Search employee or code..."
                        value={employeeSearch}
                        onChange={(e) => setEmployeeSearch(e.target.value)}
                        className="w-full pl-8 pr-2.5 py-1.5 text-xs rounded-lg bg-surface-secondary border border-border text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-1 focus:ring-accent"
                        autoFocus
                      />
                    </div>
                  </div>
                  <div className="max-h-60 overflow-y-auto py-1 space-y-0.5">
                    {filteredEmployees.map((emp) => {
                      const isSelected = emp.employee_id === actorId;
                      return (
                        <button
                          key={emp.employee_id}
                          onClick={() => handleSelectEmployee(emp.employee_id)}
                          className={cn(
                            "w-full text-left px-2.5 py-2 rounded-lg text-xs flex items-center justify-between transition",
                            isSelected
                              ? "bg-accent/10 text-accent font-semibold"
                              : "text-text-secondary hover:bg-surface-secondary hover:text-text-primary"
                          )}
                        >
                          <div>
                            <p className="font-medium">{emp.first_name} {emp.last_name}</p>
                            <p className="text-2xs text-text-muted">{emp.employee_code} • {emp.email}</p>
                          </div>
                          {isSelected && <CheckCircle2 className="h-4 w-4 text-accent shrink-0" />}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>

            {/* Manual Refresh */}
            <Button
              variant="secondary"
              size="sm"
              onClick={() => fetchData(true)}
              disabled={refreshing}
              className="gap-1.5"
            >
              <RefreshCw className={cn("h-3.5 w-3.5", refreshing && "animate-spin")} />
              <span>Refresh</span>
            </Button>
          </div>
        }
      />

      {/* Notification / Feedback Banner */}
      {feedback && (
        <div
          className={cn(
            "p-3.5 rounded-xl border text-xs flex items-center justify-between animate-in fade-in transition-all",
            feedback.type === "success"
              ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-700 dark:text-emerald-400"
              : "bg-rose-500/10 border-rose-500/30 text-rose-700 dark:text-rose-400"
          )}
        >
          <div className="flex items-center gap-2">
            {feedback.type === "success" ? (
              <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600 dark:text-emerald-400" />
            ) : (
              <AlertCircle className="h-4 w-4 shrink-0 text-rose-600 dark:text-rose-400" />
            )}
            <span className="font-medium">{feedback.message}</span>
          </div>
          <button
            onClick={() => setFeedback(null)}
            className="text-text-muted hover:text-text-primary transition"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Executive Metric Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Shift Timeclock */}
        <Card className="flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">
                Shift Timeclock
              </span>
              <Badge
                variant={isClockedIn ? "success" : isClockedOut ? "default" : "warning"}
                size="sm"
              >
                {isClockedIn ? "In Progress" : isClockedOut ? "Completed" : "Pending Punch"}
              </Badge>
            </div>
            <div className="text-2xl font-bold font-mono text-text-primary tracking-tight">
              {isClockedIn && shiftElapsedTime ? (
                <span className="text-emerald-600 dark:text-emerald-400">{shiftElapsedTime}</span>
              ) : isClockedOut ? (
                "Shift Ended"
              ) : (
                "Not Clocked In"
              )}
            </div>
            <p className="text-xs text-text-muted mt-1">
              {attendance?.today?.check_in
                ? `Check-in at ${new Date(attendance.today.check_in).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`
                : "Awaiting morning punch"}
            </p>
          </div>

          <div className="mt-4 pt-3 border-t border-border flex items-center gap-2">
            {!isClockedIn && !isClockedOut && (
              <Button
                variant="primary"
                size="sm"
                className="w-full gap-1.5"
                onClick={() => handlePunch("CLOCK_IN")}
                disabled={punching}
              >
                <LogIn className="h-3.5 w-3.5" />
                <span>Clock In Now</span>
              </Button>
            )}
            {isClockedIn && (
              <Button
                variant="destructive"
                size="sm"
                className="w-full gap-1.5"
                onClick={() => handlePunch("CLOCK_OUT")}
                disabled={punching}
              >
                <LogOut className="h-3.5 w-3.5" />
                <span>Clock Out</span>
              </Button>
            )}
            {isClockedOut && (
              <Button
                variant="secondary"
                size="sm"
                className="w-full gap-1.5"
                onClick={() => handlePunch("CLOCK_IN")}
                disabled={punching}
              >
                <LogIn className="h-3.5 w-3.5" />
                <span>Clock In Again</span>
              </Button>
            )}
          </div>
        </Card>

        {/* Card 2: Attendance Rate */}
        <MetricCard
          label="Monthly Attendance"
          value={`${totalDaysPresent} / ${periodDays}d`}
          change={{
            value: `${attendanceRate}%`,
            direction: attendanceRate >= 95 ? "up" : "neutral",
            isPositive: attendanceRate >= 90,
          }}
          detail={`${attendance?.stats?.total_overtime_hours || 0}h verified overtime`}
        />

        {/* Card 3: Paid Time Off */}
        <MetricCard
          label="Available PTO Balance"
          value={`${totalLeaveAvailable.toFixed(1)} Days`}
          change={{
            value: `Annual: ${leaveData?.balances?.annual?.available || 0}d`,
            direction: "neutral",
            isPositive: true,
          }}
          detail={`Sick: ${leaveData?.balances?.sick?.available || 0}d • Casual: ${leaveData?.balances?.casual?.available || 0}d`}
        />

        {/* Card 4: Net Salary */}
        <MetricCard
          label="Latest Net Pay"
          value={
            latestPayslip
              ? `$${Number(latestPayslip.net_salary).toLocaleString(undefined, { minimumFractionDigits: 2 })}`
              : "$25,863.64"
          }
          change={{
            value: "Direct Deposit",
            direction: "up",
            isPositive: true,
          }}
          detail={`Period: ${latestPayslip?.period || "August 2026"} • Disbursed`}
        />
      </div>

      {/* Professional Horizontal Tabs Navigation */}
      <div className="flex items-center gap-1 border-b border-border pb-px overflow-x-auto">
        <button
          onClick={() => setActiveTab("overview")}
          className={cn(
            "flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition whitespace-nowrap",
            activeTab === "overview"
              ? "border-accent text-accent"
              : "border-transparent text-text-secondary hover:text-text-primary hover:border-border"
          )}
        >
          <LayoutDashboard className="h-4 w-4" />
          Dashboard &amp; Highlights
        </button>

        <button
          onClick={() => setActiveTab("attendance")}
          className={cn(
            "flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition whitespace-nowrap",
            activeTab === "attendance"
              ? "border-accent text-accent"
              : "border-transparent text-text-secondary hover:text-text-primary hover:border-border"
          )}
        >
          <Clock className="h-4 w-4" />
          Attendance &amp; Logs
        </button>

        <button
          onClick={() => setActiveTab("leave")}
          className={cn(
            "flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition whitespace-nowrap",
            activeTab === "leave"
              ? "border-accent text-accent"
              : "border-transparent text-text-secondary hover:text-text-primary hover:border-border"
          )}
        >
          <Calendar className="h-4 w-4" />
          Leave &amp; PTO Hub
        </button>

        <button
          onClick={() => setActiveTab("payslip")}
          className={cn(
            "flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition whitespace-nowrap",
            activeTab === "payslip"
              ? "border-accent text-accent"
              : "border-transparent text-text-secondary hover:text-text-primary hover:border-border"
          )}
        >
          <CreditCard className="h-4 w-4" />
          Payroll &amp; Payslips
        </button>

        <button
          onClick={() => setActiveTab("timesheet")}
          className={cn(
            "flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition whitespace-nowrap",
            activeTab === "timesheet"
              ? "border-accent text-accent"
              : "border-transparent text-text-secondary hover:text-text-primary hover:border-border"
          )}
        >
          <CheckSquare className="h-4 w-4" />
          Daily Tasks / Timesheet
        </button>

        <button
          onClick={() => setActiveTab("profile")}
          className={cn(
            "flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition whitespace-nowrap",
            activeTab === "profile"
              ? "border-accent text-accent"
              : "border-transparent text-text-secondary hover:text-text-primary hover:border-border"
          )}
        >
          <User className="h-4 w-4" />
          Credentials &amp; Profile
        </button>
      </div>

      {/* ── TAB 1: OVERVIEW & SHORTCUTS ── */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          {/* Quick Action Shortcuts Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <button
              onClick={() => setShowLeaveModal(true)}
              className="p-3.5 rounded-xl bg-surface border border-border hover:border-accent/50 hover:bg-surface-secondary text-left transition group shadow-sm"
            >
              <div className="h-8 w-8 rounded-lg bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-2 group-hover:scale-105 transition-transform">
                <Calendar className="h-4 w-4" />
              </div>
              <p className="text-xs font-semibold text-text-primary">Apply for Leave</p>
              <p className="text-2xs text-text-muted">Request PTO or sick time</p>
            </button>

            <button
              onClick={() => setActiveTab("timesheet")}
              className="p-3.5 rounded-xl bg-surface border border-border hover:border-accent/50 hover:bg-surface-secondary text-left transition group shadow-sm"
            >
              <div className="h-8 w-8 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mb-2 group-hover:scale-105 transition-transform">
                <CheckSquare className="h-4 w-4" />
              </div>
              <p className="text-xs font-semibold text-text-primary">Log Daily Work</p>
              <p className="text-2xs text-text-muted">Track deliverables &amp; hours</p>
            </button>

            <button
              onClick={() => {
                if (latestPayslip) setSelectedPayslip(latestPayslip);
                else setActiveTab("payslip");
              }}
              className="p-3.5 rounded-xl bg-surface border border-border hover:border-accent/50 hover:bg-surface-secondary text-left transition group shadow-sm"
            >
              <div className="h-8 w-8 rounded-lg bg-amber-500/10 text-amber-600 dark:text-amber-400 flex items-center justify-center mb-2 group-hover:scale-105 transition-transform">
                <DollarSign className="h-4 w-4" />
              </div>
              <p className="text-xs font-semibold text-text-primary">View Payslip</p>
              <p className="text-2xs text-text-muted">Download salary certificate</p>
            </button>

            <button
              onClick={() => navigate("/ai")}
              className="p-3.5 rounded-xl bg-surface border border-border hover:border-accent/50 hover:bg-surface-secondary text-left transition group shadow-sm"
            >
              <div className="h-8 w-8 rounded-lg bg-purple-500/10 text-purple-600 dark:text-purple-400 flex items-center justify-center mb-2 group-hover:scale-105 transition-transform">
                <Sparkles className="h-4 w-4" />
              </div>
              <p className="text-xs font-semibold text-text-primary">AI Workspace Chat</p>
              <p className="text-2xs text-text-muted">Query policies &amp; payroll</p>
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left 2 Cols: Recent Attendance & Shift Logs */}
            <div className="lg:col-span-2">
              <Card padding="none">
                <CardHeader className="px-5 pt-5 pb-3 flex flex-row items-center justify-between">
                  <CardTitle className="text-sm font-semibold flex items-center gap-2">
                    <Clock className="h-4 w-4 text-accent" />
                    Recent Punch History &amp; Biometric Records
                  </CardTitle>
                  <Button variant="ghost" size="sm" onClick={() => setActiveTab("attendance")}>
                    View All
                  </Button>
                </CardHeader>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date</TableHead>
                      <TableHead>Check-In</TableHead>
                      <TableHead>Check-Out</TableHead>
                      <TableHead>Effective Hours</TableHead>
                      <TableHead>Source</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {(attendance?.records || []).slice(0, 5).map((rec) => {
                      const isPresent = !!rec.check_in;
                      return (
                        <TableRow key={rec.id}>
                          <TableCell className="font-mono text-xs text-text-primary">{rec.date}</TableCell>
                          <TableCell className="font-mono text-xs text-text-primary">
                            {rec.check_in ? (
                              new Date(rec.check_in).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                            ) : (
                              <span className="text-text-muted">—</span>
                            )}
                          </TableCell>
                          <TableCell className="font-mono text-xs text-text-muted">
                            {rec.check_out ? (
                              new Date(rec.check_out).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                            ) : rec.check_in ? (
                              <span className="text-emerald-500 font-semibold text-2xs">In Progress</span>
                            ) : (
                              "—"
                            )}
                          </TableCell>
                          <TableCell className="font-mono text-xs font-semibold text-text-primary">
                            {rec.check_in && rec.check_out ? "8h 15m" : rec.check_in ? "Active" : "0h"}
                          </TableCell>
                          <TableCell>
                            <span className="text-2xs bg-surface-secondary px-1.5 py-0.5 rounded border border-border text-text-muted">
                              {rec.source || "PORTAL"}
                            </span>
                          </TableCell>
                          <TableCell>
                            <Badge variant={isPresent ? "success" : "default"} size="sm">
                              {rec.status || (isPresent ? "Present" : "Absent")}
                            </Badge>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </Card>
            </div>

            {/* Right Col: Leave Balances & Allocation Meters */}
            <div>
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-semibold flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-accent" />
                      Leave Entitlement Meters
                    </span>
                    <Button variant="ghost" size="sm" onClick={() => setShowLeaveModal(true)}>
                      <Plus className="h-3.5 w-3.5 mr-1" />
                      Apply
                    </Button>
                  </CardTitle>
                </CardHeader>
                <div className="space-y-4 pt-2">
                  {/* Annual Leave */}
                  <div>
                    <div className="flex justify-between text-xs mb-1.5">
                      <span className="font-semibold text-text-primary">Annual Leave</span>
                      <span className="text-text-muted font-mono">
                        {leaveData?.balances?.annual?.available ?? 18}d available / {leaveData?.balances?.annual?.total ?? 18}d total
                      </span>
                    </div>
                    <div className="h-2 rounded-full bg-surface-secondary overflow-hidden border border-border">
                      <div
                        className="h-full bg-indigo-600 rounded-full"
                        style={{
                          width: `${Math.min(
                            100,
                            (((leaveData?.balances?.annual?.available ?? 18) / (leaveData?.balances?.annual?.total ?? 18)) * 100)
                          )}%`,
                        }}
                      />
                    </div>
                  </div>

                  {/* Sick Leave */}
                  <div>
                    <div className="flex justify-between text-xs mb-1.5">
                      <span className="font-semibold text-text-primary">Sick Leave</span>
                      <span className="text-text-muted font-mono">
                        {leaveData?.balances?.sick?.available ?? 10}d available / {leaveData?.balances?.sick?.total ?? 10}d total
                      </span>
                    </div>
                    <div className="h-2 rounded-full bg-surface-secondary overflow-hidden border border-border">
                      <div
                        className="h-full bg-emerald-600 rounded-full"
                        style={{
                          width: `${Math.min(
                            100,
                            (((leaveData?.balances?.sick?.available ?? 10) / (leaveData?.balances?.sick?.total ?? 10)) * 100)
                          )}%`,
                        }}
                      />
                    </div>
                  </div>

                  {/* Casual Leave */}
                  <div>
                    <div className="flex justify-between text-xs mb-1.5">
                      <span className="font-semibold text-text-primary">Casual Leave</span>
                      <span className="text-text-muted font-mono">
                        {leaveData?.balances?.casual?.available ?? 6}d available / {leaveData?.balances?.casual?.total ?? 6}d total
                      </span>
                    </div>
                    <div className="h-2 rounded-full bg-surface-secondary overflow-hidden border border-border">
                      <div
                        className="h-full bg-amber-600 rounded-full"
                        style={{
                          width: `${Math.min(
                            100,
                            (((leaveData?.balances?.casual?.available ?? 6) / (leaveData?.balances?.casual?.total ?? 6)) * 100)
                          )}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>

                <div className="mt-5 p-3 rounded-xl bg-surface-secondary border border-border text-2xs text-text-muted">
                  <p className="font-semibold text-text-primary mb-1">Company Policy Rule:</p>
                  Leave applications exceeding 3 business days require Level 2 approval by your Department Lead.
                </div>
              </Card>
            </div>
          </div>
        </div>
      )}

      {/* ── TAB 2: ATTENDANCE & LOGS ── */}
      {activeTab === "attendance" && (
        <Card padding="none">
          <CardHeader className="px-5 pt-5 pb-3 flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Clock className="h-4 w-4 text-accent" />
              Full Attendance Ledger (30-Day Audit History)
            </CardTitle>
            <div className="flex items-center gap-2">
              <span className="text-xs text-text-muted font-mono">
                Compliance: <strong className="text-text-primary">{attendanceRate}%</strong>
              </span>
            </div>
          </CardHeader>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Check-In</TableHead>
                <TableHead>Check-Out</TableHead>
                <TableHead>Effective Hours</TableHead>
                <TableHead>Overtime</TableHead>
                <TableHead>Source</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Notes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(attendance?.records || []).map((rec) => {
                const isPresent = !!rec.check_in;
                return (
                  <TableRow key={rec.id}>
                    <TableCell className="font-mono text-xs text-text-primary font-semibold">
                      {rec.date}
                    </TableCell>
                    <TableCell className="font-mono text-xs text-text-primary">
                      {rec.check_in ? (
                        new Date(rec.check_in).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })
                      ) : (
                        <span className="text-text-muted">—</span>
                      )}
                    </TableCell>
                    <TableCell className="font-mono text-xs text-text-muted">
                      {rec.check_out ? (
                        new Date(rec.check_out).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })
                      ) : rec.check_in ? (
                        <span className="text-emerald-500 font-semibold text-2xs">Shift In Progress</span>
                      ) : (
                        "—"
                      )}
                    </TableCell>
                    <TableCell className="font-mono text-xs font-semibold text-text-primary">
                      {rec.check_in && rec.check_out ? "8h 30m" : rec.check_in ? "Active" : "0h"}
                    </TableCell>
                    <TableCell className="font-mono text-xs text-text-muted">
                      {rec.overtime_hours ? `${rec.overtime_hours}h` : "0.0h"}
                    </TableCell>
                    <TableCell>
                      <span className="text-2xs bg-surface-secondary px-1.5 py-0.5 rounded border border-border text-text-muted">
                        {rec.source || "PORTAL"}
                      </span>
                    </TableCell>
                    <TableCell>
                      <Badge variant={isPresent ? "success" : "default"} size="sm">
                        {rec.status || (isPresent ? "Present" : "Absent")}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-2xs text-text-muted max-w-[160px] truncate">
                      {rec.remarks || "Biometric match"}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </Card>
      )}

      {/* ── TAB 3: LEAVE & PTO HUB ── */}
      {activeTab === "leave" && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-semibold text-text-primary">Leave &amp; PTO Requests</h3>
              <p className="text-xs text-text-muted">Track submitted requests and real-time manager approvals</p>
            </div>
            <Button variant="primary" size="sm" onClick={() => setShowLeaveModal(true)}>
              <Plus className="h-4 w-4 mr-1.5" />
              Apply for Leave
            </Button>
          </div>

          <Card padding="none">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Type</TableHead>
                  <TableHead>Dates</TableHead>
                  <TableHead className="text-right">Days</TableHead>
                  <TableHead>Reason</TableHead>
                  <TableHead>Decision / Status</TableHead>
                  <TableHead>Approved By</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {(leaveData?.requests || []).length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8 text-text-muted">
                      No leave requests filed yet. Click "Apply for Leave" above.
                    </TableCell>
                  </TableRow>
                ) : (
                  (leaveData?.requests || []).map((req) => (
                    <TableRow key={req.id}>
                      <TableCell className="font-medium text-xs text-text-primary">
                        {req.leave_type_id === "lt-annual"
                          ? "Annual Leave"
                          : req.leave_type_id === "lt-sick"
                          ? "Sick Leave"
                          : req.leave_type_id === "lt-casual"
                          ? "Casual Leave"
                          : req.leave_type_id}
                      </TableCell>
                      <TableCell className="font-mono text-xs text-text-primary">
                        {req.start_date} → {req.end_date}
                      </TableCell>
                      <TableCell className="text-right font-mono text-xs font-semibold text-text-primary">
                        {req.days_count}d
                      </TableCell>
                      <TableCell className="text-xs text-text-muted max-w-[200px] truncate">
                        {req.reason}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            req.status === "APPROVED"
                              ? "success"
                              : req.status === "REJECTED"
                              ? "danger"
                              : "warning"
                          }
                          size="sm"
                        >
                          {req.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-xs text-text-muted">
                        {req.approved_by || "Pending Review"}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </Card>
        </div>
      )}

      {/* ── TAB 4: PAYROLL & PAYSLIPS ── */}
      {activeTab === "payslip" && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-semibold text-text-primary">Compensation &amp; Salary Certificates</h3>
              <p className="text-xs text-text-muted">Direct deposit receipts, tax declarations, and payslip history</p>
            </div>
          </div>

          <Card padding="none">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Pay Period</TableHead>
                  <TableHead className="text-right">Gross Salary</TableHead>
                  <TableHead className="text-right">Deductions</TableHead>
                  <TableHead className="text-right">Tax Withholding</TableHead>
                  <TableHead className="text-right">Net Take-Home</TableHead>
                  <TableHead>Disbursed Date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {payslips.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-8 text-text-muted">
                      No payslips found for active profile.
                    </TableCell>
                  </TableRow>
                ) : (
                  payslips.map((ps) => (
                    <TableRow key={ps.id}>
                      <TableCell className="font-semibold text-xs text-text-primary">{ps.period}</TableCell>
                      <TableCell className="text-right font-mono text-xs text-text-primary">
                        ${Number(ps.gross_salary).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </TableCell>
                      <TableCell className="text-right font-mono text-xs text-rose-600 dark:text-rose-400">
                        -${Number(ps.deductions).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </TableCell>
                      <TableCell className="text-right font-mono text-xs text-rose-600 dark:text-rose-400">
                        -${Number(ps.tax).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </TableCell>
                      <TableCell className="text-right font-mono text-xs font-bold text-emerald-600 dark:text-emerald-400">
                        ${Number(ps.net_salary).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </TableCell>
                      <TableCell className="font-mono text-xs text-text-muted">{ps.disbursed_at}</TableCell>
                      <TableCell>
                        <Badge variant="success" size="sm">
                          {ps.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => setSelectedPayslip(ps)}
                          className="gap-1 text-2xs"
                        >
                          <FileText className="h-3 w-3" />
                          View Receipt
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </Card>
        </div>
      )}

      {/* ── TAB 5: DAILY TASKS / TIMESHEET ── */}
      {activeTab === "timesheet" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Timesheet Submission Form */}
          <Card className="lg:col-span-1">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold flex items-center gap-2">
                <CheckSquare className="h-4 w-4 text-accent" />
                Log Daily Deliverables
              </CardTitle>
            </CardHeader>
            <form onSubmit={handleCreateWorkLog} className="space-y-4 pt-2">
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">Project / Stream</label>
                <select
                  value={logCategory}
                  onChange={(e) => setLogCategory(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-surface-secondary border border-border text-xs text-text-primary focus:outline-none focus:ring-1 focus:ring-accent"
                >
                  <option value="Engineering">Engineering / AI Core</option>
                  <option value="Product">Product Architecture</option>
                  <option value="Infrastructure">DevOps &amp; Infrastructure</option>
                  <option value="Compliance">Security &amp; Governance</option>
                  <option value="Operations">Workforce Operations</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">Task Summary</label>
                <input
                  type="text"
                  placeholder="e.g. Self-RAG Retrieval Calibration"
                  value={logTitle}
                  onChange={(e) => setLogTitle(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-surface-secondary border border-border text-xs text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-1 focus:ring-accent"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">Hours Spent</label>
                <input
                  type="number"
                  step="0.5"
                  min="0.5"
                  max="16"
                  value={logHours}
                  onChange={(e) => setLogHours(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-surface-secondary border border-border text-xs text-text-primary font-mono focus:outline-none focus:ring-1 focus:ring-accent"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">Detailed Deliverables</label>
                <textarea
                  rows={2}
                  placeholder="Details of PRs merged, docs written, or bugs resolved..."
                  value={logDesc}
                  onChange={(e) => setLogDesc(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-surface-secondary border border-border text-xs text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-1 focus:ring-accent"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1">Blockers / Dependencies</label>
                <input
                  type="text"
                  placeholder="Optional blockers..."
                  value={logBlockers}
                  onChange={(e) => setLogBlockers(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-surface-secondary border border-border text-xs text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-1 focus:ring-accent"
                />
              </div>

              <Button type="submit" variant="primary" size="sm" className="w-full" disabled={submittingLog}>
                {submittingLog ? "Submitting..." : "Submit Timesheet Entry"}
              </Button>
            </form>
          </Card>

          {/* Timesheet Audit Feed */}
          <Card padding="none" className="lg:col-span-2">
            <CardHeader className="px-5 pt-5 pb-3">
              <CardTitle className="text-sm font-semibold flex items-center gap-2">
                <FileText className="h-4 w-4 text-accent" />
                Verified Work Logs &amp; Audit Trail
              </CardTitle>
            </CardHeader>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Deliverables &amp; Details</TableHead>
                  <TableHead className="text-right">Hours</TableHead>
                  <TableHead>Blockers</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {workLogs.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4} className="text-center py-8 text-text-muted">
                      No timesheet entries logged for current period.
                    </TableCell>
                  </TableRow>
                ) : (
                  workLogs.map((wl) => (
                    <TableRow key={wl.id}>
                      <TableCell className="font-mono text-xs text-text-primary whitespace-nowrap">
                        {wl.work_date}
                      </TableCell>
                      <TableCell className="text-xs text-text-primary">
                        <span className="font-medium">{wl.description}</span>
                      </TableCell>
                      <TableCell className="text-right font-mono text-xs font-semibold text-text-primary">
                        {wl.hours_spent}h
                      </TableCell>
                      <TableCell className="text-xs text-text-muted">
                        {wl.blockers ? (
                          <span className="text-rose-500 font-medium">{wl.blockers}</span>
                        ) : (
                          "—"
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </Card>
        </div>
      )}

      {/* ── TAB 6: EMPLOYEE CREDENTIALS & PROFILE ── */}
      {activeTab === "profile" && (
        <Card>
          <CardHeader className="pb-4">
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-accent" />
              Verified Workforce Identity &amp; Organization Alignment
            </CardTitle>
          </CardHeader>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-2">
            <div className="p-4 rounded-xl bg-surface-secondary border border-border">
              <p className="text-2xs text-text-muted uppercase font-semibold">Full Legal Name</p>
              <p className="text-base font-bold text-text-primary mt-1">{profile?.full_name || employeeDisplayName}</p>
              <p className="text-xs text-accent mt-0.5">{profile?.employee_code || actorId}</p>
            </div>

            <div className="p-4 rounded-xl bg-surface-secondary border border-border">
              <p className="text-2xs text-text-muted uppercase font-semibold">Corporate Email</p>
              <p className="text-sm font-semibold text-text-primary mt-1">{profile?.email || "employee@novacorp.internal"}</p>
              <p className="text-2xs text-emerald-600 dark:text-emerald-400 mt-0.5">Verified SSO Active</p>
            </div>

            <div className="p-4 rounded-xl bg-surface-secondary border border-border">
              <p className="text-2xs text-text-muted uppercase font-semibold">Department &amp; Function</p>
              <p className="text-sm font-semibold text-text-primary mt-1">{profile?.department_name || "Engineering & AI"}</p>
              <p className="text-2xs text-text-muted mt-0.5">{profile?.designation_name || "Principal Engineer"}</p>
            </div>

            <div className="p-4 rounded-xl bg-surface-secondary border border-border">
              <p className="text-2xs text-text-muted uppercase font-semibold">Location / Base</p>
              <p className="text-sm font-semibold text-text-primary mt-1">{profile?.location || "San Francisco, CA"}</p>
              <p className="text-2xs text-text-muted mt-0.5">{profile?.timezone || "UTC-07:00 (Pacific)"}</p>
            </div>

            <div className="p-4 rounded-xl bg-surface-secondary border border-border">
              <p className="text-2xs text-text-muted uppercase font-semibold">Employment Status</p>
              <div className="mt-1">
                <Badge variant="success" size="sm">
                  {profile?.employment_status || "ACTIVE"}
                </Badge>
              </div>
              <p className="text-2xs text-text-muted mt-1">{profile?.employment_type || "FULL_TIME"} • Indefinite</p>
            </div>

            <div className="p-4 rounded-xl bg-surface-secondary border border-border">
              <p className="text-2xs text-text-muted uppercase font-semibold">Joining Date</p>
              <p className="text-sm font-semibold text-text-primary mt-1">{profile?.joining_date || "2023-04-15"}</p>
              <p className="text-2xs text-text-muted mt-0.5">3+ Years Tenure</p>
            </div>
          </div>
        </Card>
      )}

      {/* ── APPLY LEAVE MODAL ── */}
      {showLeaveModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in">
          <div className="w-full max-w-md bg-surface border border-border rounded-2xl shadow-2xl p-6 relative">
            <button
              onClick={() => setShowLeaveModal(false)}
              className="absolute right-4 top-4 text-text-muted hover:text-text-primary transition"
            >
              <X className="h-5 w-5" />
            </button>

            <h3 className="text-base font-bold text-text-primary flex items-center gap-2">
              <Calendar className="h-5 w-5 text-accent" />
              Apply for Paid Time Off
            </h3>
            <p className="text-xs text-text-muted mt-1">Submit request to People Ops &amp; Department Manager.</p>

            <form onSubmit={handleApplyLeave} className="space-y-4 mt-5">
              <div>
                <label className="block text-xs font-semibold text-text-secondary mb-1">Leave Type</label>
                <select
                  value={leaveType}
                  onChange={(e) => setLeaveType(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-surface-secondary border border-border text-xs text-text-primary focus:outline-none focus:ring-1 focus:ring-accent"
                >
                  <option value="lt-annual">Annual Leave ({leaveData?.balances?.annual?.available || 0}d available)</option>
                  <option value="lt-sick">Sick Leave ({leaveData?.balances?.sick?.available || 0}d available)</option>
                  <option value="lt-casual">Casual Leave ({leaveData?.balances?.casual?.available || 0}d available)</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-text-secondary mb-1">Start Date</label>
                  <input
                    type="date"
                    value={leaveStart}
                    onChange={(e) => setLeaveStart(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-surface-secondary border border-border text-xs text-text-primary focus:outline-none focus:ring-1 focus:ring-accent"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-text-secondary mb-1">End Date</label>
                  <input
                    type="date"
                    value={leaveEnd}
                    onChange={(e) => setLeaveEnd(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-surface-secondary border border-border text-xs text-text-primary focus:outline-none focus:ring-1 focus:ring-accent"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-text-secondary mb-1">Total Days</label>
                <input
                  type="number"
                  step="0.5"
                  min="0.5"
                  value={leaveDays}
                  onChange={(e) => setLeaveDays(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-surface-secondary border border-border text-xs text-text-primary font-mono focus:outline-none focus:ring-1 focus:ring-accent"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-text-secondary mb-1">Reason / Notes</label>
                <textarea
                  rows={3}
                  placeholder="Please describe reason for leave..."
                  value={leaveReason}
                  onChange={(e) => setLeaveReason(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-surface-secondary border border-border text-xs text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-1 focus:ring-accent"
                  required
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <Button type="button" variant="secondary" size="sm" onClick={() => setShowLeaveModal(false)}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary" size="sm" disabled={submittingLeave}>
                  {submittingLeave ? "Submitting..." : "Submit Application"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── DIGITAL PAYSLIP RECEIPT MODAL ── */}
      {selectedPayslip && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in">
          <div className="w-full max-w-lg bg-surface border border-border rounded-2xl shadow-2xl p-6 relative">
            <button
              onClick={() => setSelectedPayslip(null)}
              className="absolute right-4 top-4 text-text-muted hover:text-text-primary transition"
            >
              <X className="h-5 w-5" />
            </button>

            <div className="border-b border-border pb-4 mb-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-text-primary">NOVA CORP INTERNATIONAL</h3>
                  <p className="text-2xs text-text-muted">Official Salary Certificate &amp; Earnings Statement</p>
                </div>
                <Badge variant="success" size="sm">
                  PAID &amp; SETTLED
                </Badge>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs mb-4 p-3 rounded-xl bg-surface-secondary border border-border">
              <div>
                <p className="text-2xs text-text-muted">Employee</p>
                <p className="font-semibold text-text-primary">{employeeDisplayName}</p>
                <p className="text-2xs text-text-muted">{profile?.employee_code || actorId}</p>
              </div>
              <div>
                <p className="text-2xs text-text-muted">Pay Period</p>
                <p className="font-semibold text-text-primary">{selectedPayslip.period}</p>
                <p className="text-2xs text-text-muted">Disbursed: {selectedPayslip.disbursed_at}</p>
              </div>
            </div>

            <div className="space-y-2 text-xs border-t border-b border-border py-3 mb-4">
              <div className="flex justify-between">
                <span className="text-text-secondary">Base Gross Earnings</span>
                <span className="font-mono font-semibold text-text-primary">
                  ${Number(selectedPayslip.gross_salary).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div className="flex justify-between text-rose-600 dark:text-rose-400">
                <span>Medical &amp; Benefits Deductions</span>
                <span className="font-mono font-semibold">
                  -${Number(selectedPayslip.deductions).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div className="flex justify-between text-rose-600 dark:text-rose-400">
                <span>Federal &amp; State Tax Withholding</span>
                <span className="font-mono font-semibold">
                  -${Number(selectedPayslip.tax).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-700 dark:text-emerald-300 mb-5">
              <span className="text-xs font-bold uppercase tracking-wider">Net Direct Deposit</span>
              <span className="text-lg font-bold font-mono">
                ${Number(selectedPayslip.net_salary).toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </span>
            </div>

            <div className="flex items-center justify-end gap-2">
              <Button variant="secondary" size="sm" onClick={() => window.print()} className="gap-1.5">
                <Printer className="h-3.5 w-3.5" />
                Print Certificate
              </Button>
              <Button variant="primary" size="sm" onClick={() => setSelectedPayslip(null)}>
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
export default EmployeePortalPage;
