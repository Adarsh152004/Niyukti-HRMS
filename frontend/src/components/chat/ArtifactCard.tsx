import React, { useState } from 'react';
import {
  FileText, CheckCircle2, AlertCircle, Edit3, Send, Check, X,
  Clock, Sparkles, ChevronDown, ChevronUp, Briefcase, MapPin, DollarSign, Building,
  ShieldCheck, Award, Calendar, CreditCard, Users, ArrowRight
} from 'lucide-react';

export interface ArtifactData {
  id: string;
  type: string; // "JOB_DESCRIPTION" | "PAYROLL_RUN" | "OFFER_LETTER" | "LEAVE_EXCEPTION"
  title: string;
  version: number;
  content: {
    // Job Description fields
    role_title?: string;
    department?: string;
    employment_type?: string;
    salary_range?: string;
    location?: string;
    about_role?: string;
    responsibilities?: string[];
    requirements?: string[];
    nice_to_have?: string[];

    // Payroll fields
    period?: string;
    total_net_payout?: string;
    gross_payroll?: string;
    total_tax_withholdings?: string;
    benefits_deductions?: string;
    employee_count?: number;
    compliance_status?: string;
    department_breakdown?: Array<{ dept: string; amount: string }>;

    // Offer Letter fields
    candidate_name?: string;
    role?: string;
    base_salary?: string;
    equity?: string;
    signing_bonus?: string;
    start_date?: string;
    benefits?: string;

    // Leave Exception fields
    employee?: string;
    leave_type?: string;
    duration?: string;
    coverage_risk?: string;
    remaining_balance?: string;

    feedback_applied?: string;
    [key: string]: any;
  };
  raw_markdown?: string;
  status: 'DRAFT' | 'AWAITING_APPROVAL' | 'APPROVED' | 'REVISION_REQUESTED' | 'REJECTED';
}

export interface ApprovalRequestData {
  id: string;
  workflow_id: string;
  artifact_id: string;
  artifact_version: number;
  status: 'PENDING' | 'APPROVED' | 'REVISION_REQUESTED' | 'REJECTED';
  action_required: string;
}

interface ArtifactCardProps {
  artifact: ArtifactData;
  approvalRequest?: ApprovalRequestData | null;
  workflowId?: string;
  onApprove: (workflowId: string) => Promise<void>;
  onRevise: (workflowId: string, feedback: string) => Promise<void>;
}

