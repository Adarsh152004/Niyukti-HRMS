import React, { useState, useEffect, useCallback } from 'react';

// ─── Types ────────────────────────────────────────────────────────────────────
interface Job {
  id: string;
  title: string;
  department: string;
  location: string;
  type: string;
  experience: string;
  salaryRange: string;
  description: string;
  responsibilities: string[];
  requirements: string[];
  techStack: string[];
  isActive: boolean;
  applicantCount: number;
  createdAt: string;
}

interface Application {
  _id: string;
  referenceId: string;
  fullName: string;
  email: string;
  jobTitle: string;
  jobId: string;
  status: string;
  yearsOfExperience: string;
  location: string;
  github: string;
  selectedSkills: string[];
  coverLetter?: string;
  reviewerNotes?: { author: string; note: string; createdAt: string }[];
  createdAt: string;
}

interface Dashboard {
  jobs: { total: number; active: number; closed: number };
  applications: {
    total: number;
    byStatus: Record<string, number>;
    conversionRate: string;
  };
  inquiries: { total: number };
  recentApplications: Application[];
  topJobs: Job[];
}

// ─── Constants ────────────────────────────────────────────────────────────────
const AGENT_KEY = 'azyntrix-agent-dev-key-2026';
const API = '/api/v1/agent';
const DEPARTMENTS = [
  'Frontend', 'Backend', 'Full Stack', 'Cloud & DevOps', 'Data & AI',
  'Mobile', 'Security', 'QA & Testing', 'Product & Design',
  'Engineering Leadership', 'Management', 'Sales & Marketing', 'Operations', 'HR & People',
];
const PIPELINE_STAGES = ['submitted', 'screening', 'interview_scheduled', 'offered', 'rejected'];
const STAGE_LABELS: Record<string, string> = {
  submitted: 'Applied',
  screening: 'Screening',
  interview_scheduled: 'Interview',
  offered: 'Offered',
  rejected: 'Rejected',
};
const STAGE_COLORS: Record<string, string> = {
  submitted: '#6366f1',
  screening: '#f59e0b',
  interview_scheduled: '#3b82f6',
  offered: '#10b981',
  rejected: '#ef4444',
};

// ─── API Helper ───────────────────────────────────────────────────────────────
async function agentFetch(path: string, options: RequestInit = {}) {
  const res = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      'X-Agent-Key': AGENT_KEY,
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  });
  const json = await res.json();
  if (!json.success) throw new Error(json.error || 'API Error');
  return json;
}

