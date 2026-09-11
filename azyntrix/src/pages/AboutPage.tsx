import React from 'react';
import { ArrowRight, ShieldCheck, Terminal, Users, Globe2, Sparkles, Check, Code, Clock } from '../components/Icons';

interface AboutPageProps {
  setActiveTab: (tab: string) => void;
}

export const AboutPage: React.FC<AboutPageProps> = ({ setActiveTab }) => {
  return (
    <div className="fade-in">
      
      {/* About Hero Header */}
      <section className="py-16 lg:py-24 bg-white border-b border-[#E2E8F0]">
        <div className="container-custom">
          <div className="max-w-3xl">
            <span className="font-mono text-xs uppercase tracking-wider text-[#0047FF] font-bold block mb-3">
              ABOUT AZYNTRIX // STUDIO PHILOSOPHY
            </span>
            <h1 className="text-4xl sm:text-5xl font-extrabold text-[#0F172A] tracking-tight mb-6 leading-tight">
              Crafting production-grade software through remote-first engineering mastery.
            </h1>
            <p className="text-lg text-[#475569] leading-relaxed mb-8">
              Founded on the conviction that high-performing software requires senior talent, absolute transparency, asynchronous discipline, and zero agency fluff.
            </p>

            {/* Vital Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px]">
              <div>
                <span className="font-mono font-bold text-lg text-[#0F172A] block">2021</span>
                <span className="text-[11px] text-[#64748B]">Founded & Self-Sustaining</span>
              </div>
              <div>
                <span className="font-mono font-bold text-lg text-[#0F172A] block">14 Countries</span>
                <span className="text-[11px] text-[#64748B]">100% Remote Guild</span>
              </div>
              <div>
                <span className="font-mono font-bold text-lg text-[#0F172A] block">99.4%</span>
                <span className="text-[11px] text-[#64748B]">Client Retention Rate</span>
              </div>
              <div>
                <span className="font-mono font-bold text-lg text-[#0F172A] block">Zero</span>
                <span className="text-[11px] text-[#64748B]">Junior Billing Pyramids</span>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* Origin Story Narrative & Executable Manifesto */}
      <section className="py-20 bg-[#F8FAFC] border-b border-[#E2E8F0]">
        <div className="container-custom">
          
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
            
            {/* Story Narrative */}
            <div className="lg:col-span-6 space-y-6">
              <span className="font-mono text-xs uppercase tracking-wider text-[#64748B] font-bold block">
                OUR ORIGIN & PURPOSE
              </span>
              <h2 className="text-3xl font-extrabold text-[#0F172A] leading-tight">
                Born in the cloud, built for global enterprise scale.
              </h2>
              <div className="space-y-4 text-base text-[#475569] leading-relaxed">
                <p>
                  Traditional software agencies operate on a broken model: senior partners sell the engagement, and junior generalists with minimal production experience write the code. Deadlines slip, architectures crumble under scale, and clients inherit mountains of technical debt.
                </p>
                <p>
                  Azyntrix was founded to operate as an elite engineering guild. We assemble dedicated, cross-functional squads composed exclusively of Staff and Senior software engineers, distributed systems architects, and meticulous product designers.
                </p>
                <p>
                  We collaborate asynchronously across 14+ countries, giving our clients around-the-clock engineering momentum, transparent pull requests, and production code that stands the test of time.
                </p>
              </div>
            </div>

            {/* Engineering Manifesto Terminal Card */}
            <div className="lg:col-span-6">
              <div className="bg-[#0F172A] text-white rounded-[6px] border border-[#1E293B] shadow-xl overflow-hidden font-mono text-xs">
                
                {/* Terminal Header */}
                <div className="bg-[#1E293B] px-4 py-3 flex items-center justify-between border-b border-[#334155]">
                  <div className="flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-[#38BDF8]" />
                    <span className="text-[#94A3B8] text-[11px]">engineering_manifesto.ts</span>
                  </div>
                  <span className="text-[10px] text-[#10B981] bg-[#064E3B] px-2 py-0.5 rounded">
                    Passed Strict TypeCheck
                  </span>
                </div>

                {/* Code Content */}
                <div className="p-5 space-y-2 text-[#CBD5E1] leading-relaxed">
                  <p><span className="text-[#818CF8]">export const</span> <span className="text-[#38BDF8]">AzyntrixStandard</span> = &#123;</p>
                  <p className="pl-4"><span className="text-[#94A3B8]">seniorEngineeringOnly:</span> <span className="text-[#F472B6]">true</span>,</p>
                  <p className="pl-4"><span className="text-[#94A3B8]">asynchronousByDesign:</span> <span className="text-[#F472B6]">true</span>,</p>
                  <p className="pl-4"><span className="text-[#94A3B8]">strictTypeScript:</span> <span className="text-[#F472B6]">true</span>,</p>
                  <p className="pl-4"><span className="text-[#94A3B8]">testDrivenCoverageSLO:</span> <span className="text-[#34D399]">0.95</span>,</p>
                  <p className="pl-4"><span className="text-[#94A3B8]">zeroTechnicalDebtTolerance:</span> <span className="text-[#F472B6]">true</span>,</p>
                  <p className="pl-4"><span className="text-[#94A3B8]">clientDirectAccessToGit:</span> <span className="text-[#F472B6]">true</span>,</p>
                  <p className="pl-4"><span className="text-[#94A3B8]">slas:</span> &#123;</p>
                  <p className="pl-8"><span className="text-[#94A3B8]">targetMedianTTFB:</span> <span className="text-[#FBBF24]">'&lt; 65ms'</span>,</p>
                  <p className="pl-8"><span className="text-[#94A3B8]">uptimeTarget:</span> <span className="text-[#34D399]">0.99999</span></p>
                  <p className="pl-4">&#125;</p>
                  <p>&#125; <span className="text-[#818CF8]">as const</span>;</p>
                  
                  <div className="pt-3 border-t border-[#1E293B] text-[11px] text-[#64748B]">
                    // Verified across 40+ production enterprise deployments
                  </div>
                </div>

              </div>
            </div>

          </div>

        </div>
      </section>

      {/* 6 Core Operating Values */}
      <section className="py-20 lg:py-28 bg-white border-b border-[#E2E8F0]">
        <div className="container-custom">
          
          <div className="max-w-2xl mb-16">
            <span className="font-mono text-xs uppercase tracking-wider text-[#0047FF] font-bold block mb-2">
              OUR CORE TENETS
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-[#0F172A] tracking-tight mb-4">
              Six engineering values that guide every line of code.
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            
            <div className="p-8 bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px]">
              <span className="font-mono text-xs font-bold text-[#0047FF] block mb-2">01 // CRAFTSMANSHIP</span>
              <h3 className="text-xl font-bold text-[#0F172A] mb-3">Craftsmanship Over Velocity</h3>
              <p className="text-sm text-[#475569] leading-relaxed">
                We write clean, test-driven, and maintainable software that scales gracefully. Fast hacks create technical debt; disciplined engineering builds compound enterprise value.
              </p>
            </div>

            <div className="p-8 bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px]">
              <span className="font-mono text-xs font-bold text-[#0047FF] block mb-2">02 // AUTONOMY</span>
              <h3 className="text-xl font-bold text-[#0F172A] mb-3">Asynchronous by Default</h3>
              <p className="text-sm text-[#475569] leading-relaxed">
                Deep focus time and high-context documentation over endless Zoom calls. High-trust written context empowers senior engineers to do their life’s best work.
              </p>
            </div>

            <div className="p-8 bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px]">
              <span className="font-mono text-xs font-bold text-[#0047FF] block mb-2">03 // TRANSPARENCY</span>
              <h3 className="text-xl font-bold text-[#0F172A] mb-3">Radical Code Transparency</h3>
              <p className="text-sm text-[#475569] leading-relaxed">
                Our clients have real-time access to our GitHub repositories, pull requests, automated staging environments, and sprint telemetry metrics from day one.
              </p>
            </div>

            <div className="p-8 bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px]">
              <span className="font-mono text-xs font-bold text-[#0047FF] block mb-2">04 // EVOLUTION</span>
              <h3 className="text-xl font-bold text-[#0F172A] mb-3">Continuous Stack Evolution</h3>
              <p className="text-sm text-[#475569] leading-relaxed">
                We invest heavily in evaluating modern cloud-native patterns, language runtimes (Go, Rust, TypeScript), and edge computing frameworks to give clients a competitive edge.
              </p>
            </div>

            <div className="p-8 bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px]">
              <span className="font-mono text-xs font-bold text-[#0047FF] block mb-2">05 // PARTNERSHIP</span>
              <h3 className="text-xl font-bold text-[#0F172A] mb-3">Partnership as Peers</h3>
              <p className="text-sm text-[#475569] leading-relaxed">
                We act as senior technical co-founders and advisors rather than transactional contract workers. We challenge assumptions to ensure the best architectural outcome.
              </p>
            </div>

            <div className="p-8 bg-[#F8FAFC] border border-[#E2E8F0] rounded-[4px]">
              <span className="font-mono text-xs font-bold text-[#0047FF] block mb-2">06 // SECURITY</span>
              <h3 className="text-xl font-bold text-[#0F172A] mb-3">Zero-Trust Security by Default</h3>
              <p className="text-sm text-[#475569] leading-relaxed">
                Strict data governance, encrypted communication pipelines, automated CVE scanning, and adherence to SOC2 and ISO 27001 standards are baked into our builds.
              </p>
            </div>

          </div>

        </div>
      </section>

      {/* Leadership / Architects Spotlight */}
      <section className="py-20 bg-[#F8FAFC] border-b border-[#E2E8F0]">
        <div className="container-custom">
          
          <div className="max-w-2xl mb-16">
            <span className="font-mono text-xs uppercase tracking-wider text-[#0047FF] font-bold block mb-2">
              LEADERSHIP & GUILD ARCHITECTS
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-[#0F172A] tracking-tight mb-4">
              Practitioners leading from the terminal.
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            
            <div className="p-6 bg-white border border-[#E2E8F0] rounded-[4px]">
              <div className="w-12 h-12 bg-[#0F172A] rounded-[4px] flex items-center justify-center text-white font-bold text-base mb-4">
                AV
              </div>
              <h4 className="font-bold text-base text-[#0F172A]">Dr. Alex Vance</h4>
              <span className="text-xs text-[#0047FF] font-semibold block mb-2">Co-Founder & Chief Systems Architect</span>
              <p className="text-xs text-[#64748B] leading-relaxed mb-3">
                15+ years scaling distributed systems. Former Principal Infrastructure Engineer at AWS Cloud.
              </p>
              <div className="font-mono text-[10px] text-[#0F172A] bg-[#F1F5F9] px-2 py-1 rounded inline-block">
                Focus: Go · Distributed DBs · Kafka
              </div>
            </div>

            <div className="p-6 bg-white border border-[#E2E8F0] rounded-[4px]">
              <div className="w-12 h-12 bg-[#0F172A] rounded-[4px] flex items-center justify-center text-white font-bold text-base mb-4">
                ER
              </div>
              <h4 className="font-bold text-base text-[#0F172A]">Elena Rostova</h4>
              <span className="text-xs text-[#0047FF] font-semibold block mb-2">VP of Web Engineering & Platform</span>
              <p className="text-xs text-[#64748B] leading-relaxed mb-3">
                Architect of high-traffic frontend platforms. Former Staff Frontend Lead at Stripe Ecosystem.
              </p>
              <div className="font-mono text-[10px] text-[#0F172A] bg-[#F1F5F9] px-2 py-1 rounded inline-block">
                Focus: Next.js 14 · WebAssembly · Performance
              </div>
            </div>

            <div className="p-6 bg-white border border-[#E2E8F0] rounded-[4px]">
              <div className="w-12 h-12 bg-[#0F172A] rounded-[4px] flex items-center justify-center text-white font-bold text-base mb-4">
                MT
              </div>
              <h4 className="font-bold text-base text-[#0F172A]">Marcus Thorne</h4>
              <span className="text-xs text-[#0047FF] font-semibold block mb-2">Head of Cloud & SRE Infrastructure</span>
              <p className="text-xs text-[#64748B] leading-relaxed mb-3">
                Specialist in multi-region Kubernetes resilience. Former Infrastructure Lead at Cloudflare.
              </p>
              <div className="font-mono text-[10px] text-[#0F172A] bg-[#F1F5F9] px-2 py-1 rounded inline-block">
                Focus: Terraform · ArgoCD · Zero-Trust
              </div>
            </div>

            <div className="p-6 bg-white border border-[#E2E8F0] rounded-[4px]">
              <div className="w-12 h-12 bg-[#0F172A] rounded-[4px] flex items-center justify-center text-white font-bold text-base mb-4">
                SL
              </div>
              <h4 className="font-bold text-base text-[#0F172A]">Sarah Lin</h4>
              <span className="text-xs text-[#0047FF] font-semibold block mb-2">Director of UI/UX & Design Systems</span>
              <p className="text-xs text-[#64748B] leading-relaxed mb-3">
                Expert in human cognitive workflows and design token architectures. Former Product Designer at Datadog.
              </p>
              <div className="font-mono text-[10px] text-[#0F172A] bg-[#F1F5F9] px-2 py-1 rounded inline-block">
                Focus: Design Tokens · Figma · Ergonomics
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* Conversion Banner */}
      <section className="py-20 bg-[#0F172A] text-white">
        <div className="container-custom text-center max-w-2xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white mb-4">
            Partner with senior engineers who care about craft.
          </h2>
          <p className="text-base text-[#94A3B8] mb-8">
            Let’s discuss your technical goals and roadmap.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <button onClick={() => setActiveTab('contact')} className="btn-accent text-base py-3.5 px-8">
              Start a Project →
            </button>
            <button onClick={() => setActiveTab('careers')} className="btn-secondary bg-[#1E293B] text-white border-[#334155] hover:bg-[#334155] text-base py-3.5 px-8">
              Join the Engineering Guild
            </button>
          </div>
        </div>
      </section>

    </div>
  );
};