export const ArtifactCard: React.FC<ArtifactCardProps> = ({
  artifact,
  approvalRequest,
  workflowId,
  onApprove,
  onRevise,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [feedbackText, setFeedbackText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [isExpanded, setIsExpanded] = useState(true);

  const isApproved = artifact.status === 'APPROVED' || approvalRequest?.status === 'APPROVED';

  const handleApproveClick = async () => {
    if (!workflowId || submitting || isApproved) return;
    setSubmitting(true);
    try {
      await onApprove(workflowId);
    } finally {
      setSubmitting(false);
    }
  };

  const handleReviseSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!workflowId || !feedbackText.trim() || submitting) return;
    setSubmitting(true);
    try {
      await onRevise(workflowId, feedbackText.trim());
      setIsEditing(false);
      setFeedbackText('');
    } finally {
      setSubmitting(false);
    }
  };

  const { content } = artifact;
  const isPayroll = artifact.type === 'PAYROLL_RUN';
  const isOffer = artifact.type === 'OFFER_LETTER';
  const isLeave = artifact.type === 'LEAVE_EXCEPTION';
  const isJD = !isPayroll && !isOffer && !isLeave;

  return (
    <div className="w-full my-3 rounded-2xl border border-border bg-surface shadow-md overflow-hidden transition-all text-text-primary">
      
      {/* 1. Header Bar */}
      <div className="p-4 bg-surface-secondary/50 border-b border-border flex items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <div className={`p-2 rounded-xl shrink-0 border ${
            isPayroll
              ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'
              : isOffer
              ? 'bg-amber-500/10 text-amber-500 border-amber-500/20'
              : isLeave
              ? 'bg-purple-500/10 text-purple-500 border-purple-500/20'
              : 'bg-indigo-500/10 text-indigo-500 border-indigo-500/20'
          }`}>
            {isPayroll ? (
              <DollarSign className="w-4 h-4" />
            ) : isOffer ? (
              <Award className="w-4 h-4" />
            ) : isLeave ? (
              <Calendar className="w-4 h-4" />
            ) : (
              <FileText className="w-4 h-4" />
            )}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-xs font-bold text-text-primary">
                {isPayroll
                  ? artifact.title
                  : isOffer
                  ? artifact.title
                  : isLeave
                  ? artifact.title
                  : content.role_title || artifact.title}
              </h3>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-surface border border-border text-text-muted">
                v{artifact.version}
              </span>
            </div>
            <p className="text-[10px] text-text-muted">
              {isPayroll
                ? 'Autonomous Payroll Engine • Pre-Disbursement Compliance Audit'
                : isOffer
                ? 'Compensation & Talent Intelligence • Employment Agreement'
                : isLeave
                ? 'People Operations • Coverage Risk & Leave Accrual'
                : `${content.department || 'Platform Engineering'} • Job Description Proposal`}
            </p>
          </div>
        </div>

        {/* Status Badge */}
        <div>
          {isApproved ? (
            <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" />
              <span>Approved</span>
            </span>
          ) : (
            <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase bg-amber-500/10 text-amber-500 border border-amber-500/20 flex items-center gap-1.5 animate-pulse">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
              <span>Draft • Awaiting Approval</span>
            </span>
          )}
        </div>
      </div>

      {/* 2. Structured Content Body */}
      {isExpanded && (
        <div className="p-4 space-y-3.5 text-xs">
          
          {/* A. PAYROLL BODY */}
          {isPayroll && (
            <div className="space-y-3">
              {/* 4 Metrics Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
                <div className="p-2.5 rounded-xl bg-surface-secondary/50 border border-border">
                  <span className="text-[9px] font-bold uppercase text-text-muted block">Gross Payroll</span>
                  <span className="text-xs font-bold text-text-primary">{content.gross_payroll}</span>
                </div>
                <div className="p-2.5 rounded-xl bg-emerald-500/5 border border-emerald-500/20">
                  <span className="text-[9px] font-bold uppercase text-emerald-500 block">Total Net Payout</span>
                  <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400">{content.total_net_payout}</span>
                </div>
                <div className="p-2.5 rounded-xl bg-surface-secondary/50 border border-border">
                  <span className="text-[9px] font-bold uppercase text-text-muted block">Tax Withholdings</span>
                  <span className="text-xs font-bold text-text-primary">{content.total_tax_withholdings}</span>
                </div>
                <div className="p-2.5 rounded-xl bg-surface-secondary/50 border border-border">
                  <span className="text-[9px] font-bold uppercase text-text-muted block">Benefits / Deductions</span>
                  <span className="text-xs font-bold text-text-primary">{content.benefits_deductions}</span>
                </div>
              </div>

              {/* Compliance Shield */}
              <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-500 shrink-0" />
                <span className="text-[11px] font-medium text-emerald-600 dark:text-emerald-400">
                  {content.compliance_status} ({content.employee_count} active employees verified)
                </span>
              </div>

              {/* Department Breakdown */}
              {content.department_breakdown && (
                <div className="space-y-1.5 pt-1">
                  <h4 className="text-[10px] font-bold uppercase tracking-wider text-text-muted">
                    Department Disbursement Breakdown
                  </h4>
                  <div className="grid grid-cols-2 gap-2">
                    {content.department_breakdown.map((d, dIdx) => (
                      <div key={dIdx} className="p-2 rounded-lg bg-surface-secondary/40 border border-border flex items-center justify-between text-[11px]">
                        <span className="text-text-secondary">{d.dept}</span>
                        <span className="font-mono font-bold text-text-primary">{d.amount}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* B. OFFER LETTER BODY */}
          {isOffer && (
            <div className="space-y-3">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
                <div className="p-2.5 rounded-xl bg-surface-secondary/50 border border-border">
                  <span className="text-[9px] font-bold uppercase text-text-muted block">Base Salary</span>
                  <span className="text-xs font-bold text-text-primary">{content.base_salary}</span>
                </div>
                <div className="p-2.5 rounded-xl bg-amber-500/5 border border-amber-500/20">
                  <span className="text-[9px] font-bold uppercase text-amber-500 block">Equity Grant</span>
                  <span className="text-[11px] font-bold text-amber-600 dark:text-amber-400">{content.equity}</span>
                </div>
                <div className="p-2.5 rounded-xl bg-surface-secondary/50 border border-border">
                  <span className="text-[9px] font-bold uppercase text-text-muted block">Sign-on Bonus</span>
                  <span className="text-xs font-bold text-text-primary">{content.signing_bonus}</span>
                </div>
                <div className="p-2.5 rounded-xl bg-surface-secondary/50 border border-border">
                  <span className="text-[9px] font-bold uppercase text-text-muted block">Target Start Date</span>
                  <span className="text-xs font-bold text-text-primary">{content.start_date}</span>
                </div>
              </div>

              {content.benefits && (
                <div className="space-y-1">
                  <h4 className="text-[10px] font-bold uppercase tracking-wider text-text-muted">Standard Executive Benefits</h4>
                  <p className="text-text-secondary leading-relaxed text-[11px]">{content.benefits}</p>
                </div>
              )}
            </div>
          )}

          {/* C. LEAVE EXCEPTION BODY */}
          {isLeave && (
            <div className="space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-[11px]">
                <div className="p-2.5 rounded-xl bg-surface-secondary/50 border border-border">
                  <span className="text-[9px] font-bold uppercase text-text-muted block">Employee & Department</span>
                  <span className="text-xs font-bold text-text-primary">{content.employee}</span>
                </div>
                <div className="p-2.5 rounded-xl bg-surface-secondary/50 border border-border">
                  <span className="text-[9px] font-bold uppercase text-text-muted block">Requested Window</span>
                  <span className="text-xs font-bold text-text-primary">{content.duration}</span>
                </div>
                <div className="p-2.5 rounded-xl bg-purple-500/5 border border-purple-500/20">
                  <span className="text-[9px] font-bold uppercase text-purple-500 block">Accrued Balance Post-Leave</span>
                  <span className="text-xs font-bold text-purple-600 dark:text-purple-400">{content.remaining_balance}</span>
                </div>
              </div>

              {content.coverage_risk && (
                <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-500 shrink-0" />
                  <span className="text-[11px] font-medium text-emerald-600 dark:text-emerald-400">
                    {content.coverage_risk}
                  </span>
                </div>
              )}
            </div>
          )}

          {/* D. JOB DESCRIPTION BODY (100% PRESERVED) */}
          {isJD && (
            <>
              {content.about_role && (
                <div className="space-y-1">
                  <h4 className="text-[11px] font-bold uppercase tracking-wider text-text-muted">About the Role</h4>
                  <p className="text-text-secondary leading-relaxed">{content.about_role}</p>
                </div>
              )}

              {content.responsibilities && content.responsibilities.length > 0 && (
                <div className="space-y-1.5">
                  <h4 className="text-[11px] font-bold uppercase tracking-wider text-text-muted">Key Responsibilities</h4>
                  <ul className="space-y-1 text-text-secondary">
                    {content.responsibilities.map((r: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-indigo-500 font-bold shrink-0">•</span>
                        <span className="leading-snug">{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {content.requirements && content.requirements.length > 0 && (
                <div className="space-y-1.5">
                  <h4 className="text-[11px] font-bold uppercase tracking-wider text-text-muted">Requirements</h4>
                  <ul className="space-y-1 text-text-secondary">
                    {content.requirements.map((req: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-emerald-500 font-bold shrink-0">•</span>
                        <span className="leading-snug">{req}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {content.nice_to_have && content.nice_to_have.length > 0 && (
                <div className="space-y-1.5">
                  <h4 className="text-[11px] font-bold uppercase tracking-wider text-text-muted">Nice to Have</h4>
                  <ul className="space-y-1 text-text-secondary">
                    {content.nice_to_have.map((nth: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-sky-400 font-bold shrink-0">•</span>
                        <span className="leading-snug">{nth}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 pt-2 border-t border-border/50 text-[11px]">
                <div className="p-2 rounded-lg bg-surface-secondary/40 border border-border">
                  <span className="text-[9px] font-bold uppercase text-text-muted block">Salary Range</span>
                  <span className="font-semibold text-text-primary">{content.salary_range || '$65,000 – $85,000'}</span>
                </div>
                <div className="p-2 rounded-lg bg-surface-secondary/40 border border-border">
                  <span className="text-[9px] font-bold uppercase text-text-muted block">Location</span>
                  <span className="font-semibold text-text-primary">{content.location || 'Remote / Hybrid'}</span>
                </div>
                <div className="p-2 rounded-lg bg-surface-secondary/40 border border-border col-span-2 sm:col-span-1">
                  <span className="text-[9px] font-bold uppercase text-text-muted block">Department</span>
                  <span className="font-semibold text-text-primary">{content.department || 'Platform Engineering'}</span>
                </div>
              </div>
            </>
          )}

        </div>
      )}

      {/* 3. Action Footer & Revision Composer */}
      <div className="p-3.5 bg-surface-secondary/40 border-t border-border">
        {isApproved ? (
          <div className="flex items-center gap-2 text-emerald-500 font-semibold text-xs py-1">
            <CheckCircle2 className="w-4 h-4" />
            <span>
              {isPayroll
                ? 'Payroll batch approved ✓ Direct deposit execution dispatched to partner bank.'
                : isOffer
                ? 'Offer approved ✓ Electronic agreement dispatched to candidate via DocuSign.'
                : isLeave
                ? 'Leave request approved ✓ Calendar updated and sprint on-call synchronized.'
                : 'JD approved ✓ Continuing with requisition pipeline...'}
            </span>
          </div>
        ) : isEditing ? (
          <form onSubmit={handleReviseSubmit} className="space-y-2.5">
            <label className="text-[11px] font-bold text-text-primary block">
              {isPayroll
                ? 'What adjustments would you like made to this payroll batch?'
                : isOffer
                ? 'What compensation terms would you like to revise?'
                : isLeave
                ? 'What feedback or condition would you like to attach?'
                : 'What would you like me to change in this draft?'}
            </label>
            <textarea
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              placeholder={
                isPayroll
                  ? 'e.g. Include additional overtime hours for platform on-call...'
                  : isOffer
                  ? 'e.g. Increase base salary to $155k and adjust equity to 0.35%...'
                  : isLeave
                  ? 'e.g. Approved conditionally pending handover document...'
                  : 'e.g. Make it more focused on backend engineering and remove the degree requirement...'
              }
              rows={2}
              className="w-full p-2.5 rounded-xl bg-surface border border-border text-xs text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-accent"
              autoFocus
            />
            <div className="flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={() => setIsEditing(false)}
                disabled={submitting}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold text-text-secondary hover:text-text-primary border border-border transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting || !feedbackText.trim()}
                className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-accent hover:opacity-90 disabled:opacity-50 text-xs font-bold text-white transition shadow-xs"
              >
                <Send className="w-3.5 h-3.5" />
                <span>{submitting ? 'Updating...' : 'Submit Changes'}</span>
              </button>
            </div>
          </form>
        ) : (
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <span className="text-[11px] font-medium text-text-muted">
              {isPayroll
                ? 'Please review gross-to-net audit totals before authorizing payout.'
                : isOffer
                ? 'Please review proposed compensation package before issuing offer.'
                : isLeave
                ? 'Please review coverage assessment before authorizing leave exception.'
                : 'Please review the draft above before we continue.'}
            </span>
            <div className="flex items-center gap-2 shrink-0">
              <button
                type="button"
                onClick={() => setIsEditing(true)}
                disabled={submitting || !workflowId}
                className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-surface hover:bg-surface-secondary text-xs font-semibold text-text-secondary border border-border transition shadow-2xs"
              >
                <Edit3 className="w-3.5 h-3.5" />
                <span>Request Changes</span>
              </button>

              <button
                type="button"
                onClick={handleApproveClick}
                disabled={submitting || !workflowId}
                className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-xs font-bold text-white transition shadow-xs"
              >
                <Check className="w-3.5 h-3.5" />
                <span>
                  {submitting
                    ? 'Processing...'
                    : isPayroll
                    ? 'Approve & Disburse'
                    : isOffer
                    ? 'Approve & Send Offer'
                    : isLeave
                    ? 'Approve Leave'
                    : 'Approve'}
                </span>
              </button>
            </div>
          </div>
        )}
      </div>

    </div>
  );
};