// ─── Auth Gate ────────────────────────────────────────────────────────────────
function AdminAuthGate({ onAuth }: { onAuth: () => void }) {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const correctPw = (import.meta as any).env?.VITE_ADMIN_PASSWORD || 'azyntrix-admin-2026';
    if (password === correctPw || password === 'azyntrix-admin-2026') {
      sessionStorage.setItem('azyntrix_admin_auth', '1');
      onAuth();
    } else {
      setError('Invalid access code. Please try again.');
    }
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: '#0a0a0f', fontFamily: "'Inter', sans-serif",
    }}>
      <div style={{
        background: '#12121a', border: '1px solid #1e1e2e', borderRadius: 16,
        padding: '48px 40px', width: 380, boxShadow: '0 25px 60px rgba(0,0,0,0.5)',
      }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div style={{
            width: 56, height: 56, borderRadius: 12, background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px',
            fontSize: 24,
          }}>🔐</div>
          <h1 style={{ color: '#fff', fontSize: 22, fontWeight: 700, margin: '0 0 6px' }}>Admin Access</h1>
          <p style={{ color: '#64748b', fontSize: 14, margin: 0 }}>Azyntrix HRMS Control Panel</p>
        </div>
        <form onSubmit={handleSubmit}>
          <input
            type="password"
            placeholder="Enter admin access code"
            value={password}
            onChange={e => { setPassword(e.target.value); setError(''); }}
            autoFocus
            style={{
              width: '100%', padding: '12px 16px', background: '#1a1a2e', border: '1px solid #2d2d44',
              borderRadius: 8, color: '#fff', fontSize: 14, outline: 'none', boxSizing: 'border-box',
              marginBottom: 12,
            }}
          />
          {error && <p style={{ color: '#ef4444', fontSize: 13, margin: '0 0 12px' }}>{error}</p>}
          <button
            type="submit"
            style={{
              width: '100%', padding: '12px', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
              border: 'none', borderRadius: 8, color: '#fff', fontSize: 15, fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Access Dashboard →
          </button>
          <p style={{ color: '#374151', fontSize: 12, textAlign: 'center', marginTop: 16 }}>
            Default dev code: <code style={{ color: '#6366f1' }}>azyntrix-admin-2026</code>
          </p>
        </form>
      </div>
    </div>
  );
}

// ─── Stat Card ────────────────────────────────────────────────────────────────
function StatCard({ label, value, sub, color = '#6366f1', icon }: {
  label: string; value: string | number; sub?: string; color?: string; icon: string;
}) {
  return (
    <div style={{
      background: '#12121a', border: '1px solid #1e1e2e', borderRadius: 12,
      padding: '20px 24px', flex: 1,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <span style={{ color: '#64748b', fontSize: 13, fontWeight: 500 }}>{label}</span>
        <span style={{ fontSize: 20 }}>{icon}</span>
      </div>
      <div style={{ color: '#fff', fontSize: 28, fontWeight: 700, lineHeight: 1 }}>{value}</div>
      {sub && <div style={{ color: color, fontSize: 12, marginTop: 6, fontWeight: 500 }}>{sub}</div>}
    </div>
  );
}

// ─── Job Row ──────────────────────────────────────────────────────────────────
function JobRow({ job, onToggle, onDelete, onEdit }: {
  job: Job;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
  onEdit: (job: Job) => void;
}) {
  return (
    <tr style={{ borderBottom: '1px solid #1e1e2e' }}>
      <td style={{ padding: '14px 16px' }}>
        <div style={{ color: '#fff', fontWeight: 600, fontSize: 14 }}>{job.title}</div>
        <div style={{ color: '#64748b', fontSize: 12, marginTop: 2 }}>{job.department}</div>
      </td>
      <td style={{ padding: '14px 16px', color: '#94a3b8', fontSize: 13 }}>{job.experience}</td>
      <td style={{ padding: '14px 16px', color: '#94a3b8', fontSize: 13 }}>{job.salaryRange}</td>
      <td style={{ padding: '14px 16px', color: '#6366f1', fontSize: 13, fontWeight: 600 }}>
        {job.applicantCount}
      </td>
      <td style={{ padding: '14px 16px' }}>
        <span style={{
          background: job.isActive ? 'rgba(16,185,129,0.15)' : 'rgba(100,116,139,0.15)',
          color: job.isActive ? '#10b981' : '#64748b',
          padding: '3px 10px', borderRadius: 20, fontSize: 12, fontWeight: 600,
        }}>
          {job.isActive ? '● Active' : '○ Closed'}
        </span>
      </td>
      <td style={{ padding: '14px 16px' }}>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={() => onEdit(job)} style={btnStyle('#1e293b', '#6366f1')}>Edit</button>
          <button onClick={() => onToggle(job.id)} style={btnStyle('#1e293b', '#f59e0b')}>
            {job.isActive ? 'Close' : 'Reopen'}
          </button>
          <button onClick={() => onDelete(job.id)} style={btnStyle('#1e293b', '#ef4444')}>Del</button>
        </div>
      </td>
    </tr>
  );
}

const btnStyle = (bg: string, color: string): React.CSSProperties => ({
  background: bg, color, border: `1px solid ${color}33`, padding: '5px 10px',
  borderRadius: 6, fontSize: 12, cursor: 'pointer', fontWeight: 600,
});

// ─── Application Kanban Card ──────────────────────────────────────────────────
function AppCard({ app, onAdvance }: {
  app: Application;
  onAdvance: (ref: string, status: string) => void;
}) {
  const nextStage: Record<string, string> = {
    submitted: 'screening',
    screening: 'interview_scheduled',
    interview_scheduled: 'offered',
  };
  const next = nextStage[app.status];

  return (
    <div style={{
      background: '#12121a', border: '1px solid #1e1e2e', borderRadius: 10,
      padding: 16, marginBottom: 10,
    }}>
      <div style={{ color: '#fff', fontWeight: 600, fontSize: 13 }}>{app.fullName}</div>
      <div style={{ color: '#64748b', fontSize: 12, marginTop: 2 }}>{app.jobTitle}</div>
      <div style={{ color: '#475569', fontSize: 11, marginTop: 4 }}>{app.referenceId}</div>
      <div style={{ color: '#94a3b8', fontSize: 11, marginTop: 4 }}>
        {app.yearsOfExperience} exp · {app.location}
      </div>
      {app.selectedSkills?.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 8 }}>
          {app.selectedSkills.slice(0, 3).map(s => (
            <span key={s} style={{
              background: '#1e1e2e', color: '#818cf8', padding: '2px 7px',
              borderRadius: 4, fontSize: 10,
            }}>{s}</span>
          ))}
        </div>
      )}
      <div style={{ display: 'flex', gap: 6, marginTop: 10 }}>
        {next && (
          <button
            onClick={() => onAdvance(app.referenceId, next)}
            style={{ ...btnStyle('#1a2744', '#3b82f6'), fontSize: 11 }}
          >
            → {STAGE_LABELS[next]}
          </button>
        )}
        <button
          onClick={() => onAdvance(app.referenceId, 'rejected')}
          style={{ ...btnStyle('#1e1a1a', '#ef4444'), fontSize: 11 }}
        >
          Reject
        </button>
      </div>
    </div>
  );
}

