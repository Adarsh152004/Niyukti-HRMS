import React from 'react';
import { ArrowRight, ArrowUpRight, Check, ShieldCheck, Sparkles, Layers, Cpu, Code2, Globe, Database, Terminal } from '../components/Icons';
import { servicesData } from '../data/mockData';

interface ServicesPageProps {
  setActiveTab: (tab: string) => void;
}

export const ServicesPage: React.FC<ServicesPageProps> = ({ setActiveTab }) => {
  return (
    <div className="fade-in">
      
      {/* Services Hero Header */}
      <section className="py-16 lg:py-24 bg-white border-b border-[#E2E8F0]">
        <div className="container-custom">
          <div className="max-w-3xl">
            <span className="font-mono text-xs uppercase tracking-wider text-[#0047FF] font-bold block mb-3">
              SERVICES & TECHNICAL CAPABILITIES
            </span>
            <h1 className="text-4xl sm:text-5xl font-extrabold text-[#0F172A] tracking-tight mb-6 leading-tight">
              Full-cycle digital product design, web engineering, and custom software development.
            </h1>
            <p className="text-lg text-[#475569] leading-relaxed mb-8">
              We build production-grade web applications, enterprise software architectures, and scalable digital products. Our senior teams handle every phase from discovery to deployment with uncompromised engineering rigor.
            </p>
            
            {/* Quick Metrics Bar */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px]">
              <div>
                <span className="font-mono font-bold text-lg text-[#0F172A] block">99.99%</span>
                <span className="text-[11px] text-[#64748B]">SLA Uptime Delivered</span>
              </div>
              <div>
                <span className="font-mono font-bold text-lg text-[#0F172A] block">&lt; 65ms</span>
                <span className="text-[11px] text-[#64748B]">Median API Latency</span>
              </div>
              <div>
                <span className="font-mono font-bold text-lg text-[#0F172A] block">$1.8B+</span>
                <span className="text-[11px] text-[#64748B]">Handled Volume</span>
              </div>
              <div>
                <span className="font-mono font-bold text-lg text-[#0F172A] block">100%</span>
                <span className="text-[11px] text-[#64748B]">Senior/Staff Talent</span>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* 7 Practice Offerings Breakdown */}
      <section className="py-20 bg-[#F8FAFC] border-b border-[#E2E8F0]">
        <div className="container-custom">
          
          <div className="space-y-12">
            {servicesData.map((service) => (
              <div 
                key={service.id} 
                id={service.id}
                className="p-8 lg:p-12 bg-white border border-[#E2E8F0] rounded-[4px] hover:border-[#CBD5E1] transition-all"
              >
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                  
                  {/* Left Column: Number & Core Definition */}
                  <div className="lg:col-span-6 space-y-4">
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-sm font-extrabold text-[#0047FF]">
                        {service.number} //
                      </span>
                      <span className="font-mono text-xs text-[#64748B] uppercase tracking-wider">
                        {service.sublabel}
                      </span>
                    </div>

                    <h2 className="text-2xl sm:text-3xl font-bold text-[#0F172A]">
                      {service.title}
                    </h2>

                    <p className="text-base text-[#475569] leading-relaxed">
                      {service.description}
                    </p>

                    {/* Tech Stack Chips */}
                    <div className="pt-2">
                      <span className="font-mono text-[11px] text-[#64748B] uppercase tracking-wider block mb-2">
                        Core Tech Stack
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {service.techStack.map((tech) => (
                          <span key={tech} className="bg-[#F8FAFC] border border-[#E2E8F0] text-[#0F172A] font-mono text-xs px-2.5 py-1 rounded-[3px]">
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Right Column: Key Deliverables & Technical Specs */}
                  <div className="lg:col-span-6 space-y-6">
                    <div className="p-6 bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px]">
                      <h4 className="font-mono text-xs font-bold text-[#0F172A] uppercase tracking-wider mb-3">
                        Key Deliverables & Specifications
                      </h4>
                      <ul className="space-y-2.5">
                        {service.deliverables.map((del, di) => (
                          <li key={di} className="flex items-start gap-2.5 text-sm text-[#334155]">
                            <Check className="w-4 h-4 text-[#0047FF] shrink-0 mt-0.5" />
                            <span>{del}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Performance Benchmarks */}
                    <div className="grid grid-cols-3 gap-3">
                      {service.specs.map((spec, si) => (
                        <div key={si} className="p-3 bg-white border border-[#E2E8F0] rounded-[4px] text-center">
                          <span className="font-mono font-bold text-sm text-[#0F172A] block">
                            {spec.value}
                          </span>
                          <span className="text-[10px] text-[#64748B] uppercase tracking-wider">
                            {spec.label}
                          </span>
                        </div>
                      ))}
                    </div>

                    <div className="pt-2 text-right">
                      <button
                        onClick={() => setActiveTab('contact')}
                        className="btn-primary"
                      >
                        {service.ctaText}
                        <ArrowRight className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                </div>
              </div>
            ))}
          </div>

        </div>
      </section>

      {/* 3 Consultancy Engagement Models */}
      <section className="py-20 lg:py-28 bg-white border-b border-[#E2E8F0]">
        <div className="container-custom">
          
          <div className="max-w-2xl mb-16">
            <span className="font-mono text-xs uppercase tracking-wider text-[#0047FF] font-bold block mb-2">
              ENGAGEMENT MODELS
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-[#0F172A] tracking-tight mb-4">
              Flexible partnership structures.
            </h2>
            <p className="text-[#475569] text-base leading-relaxed">
              Built to integrate seamlessly with your internal product leaders and engineering roadmap.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            
            {/* Model A */}
            <div className="p-8 border-2 border-[#0F172A] bg-white rounded-[4px] flex flex-col justify-between shadow-lg relative">
              <div className="absolute -top-3 right-6 bg-[#0047FF] text-white text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded">
                Most Selected
              </div>
              <div>
                <span className="font-mono text-xs text-[#64748B] block mb-2">MODEL A</span>
                <h3 className="text-xl font-bold text-[#0F172A] mb-3">Dedicated Engineering Squad</h3>
                <p className="text-sm text-[#475569] leading-relaxed mb-6">
                  Cross-functional squad (Lead Systems Architect, Senior Full-Stack Engineers, Product Designer) embedded directly into your Slack, Linear, and GitHub.
                </p>
                <div className="space-y-2 border-t border-[#E2E8F0] pt-4 mb-8 text-xs text-[#334155]">
                  <div className="flex items-center gap-2">
                    <Check className="w-3.5 h-3.5 text-[#0047FF]" />
                    <span>Bi-weekly agile sprints with live demos</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="w-3.5 h-3.5 text-[#0047FF]" />
                    <span>Daily asynchronous PR reviews</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="w-3.5 h-3.5 text-[#0047FF]" />
                    <span>Direct Staff-level engineering access</span>
                  </div>
                </div>
              </div>
              <button onClick={() => setActiveTab('contact')} className="btn-primary w-full">
                Select Dedicated Squad
              </button>
            </div>

            {/* Model B */}
            <div className="p-8 border border-[#E2E8F0] bg-[#F8FAFC] rounded-[4px] flex flex-col justify-between hover:border-[#CBD5E1] transition-all">
              <div>
                <span className="font-mono text-xs text-[#64748B] block mb-2">MODEL B</span>
                <h3 className="text-xl font-bold text-[#0F172A] mb-3">Fixed-Scope Project Delivery</h3>
                <p className="text-sm text-[#475569] leading-relaxed mb-6">
                  Milestone-based end-to-end delivery from specification to production cutover with guaranteed deadlines, fixed quotes, and turn-key deployment.
                </p>
                <div className="space-y-2 border-t border-[#E2E8F0] pt-4 mb-8 text-xs text-[#334155]">
                  <div className="flex items-center gap-2">
                    <Check className="w-3.5 h-3.5 text-[#0047FF]" />
                    <span>Defined scope, milestones & deliverables</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="w-3.5 h-3.5 text-[#0047FF]" />
                    <span>Guaranteed production launch schedule</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="w-3.5 h-3.5 text-[#0047FF]" />
                    <span>60-day post-launch warranty included</span>
                  </div>
                </div>
              </div>
              <button onClick={() => setActiveTab('contact')} className="btn-secondary w-full">
                Scope a Project
              </button>
            </div>

            {/* Model C */}
            <div className="p-8 border border-[#E2E8F0] bg-[#F8FAFC] rounded-[4px] flex flex-col justify-between hover:border-[#CBD5E1] transition-all">
              <div>
                <span className="font-mono text-xs text-[#64748B] block mb-2">MODEL C</span>
                <h3 className="text-xl font-bold text-[#0F172A] mb-3">Technical Advisory & Audit</h3>
                <p className="text-sm text-[#475569] leading-relaxed mb-6">
                  Comprehensive architectural review, security vulnerability audit, database query profiling, and actionable 12-month scalability roadmap.
                </p>
                <div className="space-y-2 border-t border-[#E2E8F0] pt-4 mb-8 text-xs text-[#334155]">
                  <div className="flex items-center gap-2">
                    <Check className="w-3.5 h-3.5 text-[#0047FF]" />
                    <span>2 to 4-week intensive codebase audit</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="w-3.5 h-3.5 text-[#0047FF]" />
                    <span>Detailed executive findings & threat memo</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="w-3.5 h-3.5 text-[#0047FF]" />
                    <span>Step-by-step refactoring priority backlog</span>
                  </div>
                </div>
              </div>
              <button onClick={() => setActiveTab('contact')} className="btn-secondary w-full">
                Request Architecture Audit
              </button>
            </div>

          </div>

        </div>
      </section>

      {/* 4-Phase Delivery Process */}
      <section className="py-20 bg-[#F8FAFC] border-b border-[#E2E8F0]">
        <div className="container-custom">
          
          <div className="text-center max-w-2xl mx-auto mb-16">
            <span className="font-mono text-xs uppercase tracking-wider text-[#0047FF] font-bold block mb-2">
              OUR OPERATING CADENCE
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-[#0F172A] tracking-tight">
              From architecture to production telemetry.
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="p-6 bg-white border border-[#E2E8F0] rounded-[4px]">
              <span className="font-mono text-xs font-bold text-[#0047FF] block mb-2">PHASE 01</span>
              <h3 className="font-bold text-lg text-[#0F172A] mb-2">Architecture & Discovery</h3>
              <p className="text-xs sm:text-sm text-[#475569] leading-relaxed">
                Requirements decomposition, schema modeling, threat modeling, and comprehensive RFC blueprints before writing code.
              </p>
            </div>

            <div className="p-6 bg-white border border-[#E2E8F0] rounded-[4px]">
              <span className="font-mono text-xs font-bold text-[#0047FF] block mb-2">PHASE 02</span>
              <h3 className="font-bold text-lg text-[#0F172A] mb-2">Sprint Iteration & Previews</h3>
              <p className="text-xs sm:text-sm text-[#475569] leading-relaxed">
                Two-week agile sprints, ephemeral preview deployments per PR, automated lint/type check gates, and continuous demo syncs.
              </p>
            </div>

            <div className="p-6 bg-white border border-[#E2E8F0] rounded-[4px]">
              <span className="font-mono text-xs font-bold text-[#0047FF] block mb-2">PHASE 03</span>
              <h3 className="font-bold text-lg text-[#0F172A] mb-2">QA & Load Simulation</h3>
              <p className="text-xs sm:text-sm text-[#475569] leading-relaxed">
                Automated E2E suites, chaotic network simulation, distributed load generation up to 100k req/s, and security audit sign-off.
              </p>
            </div>

            <div className="p-6 bg-white border border-[#E2E8F0] rounded-[4px]">
              <span className="font-mono text-xs font-bold text-[#0047FF] block mb-2">PHASE 04</span>
              <h3 className="font-bold text-lg text-[#0F172A] mb-2">Telemetry & Handover</h3>
              <p className="text-xs sm:text-sm text-[#475569] leading-relaxed">
                Zero-downtime blue/green cutover, full Datadog observability dashboards, automated runbooks, and clean repo ownership transfer.
              </p>
            </div>
          </div>

        </div>
      </section>

      {/* Conversion Banner */}
      <section className="py-20 bg-[#0F172A] text-white">
        <div className="container-custom text-center max-w-3xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white mb-6">
            Ready to build your next software platform?
          </h2>
          <p className="text-base text-[#94A3B8] mb-8">
            Tell us about your technical requirements. We will prepare an initial architectural feasibility review within 24 business hours.
          </p>
          <button
            onClick={() => setActiveTab('contact')}
            className="btn-accent text-base py-3.5 px-8"
          >
            Initiate Project Discovery →
          </button>
        </div>
      </section>

    </div>
  );
};
