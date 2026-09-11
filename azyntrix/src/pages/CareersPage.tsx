import React, { useState, useEffect } from 'react';
import { ArrowRight, ArrowUpRight, Search, Check, Sparkles, Globe, DollarSign, Laptop, Heart, Plane, Calendar, ShieldCheck, Loader2 } from '../components/Icons';
import { openPositionsData } from '../data/mockData';
import { Link } from '../context/RouterContext';

interface CareersPageProps {
  setActiveTab: (tab: string) => void;
  onOpenJobDetail: (jobId: string) => void;
}

export const CareersPage: React.FC<CareersPageProps> = ({ onOpenJobDetail }) => {
  const [jobs, setJobs] = useState(openPositionsData);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState('all');

  // Fetch live jobs from Node.js / MongoDB Backend
  useEffect(() => {
    let isMounted = true;
    async function fetchLiveJobs() {
      try {
        setIsLoading(true);
        const res = await fetch('/api/v1/jobs');
        if (res.ok) {
          const json = await res.json();
          if (json.success && Array.isArray(json.data) && json.data.length > 0 && isMounted) {
            // Map backend schema to UI format seamlessly
            const formatted = json.data.map((j: any) => ({
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
              applicantCount: j.applicantCount || 0,
            }));
            setJobs(formatted);
          }
        }
      } catch (err) {
        console.info('[Azyntrix Careers] Using resilient mock data cache');
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }

    fetchLiveJobs();
    return () => { isMounted = false; };
  }, []);

  const departments = [
    { id: 'all', label: `All Departments (${jobs.length})` },
    { id: 'Frontend', label: `Frontend & Web (${jobs.filter(j => j.department === 'Frontend').length})` },
    { id: 'Backend', label: `Backend & Systems (${jobs.filter(j => j.department === 'Backend').length})` },
    { id: 'Cloud & DevOps', label: `Cloud & SRE (${jobs.filter(j => j.department === 'Cloud & DevOps').length})` },
    { id: 'Product & Design', label: `Product & Design (${jobs.filter(j => j.department === 'Product & Design').length})` }
  ];

  const filteredJobs = jobs.filter(job => {
    const matchesDept = selectedDepartment === 'all' || job.department === selectedDepartment;
    const matchesSearch = searchQuery === '' || 
      job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.techStack.some(t => t.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesDept && matchesSearch;
  });

  return (
    <div className="fade-in">
      
      {/* Careers Hero */}
      <section className="py-16 lg:py-24 bg-white border-b border-[#E2E8F0]">
        <div className="container-custom">
          <div className="max-w-3xl">
            <span className="font-mono text-xs uppercase tracking-wider text-[#0047FF] font-bold block mb-3">
              CAREERS // JOIN THE GUILD
            </span>
            <h1 className="text-4xl sm:text-5xl font-extrabold text-[#0F172A] tracking-tight mb-6 leading-tight">
              Build high-impact distributed systems from anywhere in the world.
            </h1>
            <p className="text-lg text-[#475569] leading-relaxed mb-8">
              We are looking for exceptional software engineers, distributed systems architects, and UI/UX craftsmen who thrive in deep-focus, asynchronous, zero-bureaucracy environments.
            </p>

            {/* Hiring Metrics Strip */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px]">
              <div>
                <span className="font-mono font-bold text-lg text-[#0F172A] block">100% Remote</span>
                <span className="text-[11px] text-[#64748B]">Worldwide Forever</span>
              </div>
              <div>
                <span className="font-mono font-bold text-lg text-[#0F172A] block">$3,500</span>
                <span className="text-[11px] text-[#64748B]">Home Studio Grant</span>
              </div>
              <div>
                <span className="font-mono font-bold text-lg text-[#0F172A] block">4-Day Weeks</span>
                <span className="text-[11px] text-[#64748B]">Focus Block Option</span>
              </div>
              <div>
                <span className="font-mono font-bold text-lg text-[#0F172A] block">$4,000 / yr</span>
                <span className="text-[11px] text-[#64748B]">Continuous Learning</span>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* 8-Card Perks Grid */}
      <section className="py-16 bg-[#F8FAFC] border-b border-[#E2E8F0]">
        <div className="container-custom">
          <span className="font-mono text-xs uppercase tracking-wider text-[#64748B] font-bold block mb-2">
            WHY WORK AT AZYNTRIX
          </span>
          <h2 className="text-2xl sm:text-3xl font-bold text-[#0F172A] mb-8">
            Engineered for builders, not bureaucrats.
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            
            <div className="p-6 bg-white border border-[#E2E8F0] rounded-[4px]">
              <div className="w-8 h-8 bg-[#EFF6FF] rounded flex items-center justify-center text-[#0047FF] mb-3">
                <DollarSign className="w-4 h-4" />
              </div>
              <h4 className="font-bold text-sm text-[#0F172A] mb-1">Equal Global Pay</h4>
              <p className="text-xs text-[#64748B] leading-relaxed">
                Top-tier USD compensation benchmarked to top tech hubs without regional penalties.
              </p>
            </div>

            <div className="p-6 bg-white border border-[#E2E8F0] rounded-[4px]">
              <div className="w-8 h-8 bg-[#EFF6FF] rounded flex items-center justify-center text-[#0047FF] mb-3">
                <Laptop className="w-4 h-4" />
              </div>
              <h4 className="font-bold text-sm text-[#0F172A] mb-1">Top-Spec Hardware</h4>
              <p className="text-xs text-[#64748B] leading-relaxed">
                Latest M3 Max MacBook Pro or Linux workstation refresh every 24 months.
              </p>
            </div>

            <div className="p-6 bg-white border border-[#E2E8F0] rounded-[4px]">
              <div className="w-8 h-8 bg-[#EFF6FF] rounded flex items-center justify-center text-[#0047FF] mb-3">
                <Globe className="w-4 h-4" />
              </div>
              <h4 className="font-bold text-sm text-[#0F172A] mb-1">Asynchronous Workflow</h4>
              <p className="text-xs text-[#64748B] leading-relaxed">
                Zero daily standup meetings. Written updates and autonomous ownership.
              </p>
            </div>

            <div className="p-6 bg-white border border-[#E2E8F0] rounded-[4px]">
              <div className="w-8 h-8 bg-[#EFF6FF] rounded flex items-center justify-center text-[#0047FF] mb-3">
                <Heart className="w-4 h-4" />
              </div>
              <h4 className="font-bold text-sm text-[#0F172A] mb-1">Comprehensive Health</h4>
              <p className="text-xs text-[#64748B] leading-relaxed">
                Premium international health, dental, and mental wellness coverage worldwide.
              </p>
            </div>

            <div className="p-6 bg-white border border-[#E2E8F0] rounded-[4px]">
              <div className="w-8 h-8 bg-[#EFF6FF] rounded flex items-center justify-center text-[#0047FF] mb-3">
                <Calendar className="w-4 h-4" />
              </div>
              <h4 className="font-bold text-sm text-[#0F172A] mb-1">Unlimited Flexible PTO</h4>
              <p className="text-xs text-[#64748B] leading-relaxed">
                Minimum 28 days required vacation per year with full recharge support.
              </p>
            </div>

            <div className="p-6 bg-white border border-[#E2E8F0] rounded-[4px]">
              <div className="w-8 h-8 bg-[#EFF6FF] rounded flex items-center justify-center text-[#0047FF] mb-3">
                <Plane className="w-4 h-4" />
              </div>
              <h4 className="font-bold text-sm text-[#0F172A] mb-1">Global Guild Offsites</h4>
              <p className="text-xs text-[#64748B] leading-relaxed">
                Bi-annual fully funded international engineering retreats (Lisbon, Tokyo, Zurich).
              </p>
            </div>

            <div className="p-6 bg-white border border-[#E2E8F0] rounded-[4px]">
              <div className="w-8 h-8 bg-[#EFF6FF] rounded flex items-center justify-center text-[#0047FF] mb-3">
                <Sparkles className="w-4 h-4" />
              </div>
              <h4 className="font-bold text-sm text-[#0F172A] mb-1">Open Source Fridays</h4>
              <p className="text-xs text-[#64748B] leading-relaxed">
                Dedicate 20% of your engineering time to contributing to foundational OSS tools.
              </p>
            </div>

            <div className="p-6 bg-white border border-[#E2E8F0] rounded-[4px]">
              <div className="w-8 h-8 bg-[#EFF6FF] rounded flex items-center justify-center text-[#0047FF] mb-3">
                <Check className="w-4 h-4" />
              </div>
              <h4 className="font-bold text-sm text-[#0F172A] mb-1">Transparent Equity</h4>
              <p className="text-xs text-[#64748B] leading-relaxed">
                Direct profit-sharing and guild token pool distributions on every engagement.
              </p>
            </div>

          </div>
        </div>
      </section>

      {/* Open Positions Grid with Live Database Hook */}
      <section className="py-20 bg-white border-b border-[#E2E8F0]">
        <div className="container-custom">
          
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="font-mono text-xs uppercase tracking-wider text-[#0047FF] font-bold">
                  ACTIVE OPENINGS
                </span>
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#ECFDF5] border border-[#A7F3D0] text-[10px] font-mono text-[#059669] font-bold">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse"></span>
                  LIVE MONGODB POOL
                </span>
              </div>
              <h2 className="text-3xl font-extrabold text-[#0F172A] tracking-tight">
                Current Guild Opportunities
              </h2>
            </div>
            
            {/* Search Input */}
            <div className="w-full md:w-80 relative">
              <input
                type="text"
                placeholder="Search stack (e.g. Next.js, Go)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="form-input text-xs pl-9 py-2.5"
              />
              <Search className="w-4 h-4 text-[#94A3B8] absolute left-3 top-3" />
            </div>
          </div>

          {/* Department Filter Pills */}
          <div className="flex flex-wrap gap-2 pb-8 mb-8 border-b border-[#E2E8F0]">
            {departments.map((dept) => (
              <button
                key={dept.id}
                onClick={() => setSelectedDepartment(dept.id)}
                className={`px-3.5 py-1.5 rounded-[4px] text-xs font-mono transition-colors ${
                  selectedDepartment === dept.id
                    ? 'bg-[#0F172A] text-white font-bold'
                    : 'bg-[#F8FAFC] border border-[#E2E8F0] text-[#475569] hover:text-[#0F172A]'
                }`}
              >
                {dept.label}
              </button>
            ))}
          </div>

          {/* Job Listings List */}
          <div className="space-y-4">
            {isLoading ? (
              <div className="text-center py-12 border border-[#E2E8F0] rounded-[4px] p-6 bg-[#F8FAFC] flex flex-col items-center justify-center gap-3">
                <Loader2 className="w-6 h-6 text-[#0047FF]" />
                <p className="text-xs font-mono text-[#64748B]">Syncing positions from MongoDB Atlas cluster...</p>
              </div>
            ) : filteredJobs.length === 0 ? (
              <div className="text-center py-12 border border-dashed border-[#E2E8F0] rounded-[4px] p-6">
                <p className="text-sm text-[#64748B]">No open positions matching your search filters.</p>
                <button 
                  onClick={() => { setSearchQuery(''); setSelectedDepartment('all'); }}
                  className="btn-secondary text-xs mt-3"
                >
                  Reset Filters
                </button>
              </div>
            ) : (
              filteredJobs.map((job) => (
                <div
                  key={job.id}
                  className="p-6 lg:p-8 bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px] hover:border-[#CBD5E1] transition-all flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 group"
                >
                  <div className="space-y-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-mono text-xs font-bold text-[#0047FF] bg-[#EFF6FF] px-2 py-0.5 rounded">
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

                    <h3 className="text-xl font-bold text-[#0F172A] group-hover:text-[#0047FF] transition-colors">
                      {job.title}
                    </h3>

                    <p className="text-sm text-[#475569] max-w-2xl leading-relaxed">
                      {job.overview}
                    </p>

                    <div className="flex flex-wrap gap-1.5 pt-2">
                      {job.techStack.map((tech) => (
                        <span key={tech} className="bg-white border border-[#E2E8F0] font-mono text-[11px] px-2 py-0.5 rounded text-[#334155]">
                          {tech}
                        </span>
                      ))}
                    </div>
                  </div>

                  <Link
                    href={`/careers/${job.id}`}
                    onClick={() => onOpenJobDetail(job.id)}
                    className="btn-primary whitespace-nowrap self-stretch lg:self-auto text-xs py-3 px-5 text-center justify-center"
                  >
                    View Role & Apply →
                  </Link>
                </div>
              ))
            )}
          </div>

        </div>
      </section>

      {/* Transparent 4-Stage Hiring Process */}
      <section className="py-20 bg-[#F8FAFC] border-b border-[#E2E8F0]">
        <div className="container-custom">
          <div className="max-w-3xl mb-12">
            <span className="font-mono text-xs uppercase tracking-wider text-[#64748B] font-bold block mb-2">
              HIRING TRANSPARENCY
            </span>
            <h2 className="text-3xl font-bold text-[#0F172A] tracking-tight mb-4">
              A humane, peer-to-peer technical evaluation.
            </h2>
            <p className="text-[#64748B] text-base leading-relaxed">
              We respect your time. No generic algorithmic LeetCode puzzles, no take-home tests longer than 90 minutes, and every application is reviewed by senior engineering staff.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            
            <div className="p-6 bg-white border border-[#E2E8F0] rounded-[4px] relative">
              <span className="font-mono font-bold text-3xl text-[#E2E8F0] block mb-4">01</span>
              <h4 className="font-bold text-base text-[#0F172A] mb-2">Async Code Review</h4>
              <p className="text-xs text-[#64748B] leading-relaxed">
                Review of your GitHub portfolio, open-source work, or past system architectures (48h turnaround).
              </p>
            </div>

            <div className="p-6 bg-white border border-[#E2E8F0] rounded-[4px] relative">
              <span className="font-mono font-bold text-3xl text-[#E2E8F0] block mb-4">02</span>
              <h4 className="font-bold text-base text-[#0F172A] mb-2">Architecture Deep Dive</h4>
              <p className="text-xs text-[#64748B] leading-relaxed">
                60-minute technical dialogue with a Lead Architect discussing real-world trade-offs and scaling bottlenecks.
              </p>
            </div>

            <div className="p-6 bg-white border border-[#E2E8F0] rounded-[4px] relative">
              <span className="font-mono font-bold text-3xl text-[#E2E8F0] block mb-4">03</span>
              <h4 className="font-bold text-base text-[#0F172A] mb-2">Paid Practical Sprint</h4>
              <p className="text-xs text-[#64748B] leading-relaxed">
                A 3-hour paid mini-collaboration on a simulated real project to evaluate asynchronous pairing.
              </p>
            </div>

            <div className="p-6 bg-white border border-[#E2E8F0] rounded-[4px] relative">
              <span className="font-mono font-bold text-3xl text-[#E2E8F0] block mb-4">04</span>
              <h4 className="font-bold text-base text-[#0F172A] mb-2">Bilateral Offer</h4>
              <p className="text-xs text-[#64748B] leading-relaxed">
                Standardized USD salary tiers, token equity, hardware stipend, and immediate start onboarding.
              </p>
            </div>

          </div>
        </div>
      </section>

    </div>
  );
};
