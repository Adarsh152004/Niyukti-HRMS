import React, { useState } from 'react';
import { Menu, X, ArrowUpRight, ShieldCheck } from './Icons';
import { Link, useRouter } from '../context/RouterContext';

interface NavigationProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onOpenJobDetail?: (jobId: string) => void;
}

export const Navigation: React.FC<NavigationProps> = ({ activeTab }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { navigate } = useRouter();

  const navItems = [
    { id: 'home', path: '/', label: 'Home' },
    { id: 'services', path: '/services', label: 'Services' },
    { id: 'work', path: '/work', label: 'Work' },
    { id: 'about', path: '/about', label: 'About' },
    { id: 'careers', path: '/careers', label: 'Careers', badge: '6 Openings' },
    { id: 'contact', path: '/contact', label: 'Contact' }
  ];

  return (
    <header className="sticky top-0 z-50 bg-[#FFFFFF]/95 backdrop-blur-md border-b border-[#E2E8F0] transition-all">
      <div className="container-custom">
        <div className="flex items-center justify-between h-20">
          
          {/* Brand Logo & Studio Identity */}
          <div className="flex items-center gap-6">
            <Link 
              href="/"
              className="flex items-center gap-2.5 text-left group focus:outline-none"
            >
              <div className="w-8 h-8 bg-[#0F172A] rounded-[4px] flex items-center justify-center text-white font-bold text-sm tracking-tight transition-transform group-hover:scale-105">
                <span className="text-[#0047FF]">▲</span>
              </div>
              <div>
                <span className="font-display font-extrabold text-lg tracking-tight text-[#0F172A] block leading-none">
                  AZYNTRIX
                </span>
                <span className="font-mono-spec text-[10px] text-[#64748B] tracking-wider uppercase block mt-0.5">
                  Software Engineering
                </span>
              </div>
            </Link>

            {/* Subtle System Status Beacon */}
            <div className="hidden xl:flex items-center gap-2 pl-4 border-l border-[#E2E8F0] py-1 text-xs text-[#64748B]">
              <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse"></span>
              <span className="font-mono text-[11px]">Deploy Ready · v2.4.0</span>
            </div>
          </div>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-1 lg:gap-2">
            {navItems.map((item) => {
              const isActive = activeTab === item.id;
              return (
                <Link
                  key={item.id}
                  href={item.path}
                  className={`relative px-3.5 py-2 rounded-[4px] text-sm font-medium transition-colors flex items-center gap-1.5 ${
                    isActive 
                      ? 'text-[#0F172A] font-semibold bg-[#F1F5F9]' 
                      : 'text-[#475569] hover:text-[#0F172A] hover:bg-[#F8FAFC]'
                  }`}
                >
                  {item.label}
                  {item.badge && (
                    <span className="bg-[#EFF6FF] text-[#0047FF] border border-[#BFDBFE] text-[10px] font-bold px-1.5 py-0.5 rounded-[3px] tracking-tight">
                      {item.badge}
                    </span>
                  )}
                  {isActive && (
                    <span className="absolute bottom-0 left-3.5 right-3.5 h-[2px] bg-[#0F172A] rounded-full" />
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Header Action Buttons */}
          <div className="hidden md:flex items-center gap-3">
            <Link
              href="/contact"
              className="btn-primary"
            >
              Start a Project
              <ArrowUpRight className="w-4 h-4 text-[#94A3B8]" />
            </Link>
          </div>

          {/* Mobile Menu Toggle Button */}
          <div className="flex md:hidden items-center gap-2">
            <Link
              href="/contact"
              className="btn-primary text-xs py-2 px-3"
            >
              Start
            </Link>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2.5 rounded-[4px] border border-[#E2E8F0] bg-white text-[#0F172A] hover:bg-[#F8FAFC]"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer Navigation */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-[#E2E8F0] bg-white px-6 py-6 shadow-xl animate-fadeIn">
          <div className="flex flex-col gap-2">
            {navItems.map((item) => {
              const isActive = activeTab === item.id;
              return (
                <Link
                  key={item.id}
                  href={item.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center justify-between px-4 py-3 rounded-[4px] text-base font-medium transition-colors text-left ${
                    isActive 
                      ? 'bg-[#F1F5F9] text-[#0F172A] font-bold' 
                      : 'text-[#475569] hover:bg-[#F8FAFC] hover:text-[#0F172A]'
                  }`}
                >
                  <span>{item.label}</span>
                  {item.badge ? (
                    <span className="bg-[#EFF6FF] text-[#0047FF] border border-[#BFDBFE] text-xs font-semibold px-2 py-0.5 rounded-[3px]">
                      {item.badge}
                    </span>
                  ) : (
                    <ArrowUpRight className="w-4 h-4 text-[#94A3B8]" />
                  )}
                </Link>
              );
            })}
            <div className="pt-4 mt-2 border-t border-[#E2E8F0] flex flex-col gap-2">
              <Link
                href="/contact"
                onClick={() => setMobileMenuOpen(false)}
                className="btn-primary w-full py-3.5 text-center justify-center text-sm"
              >
                Initiate Project Discovery →
              </Link>
              <div className="flex items-center justify-center gap-2 pt-2 text-xs text-[#64748B]">
                <ShieldCheck className="w-4 h-4 text-[#10B981]" />
                <span>Strict Bilateral NDA Enforced</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};
