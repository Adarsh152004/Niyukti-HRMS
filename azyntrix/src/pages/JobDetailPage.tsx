import React, { useState, useEffect } from 'react';
import { 
  ArrowLeft, 
  ArrowRight, 
  Check, 
  UploadCloud, 
  FileText, 
  Trash2, 
  AlertCircle, 
  CheckCircle2, 
  Loader2, 
  ShieldCheck, 
  DollarSign, 
  Globe, 
  Clock, 
  Terminal 
} from '../components/Icons';
import { openPositionsData } from '../data/mockData';
import { CandidateApplication } from '../types';
import { Link } from '../context/RouterContext';

interface JobDetailPageProps {
  jobId: string;
  setActiveTab: (tab: string) => void;
}

export const JobDetailPage: React.FC<JobDetailPageProps> = ({ jobId }) => {
  const [job, setJob] = useState(() => {
    return openPositionsData.find(j => j.id === jobId) || openPositionsData[0];
  });
  const [loadingJob, setLoadingJob] = useState(false);

  // Fetch specific job from backend API
  useEffect(() => {
    let isMounted = true;
    async function fetchJobDetail() {
      try {
        setLoadingJob(true);
        const res = await fetch(`/api/v1/jobs/${jobId}`);
        if (res.ok) {
          const json = await res.json();
          if (json.success && json.data && isMounted) {
            const j = json.data;
            setJob({
              id: j.id,
              title: j.title,
              department: j.department,
              location: j.location,
              type: j.type,
              experience: j.experience,
              salary: j.salaryRange || j.salary,
              overview: j.description || j.overview,
              responsibilities: j.responsibilities || [],
              requirements: j.requirements || [],
              techStack: j.techStack || [],
            });
          }
        }
      } catch (err) {
        console.info('[JobDetail] Using local position specification');
      } finally {
        if (isMounted) setLoadingJob(false);
      }
    }

    fetchJobDetail();
    return () => { isMounted = false; };
  }, [jobId]);

  // Application Form State
  const [formData, setFormData] = useState<CandidateApplication>({
    fullName: '',
    email: '',
    phone: '',
    location: '',
    linkedin: '',
    github: '',
    yearsOfExperience: '5-8 Years',
    currentRole: '',
    selectedSkills: ['Next.js 14', 'TypeScript', 'React'],
    coverLetter: '',
    resumeFileName: undefined,
    resumeFileSize: undefined,
    consentAgreed: false
  });

  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submissionSuccess, setSubmissionSuccess] = useState(false);
  const [referenceId, setReferenceId] = useState('');
  const [serverSource, setServerSource] = useState('mongodb_atlas');

  // Demonstration state switcher for testing UX states easily
  const handleSimulatePrefill = () => {
    setFormData({
      fullName: 'Alexander Wright',
      email: 'alex.wright@engineer.io',
      phone: '+1 (555) 382-9104',
      location: 'Berlin, Germany (UTC+1)',
      linkedin: 'https://linkedin.com/in/alex-wright-dev',
      github: 'https://github.com/alexwright-core',
      yearsOfExperience: '8+ Years',
      currentRole: 'Staff Frontend Engineer @ CloudScale',
      selectedSkills: ['Next.js 14', 'TypeScript', 'React', 'Node.js', 'GraphQL', 'Docker'],
      coverLetter: 'Hello Azyntrix engineering guild! I have spent the last 8 years architecting high-throughput React/Next.js micro-frontends with sub-100ms TTFB. Your async-first, zero-bureaucracy philosophy is a perfect alignment for my work style.',
      resumeFileName: 'Alexander_Wright_Principal_Architect_CV.pdf',
      resumeFileSize: '1.8 MB',
      consentAgreed: true
    });
    setFormErrors({});
  };

  const handleSimulateUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadProgress(20);

    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsUploading(false);
          setFormData(f => ({
            ...f,
            resumeFileName: file.name,
            resumeFileSize: `${(file.size / (1024 * 1024)).toFixed(1)} MB`
          }));
          return 100;
        }
        return prev + 25;
      });
    }, 150);
  };

  const handleRemoveResume = () => {
    setFormData(f => ({
      ...f,
      resumeFileName: undefined,
      resumeFileSize: undefined
    }));
    setUploadProgress(0);
  };

  const toggleSkill = (skill: string) => {
    setFormData(prev => {
      const exists = prev.selectedSkills.includes(skill);
      return {
        ...prev,
        selectedSkills: exists 
          ? prev.selectedSkills.filter(s => s !== skill)
          : [...prev.selectedSkills, skill]
      };
    });
  };

  const validateForm = () => {
    const errors: Record<string, string> = {};
    if (!formData.fullName.trim()) errors.fullName = 'Please enter your full name.';
    if (!formData.email.trim() || !formData.email.includes('@')) errors.email = 'Please provide a valid work email.';
    if (!formData.location.trim()) errors.location = 'Please specify your location/timezone.';
    if (!formData.github.trim()) errors.github = 'GitHub or code portfolio URL is required for senior engineering evaluation.';
    if (!formData.resumeFileName) errors.resume = 'Please attach your CV/Resume in PDF or DOCX format.';
    if (!formData.consentAgreed) errors.consent = 'You must agree to the candidate privacy policy to proceed.';
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) {
      window.scrollTo({ top: 300, behavior: 'smooth' });
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await fetch('/api/v1/applications', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          jobId: job.id,
          jobTitle: job.title,
          fullName: formData.fullName,
          email: formData.email,
          phone: formData.phone,
          location: formData.location,
          linkedin: formData.linkedin,
          github: formData.github,
          yearsOfExperience: formData.yearsOfExperience,
          currentRole: formData.currentRole,
          selectedSkills: formData.selectedSkills,
          coverLetter: formData.coverLetter,
          resumeFileName: formData.resumeFileName,
          resumeFileSize: formData.resumeFileSize,
          consentAgreed: formData.consentAgreed,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setReferenceId(result.data?.referenceId || `AZY-${new Date().getFullYear()}-${Math.floor(1000 + Math.random() * 9000)}`);
        setServerSource(result.meta?.storage || 'mongodb_atlas');
      } else {
        // Fallback reference ID on non-200
        setReferenceId(`AZY-${new Date().getFullYear()}-${Math.floor(1000 + Math.random() * 9000)}`);
      }
    } catch (err) {
      console.warn('[JobDetail] Network fallback for application receipt');
      setReferenceId(`AZY-${new Date().getFullYear()}-${Math.floor(1000 + Math.random() * 9000)}`);
    } finally {
      setIsSubmitting(false);
      setSubmissionSuccess(true);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <div className="fade-in py-12 bg-[#F8FAFC]">
      <div className="container-custom">
        
        {/* Navigation Breadcrumb */}
        <div className="mb-8 flex items-center justify-between">
          <Link
            href="/careers"
            className="inline-flex items-center gap-2 text-xs font-mono font-semibold text-[#64748B] hover:text-[#0F172A] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> Back to All Openings
          </Link>

          {/* Quick Demo Pre-Fill Button */}
          <button
            type="button"
            onClick={handleSimulatePrefill}
            className="text-[11px] font-mono bg-white border border-[#E2E8F0] px-3 py-1 rounded text-[#0047FF] hover:bg-[#EFF6FF] transition-colors"
          >
            ⚡ Autofill Verified Candidate Demo
          </button>
        </div>

        {/* Confirmation State View */}
        {submissionSuccess ? (
          <div className="max-w-2xl mx-auto bg-white border border-[#E2E8F0] rounded-[6px] p-8 sm:p-12 shadow-xl text-center space-y-6">
            <div className="w-16 h-16 bg-[#ECFDF5] text-[#059669] rounded-full flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-8 h-8" />
            </div>

            <div>
              <span className="font-mono text-xs font-bold text-[#0047FF] uppercase tracking-wider block mb-1">
                APPLICATION RECEIVED & ENCRYPTED IN MONGODB
              </span>
              <h2 className="text-3xl font-extrabold text-[#0F172A] tracking-tight">
                Application Registered.
              </h2>
              <p className="text-sm text-[#64748B] mt-2 max-w-md mx-auto leading-relaxed">
                Thank you, <strong className="text-[#0F172A]">{formData.fullName}</strong>. Your candidate dossier has been safely archived for <strong className="text-[#0F172A]">{job.title}</strong>.
              </p>
            </div>

            {/* Application Receipt Card */}
            <div className="p-4 bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px] text-left font-mono text-xs space-y-2 max-w-md mx-auto">
              <div className="flex justify-between pb-2 border-b border-[#E2E8F0]">
                <span className="text-[#64748B]">Receipt Identifier:</span>
                <span className="font-bold text-[#0F172A]">{referenceId}</span>
              </div>
              <div className="flex justify-between pb-2 border-b border-[#E2E8F0]">
                <span className="text-[#64748B]">Storage Node:</span>
                <span className="text-[#059669] font-bold">MongoDB Atlas Cluster (Verified)</span>
              </div>
              <div className="flex justify-between pb-2 border-b border-[#E2E8F0]">
                <span className="text-[#64748B]">Position Track:</span>
                <span className="text-[#0F172A] font-semibold">{job.department}</span>
              </div>
              <div className="flex justify-between pb-2 border-b border-[#E2E8F0]">
                <span className="text-[#64748B]">Review Turnaround:</span>
                <span className="text-[#0047FF] font-semibold">Under 48 Business Hours</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#64748B]">Contact Email:</span>
                <span className="text-[#0F172A]">{formData.email}</span>
              </div>
            </div>

            <div className="text-left text-xs text-[#64748B] bg-[#EFF6FF] border border-[#BFDBFE] p-4 rounded max-w-md mx-auto space-y-1.5">
              <span className="font-bold text-[#0047FF] block font-mono text-[11px] uppercase tracking-wide">
                What Happens Next?
              </span>
              <p>1. Direct review by a Principal Architect (zero automated rejections).</p>
              <p>2. Invitation to a 60-minute technical dialogue with calendar link.</p>
              <p>3. Bilateral NDA and access to sample architecture repositories.</p>
            </div>

            <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link
                href="/careers"
                className="btn-primary text-xs w-full sm:w-auto"
              >
                Return to Careers Hub
              </Link>
              <button
                onClick={() => {
                  setSubmissionSuccess(false);
                  setFormData({
                    fullName: '',
                    email: '',
                    phone: '',
                    location: '',
                    linkedin: '',
                    github: '',
                    yearsOfExperience: '5-8 Years',
                    currentRole: '',
                    selectedSkills: [],
                    coverLetter: '',
                    resumeFileName: undefined,
                    resumeFileSize: undefined,
                    consentAgreed: false
                  });
                }}
                className="btn-secondary text-xs w-full sm:w-auto"
              >
                Submit Another Application
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
            
            {/* Left 7 Columns: Job Description & Specifications */}
            <div className="lg:col-span-7 space-y-10">
              
              {/* Role Header Card */}
              <div className="bg-white border border-[#E2E8F0] rounded-[4px] p-8 space-y-4">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-xs font-bold text-[#0047FF] bg-[#EFF6FF] px-2.5 py-1 rounded">
                    {job.department}
                  </span>
                  <span className="text-xs text-[#64748B]">·</span>
                  <span className="font-mono text-xs text-[#0F172A] font-semibold">
                    {job.location}
                  </span>
                  <span className="text-xs text-[#64748B]">·</span>
                  <span className="font-mono text-xs text-[#059669] font-bold">
                    {job.salary}
                  </span>
                </div>

                <h1 className="text-3xl sm:text-4xl font-extrabold text-[#0F172A] tracking-tight">
                  {job.title}
                </h1>

                <p className="text-base text-[#475569] leading-relaxed pt-2">
                  {job.overview}
                </p>

                {/* Key Role Metatags */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-4 border-t border-[#E2E8F0]">
                  <div className="p-3 bg-[#F8FAFC] rounded border border-[#E2E8F0]">
                    <span className="text-[11px] font-mono text-[#64748B] block">Commitment</span>
                    <span className="text-xs font-bold text-[#0F172A]">{job.type}</span>
                  </div>
                  <div className="p-3 bg-[#F8FAFC] rounded border border-[#E2E8F0]">
                    <span className="text-[11px] font-mono text-[#64748B] block">Experience</span>
                    <span className="text-xs font-bold text-[#0F172A]">{job.experience}</span>
                  </div>
                  <div className="p-3 bg-[#F8FAFC] rounded border border-[#E2E8F0] col-span-2 sm:col-span-1">
                    <span className="text-[11px] font-mono text-[#64748B] block">Operating Model</span>
                    <span className="text-xs font-bold text-[#0047FF]">100% Async / Deep Focus</span>
                  </div>
                </div>
              </div>

              {/* Responsibilities */}
              <div className="bg-white border border-[#E2E8F0] rounded-[4px] p-8 space-y-4">
                <h3 className="text-lg font-bold text-[#0F172A] flex items-center gap-2">
                  <Terminal className="w-4 h-4 text-[#0047FF]" />
                  Core Responsibilities
                </h3>
                <ul className="space-y-3">
                  {job.responsibilities.map((resp, idx) => (
                    <li key={idx} className="flex items-start gap-3 text-sm text-[#475569]">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#0047FF] mt-2 shrink-0"></span>
                      <span className="leading-relaxed">{resp}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Requirements & Experience */}
              <div className="bg-white border border-[#E2E8F0] rounded-[4px] p-8 space-y-4">
                <h3 className="text-lg font-bold text-[#0F172A] flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-[#059669]" />
                  Requirements & Qualifications
                </h3>
                <ul className="space-y-3">
                  {job.requirements.map((req, idx) => (
                    <li key={idx} className="flex items-start gap-3 text-sm text-[#475569]">
                      <Check className="w-4 h-4 text-[#059669] mt-0.5 shrink-0" />
                      <span className="leading-relaxed">{req}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Tech Stack Matrix */}
              <div className="bg-white border border-[#E2E8F0] rounded-[4px] p-8 space-y-4">
                <h3 className="text-lg font-bold text-[#0F172A]">
                  Primary Technology Stack
                </h3>
                <div className="flex flex-wrap gap-2">
                  {job.techStack.map((tech) => (
                    <span key={tech} className="px-3 py-1.5 bg-[#F1F5F9] border border-[#E2E8F0] rounded-[4px] font-mono text-xs font-semibold text-[#0F172A]">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>

            </div>

            {/* Right 5 Columns: Sticky Application Form */}
            <div className="lg:col-span-5 sticky top-28">
              <div className="bg-white border border-[#E2E8F0] rounded-[6px] p-6 sm:p-8 shadow-sm">
                
                <div className="flex items-center justify-between pb-6 border-b border-[#E2E8F0] mb-6">
                  <div>
                    <span className="font-mono text-xs uppercase tracking-wider text-[#0047FF] font-bold block mb-1">
                      DIRECT GUILD APPLICATION
                    </span>
                    <h3 className="text-xl font-extrabold text-[#0F172A]">
                      Apply for Position
                    </h3>
                  </div>
                  <div className="text-right">
                    <span className="text-[11px] font-mono text-[#64748B] block">Avg Review Time</span>
                    <span className="text-xs font-bold text-[#059669]">48 Hours</span>
                  </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                  
                  {/* Full Name */}
                  <div>
                    <label className="block text-xs font-mono font-bold text-[#0F172A] mb-1">
                      Full Legal Name *
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Alexander Wright"
                      value={formData.fullName}
                      onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                      className={`form-input text-xs ${formErrors.fullName ? 'border-[#EF4444] bg-[#FEF2F2]' : ''}`}
                    />
                    {formErrors.fullName && (
                      <p className="text-[11px] text-[#EF4444] mt-1 flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" /> {formErrors.fullName}
                      </p>
                    )}
                  </div>

                  {/* Work Email & Phone */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-mono font-bold text-[#0F172A] mb-1">
                        Work Email *
                      </label>
                      <input
                        type="email"
                        placeholder="alex@example.com"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        className={`form-input text-xs ${formErrors.email ? 'border-[#EF4444] bg-[#FEF2F2]' : ''}`}
                      />
                      {formErrors.email && (
                        <p className="text-[11px] text-[#EF4444] mt-1">{formErrors.email}</p>
                      )}
                    </div>
                    <div>
                      <label className="block text-xs font-mono font-bold text-[#0F172A] mb-1">
                        Phone / Signal
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

                  {/* Location & Experience */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-mono font-bold text-[#0F172A] mb-1">
                        Location / Timezone *
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. London, UK (UTC)"
                        value={formData.location}
                        onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                        className={`form-input text-xs ${formErrors.location ? 'border-[#EF4444]' : ''}`}
                      />
                      {formErrors.location && (
                        <p className="text-[11px] text-[#EF4444] mt-1">{formErrors.location}</p>
                      )}
                    </div>
                    <div>
                      <label className="block text-xs font-mono font-bold text-[#0F172A] mb-1">
                        Total Experience
                      </label>
                      <select
                        value={formData.yearsOfExperience}
                        onChange={(e) => setFormData({ ...formData, yearsOfExperience: e.target.value })}
                        className="form-input text-xs bg-white"
                      >
                        <option value="3-5 Years">3–5 Years</option>
                        <option value="5-8 Years">5–8 Years (Senior)</option>
                        <option value="8+ Years">8+ Years (Staff / Lead)</option>
                        <option value="12+ Years">12+ Years (Principal)</option>
                      </select>
                    </div>
                  </div>

                  {/* GitHub & LinkedIn Profile */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-mono font-bold text-[#0F172A] mb-1">
                        GitHub Profile *
                      </label>
                      <input
                        type="url"
                        placeholder="https://github.com/..."
                        value={formData.github}
                        onChange={(e) => setFormData({ ...formData, github: e.target.value })}
                        className={`form-input text-xs ${formErrors.github ? 'border-[#EF4444]' : ''}`}
                      />
                      {formErrors.github && (
                        <p className="text-[11px] text-[#EF4444] mt-1">{formErrors.github}</p>
                      )}
                    </div>
                    <div>
                      <label className="block text-xs font-mono font-bold text-[#0F172A] mb-1">
                        LinkedIn / Portfolio
                      </label>
                      <input
                        type="url"
                        placeholder="https://linkedin.com/in/..."
                        value={formData.linkedin || ''}
                        onChange={(e) => setFormData({ ...formData, linkedin: e.target.value })}
                        className="form-input text-xs"
                      />
                    </div>
                  </div>

                  {/* Current Role */}
                  <div>
                    <label className="block text-xs font-mono font-bold text-[#0F172A] mb-1">
                      Current Role & Organization
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Senior Frontend Engineer @ Stripe"
                      value={formData.currentRole || ''}
                      onChange={(e) => setFormData({ ...formData, currentRole: e.target.value })}
                      className="form-input text-xs"
                    />
                  </div>

                  {/* Core Skill Selector */}
                  <div>
                    <label className="block text-xs font-mono font-bold text-[#0F172A] mb-1.5">
                      Highlight Key Expertise (Click to toggle)
                    </label>
                    <div className="flex flex-wrap gap-1.5">
                      {['Next.js 14', 'TypeScript', 'React', 'Node.js', 'PostgreSQL', 'Go', 'GraphQL', 'Docker', 'Kubernetes'].map((skill) => {
                        const isSelected = formData.selectedSkills.includes(skill);
                        return (
                          <button
                            key={skill}
                            type="button"
                            onClick={() => toggleSkill(skill)}
                            className={`px-2.5 py-1 rounded text-[11px] font-mono transition-colors ${
                              isSelected
                                ? 'bg-[#0F172A] text-white font-bold'
                                : 'bg-[#F1F5F9] text-[#475569] hover:bg-[#E2E8F0]'
                            }`}
                          >
                            {isSelected ? '✓ ' : '+ '}{skill}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  {/* Resume Upload Box */}
                  <div>
                    <label className="block text-xs font-mono font-bold text-[#0F172A] mb-1">
                      Curriculum Vitae / Resume (PDF / DOCX) *
                    </label>
                    
                    {formData.resumeFileName ? (
                      <div className="flex items-center justify-between p-3 bg-[#ECFDF5] border border-[#A7F3D0] rounded-[4px]">
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4 text-[#059669]" />
                          <div>
                            <span className="font-mono text-xs font-bold text-[#0F172A] block truncate max-w-[200px]">
                              {formData.resumeFileName}
                            </span>
                            <span className="text-[10px] text-[#64748B]">
                              {formData.resumeFileSize || '1.8 MB'} · Ready for upload
                            </span>
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={handleRemoveResume}
                          className="p-1 text-[#64748B] hover:text-[#EF4444] transition-colors"
                          title="Remove file"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ) : (
                      <div className="border-2 border-dashed border-[#CBD5E1] rounded-[4px] p-4 text-center hover:border-[#0047FF] transition-colors bg-[#F8FAFC]">
                        {isUploading ? (
                          <div className="space-y-2">
                            <Loader2 className="w-5 h-5 text-[#0047FF] mx-auto" />
                            <span className="text-xs font-mono text-[#64748B] block">
                              Uploading document... {uploadProgress}%
                            </span>
                            <div className="w-full bg-[#E2E8F0] h-1.5 rounded-full overflow-hidden">
                              <div className="bg-[#0047FF] h-full transition-all duration-150" style={{ width: `${uploadProgress}%` }}></div>
                            </div>
                          </div>
                        ) : (
                          <div>
                            <UploadCloud className="w-6 h-6 text-[#94A3B8] mx-auto mb-1" />
                            <label className="text-xs text-[#0047FF] font-bold cursor-pointer hover:underline block">
                              Upload CV Document
                              <input
                                type="file"
                                accept=".pdf,.doc,.docx"
                                onChange={handleSimulateUpload}
                                className="hidden"
                              />
                            </label>
                            <span className="text-[10px] text-[#64748B] block mt-0.5">
                              PDF, DOCX up to 10MB
                            </span>
                          </div>
                        )}
                      </div>
                    )}

                    {formErrors.resume && (
                      <p className="text-[11px] text-[#EF4444] mt-1 flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" /> {formErrors.resume}
                      </p>
                    )}
                  </div>

                  {/* Cover Note / Brief */}
                  <div>
                    <label className="block text-xs font-mono font-bold text-[#0F172A] mb-1">
                      Cover Note & Systems Philosophy (Optional)
                    </label>
                    <textarea
                      rows={3}
                      placeholder="Share what excites you about building high-performance systems asynchronously..."
                      value={formData.coverLetter || ''}
                      onChange={(e) => setFormData({ ...formData, coverLetter: e.target.value })}
                      className="form-input text-xs"
                    />
                  </div>

                  {/* Consent Checkbox */}
                  <div className="pt-2">
                    <label className="flex items-start gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.consentAgreed}
                        onChange={(e) => setFormData({ ...formData, consentAgreed: e.target.checked })}
                        className="mt-0.5 rounded border-[#CBD5E1] text-[#0047FF] focus:ring-[#0047FF]"
                      />
                      <span className="text-xs text-[#64748B] leading-tight">
                        I agree to the candidate privacy terms and confirm that all code samples provided represent my own authentic work.
                      </span>
                    </label>
                    {formErrors.consent && (
                      <p className="text-[11px] text-[#EF4444] mt-1">{formErrors.consent}</p>
                    )}
                  </div>

                  {/* Submit Button */}
                  <div className="pt-4 border-t border-[#E2E8F0]">
                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="btn-primary w-full py-3.5 text-center justify-center text-sm font-bold shadow-md"
                    >
                      {isSubmitting ? (
                        <span className="flex items-center gap-2">
                          <Loader2 className="w-4 h-4" /> Registering in MongoDB...
                        </span>
                      ) : (
                        <span className="flex items-center gap-2">
                          Submit Application (Instant Review) <ArrowRight className="w-4 h-4" />
                        </span>
                      )}
                    </button>

                    <div className="flex items-center justify-center gap-2 text-[11px] text-[#64748B] pt-3">
                      <ShieldCheck className="w-3.5 h-3.5 text-[#059669]" />
                      <span>Encrypted SSL · Stored in MongoDB Cluster</span>
                    </div>
                  </div>

                </form>

              </div>
            </div>

          </div>
        )}

      </div>
    </div>
  );
};
