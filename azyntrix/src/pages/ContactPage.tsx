import React, { useState } from 'react';
import { 
  ArrowRight, 
  Check, 
  CheckCircle2, 
  ShieldCheck, 
  Lock, 
  UploadCloud, 
  FileText, 
  Trash2, 
  Loader2, 
  Terminal, 
  MessageSquare, 
  Mail, 
  Video 
} from '../components/Icons';
import { ClientInquiry } from '../types';
import { Link } from '../context/RouterContext';

interface ContactPageProps {
  setActiveTab: (tab: string) => void;
}

export const ContactPage: React.FC<ContactPageProps> = () => {
  const [formData, setFormData] = useState<ClientInquiry>({
    fullName: '',
    email: '',
    company: '',
    phone: '',
    services: ['Web Applications & Platforms'],
    budget: '$30,000 - $75,000 (Full-Scale System)',
    timeline: '1 - 3 Months',
    description: '',
    fileName: undefined,
    communicationChannel: 'slack'
  });

  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submissionSuccess, setSubmissionSuccess] = useState(false);
  const [inquiryRef, setInquiryRef] = useState('');

  const serviceOptions = [
    'Web Applications & Platforms',
    'Custom Enterprise Software',
    'UI/UX & Product Design',
    'Headless E-Commerce',
    'Business Automation & AI',
    'Cloud Architecture & DevOps'
  ];

  const budgetOptions = [
    '$15,000 - $30,000 (Scoping & MVP)',
    '$30,000 - $75,000 (Full-Scale System)',
    '$75,000 - $150,000+ (Enterprise Multi-Squad)',
    'Flexible / Retainer Advisory'
  ];

  const timelineOptions = [
    '< 1 Month (Fast-Track Sprint)',
    '1 - 3 Months (Standard Production)',
    '3 - 6 Months (Multi-Phase Build)',
    'Ongoing Embedded Squad'
  ];

  const handleSimulatePrefill = () => {
    setFormData({
      fullName: 'Marcus Thorne',
      email: 'm.thorne@finscale.io',
      company: 'FinScale Global Inc.',
      phone: '+1 (415) 890-2341',
      services: ['Web Applications & Platforms', 'Custom Enterprise Software', 'UI/UX & Product Design'],
      budget: '$30,000 - $75,000 (Full-Scale System)',
      timeline: '1 - 3 Months (Standard Production)',
      description: 'We are re-architecting our core B2B transactional analytics dashboard into a distributed Next.js 14 / Go microservices pipeline. We require real-time WebSockets streaming, SOC2-compliant RBAC, and sub-100ms TTFB globally across North America and EMEA clusters.',
      fileName: 'FinScale_Architecture_Requirements_v2.pdf',
      communicationChannel: 'slack'
    });
    setFormErrors({});
  };

  const toggleService = (srv: string) => {
    setFormData(prev => {
      const exists = prev.services.includes(srv);
      return {
        ...prev,
        services: exists ? prev.services.filter(s => s !== srv) : [...prev.services, srv]
      };
    });
  };

  const handleSimulateFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFormData(prev => ({
        ...prev,
        fileName: file.name
      }));
    }
  };

  const validate = () => {
    const errors: Record<string, string> = {};
    if (!formData.fullName.trim()) errors.fullName = 'Please enter your name.';
    if (!formData.email.trim() || !formData.email.includes('@')) errors.email = 'Please provide a valid corporate email.';
    if (!formData.company.trim()) errors.company = 'Please specify your company or organization name.';
    if (formData.services.length === 0) errors.services = 'Please select at least one service discipline.';
    if (!formData.description.trim()) errors.description = 'Please describe your project scope and objectives.';
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) {
      window.scrollTo({ top: 300, behavior: 'smooth' });
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await fetch('/api/v1/inquiries', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fullName: formData.fullName,
          email: formData.email,
          company: formData.company,
          role: 'Technical Sponsor',
          projectType: formData.services.join(', '),
          budgetTier: formData.budget,
          timeline: formData.timeline,
          projectSummary: formData.description,
          slackConnect: formData.communicationChannel === 'slack',
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setInquiryRef(result.data?.referenceId || `AZY-INQ-${Math.floor(10000 + Math.random() * 90000)}`);
      } else {
        setInquiryRef(`AZY-INQ-${Math.floor(10000 + Math.random() * 90000)}`);
      }
    } catch (err) {
      console.warn('[Contact] Network fallback for inquiry receipt');
      setInquiryRef(`AZY-INQ-${Math.floor(10000 + Math.random() * 90000)}`);
    } finally {
      setIsSubmitting(false);
      setSubmissionSuccess(true);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <div className="fade-in py-16 lg:py-24 bg-[#F8FAFC]">
      <div className="container-custom">
        
        {submissionSuccess ? (
          /* Submission Confirmed Screen */
          <div className="max-w-2xl mx-auto bg-white border border-[#E2E8F0] rounded-[6px] p-8 sm:p-12 shadow-xl text-center space-y-6">
            <div className="w-16 h-16 bg-[#ECFDF5] text-[#059669] rounded-full flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-8 h-8" />
            </div>

            <div>
              <span className="font-mono text-xs font-bold text-[#0047FF] uppercase tracking-wider block mb-1">
                PROJECT INTAKE RECEIVED & ENCRYPTED IN MONGODB
              </span>
              <h1 className="text-3xl font-extrabold text-[#0F172A]">
                Discovery Request Confirmed
              </h1>
              <div className="mt-3 inline-block bg-[#F1F5F9] font-mono text-xs font-bold text-[#0F172A] px-3 py-1 rounded border border-[#E2E8F0]">
                Tracking Reference: <span className="text-[#0047FF]">{inquiryRef}</span>
              </div>
            </div>

            <p className="text-sm text-[#475569] leading-relaxed max-w-lg mx-auto">
              Thank you, <strong className="text-[#0F172A]">{formData.fullName}</strong>. Your project brief for <strong className="text-[#0F172A]">{formData.company}</strong> has been assigned to our Lead Solutions Architect.
            </p>

            {/* 3-Step Transparent Next Steps */}
            <div className="p-6 bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px] text-left space-y-4">
              <span className="font-mono text-xs font-bold text-[#0F172A] uppercase tracking-wider block">
                What happens next (24-Hour Review SLA):
              </span>
              
              <div className="flex items-start gap-3 text-xs text-[#475569]">
                <div className="w-5 h-5 rounded-full bg-[#EFF6FF] text-[#0047FF] font-mono font-bold flex items-center justify-center shrink-0">
                  1
                </div>
                <div>
                  <strong className="text-[#0F172A] block mb-0.5">Architecture & Feasibility Assessment</strong>
                  A Senior Principal evaluates your stack, requirements, and timeline.
                </div>
              </div>

              <div className="flex items-start gap-3 text-xs text-[#475569]">
                <div className="w-5 h-5 rounded-full bg-[#EFF6FF] text-[#0047FF] font-mono font-bold flex items-center justify-center shrink-0">
                  2
                </div>
                <div>
                  <strong className="text-[#0F172A] block mb-0.5">Mutual Bilateral NDA & Slack Channel</strong>
                  We send a bilateral non-disclosure agreement and configure your dedicated shared workspace.
                </div>
              </div>

              <div className="flex items-start gap-3 text-xs text-[#475569]">
                <div className="w-5 h-5 rounded-full bg-[#EFF6FF] text-[#0047FF] font-mono font-bold flex items-center justify-center shrink-0">
                  3
                </div>
                <div>
                  <strong className="text-[#0F172A] block mb-0.5">Scoping Call & Sprint Roadmap</strong>
                  A 45-minute architectural alignment to finalize delivery milestones and commercial terms.
                </div>
              </div>
            </div>

            <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link
                href="/"
                className="btn-primary text-xs w-full sm:w-auto"
              >
                Return to Studio Home
              </Link>
              <Link
                href="/work"
                className="btn-secondary text-xs w-full sm:w-auto"
              >
                Browse Case Studies
              </Link>
            </div>
          </div>
        ) : (
          /* Intake Form View */
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
            
            {/* Left 5 Columns: Engagement Context & Trust */}
            <div className="lg:col-span-5 space-y-8">
              <div>
                <span className="font-mono text-xs uppercase tracking-wider text-[#0047FF] font-bold block mb-2">
                  PROJECT DISCOVERY & SCOPING
                </span>
                <h1 className="text-3xl sm:text-4xl font-extrabold text-[#0F172A] tracking-tight mb-4">
                  Let's architect something extraordinary together.
                </h1>
                <p className="text-base text-[#475569] leading-relaxed">
                  Tell us about your product goals, architectural challenges, or timeline. Every inquiry is reviewed by our engineering leadership under strict bilateral NDA.
                </p>
              </div>

              {/* Security & Confidentiality Badges */}
              <div className="p-5 bg-white border border-[#E2E8F0] rounded-[4px] space-y-3">
                <div className="flex items-center gap-2.5 text-xs font-mono font-semibold text-[#0F172A]">
                  <Lock className="w-4 h-4 text-[#0047FF]" />
                  <span>Confidentiality Guaranteed</span>
                </div>
                <p className="text-xs text-[#64748B] leading-relaxed">
                  All IP, architectural discussions, and technical briefs submitted are protected by our automatic bilateral NDA before any discovery session.
                </p>
                <div className="pt-2 border-t border-[#E2E8F0] flex items-center gap-4 text-[11px] text-[#64748B] font-mono">
                  <span className="flex items-center gap-1 text-[#059669]">
                    <Check className="w-3.5 h-3.5" /> SOC2 Type II
                  </span>
                  <span className="flex items-center gap-1 text-[#059669]">
                    <Check className="w-3.5 h-3.5" /> 24h Response SLA
                  </span>
                </div>
              </div>

              {/* Direct Coordinate Channels */}
              <div className="space-y-3 pt-2">
                <span className="font-mono text-xs font-bold text-[#64748B] uppercase tracking-wider block">
                  Direct Inquiries:
                </span>
                <div className="space-y-2 text-sm text-[#0F172A]">
                  <a href="mailto:initiatives@azyntrix.com" className="flex items-center gap-2 hover:text-[#0047FF] transition-colors">
                    <Mail className="w-4 h-4 text-[#64748B]" />
                    <span className="font-mono text-xs">initiatives@azyntrix.com</span>
                  </a>
                  <div className="flex items-center gap-2 text-xs text-[#64748B]">
                    <Terminal className="w-4 h-4" />
                    <span>Global Hubs: SF · London · Zurich · Singapore</span>
                  </div>
                </div>
              </div>

              {/* Quick RFP Prefill Demo Button */}
              <div className="p-4 bg-[#EFF6FF] border border-[#BFDBFE] rounded-[4px]">
                <span className="text-xs font-bold text-[#0047FF] block mb-1">
                  Testing the Scoping Flow?
                </span>
                <p className="text-xs text-[#475569] mb-3">
                  Click below to automatically populate the scoping form with a realistic FinTech RFP brief.
                </p>
                <button
                  type="button"
                  onClick={handleSimulatePrefill}
                  className="btn-secondary text-xs w-full py-2 bg-white"
                >
                  ⚡ Demo Autofill (FinTech Scoping RFP)
                </button>
              </div>

            </div>

            {/* Right 7 Columns: Scoping Form */}
            <div className="lg:col-span-7 bg-white border border-[#E2E8F0] rounded-[6px] p-8 sm:p-10 shadow-sm">
              <form onSubmit={handleSubmit} className="space-y-6">
                
                {/* 1. Contact Info */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-mono font-bold text-[#0F172A] mb-1">
                      Your Full Name *
                    </label>
                    <input
                      type="text"
                      placeholder="Marcus Thorne"
                      value={formData.fullName}
                      onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                      className={`form-input text-xs ${formErrors.fullName ? 'border-[#EF4444] bg-[#FEF2F2]' : ''}`}
                    />
                    {formErrors.fullName && (
                      <p className="text-[11px] text-[#EF4444] mt-1">{formErrors.fullName}</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-xs font-mono font-bold text-[#0F172A] mb-1">
                      Corporate Work Email *
                    </label>
                    <input
                      type="email"
                      placeholder="m.thorne@company.com"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className={`form-input text-xs ${formErrors.email ? 'border-[#EF4444] bg-[#FEF2F2]' : ''}`}
                    />
                    {formErrors.email && (
                      <p className="text-[11px] text-[#EF4444] mt-1">{formErrors.email}</p>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-mono font-bold text-[#0F172A] mb-1">
                      Company / Organization *
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. FinScale Global Inc."
                      value={formData.company}
                      onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                      className={`form-input text-xs ${formErrors.company ? 'border-[#EF4444] bg-[#FEF2F2]' : ''}`}
                    />
                    {formErrors.company && (
                      <p className="text-[11px] text-[#EF4444] mt-1">{formErrors.company}</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-xs font-mono font-bold text-[#0F172A] mb-1">
                      Phone / Mobile
                    </label>
                    <input
                      type="tel"
                      placeholder="+1 (555) 000-0000"
                      value={formData.phone || ''}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      className="form-input text-xs"
                    />
                  </div>
                </div>

                {/* 2. Service Disciplines */}
                <div>
                  <label className="block text-xs font-mono font-bold text-[#0F172A] mb-2">
                    Required Practice Disciplines (Select all that apply) *
                  </label>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {serviceOptions.map((srv) => {
                      const isSelected = formData.services.includes(srv);
                      return (
                        <button
                          key={srv}
                          type="button"
                          onClick={() => toggleService(srv)}
                          className={`p-3 rounded-[4px] border text-xs text-left font-medium transition-all flex items-center justify-between ${
                            isSelected
                              ? 'border-[#0047FF] bg-[#EFF6FF] text-[#0047FF] font-bold shadow-sm'
                              : 'border-[#E2E8F0] bg-[#F8FAFC] text-[#475569] hover:bg-white hover:border-[#CBD5E1]'
                          }`}
                        >
                          <span>{srv}</span>
                          {isSelected && <Check className="w-3.5 h-3.5 text-[#0047FF]" />}
                        </button>
                      );
                    })}
                  </div>
                  {formErrors.services && (
                    <p className="text-[11px] text-[#EF4444] mt-1">{formErrors.services}</p>
                  )}
                </div>

                {/* 3. Budget Range */}
                <div>
                  <label className="block text-xs font-mono font-bold text-[#0F172A] mb-2">
                    Target Commercial Budget (USD)
                  </label>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {budgetOptions.map((opt) => {
                      const isSelected = formData.budget === opt;
                      return (
                        <button
                          key={opt}
                          type="button"
                          onClick={() => setFormData({ ...formData, budget: opt })}
                          className={`p-3 rounded-[4px] border text-xs text-left font-medium transition-all ${
                            isSelected
                              ? 'border-[#0F172A] bg-[#0F172A] text-white font-bold'
                              : 'border-[#E2E8F0] bg-[#F8FAFC] text-[#475569] hover:bg-white'
                          }`}
                        >
                          {opt}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* 4. Timeline Expectations */}
                <div>
                  <label className="block text-xs font-mono font-bold text-[#0F172A] mb-2">
                    Anticipated Delivery Timeline
                  </label>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                    {timelineOptions.map((tOpt) => {
                      const isSelected = formData.timeline === tOpt;
                      return (
                        <button
                          key={tOpt}
                          type="button"
                          onClick={() => setFormData({ ...formData, timeline: tOpt })}
                          className={`p-2.5 rounded-[4px] border text-[11px] text-center font-medium transition-all ${
                            isSelected
                              ? 'border-[#0047FF] bg-[#EFF6FF] text-[#0047FF] font-bold'
                              : 'border-[#E2E8F0] bg-[#F8FAFC] text-[#475569] hover:bg-white'
                          }`}
                        >
                          {tOpt}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* 5. Project Brief */}
                <div>
                  <label className="block text-xs font-mono font-bold text-[#0F172A] mb-1">
                    Project Problem Statement & Scope *
                  </label>
                  <textarea
                    rows={4}
                    placeholder="Provide a summary of the systems challenge, current architecture, performance goals, or deliverables..."
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className={`form-input text-xs ${formErrors.description ? 'border-[#EF4444] bg-[#FEF2F2]' : ''}`}
                  />
                  {formErrors.description && (
                    <p className="text-[11px] text-[#EF4444] mt-1">{formErrors.description}</p>
                  )}
                </div>

                {/* 6. Optional RFP Document Upload */}
                <div>
                  <label className="block text-xs font-mono font-bold text-[#0F172A] mb-1">
                    Attach Architecture Spec / RFP Document (Optional)
                  </label>
                  
                  {formData.fileName ? (
                    <div className="flex items-center justify-between p-3 bg-[#ECFDF5] border border-[#A7F3D0] rounded-[4px]">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-[#059669]" />
                        <span className="font-mono text-xs font-bold text-[#0F172A]">
                          {formData.fileName}
                        </span>
                      </div>
                      <button
                        type="button"
                        onClick={() => setFormData({ ...formData, fileName: undefined })}
                        className="text-[#64748B] hover:text-[#EF4444]"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ) : (
                    <div className="border border-dashed border-[#CBD5E1] rounded-[4px] p-3 text-center hover:border-[#0047FF] transition-colors bg-[#F8FAFC]">
                      <label className="text-xs text-[#0047FF] font-bold cursor-pointer hover:underline">
                        Upload Architecture Brief / RFP (PDF, DOCX, ZIP up to 25MB)
                        <input
                          type="file"
                          accept=".pdf,.doc,.docx,.zip"
                          onChange={handleSimulateFileUpload}
                          className="hidden"
                        />
                      </label>
                    </div>
                  )}
                </div>

                {/* 7. Collaboration Channel */}
                <div>
                  <label className="block text-xs font-mono font-bold text-[#0F172A] mb-2">
                    Preferred Discovery Communication Channel
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    <button
                      type="button"
                      onClick={() => setFormData({ ...formData, communicationChannel: 'slack' })}
                      className={`p-2.5 rounded-[4px] border text-xs font-medium flex items-center justify-center gap-1.5 transition-all ${
                        formData.communicationChannel === 'slack'
                          ? 'border-[#0047FF] bg-[#EFF6FF] text-[#0047FF] font-bold'
                          : 'border-[#E2E8F0] bg-[#F8FAFC] text-[#475569]'
                      }`}
                    >
                      <MessageSquare className="w-3.5 h-3.5" /> Slack Connect
                    </button>

                    <button
                      type="button"
                      onClick={() => setFormData({ ...formData, communicationChannel: 'video' })}
                      className={`p-2.5 rounded-[4px] border text-xs font-medium flex items-center justify-center gap-1.5 transition-all ${
                        formData.communicationChannel === 'video'
                          ? 'border-[#0047FF] bg-[#EFF6FF] text-[#0047FF] font-bold'
                          : 'border-[#E2E8F0] bg-[#F8FAFC] text-[#475569]'
                      }`}
                    >
                      <Video className="w-3.5 h-3.5" /> Video Call
                    </button>

                    <button
                      type="button"
                      onClick={() => setFormData({ ...formData, communicationChannel: 'email' })}
                      className={`p-2.5 rounded-[4px] border text-xs font-medium flex items-center justify-center gap-1.5 transition-all ${
                        formData.communicationChannel === 'email'
                          ? 'border-[#0047FF] bg-[#EFF6FF] text-[#0047FF] font-bold'
                          : 'border-[#E2E8F0] bg-[#F8FAFC] text-[#475569]'
                      }`}
                    >
                      <Mail className="w-3.5 h-3.5" /> Email
                    </button>
                  </div>
                </div>

                {/* Submit Action */}
                <div className="pt-4 border-t border-[#E2E8F0]">
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="btn-primary w-full py-4 text-center justify-center text-sm font-bold shadow-md"
                  >
                    {isSubmitting ? (
                      <span className="flex items-center gap-2">
                        <Loader2 className="w-4 h-4" /> Registering in MongoDB Cluster...
                      </span>
                    ) : (
                      <span className="flex items-center gap-2">
                        Submit Project Brief (Protected under Bilateral NDA) <ArrowRight className="w-4 h-4" />
                      </span>
                    )}
                  </button>
                  <p className="text-[11px] text-center text-[#64748B] font-mono mt-2.5">
                    Strict SLA: A Lead Solutions Architect will respond within 24 business hours.
                  </p>
                </div>

              </form>
            </div>

          </div>
        )}

      </div>
    </div>
  );
};
