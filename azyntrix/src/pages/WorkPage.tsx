import React, { useState } from 'react';
import { ArrowRight, ArrowUpRight, Check, X, Shield, Globe, Terminal, ArrowLeft } from '../components/Icons';
import { caseStudiesData } from '../data/mockData';
import { CaseStudy } from '../types';

interface WorkPageProps {
  setActiveTab: (tab: string) => void;
  selectedCaseId?: string | null;
  onClearSelectedCase?: () => void;
}

export const WorkPage: React.FC<WorkPageProps> = ({ setActiveTab, selectedCaseId, onClearSelectedCase }) => {
  const [activeCategory, setActiveCategory] = useState('all');
  const [activeModalCase, setActiveModalCase] = useState<CaseStudy | null>(
    selectedCaseId ? caseStudiesData.find(c => c.id === selectedCaseId) || null : null
  );

  const categories = [
    { id: 'all', label: 'All Projects (3)' },
    { id: 'fintech', label: 'FinTech & Payments (1)' },
    { id: 'healthcare', label: 'Healthcare & Clinical (1)' },
    { id: 'ecommerce', label: 'E-Commerce & Retail (1)' }
  ];

  const filteredProjects = activeCategory === 'all' 
    ? caseStudiesData 
    : caseStudiesData.filter(c => {
        if (activeCategory === 'fintech') return c.industry.toLowerCase().includes('fintech');
        if (activeCategory === 'healthcare') return c.industry.toLowerCase().includes('healthcare');
        if (activeCategory === 'ecommerce') return c.industry.toLowerCase().includes('commerce');
        return true;
      });

  return (
    <div className="fade-in">
      
      {/* Work Hero Header */}
      <section className="py-16 lg:py-24 bg-white border-b border-[#E2E8F0]">
        <div className="container-custom">
          <div className="max-w-3xl">
            <span className="font-mono text-xs uppercase tracking-wider text-[#0047FF] font-bold block mb-3">
              CASE STUDIES & PRODUCTION SYSTEMS
            </span>
            <h1 className="text-4xl sm:text-5xl font-extrabold text-[#0F172A] tracking-tight mb-6 leading-tight">
              Engineered for scale, resilience, and verified business outcomes.
            </h1>
            <p className="text-lg text-[#475569] leading-relaxed mb-8">
              Explore in-depth architectural breakdowns of production web applications and custom software platforms engineered by Azyntrix for high-growth ventures and global enterprises.
            </p>

            {/* Impact Strip */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px]">
              <div>
                <span className="font-mono font-bold text-lg text-[#0F172A] block">$840M+</span>
                <span className="text-[11px] text-[#64748B]">Transaction Volume</span>
              </div>
              <div>
                <span className="font-mono font-bold text-lg text-[#0F172A] block">99.999%</span>
                <span className="text-[11px] text-[#64748B]">Peak SLA Uptime</span>
              </div>
              <div>
                <span className="font-mono font-bold text-lg text-[#0F172A] block">74ms</span>
                <span className="text-[11px] text-[#64748B]">P99 Latency Cut</span>
              </div>
              <div>
                <span className="font-mono font-bold text-lg text-[#0F172A] block">0 Breaches</span>
                <span className="text-[11px] text-[#64748B]">SOC2 / HIPAA Audited</span>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* Filter Tabs */}
      <section className="py-6 bg-[#F8FAFC] border-b border-[#E2E8F0] sticky top-20 z-30 backdrop-blur-md bg-white/90">
        <div className="container-custom flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-2">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.id)}
                className={`px-3.5 py-1.5 rounded-[4px] text-xs font-mono font-medium transition-colors ${
                  activeCategory === cat.id
                    ? 'bg-[#0F172A] text-white'
                    : 'bg-white border border-[#E2E8F0] text-[#475569] hover:text-[#0F172A]'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>
          <span className="font-mono text-xs text-[#64748B]">
            Showing {filteredProjects.length} Verified Production Cases
          </span>
        </div>
      </section>

      {/* Editorial Case Studies Feed */}
      <section className="py-16 lg:py-24 bg-[#F8FAFC]">
        <div className="container-custom space-y-16">
          {filteredProjects.map((project) => (
            <article 
              key={project.id}
              className="bg-white border border-[#E2E8F0] rounded-[4px] p-8 lg:p-12 hover:border-[#CBD5E1] transition-all"
            >
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
                
                {/* Left Overview Column */}
                <div className="lg:col-span-6 space-y-6">
                  
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs font-bold text-[#64748B]">
                      CASE STUDY {project.number}
                    </span>
                    <span className="text-[#CBD5E1]">·</span>
                    <span className="text-xs font-bold text-[#0047FF] bg-[#EFF6FF] px-2.5 py-0.5 rounded-[3px]">
                      {project.industry}
                    </span>
                  </div>

                  <div>
                    <span className="text-sm font-bold text-[#64748B] block mb-1">CLIENT: {project.client}</span>
                    <h2 className="text-2xl sm:text-3xl font-extrabold text-[#0F172A] leading-tight mb-3">
                      {project.title}
                    </h2>
                    <p className="text-base text-[#475569] leading-relaxed">
                      {project.tagline}
                    </p>
                  </div>

                  {/* Challenge vs Solution Summary */}
                  <div className="space-y-4 pt-2">
                    <div className="p-4 bg-[#F8FAFC] border-l-2 border-[#E11D48] rounded-r-[4px]">
                      <span className="font-mono text-[11px] uppercase font-bold text-[#E11D48] block mb-1">
                        The Engineering Challenge
                      </span>
                      <p className="text-xs text-[#334155] leading-relaxed">
                        {project.challenge}
                      </p>
                    </div>

                    <div className="p-4 bg-[#F8FAFC] border-l-2 border-[#059669] rounded-r-[4px]">
                      <span className="font-mono text-[11px] uppercase font-bold text-[#059669] block mb-1">
                        The Architectural Solution
                      </span>
                      <p className="text-xs text-[#334155] leading-relaxed">
                        {project.solution}
                      </p>
                    </div>
                  </div>

                  <div className="pt-2">
                    <button
                      onClick={() => setActiveModalCase(project)}
                      className="btn-primary"
                    >
                      Inspect Full Architecture Blueprint →
                    </button>
                  </div>

                </div>

                {/* Right Metrics & Topology Column */}
                <div className="lg:col-span-6 space-y-6">
                  
                  {/* Hard Metrics Grid */}
                  <div className="p-6 bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px]">
                    <span className="font-mono text-xs uppercase font-bold text-[#64748B] block mb-4">
                      Quantifiable Production Outcomes
                    </span>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                      {project.metrics.map((metric, mi) => (
                        <div key={mi} className="p-3 bg-white border border-[#E2E8F0] rounded-[4px]">
                          <span className="font-display font-extrabold text-2xl text-[#0F172A] block mb-0.5">
                            {metric.value}
                          </span>
                          <span className="text-xs font-bold text-[#0F172A] block">{metric.label}</span>
                          <span className="text-[11px] text-[#64748B] block mt-1 leading-tight">{metric.detail}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Architecture Topology Comparison */}
                  <div className="p-6 bg-white border border-[#E2E8F0] rounded-[4px] space-y-3 font-mono text-xs">
                    <span className="uppercase text-[11px] text-[#64748B] font-bold block mb-1">
                      System Migration Flow
                    </span>
                    <div className="p-3 bg-[#FFF1F2] border border-[#FECDD3] rounded text-[#9F1239]">
                      <span className="font-bold block mb-0.5">Legacy Pipeline:</span>
                      {project.architecture.legacy}
                    </div>
                    <div className="p-3 bg-[#ECFDF5] border border-[#A7F3D0] rounded text-[#065F46]">
                      <span className="font-bold block mb-0.5">Modern Azyntrix Architecture:</span>
                      {project.architecture.modern}
                    </div>
                  </div>

                  {/* Client Quote */}
                  {project.testimonial && (
                    <div className="p-4 bg-[#F8FAFC] border-l-2 border-[#0047FF] rounded-r-[4px]">
                      <p className="italic text-xs text-[#475569] leading-relaxed mb-2">
                        "{project.testimonial.quote}"
                      </p>
                      <span className="font-semibold text-xs text-[#0F172A] block">
                        — {project.testimonial.author}, {project.testimonial.role} ({project.testimonial.company})
                      </span>
                    </div>
                  )}

                  {/* Tech Stack Badges */}
                  <div className="flex flex-wrap gap-1.5 pt-2">
                    {project.technologies.map((tech) => (
                      <span key={tech} className="bg-[#F1F5F9] border border-[#E2E8F0] font-mono text-xs px-2.5 py-1 rounded text-[#0F172A]">
                        {tech}
                      </span>
                    ))}
                  </div>

                </div>

              </div>
            </article>
          ))}
        </div>
      </section>

      {/* Case Study Deep-Dive Blueprint Modal */}
      {activeModalCase && (
        <div className="fixed inset-0 z-50 bg-[#0F172A]/70 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6 overflow-y-auto animate-fadeIn">
          <div className="bg-white border border-[#CBD5E1] rounded-[6px] max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl p-6 sm:p-10 space-y-8 my-8">
            
            {/* Modal Header */}
            <div className="flex items-start justify-between pb-6 border-b border-[#E2E8F0]">
              <div>
                <span className="font-mono text-xs font-bold text-[#0047FF] uppercase tracking-wider block mb-1">
                  CASE STUDY {activeModalCase.number} // DETAILED ARCHITECTURE
                </span>
                <h2 className="text-2xl sm:text-3xl font-extrabold text-[#0F172A]">
                  {activeModalCase.title}
                </h2>
                <span className="text-xs text-[#64748B]">Client: {activeModalCase.client} ({activeModalCase.industry})</span>
              </div>
              <button
                onClick={() => {
                  setActiveModalCase(null);
                  if (onClearSelectedCase) onClearSelectedCase();
                }}
                className="p-2 border border-[#E2E8F0] rounded hover:bg-[#F8FAFC]"
              >
                <X className="w-5 h-5 text-[#64748B]" />
              </button>
            </div>

            {/* Deep-Dive Sections */}
            <div className="space-y-6">
              
              <div>
                <h4 className="font-mono text-xs uppercase font-bold text-[#0F172A] tracking-wider mb-2">
                  01. Technical Background & Bottlenecks
                </h4>
                <p className="text-sm text-[#475569] leading-relaxed">
                  {activeModalCase.challenge}
                </p>
              </div>

              <div>
                <h4 className="font-mono text-xs uppercase font-bold text-[#0F172A] tracking-wider mb-2">
                  02. Architectural Blueprint & Technical Implementation
                </h4>
                <p className="text-sm text-[#475569] leading-relaxed mb-4">
                  {activeModalCase.solution}
                </p>
                <div className="p-4 bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px] font-mono text-xs space-y-2 text-[#334155]">
                  <div className="flex items-center gap-2 text-[#0047FF] font-bold">
                    <Terminal className="w-4 h-4" /> System Topology Specification:
                  </div>
                  <p className="pl-6 border-l border-[#E2E8F0]">
                    {activeModalCase.architecture.modern}
                  </p>
                </div>
              </div>

              <div>
                <h4 className="font-mono text-xs uppercase font-bold text-[#0F172A] tracking-wider mb-3">
                  03. Measured Production Benchmarks
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {activeModalCase.metrics.map((m, mi) => (
                    <div key={mi} className="p-4 bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px]">
                      <span className="font-mono font-extrabold text-xl text-[#0F172A] block">{m.value}</span>
                      <span className="text-xs font-bold text-[#0F172A] block">{m.label}</span>
                      <span className="text-[11px] text-[#64748B] mt-1 block">{m.detail}</span>
                    </div>
                  ))}
                </div>
              </div>

            </div>

            {/* Modal Footer */}
            <div className="pt-6 border-t border-[#E2E8F0] flex flex-wrap items-center justify-between gap-4">
              <button
                onClick={() => {
                  setActiveModalCase(null);
                  if (onClearSelectedCase) onClearSelectedCase();
                }}
                className="btn-secondary text-xs py-2 px-4"
              >
                Close Blueprint
              </button>
              <button
                onClick={() => {
                  setActiveModalCase(null);
                  setActiveTab('contact');
                }}
                className="btn-primary text-xs py-2 px-5"
              >
                Schedule Similar Architecture Scope →
              </button>
            </div>

          </div>
        </div>
      )}

      {/* Conversion Banner */}
      <section className="py-20 bg-[#0F172A] text-white">
        <div className="container-custom text-center max-w-2xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white mb-4">
            Have a complex engineering challenge?
          </h2>
          <p className="text-base text-[#94A3B8] mb-8">
            Speak directly with our senior architects to de-risk your software roadmap.
          </p>
          <button onClick={() => setActiveTab('contact')} className="btn-accent text-base py-3.5 px-8">
            Start a Project →
          </button>
        </div>
      </section>

    </div>
  );
};
