import React from 'react';
import { ArrowUpRight, Shield, Globe, Terminal } from './Icons';
import { Link } from '../context/RouterContext';

interface FooterProps {
  setActiveTab?: (tab: string) => void;
}

export const Footer: React.FC<FooterProps> = () => {
  return (
    <footer className="bg-[#0F172A] text-white pt-20 pb-12 border-t border-[#1E293B]">
      <div className="container-custom">
        
        {/* Studio Top Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-12 pb-16 border-b border-[#1E293B]">
          
          {/* Column 1: Studio Identity & Positioning */}
          <div className="lg:col-span-2">
            <Link href="/" className="flex items-center gap-2.5 mb-5 group">
              <div className="w-8 h-8 bg-white rounded-[4px] flex items-center justify-center text-[#0F172A] font-bold text-sm transition-transform group-hover:scale-105">
                <span className="text-[#0047FF]">▲</span>
              </div>
              <span className="font-display font-extrabold text-xl tracking-tight text-white">
                AZYNTRIX
              </span>
            </Link>
            <p className="text-[#94A3B8] text-sm leading-relaxed max-w-sm mb-6">
              Azyntrix is an elite software engineering consultancy and digital product studio. We engineer custom web applications, distributed backend systems, and high-performance digital platforms for forward-thinking enterprises.
            </p>
            <div className="flex flex-col gap-2 font-mono text-xs text-[#64748B]">
              <div className="flex items-center gap-2">
                <Globe className="w-3.5 h-3.5 text-[#38BDF8]" />
                <span>Operating Model: 100% Remote & Distributed</span>
              </div>
              <div className="flex items-center gap-2">
                <Shield className="w-3.5 h-3.5 text-[#10B981]" />
                <span>Enterprise SOC2 Type II & Bilateral NDA</span>
              </div>
            </div>
          </div>

          {/* Column 2: Capabilities & Services */}
          <div>
            <h4 className="font-mono-spec uppercase text-xs tracking-wider text-[#94A3B8] font-bold mb-4">
              Practices
            </h4>
            <ul className="space-y-2.5 text-sm text-[#CBD5E1]">
              <li>
                <Link href="/services" className="hover:text-white transition-colors">
                  Web Applications
                </Link>
              </li>
              <li>
                <Link href="/services" className="hover:text-white transition-colors">
                  Custom Enterprise Software
                </Link>
              </li>
              <li>
                <Link href="/services" className="hover:text-white transition-colors">
                  UI/UX Design Systems
                </Link>
              </li>
              <li>
                <Link href="/services" className="hover:text-white transition-colors">
                  Headless E-Commerce
                </Link>
              </li>
              <li>
                <Link href="/services" className="hover:text-white transition-colors">
                  Business Automation & AI
                </Link>
              </li>
              <li>
                <Link href="/services" className="hover:text-white transition-colors">
                  Cloud Infrastructure & SLAs
                </Link>
              </li>
            </ul>
          </div>

          {/* Column 3: Selected Case Studies */}
          <div>
            <h4 className="font-mono-spec uppercase text-xs tracking-wider text-[#94A3B8] font-bold mb-4">
              Case Studies
            </h4>
            <ul className="space-y-2.5 text-sm text-[#CBD5E1]">
              <li>
                <Link href="/work" className="hover:text-white transition-colors flex items-center gap-1">
                  PayGrid Global <ArrowUpRight className="w-3 h-3 text-[#64748B]" />
                </Link>
              </li>
              <li>
                <Link href="/work" className="hover:text-white transition-colors flex items-center gap-1">
                  CarePoint Telehealth <ArrowUpRight className="w-3 h-3 text-[#64748B]" />
                </Link>
              </li>
              <li>
                <Link href="/work" className="hover:text-white transition-colors flex items-center gap-1">
                  AuraCommerce Engine <ArrowUpRight className="w-3 h-3 text-[#64748B]" />
                </Link>
              </li>
              <li>
                <Link href="/work" className="hover:text-white transition-colors flex items-center gap-1">
                  NexusCorp Automation <ArrowUpRight className="w-3 h-3 text-[#64748B]" />
                </Link>
              </li>
            </ul>
          </div>

          {/* Column 4: Studio & Careers */}
          <div>
            <h4 className="font-mono-spec uppercase text-xs tracking-wider text-[#94A3B8] font-bold mb-4">
              Company
            </h4>
            <ul className="space-y-2.5 text-sm text-[#CBD5E1]">
              <li>
                <Link href="/about" className="hover:text-white transition-colors">
                  About Azyntrix
                </Link>
              </li>
              <li>
                <Link href="/careers" className="hover:text-white transition-colors flex items-center gap-1.5">
                  Careers 
                  <span className="bg-[#1E293B] text-[#38BDF8] border border-[#334155] text-[10px] font-bold px-1.5 py-0.5 rounded-[3px]">
                    6 Openings
                  </span>
                </Link>
              </li>
              <li>
                <Link href="/about" className="hover:text-white transition-colors">
                  Engineering Manifesto
                </Link>
              </li>
              <li>
                <Link href="/contact" className="hover:text-white transition-colors">
                  Start a Project
                </Link>
              </li>
              <li>
                <a href="mailto:initiatives@azyntrix.com" className="hover:text-white transition-colors">
                  Security & SOC2
                </a>
              </li>
            </ul>
          </div>

        </div>

        {/* Global Hub Coordinates & Node Status */}
        <div className="py-10 grid grid-cols-2 md:grid-cols-4 gap-6 border-b border-[#1E293B] text-xs font-mono text-[#94A3B8]">
          <div className="space-y-1">
            <span className="text-[#64748B] block uppercase tracking-wider text-[10px]">Node 01 // Pacific</span>
            <p className="font-medium text-[#E2E8F0]">San Francisco, CA</p>
            <span className="text-[11px] text-[#64748B]">37.7749° N, 122.4194° W</span>
          </div>
          <div className="space-y-1">
            <span className="text-[#64748B] block uppercase tracking-wider text-[10px]">Node 02 // Eastern</span>
            <p className="font-medium text-[#E2E8F0]">New York, NY</p>
            <span className="text-[11px] text-[#64748B]">40.7128° N, 74.0060° W</span>
          </div>
          <div className="space-y-1">
            <span className="text-[#64748B] block uppercase tracking-wider text-[10px]">Node 03 // Europe</span>
            <p className="font-medium text-[#E2E8F0]">London, UK</p>
            <span className="text-[11px] text-[#64748B]">51.5074° N, 0.1278° W</span>
          </div>
          <div className="space-y-1">
            <span className="text-[#64748B] block uppercase tracking-wider text-[10px]">Node 04 // Central</span>
            <p className="font-medium text-[#E2E8F0]">Zurich, CH</p>
            <span className="text-[11px] text-[#64748B]">47.3769° N, 8.5417° E</span>
          </div>
        </div>

        {/* Bottom Legal & Telemetry Line */}
        <div className="pt-8 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-[#64748B]">
          <div className="flex items-center gap-6">
            <span>© {new Date().getFullYear()} Azyntrix LLC. All rights reserved.</span>
            <span className="hidden sm:inline">•</span>
            <span className="font-mono text-[11px]">Primary ASN: AS-49120</span>
          </div>

          <div className="flex items-center gap-6">
            <Link href="/contact" className="hover:text-[#94A3B8] transition-colors">Privacy Policy</Link>
            <Link href="/contact" className="hover:text-[#94A3B8] transition-colors">Terms of Engagement</Link>
            <Link href="/contact" className="hover:text-[#94A3B8] transition-colors">Responsible Disclosure</Link>
          </div>
        </div>

      </div>
    </footer>
  );
};