// ─── Post Job Modal ────────────────────────────────────────────────────────────
function PostJobModal({ onClose, onSuccess }: { onClose: () => void; onSuccess: () => void }) {
  const [form, setForm] = useState({
    title: '', department: 'Backend', description: '', experience: 'Mid Level',
    salaryRange: '', location: 'Remote (Worldwide)', type: 'Full-Time',
    techStack: '', responsibilities: '', requirements: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await agentFetch('/jobs', {
        method: 'POST',
        body: JSON.stringify({
          ...form,
          techStack: form.techStack.split(',').map(s => s.trim()).filter(Boolean),
          responsibilities: form.responsibilities.split('\n').map(s => s.trim()).filter(Boolean),
          requirements: form.requirements.split('\n').map(s => s.trim()).filter(Boolean),
        }),
      });
      onSuccess();
      onClose();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const inputStyle: React.CSSProperties = {
    width: '100%', background: '#1a1a2e', border: '1px solid #2d2d44',
    borderRadius: 8, color: '#fff', padding: '10px 14px', fontSize: 14,
    outline: 'none', boxSizing: 'border-box',
  };

  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', display: 'flex',
      alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: 20,
    }}>
      <div style={{
        background: '#12121a', border: '1px solid #1e1e2e', borderRadius: 16,
        padding: 32, width: '100%', maxWidth: 600, maxHeight: '90vh', overflowY: 'auto',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24 }}>
          <h2 style={{ color: '#fff', margin: 0, fontSize: 20, fontWeight: 700 }}>Post New Job</h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#64748b', fontSize: 20, cursor: 'pointer' }}>✕</button>
        </div>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            <div>
              <label style={{ color: '#94a3b8', fontSize: 12, display: 'block', marginBottom: 6 }}>Job Title *</label>
              <input required style={inputStyle} placeholder="e.g. Senior React Engineer"
                value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} />
            </div>
            <div>
              <label style={{ color: '#94a3b8', fontSize: 12, display: 'block', marginBottom: 6 }}>Department *</label>
              <select required style={{ ...inputStyle }} value={form.department}
                onChange={e => setForm(f => ({ ...f, department: e.target.value }))}>
                {DEPARTMENTS.map(d => <option key={d} value={d}>{d}</option>)}
              </select>
            </div>
          </div>
          <div>
            <label style={{ color: '#94a3b8', fontSize: 12, display: 'block', marginBottom: 6 }}>Description *</label>
            <textarea required rows={3} style={{ ...inputStyle, resize: 'vertical' }}
              placeholder="Role overview and responsibilities summary..."
              value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            <div>
              <label style={{ color: '#94a3b8', fontSize: 12, display: 'block', marginBottom: 6 }}>Experience Level</label>
              <select style={inputStyle} value={form.experience}
                onChange={e => setForm(f => ({ ...f, experience: e.target.value }))}>
                {['Junior (1-2 Years)', 'Mid Level (3-4 Years)', '5+ Years', '6+ Years', '8+ Years', 'Staff / Principal'].map(e => (
                  <option key={e} value={e}>{e}</option>
                ))}
              </select>
            </div>
            <div>
              <label style={{ color: '#94a3b8', fontSize: 12, display: 'block', marginBottom: 6 }}>Salary Range</label>
              <input style={inputStyle} placeholder="e.g. $120,000 – $160,000 USD"
                value={form.salaryRange} onChange={e => setForm(f => ({ ...f, salaryRange: e.target.value }))} />
            </div>
          </div>
          <div>
            <label style={{ color: '#94a3b8', fontSize: 12, display: 'block', marginBottom: 6 }}>Tech Stack (comma-separated)</label>
            <input style={inputStyle} placeholder="React, TypeScript, Node.js, PostgreSQL"
              value={form.techStack} onChange={e => setForm(f => ({ ...f, techStack: e.target.value }))} />
          </div>
          <div>
            <label style={{ color: '#94a3b8', fontSize: 12, display: 'block', marginBottom: 6 }}>Key Responsibilities (one per line)</label>
            <textarea rows={4} style={{ ...inputStyle, resize: 'vertical' }}
              placeholder="Lead architecture decisions&#10;Mentor junior engineers&#10;Work with client CTOs"
              value={form.responsibilities} onChange={e => setForm(f => ({ ...f, responsibilities: e.target.value }))} />
          </div>
          <div>
            <label style={{ color: '#94a3b8', fontSize: 12, display: 'block', marginBottom: 6 }}>Requirements (one per line)</label>
            <textarea rows={4} style={{ ...inputStyle, resize: 'vertical' }}
              placeholder="5+ years of production React experience&#10;Strong TypeScript skills&#10;Remote-first mindset"
              value={form.requirements} onChange={e => setForm(f => ({ ...f, requirements: e.target.value }))} />
          </div>
          {error && <p style={{ color: '#ef4444', fontSize: 13, margin: 0 }}>{error}</p>}
          <button type="submit" disabled={loading} style={{
            background: loading ? '#1e1e2e' : 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            color: loading ? '#475569' : '#fff', border: 'none', borderRadius: 8,
            padding: '12px', fontSize: 15, fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer',
          }}>
            {loading ? 'Publishing...' : '🚀 Publish Job Listing'}
          </button>
        </form>
      </div>
    </div>
  );
}

