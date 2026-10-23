import React from 'react';
import { ArrowLeft, Terminal, Shield } from '../components/Icons';
import { Link } from '../context/RouterContext';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-[70vh] flex items-center justify-center py-20 px-4">
      <div className="max-w-xl w-full text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#FEF2F2] border border-[#FCA5A5]/40 text-[#DC2626] font-mono text-xs font-semibold mb-6">
          <Terminal size={14} />
          <span>HTTP 404 • ROUTE_NOT_RESOLVED</span>
        </div>

        <h1 className="font-display font-extrabold text-5xl sm:text-6xl text-[#0F172A] tracking-tight mb-4">
          Route Not Found.
        </h1>

        <p className="text-[#64748B] text-lg mb-8 leading-relaxed">
          The requested coordinate does not map to any active practice area, case study, or guild position.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link 
            href="/"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 bg-[#0F172A] text-white font-medium text-sm rounded-[4px] hover:bg-[#0047FF] transition-colors"
          >
            <ArrowLeft size={16} />
            <span>Return to Studio Home</span>
          </Link>

          <Link 
            href="/services"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 bg-white text-[#0F172A] border border-[#E2E8F0] font-medium text-sm rounded-[4px] hover:bg-[#F8FAFC] transition-colors"
          >
            <span>Explore Practice Areas</span>
          </Link>
        </div>

        <div className="mt-12 pt-8 border-t border-[#E2E8F0] flex items-center justify-center gap-2 text-xs font-mono text-[#94A3B8]">
          <Shield size={14} className="text-[#10B981]" />
          <span>AZYNTRIX ROUTER ENGINE • ZERO DEADLOCKS GUARANTEED</span>
        </div>
      </div>
    </div>
  );
};
