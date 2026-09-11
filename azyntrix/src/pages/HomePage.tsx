import React from 'react';
import { 
  ArrowRight, 
  ArrowUpRight, 
  CheckCircle2, 
  Layers, 
  Code2, 
  Sparkles, 
  ShieldCheck, 
  Cpu, 
  Zap, 
  Globe2, 
  Clock, 
  Users 
} from '../components/Icons';
import { servicesData, caseStudiesData } from '../data/mockData';

interface HomePageProps {
  setActiveTab: (tab: string) => void;
  onOpenCaseStudy: (caseId: string) => void;
  onOpenJobDetail: (jobId: string) => void;
}

export const HomePage: React.FC<HomePageProps> = ({ setActiveTab, onOpenCaseStudy, onOpenJobDetail }) => {
  const primaryFeaturedProjects = caseStudiesData.slice(0, 2);

  return (
    <div className="fade-in">
      
      {/* 1. EDITORIAL HERO SECTION */}
      <section className="pt-16 pb-20 lg:pt-24 lg:pb-28 border-b border-[#E2E8F0] bg-white">
        <div className="container-custom">
          
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
            
            {/* Left Column: Typographic Narrative */}
            <div className="lg:col-span-7">
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#F1F5F9] border border-[#E2E8F0] rounded-[3px] text-xs font-mono text-[#0F172A] mb-6">
                <span className="w-1.5 h-1.5 rounded-full bg-[#0047FF]"></span>
                <span className="font-semibold uppercase tracking-wider">Software Engineering & Digital Product Studio</span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-[3.4rem] font-extrabold text-[#0F172A] leading-[1.12] tracking-tight mb-6">
                We engineer custom web applications & digital software systems for ambitious businesses.
              </h1>

              <p className="text-lg sm:text-xl text-[#475569] leading-relaxed max-w-2xl mb-8 font-normal">
                Azyntrix partners with enterprise technology leaders and venture-backed companies to architect, build, and scale mission-critical software solutions with uncompromised engineering standards.
              </p>

              {/* Action Cluster */}
              <div className="flex flex-wrap items-center gap-4 pt-2 mb-10">
                <button
                  onClick={() => setActiveTab('contact')}
                  className="btn-primary text-base py-3.5 px-6"
                >
                  Start a Project
                  <ArrowRight className="w-4 h-4 text-[#94A3B8]" />
                </button>
                <button
                  onClick={() => setActiveTab('work')}
                  className="btn-secondary text-base py-3.5 px-6"
                >
                  View Selected Work
                  <ArrowUpRight className="w-4 h-4 text-[#64748B]" />
                </button>
              </div>

              {/* High-Trust Telemetry Grid */}
              <div className="pt-6 border-t border-[#E2E8F0] grid grid-cols-3 gap-6">
                <div>
                  <span className="font-display font-extrabold text-2xl text-[#0F172A] block">
                    99.999%
                  </span>
                  <span className="text-xs text-[#64748B] font-medium">Production SLA Uptime</span>
                </div>
                <div>
                  <span className="font-display font-extrabold text-2xl text-[#0F172A] block">
                    &lt; 75ms
                  </span>
                  <span className="text-xs text-[#64748B] font-medium">Median API TTFB</span>
                </div>
                <div>
                  <span className="font-display font-extrabold text-2xl text-[#0F172A] block">
                    100%
                  </span>
                  <span className="text-xs text-[#64748B] font-medium">Senior / Staff Engineers</span>
                </div>
              </div>

            </div>

            {/* Right Column: Realistic Enterprise Web App Preview */}
            <div className="lg:col-span-5">
              <div className="bg-[#FFFFFF] border border-[#CBD5E1] rounded-[6px] shadow-2xl shadow-slate-200/80 overflow-hidden">
                
                {/* Clean Browser Bar Header */}
                <div className="bg-[#F8FAFC] border-b border-[#E2E8F0] px-4 py-2.5 flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#E2E8F0]"></span>
                    <span className="w-2.5 h-2.5 rounded-full bg-[#E2E8F0]"></span>
                    <span className="w-2.5 h-2.5 rounded-full bg-[#E2E8F0]"></span>
                  </div>
                  <div className="font-mono text-[11px] text-[#64748B] bg-white border border-[#E2E8F0] px-3 py-0.5 rounded-[3px] truncate max-w-[200px]">
                    app.paygrid.internal/settlement
                  </div>
                  <div className="w-3"></div>
                </div>

                {/* Realistic Web Application UI Inside */}
                <div className="p-5 bg-white space-y-4 text-xs font-sans">
                  
                  {/* Top Stats Bar */}
                  <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
                    <div>
                      <span className="text-[#64748B] text-[11px] block">Settlement Throughput</span>
                      <span className="font-mono font-bold text-sm text-[#0F172A]">$18,420,910.45</span>
                    </div>
                    <div className="text-right">
                      <span className="inline-flex items-center gap-1 text-[11px] text-[#059669] font-semibold bg-[#ECFDF5] px-2 py-0.5 rounded-[3px]">
                        <CheckCircle2 className="w-3 h-3" /> Live Event Mesh
                      </span>
                    </div>
                  </div>

                  {/* Micro Settlement Table */}
                  <div className="border border-[#E2E8F0] rounded-[4px] overflow-hidden">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[11px] text-[#64748B] font-mono">
                          <th className="py-2 px-3">Batch ID</th>
                          <th className="py-2 px-3">Latency</th>
                          <th className="py-2 px-3 text-right">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#F1F5F9] font-mono text-[11px] text-[#0F172A]">
                        <tr>
                          <td className="py-2 px-3 font-semibold">#TX-94182</td>
                          <td className="py-2 px-3 text-[#059669]">14ms</td>
                          <td className="py-2 px-3 text-right">
                            <span className="bg-[#F1F5F9] text-[#0F172A] font-bold px-1.5 py-0.5 rounded text-[10px]">
                              Settled
                            </span>
                          </td>
                        </tr>
                        <tr>
                          <td className="py-2 px-3 font-semibold">#TX-94183</td>
                          <td className="py-2 px-3 text-[#059669]">18ms</td>
                          <td className="py-2 px-3 text-right">
                            <span className="bg-[#F1F5F9] text-[#0F172A] font-bold px-1.5 py-0.5 rounded text-[10px]">
                              Settled
                            </span>
                          </td>
                        </tr>
                        <tr>
                          <td className="py-2 px-3 font-semibold">#TX-94184</td>
                          <td className="py-2 px-3 text-[#059669]">12ms</td>
                          <td className="py-2 px-3 text-right">
                            <span className="bg-[#EFF6FF] text-[#0047FF] font-bold px-1.5 py-0.5 rounded text-[10px]">
                              Replicating
                            </span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  {/* Latency Telemetry Graph Representation */}
                  <div className="p-3 bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px]">
                    <div className="flex items-center justify-between text-[11px] font-mono text-[#64748B] mb-2">
                      <span>P99 Real-Time Response</span>
                      <span className="text-[#059669] font-bold">14.2ms Avg</span>
                    </div>
                    <div className="h-9 flex items-end gap-1">
                      {[35, 42, 38, 48, 40, 52, 36, 30, 44, 38, 32, 28, 40, 36, 32, 29, 31, 35, 30, 28].map((h, i) => (
                        <div 
                          key={i} 
                          style={{ height: `${h}%` }} 
                          className={`flex-1 rounded-t-[1px] ${i === 18 ? 'bg-[#0047FF]' : 'bg-[#CBD5E1]'}`}
                        />
                      ))}
                    </div>
                  </div>

                  {/* Architecture Tags */}
                  <div className="flex items-center justify-between text-[11px] text-[#64748B] pt-1">
                    <span>Engine: Go 1.22 + Kafka</span>
                    <span className="font-mono text-[#0F172A] font-bold">SOC2 Audited</span>
                  </div>

                </div>

              </div>
            </div>

          </div>

        </div>
      </section>

      {/* 2. CLIENT TRUST BAR */}
      <section className="py-12 bg-[#F8FAFC] border-b border-[#E2E8F0]">
        <div className="container-custom">
          <p className="font-mono text-xs uppercase tracking-wider text-[#64748B] text-center mb-8">
            Trusted by engineering leadership at high-growth ventures & global organizations
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6 items-center text-center">
            {['STRIPE ECOSYSTEM', 'MERIDIAN HEALTH', 'SCALEFLOW', 'AURA COMMERCE', 'VERIDIAN SYSTEMS', 'NEXUSTECH'].map((brand, i) => (
              <div 
                key={i} 
                className="py-4 px-3 bg-white border border-[#E2E8F0] rounded-[4px] font-display font-extrabold text-xs tracking-wider text-[#475569]"
              >
                {brand}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 3. CORE PRACTICES (3-COLUMN STRUCTURED GRID) */}
      <section className="py-20 lg:py-28 bg-white border-b border-[#E2E8F0]">
        <div className="container-custom">
          
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-16 gap-6">
            <div>
              <span className="font-mono text-xs uppercase tracking-wider text-[#0047FF] font-bold block mb-2">
                PRACTICES & CAPABILITIES
              </span>
              <h2 className="text-3xl sm:text-4xl font-extrabold text-[#0F172A] tracking-tight">
                Specialized software disciplines.
              </h2>
            </div>
            <button
              onClick={() => setActiveTab('services')}
              className="inline-flex items-center gap-1.5 text-sm font-semibold text-[#0047FF] hover:underline"
            >
              Explore all 7 practices & deliverables <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            
            {/* Practice 1 */}
            <div className="p-8 bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px] flex flex-col justify-between hover:border-[#CBD5E1] transition-all">
              <div>
                <div className="font-mono font-bold text-xs text-[#64748B] mb-4">01 // FRONTEND ARCHITECTURE</div>
                <h3 className="text-xl font-bold text-[#0F172A] mb-3">
                  Web Applications & Reactive Platforms
                </h3>
                <p className="text-sm text-[#475569] leading-relaxed mb-6">
                  High-performance web apps built with Next.js 14, React, and TypeScript. Optimized for sub-100ms response times, micro-frontend modularity, and seamless state synchronization.
                </p>
                <div className="flex flex-wrap gap-1.5 mb-8">
                  {['Next.js 14', 'React', 'TypeScript', 'GraphQL', 'Tailwind'].map((tech) => (
                    <span key={tech} className="bg-white border border-[#E2E8F0] text-[#0F172A] font-mono text-[11px] px-2 py-0.5 rounded-[3px]">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
              <button
                onClick={() => setActiveTab('services')}
                className="inline-flex items-center gap-1 text-xs font-bold text-[#0F172A] hover:text-[#0047FF] transition-colors"
              >
                View Deliverables <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Practice 2 */}
            <div className="p-8 bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px] flex flex-col justify-between hover:border-[#CBD5E1] transition-all">
              <div>
                <div className="font-mono font-bold text-xs text-[#64748B] mb-4">02 // DISTRIBUTED SYSTEMS</div>
                <h3 className="text-xl font-bold text-[#0F172A] mb-3">
                  Custom Software & Resilient Backends
                </h3>
                <p className="text-sm text-[#475569] leading-relaxed mb-6">
                  Fault-tolerant backend architectures engineered with Go, Python, and Kafka. Designed for massive transactional scale, CQRS event sourcing, and high-concurrency workloads.
                </p>
                <div className="flex flex-wrap gap-1.5 mb-8">
                  {['Go', 'Python', 'Kafka', 'PostgreSQL', 'Docker'].map((tech) => (
                    <span key={tech} className="bg-white border border-[#E2E8F0] text-[#0F172A] font-mono text-[11px] px-2 py-0.5 rounded-[3px]">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
              <button
                onClick={() => setActiveTab('services')}
                className="inline-flex items-center gap-1 text-xs font-bold text-[#0F172A] hover:text-[#0047FF] transition-colors"
              >
                View Deliverables <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Practice 3 */}
            <div className="p-8 bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px] flex flex-col justify-between hover:border-[#CBD5E1] transition-all">
              <div>
                <div className="font-mono font-bold text-xs text-[#64748B] mb-4">03 // PRODUCT DESIGN</div>
                <h3 className="text-xl font-bold text-[#0F172A] mb-3">
                  UI/UX & Enterprise Design Systems
                </h3>
                <p className="text-sm text-[#475569] leading-relaxed mb-6">
                  Human-crafted digital product design and multi-platform design systems in Figma. Engineered for cognitive clarity, accessible WCAG 2.1 AAA compliance, and design-token automation.
                </p>
                <div className="flex flex-wrap gap-1.5 mb-8">
                  {['Figma Tokens', 'Storybook', 'WCAG AAA', 'Design Systems'].map((tech) => (
                    <span key={tech} className="bg-white border border-[#E2E8F0] text-[#0F172A] font-mono text-[11px] px-2 py-0.5 rounded-[3px]">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
              <button
                onClick={() => setActiveTab('services')}
                className="inline-flex items-center gap-1 text-xs font-bold text-[#0F172A] hover:text-[#0047FF] transition-colors"
              >
                View Deliverables <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>

          </div>

        </div>
      </section>

      {/* 4. SELECTED EDITORIAL CASE STUDIES */}
      <section className="py-20 lg:py-28 bg-[#F8FAFC] border-b border-[#E2E8F0]">
        <div className="container-custom">
          
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-16 gap-6">
            <div>
              <span className="font-mono text-xs uppercase tracking-wider text-[#0047FF] font-bold block mb-2">
                SELECTED WORK & CASE STUDIES
              </span>
              <h2 className="text-3xl sm:text-4xl font-extrabold text-[#0F172A] tracking-tight">
                Engineered for scale & measurable impact.
              </h2>
            </div>
            <button
              onClick={() => setActiveTab('work')}
              className="inline-flex items-center gap-1.5 text-sm font-semibold text-[#0F172A] hover:text-[#0047FF]"
            >
              Browse all production case studies <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-12">
            {primaryFeaturedProjects.map((project) => (
              <div 
                key={project.id}
                className="bg-white border border-[#E2E8F0] rounded-[4px] p-8 lg:p-12 hover:border-[#CBD5E1] transition-all"
              >
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
                  
                  {/* Left Specs */}
                  <div className="lg:col-span-6 space-y-5">
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-xs font-bold text-[#64748B]">
                        PROJECT {project.number}
                      </span>
                      <span className="text-[#CBD5E1]">·</span>
                      <span className="text-xs font-semibold text-[#0047FF] bg-[#EFF6FF] px-2 py-0.5 rounded-[3px]">
                        {project.industry}
                      </span>
                    </div>

                    <h3 className="text-2xl sm:text-3xl font-extrabold text-[#0F172A] leading-tight">
                      {project.title}
                    </h3>

                    <p className="text-base text-[#475569] leading-relaxed">
                      {project.tagline}
                    </p>

                    <div className="p-4 bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px]">
                      <span className="font-mono text-[11px] text-[#64748B] block uppercase tracking-wider mb-1">
                        Architecture Solution
                      </span>
                      <p className="text-xs font-mono text-[#0F172A] leading-normal">
                        {project.architecture.modern}
                      </p>
                    </div>

                    <div className="flex items-center gap-6 pt-2">
                      {project.metrics.map((metric, mi) => (
                        <div key={mi}>
                          <span className="font-display font-extrabold text-xl text-[#0F172A] block">
                            {metric.value}
                          </span>
                          <span className="text-xs text-[#64748B] font-medium">{metric.label}</span>
                        </div>
                      ))}
                    </div>

                    <div className="pt-2">
                      <button
                        onClick={() => {
                          onOpenCaseStudy(project.id);
                          setActiveTab('work');
                        }}
                        className="btn-primary"
                      >
                        Read Full Case Study
                        <ArrowRight className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Right Editorial Preview Card */}
                  <div className="lg:col-span-6">
                    <div className="bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px] p-6 space-y-4">
                      <div className="flex items-center justify-between pb-3 border-b border-[#E2E8F0]">
                        <span className="font-display font-bold text-sm text-[#0F172A]">{project.client}</span>
                        <span className="font-mono text-xs text-[#059669] font-semibold bg-[#ECFDF5] px-2 py-0.5 rounded">
                          Production Verified
                        </span>
                      </div>

                      {project.testimonial && (
                        <blockquote className="italic text-sm text-[#475569] border-l-2 border-[#0047FF] pl-4 py-1 leading-relaxed">
                          "{project.testimonial.quote}"
                          <footer className="mt-2 text-xs font-semibold text-[#0F172A] not-italic">
                            — {project.testimonial.author}, {project.testimonial.role}
                          </footer>
                        </blockquote>
                      )}

                      <div className="pt-2 flex flex-wrap gap-2">
                        {project.technologies.map((t) => (
                          <span key={t} className="bg-white border border-[#E2E8F0] font-mono text-xs px-2.5 py-1 rounded text-[#0F172A]">
                            {t}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                </div>
              </div>
            ))}
          </div>

        </div>
      </section>

      {/* 5. HOW WE WORK (DELIVERY PRINCIPLES) */}
      <section className="py-20 lg:py-28 bg-white border-b border-[#E2E8F0]">
        <div className="container-custom">
          
          <div className="max-w-2xl mb-16">
            <span className="font-mono text-xs uppercase tracking-wider text-[#0047FF] font-bold block mb-2">
              DELIVERY PRINCIPLES
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-[#0F172A] tracking-tight mb-4">
              How Azyntrix builds software differently.
            </h2>
            <p className="text-[#475569] text-base leading-relaxed">
              We eliminate traditional consulting bureaucracy, junior-heavy billing pyramids, and opaque timelines. You work directly with battle-tested senior engineers.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            
            <div className="p-6 border border-[#E2E8F0] bg-[#F8FAFC] rounded-[4px]">
              <div className="w-10 h-10 bg-[#0F172A] rounded-[4px] flex items-center justify-center text-white mb-5">
                <Users className="w-5 h-5 text-[#38BDF8]" />
              </div>
              <h3 className="font-bold text-lg text-[#0F172A] mb-2">01. Senior Engineering</h3>
              <p className="text-xs sm:text-sm text-[#475569] leading-relaxed">
                Zero junior proxies or outsourced handoffs. Every sprint commit is authored and reviewed by Staff-level architects.
              </p>
            </div>

            <div className="p-6 border border-[#E2E8F0] bg-[#F8FAFC] rounded-[4px]">
              <div className="w-10 h-10 bg-[#0F172A] rounded-[4px] flex items-center justify-center text-white mb-5">
                <Clock className="w-5 h-5 text-[#38BDF8]" />
              </div>
              <h3 className="font-bold text-lg text-[#0F172A] mb-2">02. Async Autonomy</h3>
              <p className="text-xs sm:text-sm text-[#475569] leading-relaxed">
                Document-first collaboration with high-context PR reviews, live ephemeral staging demos, and zero calendar bloat.
              </p>
            </div>

            <div className="p-6 border border-[#E2E8F0] bg-[#F8FAFC] rounded-[4px]">
              <div className="w-10 h-10 bg-[#0F172A] rounded-[4px] flex items-center justify-center text-white mb-5">
                <ShieldCheck className="w-5 h-5 text-[#38BDF8]" />
              </div>
              <h3 className="font-bold text-lg text-[#0F172A] mb-2">03. Zero Tech Debt</h3>
              <p className="text-xs sm:text-sm text-[#475569] leading-relaxed">
                Strict type safety, automated end-to-end testing, and immutable architecture blueprints that stand up to scale.
              </p>
            </div>

            <div className="p-6 border border-[#E2E8F0] bg-[#F8FAFC] rounded-[4px]">
              <div className="w-10 h-10 bg-[#0F172A] rounded-[4px] flex items-center justify-center text-white mb-5">
                <Zap className="w-5 h-5 text-[#38BDF8]" />
              </div>
              <h3 className="font-bold text-lg text-[#0F172A] mb-2">04. Clean Handoff</h3>
              <p className="text-xs sm:text-sm text-[#475569] leading-relaxed">
                Full intellectual property assignment, clean git repos, automated CI/CD pipelines, and zero vendor lock-in.
              </p>
            </div>

          </div>

        </div>
      </section>

      {/* 6. CAREERS TEASER BANNER */}
      <section className="py-16 bg-[#F8FAFC] border-b border-[#E2E8F0]">
        <div className="container-custom">
          <div className="p-8 lg:p-12 bg-white border border-[#E2E8F0] rounded-[4px] flex flex-col md:flex-row items-start md:items-center justify-between gap-8">
            <div className="max-w-xl">
              <span className="font-mono text-xs font-bold text-[#0047FF] uppercase tracking-wider block mb-2">
                JOIN OUR DISTRIBUTED GUILD
              </span>
              <h3 className="text-2xl sm:text-3xl font-extrabold text-[#0F172A] mb-3">
                We are hiring senior software engineers and designers.
              </h3>
              <p className="text-sm text-[#475569] leading-relaxed">
                100% remote worldwide, transparent global pay bands ($120k - $210k USD), 4-day focus weeks, and $4,000 annual learning stipends.
              </p>
            </div>
            <button
              onClick={() => setActiveTab('careers')}
              className="btn-secondary whitespace-nowrap text-sm py-3 px-6"
            >
              Explore 6 Open Roles →
            </button>
          </div>
        </div>
      </section>

      {/* 7. CONVERSION CALLOUT */}
      <section className="py-20 lg:py-24 bg-[#0F172A] text-white">
        <div className="container-custom text-center max-w-3xl mx-auto">
          <span className="font-mono text-xs uppercase tracking-wider text-[#38BDF8] font-bold block mb-3">
            INITIATE TECHNICAL DISCOVERY
          </span>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight mb-6">
            Have a mission-critical software project in mind?
          </h2>
          <p className="text-base sm:text-lg text-[#94A3B8] leading-relaxed mb-8">
            Schedule an initial 30-minute discovery consultation directly with our Lead Solutions Architects. No aggressive sales pitch — just straightforward architectural exploration.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <button
              onClick={() => setActiveTab('contact')}
              className="btn-accent text-base py-3.5 px-8"
            >
              Schedule Discovery Call →
            </button>
            <button
              onClick={() => setActiveTab('services')}
              className="btn-secondary bg-[#1E293B] text-white border-[#334155] hover:bg-[#334155] text-base py-3.5 px-8"
            >
              Review Engagement Models
            </button>
          </div>
          <div className="pt-8 text-xs text-[#64748B] flex items-center justify-center gap-2">
            <ShieldCheck className="w-4 h-4 text-[#10B981]" />
            <span>All inquiries protected under automatic bilateral Non-Disclosure Agreement (NDA)</span>
          </div>
        </div>
      </section>

    </div>
  );
};