// ─── Main Admin Page ──────────────────────────────────────────────────────────
export function AdminPage() {
  const [authed, setAuthed] = useState(() => sessionStorage.getItem('azyntrix_admin_auth') === '1');
  const [tab, setTab] = useState<'overview' | 'jobs' | 'applications'>('overview');
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(false);
  const [showPostModal, setShowPostModal] = useState(false);
  const [toast, setToast] = useState('');
  const [editJob, setEditJob] = useState<Job | null>(null);

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(''), 3500);
  };

  const loadDashboard = useCallback(async () => {
    try {
      const res = await agentFetch('/dashboard');
      setDashboard(res.dashboard);
    } catch (e) { console.error(e); }
  }, []);

  const loadJobs = useCallback(async () => {
    setLoading(true);
    try {
      const res = await agentFetch('/jobs?limit=100');
      setJobs(res.data || []);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  }, []);

  const loadApplications = useCallback(async () => {
    setLoading(true);
    try {
      const res = await agentFetch('/applications?limit=200');
      setApplications(res.data || []);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  }, []);

  useEffect(() => {
    if (!authed) return;
    loadDashboard();
    loadJobs();
    loadApplications();
  }, [authed, loadDashboard, loadJobs, loadApplications]);

  const handleToggleJob = async (jobId: string) => {
    try {
      const res = await agentFetch(`/jobs/${jobId}/toggle`, { method: 'PATCH', body: '{}' });
      showToast(res.message);
      loadJobs(); loadDashboard();
    } catch (e: any) { showToast(`Error: ${e.message}`); }
  };

  const handleDeleteJob = async (jobId: string) => {
    if (!confirm('Close this job listing? (Soft-delete — can be reopened)')) return;
    try {
      const res = await agentFetch(`/jobs/${jobId}?hardDelete=false`, { method: 'DELETE' });
      showToast(res.message);
      loadJobs(); loadDashboard();
    } catch (e: any) { showToast(`Error: ${e.message}`); }
  };

  const handleAdvanceApp = async (refId: string, status: string) => {
    try {
      const res = await agentFetch(`/applications/${refId}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status, reviewerName: 'Admin Dashboard' }),
      });
      showToast(res.message);
      loadApplications(); loadDashboard();
    } catch (e: any) { showToast(`Error: ${e.message}`); }
  };

  if (!authed) return <AdminAuthGate onAuth={() => setAuthed(true)} />;

  const s: React.CSSProperties = { fontFamily: "'Inter', sans-serif" };

  // Group applications by status for kanban
  const appsByStatus: Record<string, Application[]> = {};
  PIPELINE_STAGES.forEach(stage => { appsByStatus[stage] = []; });
  applications.forEach(app => {
    if (appsByStatus[app.status]) appsByStatus[app.status].push(app);
  });

  return (
    <div style={{ ...s, minHeight: '100vh', background: '#0a0a0f', color: '#fff' }}>
      {/* Top Bar */}
      <div style={{
        background: '#12121a', borderBottom: '1px solid #1e1e2e',
        padding: '0 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        height: 60,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            width: 32, height: 32, background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16,
          }}>⚡</div>
          <span style={{ color: '#fff', fontWeight: 700, fontSize: 16 }}>Azyntrix Admin</span>
          <span style={{ color: '#374151', fontSize: 14 }}>/ HRMS Control Panel</span>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            onClick={() => { loadDashboard(); loadJobs(); loadApplications(); }}
            style={btnStyle('#1e1e2e', '#6366f1')}
          >↺ Refresh</button>
          <button onClick={() => setShowPostModal(true)} style={{
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', border: 'none',
            color: '#fff', padding: '7px 16px', borderRadius: 8, fontSize: 13,
            fontWeight: 600, cursor: 'pointer',
          }}>+ Post Job</button>
        </div>
      </div>

      {/* Tab Nav */}
      <div style={{ padding: '0 32px', borderBottom: '1px solid #1e1e2e', display: 'flex', gap: 0 }}>
        {(['overview', 'jobs', 'applications'] as const).map(t => (
          <button key={t} onClick={() => setTab(t)} style={{
            background: 'none', border: 'none', color: tab === t ? '#6366f1' : '#64748b',
            padding: '16px 20px', fontSize: 14, fontWeight: tab === t ? 700 : 500,
            cursor: 'pointer', borderBottom: tab === t ? '2px solid #6366f1' : '2px solid transparent',
            marginBottom: -1, textTransform: 'capitalize',
          }}>{t === 'applications' ? 'Pipeline' : t.charAt(0).toUpperCase() + t.slice(1)}</button>
        ))}
      </div>

      {/* Content */}
      <div style={{ padding: 32 }}>

        {/* ── OVERVIEW TAB ── */}
        {tab === 'overview' && dashboard && (
          <div>
            <h2 style={{ color: '#fff', fontWeight: 700, fontSize: 20, margin: '0 0 24px' }}>
              📊 Dashboard Overview
            </h2>

            {/* Stats */}
            <div style={{ display: 'flex', gap: 16, marginBottom: 32 }}>
              <StatCard label="Total Jobs" value={dashboard.jobs.total}
                sub={`${dashboard.jobs.active} active · ${dashboard.jobs.closed} closed`} icon="💼" />
              <StatCard label="Total Applications" value={dashboard.applications.total}
                sub={`Conversion: ${dashboard.applications.conversionRate}`} icon="📋" color="#10b981" />
              <StatCard label="In Screening" value={dashboard.applications.byStatus.screening || 0}
                sub="Candidates under review" icon="🔍" color="#f59e0b" />
              <StatCard label="Interview Stage" value={dashboard.applications.byStatus.interview_scheduled || 0}
                sub="Scheduled interviews" icon="🎯" color="#3b82f6" />
              <StatCard label="Offers Extended" value={dashboard.applications.byStatus.offered || 0}
                sub="Awaiting acceptance" icon="✅" color="#10b981" />
              <StatCard label="Client Inquiries" value={dashboard.inquiries.total}
                sub="Project leads received" icon="📩" color="#8b5cf6" />
            </div>

            {/* Pipeline Bar */}
            <div style={{ background: '#12121a', border: '1px solid #1e1e2e', borderRadius: 12, padding: 24, marginBottom: 24 }}>
              <h3 style={{ color: '#fff', margin: '0 0 16px', fontSize: 16, fontWeight: 600 }}>Application Pipeline</h3>
              <div style={{ display: 'flex', gap: 12 }}>
                {PIPELINE_STAGES.map(stage => {
                  const count = dashboard.applications.byStatus[stage] || 0;
                  const pct = dashboard.applications.total > 0
                    ? Math.round((count / dashboard.applications.total) * 100) : 0;
                  return (
                    <div key={stage} style={{ flex: 1, textAlign: 'center' }}>
                      <div style={{
                        height: 80, background: '#0a0a0f', borderRadius: 8, position: 'relative',
                        overflow: 'hidden', marginBottom: 8,
                      }}>
                        <div style={{
                          position: 'absolute', bottom: 0, left: 0, right: 0,
                          height: `${Math.max(pct, 5)}%`,
                          background: `${STAGE_COLORS[stage]}33`,
                          borderTop: `2px solid ${STAGE_COLORS[stage]}`,
                          transition: 'height 0.5s ease',
                        }} />
                        <div style={{
                          position: 'absolute', inset: 0, display: 'flex',
                          alignItems: 'center', justifyContent: 'center',
                          color: STAGE_COLORS[stage], fontSize: 20, fontWeight: 700,
                        }}>{count}</div>
                      </div>
                      <div style={{ color: '#94a3b8', fontSize: 12 }}>{STAGE_LABELS[stage]}</div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Recent Applications */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
              <div style={{ background: '#12121a', border: '1px solid #1e1e2e', borderRadius: 12, padding: 24 }}>
                <h3 style={{ color: '#fff', margin: '0 0 16px', fontSize: 16, fontWeight: 600 }}>🕐 Recent Applications</h3>
                {dashboard.recentApplications.map(app => (
                  <div key={app._id} style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    padding: '10px 0', borderBottom: '1px solid #1a1a2e',
                  }}>
                    <div>
                      <div style={{ color: '#fff', fontSize: 13, fontWeight: 600 }}>{app.fullName}</div>
                      <div style={{ color: '#64748b', fontSize: 12 }}>{app.jobTitle}</div>
                    </div>
                    <span style={{
                      background: `${STAGE_COLORS[app.status] || '#64748b'}22`,
                      color: STAGE_COLORS[app.status] || '#64748b',
                      padding: '2px 8px', borderRadius: 10, fontSize: 11, fontWeight: 600,
                    }}>{STAGE_LABELS[app.status] || app.status}</span>
                  </div>
                ))}
              </div>

              <div style={{ background: '#12121a', border: '1px solid #1e1e2e', borderRadius: 12, padding: 24 }}>
                <h3 style={{ color: '#fff', margin: '0 0 16px', fontSize: 16, fontWeight: 600 }}>🔥 Top Jobs by Applicants</h3>
                {dashboard.topJobs.map((job, i) => (
                  <div key={job.id} style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    padding: '10px 0', borderBottom: '1px solid #1a1a2e',
                  }}>
                    <div>
                      <div style={{ color: '#fff', fontSize: 13, fontWeight: 600 }}>
                        <span style={{ color: '#6366f1', marginRight: 8 }}>#{i + 1}</span>
                        {job.title}
                      </div>
                      <div style={{ color: '#64748b', fontSize: 12 }}>{job.department}</div>
                    </div>
                    <span style={{ color: '#6366f1', fontWeight: 700, fontSize: 15 }}>
                      {job.applicantCount}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ── JOBS TAB ── */}
        {tab === 'jobs' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
              <h2 style={{ color: '#fff', fontWeight: 700, fontSize: 20, margin: 0 }}>
                💼 Job Listings ({jobs.length})
              </h2>
              <button onClick={() => setShowPostModal(true)} style={{
                background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', border: 'none',
                color: '#fff', padding: '10px 20px', borderRadius: 8, fontSize: 14,
                fontWeight: 600, cursor: 'pointer',
              }}>+ Post New Job</button>
            </div>
            {loading ? (
              <div style={{ color: '#64748b', textAlign: 'center', padding: 40 }}>Loading jobs...</div>
            ) : (
              <div style={{ background: '#12121a', border: '1px solid #1e1e2e', borderRadius: 12, overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ background: '#0f0f1a', borderBottom: '1px solid #1e1e2e' }}>
                      {['Position', 'Experience', 'Salary', 'Applicants', 'Status', 'Actions'].map(h => (
                        <th key={h} style={{
                          padding: '12px 16px', color: '#64748b', fontSize: 12,
                          fontWeight: 600, textAlign: 'left', textTransform: 'uppercase', letterSpacing: '0.05em',
                        }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {jobs.map(job => (
                      <JobRow key={job.id} job={job}
                        onToggle={handleToggleJob}
                        onDelete={handleDeleteJob}
                        onEdit={setEditJob}
                      />
                    ))}
                    {jobs.length === 0 && (
                      <tr><td colSpan={6} style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>
                        No jobs yet. Click "+ Post New Job" to create one.
                      </td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* ── APPLICATIONS / PIPELINE TAB ── */}
        {tab === 'applications' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
              <h2 style={{ color: '#fff', fontWeight: 700, fontSize: 20, margin: 0 }}>
                📋 Application Pipeline ({applications.length} total)
              </h2>
            </div>
            {loading ? (
              <div style={{ color: '#64748b', textAlign: 'center', padding: 40 }}>Loading applications...</div>
            ) : (
              <div style={{ display: 'flex', gap: 16, overflowX: 'auto', paddingBottom: 16 }}>
                {PIPELINE_STAGES.map(stage => (
                  <div key={stage} style={{
                    flex: '0 0 260px', background: '#0d0d1a',
                    border: `1px solid ${STAGE_COLORS[stage]}33`, borderRadius: 12, padding: 16,
                  }}>
                    <div style={{
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14,
                    }}>
                      <span style={{ color: STAGE_COLORS[stage], fontWeight: 700, fontSize: 13 }}>
                        {STAGE_LABELS[stage]}
                      </span>
                      <span style={{
                        background: `${STAGE_COLORS[stage]}22`, color: STAGE_COLORS[stage],
                        borderRadius: 20, padding: '2px 8px', fontSize: 12, fontWeight: 700,
                      }}>{appsByStatus[stage].length}</span>
                    </div>
                    <div style={{ maxHeight: 'calc(100vh - 300px)', overflowY: 'auto' }}>
                      {appsByStatus[stage].map(app => (
                        <AppCard key={app._id} app={app} onAdvance={handleAdvanceApp} />
                      ))}
                      {appsByStatus[stage].length === 0 && (
                        <div style={{ color: '#374151', fontSize: 13, textAlign: 'center', padding: '20px 0' }}>
                          No candidates
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Toast */}
      {toast && (
        <div style={{
          position: 'fixed', bottom: 24, right: 24, background: '#10b981',
          color: '#fff', padding: '12px 20px', borderRadius: 10, fontSize: 14,
          fontWeight: 600, boxShadow: '0 8px 24px rgba(0,0,0,0.4)', zIndex: 9999,
          animation: 'slideUp 0.3s ease',
        }}>{toast}</div>
      )}

      {/* Post Job Modal */}
      {showPostModal && (
        <PostJobModal
          onClose={() => setShowPostModal(false)}
          onSuccess={() => { loadJobs(); loadDashboard(); showToast('Job published successfully! ✅'); }}
        />
      )}
    </div>
  );
}

export default AdminPage;
