import React, { useState, useMemo } from 'react';
import {
  User,
  LayoutGrid,
  Table as TableIcon,
  Search,
  ChevronDown,
  ChevronUp,
  MapPin,
  Mail,
  Calendar,
  Briefcase,
  Hash,
  Sparkles,
  ExternalLink,
} from 'lucide-react';

interface AIMarkdownRendererProps {
  content: string;
  className?: string;
}

// Parses inline Markdown elements (bold, italic, code, links)
export function parseInline(text: string): React.ReactNode {
  if (!text) return null;

  const regex = /(`[^`]+`)|(\*\*[^*]+\*\*)|(\*[^*]+\*)|(\[([^\]]+)\]\(([^)]+)\))/g;

  const parts: React.ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  let keyIdx = 0;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }

    const [full, codeMatch, boldMatch, italicMatch, linkMatch, linkText, linkUrl] = match;

    if (codeMatch) {
      const codeStr = codeMatch.slice(1, -1);
      parts.push(
        <code
          key={keyIdx++}
          className="rounded px-1.5 py-0.5 bg-slate-900 text-emerald-400 font-mono text-[11px] border border-slate-700/60"
        >
          {codeStr}
        </code>
      );
    } else if (boldMatch) {
      const boldText = boldMatch.slice(2, -2);
      parts.push(
        <strong key={keyIdx++} className="font-semibold text-white">
          {parseInline(boldText)}
        </strong>
      );
    } else if (italicMatch) {
      const italicText = italicMatch.slice(1, -1);
      parts.push(
        <em key={keyIdx++} className="italic text-slate-300">
          {parseInline(italicText)}
        </em>
      );
    } else if (linkMatch) {
      parts.push(
        <a
          key={keyIdx++}
          href={linkUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="text-emerald-400 hover:underline underline-offset-2 transition-colors font-medium"
        >
          {linkText}
        </a>
      );
    } else {
      parts.push(full);
    }

    lastIndex = regex.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }

  return parts.length > 0 ? parts : text;
}

// Format status badge pill
function renderStatusPill(val: string) {
  const s = val.toUpperCase().trim();
  if (['ACTIVE', 'APPROVED', 'COMPLETED', 'SUCCESS', 'ON_TRACK', 'ONLINE'].includes(s)) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
        {val}
      </span>
    );
  }
  if (['PENDING', 'IN_PROGRESS', 'REVIEW', 'WARNING', 'ON_LEAVE', 'AWAITING'].some(k => s.includes(k))) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/15 text-amber-400 border border-amber-500/30">
        <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
        {val}
      </span>
    );
  }
  if (['REJECTED', 'INACTIVE', 'TERMINATED', 'FAILED', 'OFFLINE', 'ABSENT'].some(k => s.includes(k))) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/15 text-rose-400 border border-rose-500/30">
        <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
        {val}
      </span>
    );
  }
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-800 text-slate-300 border border-slate-700">
      {val}
    </span>
  );
}

// Helper to get initials
function getInitials(nameStr: string) {
  const cleaned = nameStr.replace(/[^a-zA-Z\s]/g, '').trim();
  if (!cleaned) return 'ID';
  const words = cleaned.split(/\s+/);
  if (words.length >= 2) {
    return (words[0][0] + words[1][0]).toUpperCase();
  }
  return cleaned.slice(0, 2).toUpperCase();
}

// Dedicated Mobile Responsive Cards & Table Component
export const MobileTableOrCards: React.FC<{
  headers: string[];
  rows: string[][];
}> = ({ headers, rows }) => {
  const [viewMode, setViewMode] = useState<'cards' | 'table'>('cards');
  const [isExpanded, setIsExpanded] = useState(false);
  const [filterQuery, setFilterQuery] = useState('');

  const lowerHeaders = useMemo(() => headers.map(h => h.toLowerCase().trim()), [headers]);

  // Find key column roles
  const nameIdx = useMemo(() => {
    let idx = lowerHeaders.findIndex(h => h === 'name' || h.includes('employee name') || h.includes('full name'));
    if (idx === -1) idx = lowerHeaders.findIndex(h => h.includes('name') || h.includes('title') || h.includes('item'));
    if (idx === -1) idx = lowerHeaders.findIndex(h => !h.includes('id') && !h.includes('code'));
    return idx !== -1 ? idx : 0;
  }, [lowerHeaders]);

  const codeIdx = useMemo(() => lowerHeaders.findIndex(h => h.includes('code') || h === 'id' || h.includes('employee id')), [lowerHeaders]);
  const roleIdx = useMemo(() => lowerHeaders.findIndex((h, idx) => idx !== nameIdx && (h.includes('designation') || h.includes('role') || h.includes('position') || h.includes('title'))), [lowerHeaders, nameIdx]);
  const deptIdx = useMemo(() => lowerHeaders.findIndex(h => h.includes('department') || h.includes('dept') || h.includes('team')), [lowerHeaders]);
  const statusIdx = useMemo(() => lowerHeaders.findIndex(h => h.includes('status') || h.includes('state') || h.includes('stage')), [lowerHeaders]);
  const emailIdx = useMemo(() => lowerHeaders.findIndex(h => h.includes('email') || h.includes('mail')), [lowerHeaders]);
  const locIdx = useMemo(() => lowerHeaders.findIndex(h => h.includes('location') || h.includes('city') || h.includes('office')), [lowerHeaders]);
  const dateIdx = useMemo(() => lowerHeaders.findIndex(h => h.includes('date') || h.includes('joined') || h.includes('created')), [lowerHeaders]);
  const typeIdx = useMemo(() => lowerHeaders.findIndex(h => h.includes('type') || h.includes('employment')), [lowerHeaders]);

  // Rows filtered by search
  const filteredRows = useMemo(() => {
    if (!filterQuery.trim()) return rows;
    const q = filterQuery.toLowerCase();
    return rows.filter(row => row.some(cell => cell.toLowerCase().includes(q)));
  }, [rows, filterQuery]);

  const displayLimit = 3;
  const visibleRows = isExpanded || filteredRows.length <= displayLimit ? filteredRows : filteredRows.slice(0, displayLimit);

  // 1. KPI 2-Column Summary Mode
  if (headers.length === 2 && rows.length <= 8) {
    return (
      <div className="my-2.5">
        <div className="flex items-center justify-between mb-1.5 px-0.5">
          <span className="text-[11px] font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-3 h-3 text-emerald-400" />
            Summary Breakdown
          </span>
          <span className="text-[10px] text-slate-500 font-mono">{rows.length} metrics</span>
        </div>
        <div className="grid grid-cols-2 gap-2">
          {rows.map((row, idx) => (
            <div
              key={idx}
              className="bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 rounded-xl p-2.5 flex flex-col justify-between shadow-xs"
            >
              <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider truncate">
                {row[0]}
              </span>
              <span className="text-sm font-bold text-emerald-400 mt-1 truncate">
                {row[1]}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="my-3 space-y-2">
      {/* Executive Control Bar: Count + Search + Cards/Table Toggle */}
      <div className="flex items-center justify-between gap-2 bg-slate-900/90 border border-slate-800 px-2.5 py-1.5 rounded-xl backdrop-blur">
        <div className="flex items-center gap-1.5 shrink-0">
          <User className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-xs font-bold text-white">
            {filteredRows.length} {filteredRows.length === 1 ? 'Record' : 'Records'}
          </span>
        </div>

        {/* Search if > 4 items */}
        {rows.length > 4 && (
          <div className="relative flex-1 max-w-[130px]">
            <Search className="w-3 h-3 absolute left-1.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={filterQuery}
              onChange={(e) => setFilterQuery(e.target.value)}
              placeholder="Quick filter..."
              className="h-6 w-full pl-5 pr-1.5 text-[10px] bg-slate-950 border border-slate-700/80 rounded-lg text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>
        )}

        {/* View mode toggle */}
        <div className="flex items-center bg-slate-950 p-0.5 rounded-lg border border-slate-800 shrink-0">
          <button
            onClick={() => setViewMode('cards')}
            className={`flex items-center gap-1 px-2 py-1 rounded-md text-[10px] font-semibold transition-all ${
              viewMode === 'cards'
                ? 'bg-emerald-500/20 text-emerald-400 shadow-xs'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <LayoutGrid className="w-3 h-3" />
            Cards
          </button>
          <button
            onClick={() => setViewMode('table')}
            className={`flex items-center gap-1 px-2 py-1 rounded-md text-[10px] font-semibold transition-all ${
              viewMode === 'table'
                ? 'bg-emerald-500/20 text-emerald-400 shadow-xs'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <TableIcon className="w-3 h-3" />
            Table
          </button>
        </div>
      </div>

      {/* Mode A: Native Mobile Executive Cards */}
      {viewMode === 'cards' ? (
        <div className="space-y-2">
          {visibleRows.map((row, rIdx) => {
            const primaryName = row[nameIdx] || 'Employee Record';
            const codeVal = codeIdx !== -1 ? row[codeIdx] : null;
            const roleVal = roleIdx !== -1 ? row[roleIdx] : null;
            const deptVal = deptIdx !== -1 ? row[deptIdx] : null;
            const statusVal = statusIdx !== -1 ? row[statusIdx] : null;
            const emailVal = emailIdx !== -1 ? row[emailIdx] : null;
            const locVal = locIdx !== -1 ? row[locIdx] : null;
            const dateVal = dateIdx !== -1 ? row[dateIdx] : null;
            const typeVal = typeIdx !== -1 ? row[typeIdx] : null;

            // Extra fields not highlighted above
            const usedIndices = new Set([nameIdx, codeIdx, roleIdx, deptIdx, statusIdx, emailIdx, locIdx, dateIdx, typeIdx]);
            const extraFields = headers
              .map((h, i) => ({ header: h, value: row[i] }))
              .filter((_, i) => !usedIndices.has(i) && row[i] && row[i] !== '--');

            return (
              <div
                key={rIdx}
                className="bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-800/90 rounded-xl p-3 shadow-md hover:border-slate-700 transition-all space-y-2"
              >
                {/* Top Row: Avatar + Name/Role + Status Pill */}
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2.5 min-w-0">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-emerald-600 to-teal-500 text-white font-bold text-xs flex items-center justify-center shrink-0 shadow-inner">
                      {getInitials(primaryName)}
                    </div>
                    <div className="min-w-0">
                      <div className="text-xs font-bold text-white tracking-tight truncate">
                        {primaryName}
                      </div>
                      {(roleVal || deptVal) && (
                        <div className="text-[11px] text-slate-400 truncate">
                          {roleVal}
                          {roleVal && deptVal && ' · '}
                          {deptVal}
                        </div>
                      )}
                    </div>
                  </div>

                  {statusVal && <div className="shrink-0">{renderStatusPill(statusVal)}</div>}
                </div>

                {/* Middle Row: Key Badges (Code, Location, Type, Date) */}
                <div className="flex flex-wrap gap-1.5 pt-0.5">
                  {codeVal && (
                    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md text-[10px] font-mono bg-slate-800/80 text-emerald-300 border border-slate-700/60">
                      <Hash className="w-2.5 h-2.5 text-emerald-400" />
                      {codeVal}
                    </span>
                  )}
                  {locVal && (
                    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md text-[10px] bg-slate-800/60 text-slate-300 border border-slate-700/50">
                      <MapPin className="w-2.5 h-2.5 text-slate-400" />
                      {locVal}
                    </span>
                  )}
                  {typeVal && (
                    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md text-[10px] bg-slate-800/60 text-slate-300 border border-slate-700/50">
                      <Briefcase className="w-2.5 h-2.5 text-slate-400" />
                      {typeVal}
                    </span>
                  )}
                  {dateVal && (
                    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md text-[10px] bg-slate-800/60 text-slate-300 border border-slate-700/50">
                      <Calendar className="w-2.5 h-2.5 text-slate-400" />
                      {dateVal}
                    </span>
                  )}
                </div>

                {/* Bottom Row: Direct Email Action + Extra Info */}
                {(emailVal || extraFields.length > 0) && (
                  <div className="pt-1 border-t border-slate-800/70 flex flex-wrap items-center justify-between gap-1.5 text-[10px]">
                    {emailVal && (
                      <a
                        href={`mailto:${emailVal}`}
                        className="inline-flex items-center gap-1 text-slate-300 hover:text-emerald-400 transition-colors"
                      >
                        <Mail className="w-2.5 h-2.5 text-slate-400" />
                        <span className="truncate max-w-[200px]">{emailVal}</span>
                      </a>
                    )}
                    {extraFields.map((f, fIdx) => (
                      <span key={fIdx} className="text-slate-400">
                        <strong className="text-slate-300 font-semibold">{f.header}:</strong> {f.value}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            );
          })}

          {/* Expand / Collapse Button if rows > displayLimit */}
          {filteredRows.length > displayLimit && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="w-full py-2 px-3 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 text-xs font-semibold text-emerald-400 hover:text-emerald-300 flex items-center justify-center gap-1.5 transition-all shadow-xs"
            >
              {isExpanded ? (
                <>
                  <ChevronUp className="w-3.5 h-3.5" />
                  Show less (displaying all {filteredRows.length})
                </>
              ) : (
                <>
                  <ChevronDown className="w-3.5 h-3.5" />
                  Show all {filteredRows.length} records ({filteredRows.length - displayLimit} more)
                </>
              )}
            </button>
          )}
        </div>
      ) : (
        /* Mode B: Raw Table with Horizontal Scroll */
        <div className="overflow-hidden rounded-xl border border-slate-700/80 bg-slate-900/90 shadow-md">
          <div className="overflow-x-auto no-scrollbar max-h-72">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-800/80 border-b border-slate-700 text-slate-300 font-semibold tracking-wide sticky top-0 backdrop-blur">
                  {headers.map((th, thIdx) => (
                    <th key={thIdx} className="py-2 px-3 text-[11px] font-semibold tracking-wider text-slate-300 uppercase whitespace-nowrap">
                      {parseInline(th)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filteredRows.map((row, rIdx) => (
                  <tr
                    key={rIdx}
                    className={`transition-colors duration-150 ${
                      rIdx % 2 === 0 ? 'bg-transparent' : 'bg-slate-800/30'
                    } hover:bg-slate-800/60`}
                  >
                    {row.map((cell, cIdx) => (
                      <td key={cIdx} className="py-2 px-3 text-slate-200 text-xs leading-relaxed whitespace-nowrap">
                        {cIdx === statusIdx ? renderStatusPill(cell) : parseInline(cell)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export const AIMarkdownRenderer: React.FC<AIMarkdownRendererProps> = ({ content, className = '' }) => {
  if (!content) return null;

  const lines = content.split('\n');
  const nodes: React.ReactNode[] = [];
  let i = 0;
  let keyCount = 0;

  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();

    // 1. Empty lines
    if (trimmed === '') {
      i++;
      continue;
    }

    // 2. Fenced code block (```lang)
    if (trimmed.startsWith('```')) {
      const lang = trimmed.slice(3).trim();
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].trim().startsWith('```')) {
        codeLines.push(lines[i]);
        i++;
      }
      if (i < lines.length && lines[i].trim().startsWith('```')) {
        i++; // skip closing ```
      }
      nodes.push(
        <div key={`code-${keyCount++}`} className="my-2 rounded-lg overflow-hidden border border-slate-700 bg-slate-950 p-2.5 text-xs font-mono text-emerald-300 overflow-x-auto">
          {lang && <div className="text-[10px] uppercase font-bold text-slate-400 mb-1">{lang}</div>}
          <pre className="whitespace-pre">{codeLines.join('\n')}</pre>
        </div>
      );
      continue;
    }

    // 3. Markdown Table (| header | header |) -> Rendered via MobileTableOrCards
    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      const tableLines: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith('|') && lines[i].trim().endsWith('|')) {
        tableLines.push(lines[i].trim());
        i++;
      }

      if (tableLines.length >= 2) {
        const rawHeaders = tableLines[0]
          .split('|')
          .slice(1, -1)
          .map((c) => c.trim());

        const rows: string[][] = [];
        for (let r = 2; r < tableLines.length; r++) {
          const cells = tableLines[r]
            .split('|')
            .slice(1, -1)
            .map((c) => c.trim());
          rows.push(cells);
        }

        nodes.push(
          <MobileTableOrCards
            key={`tbl-${keyCount++}`}
            headers={rawHeaders}
            rows={rows}
          />
        );
        continue;
      }
    }

    // 4. Headings (#, ##, ###, ####)
    if (trimmed.startsWith('#')) {
      const headingMatch = trimmed.match(/^(#{1,6})\s+(.*)$/);
      if (headingMatch) {
        const level = headingMatch[1].length;
        const text = headingMatch[2];

        if (level === 1) {
          nodes.push(
            <h1 key={`h1-${keyCount++}`} className="text-sm font-bold text-white mt-3 mb-1 flex items-center gap-1.5 border-b border-slate-800 pb-1">
              {parseInline(text)}
            </h1>
          );
        } else if (level === 2) {
          nodes.push(
            <h2 key={`h2-${keyCount++}`} className="text-xs font-bold text-white mt-2 mb-1 flex items-center gap-1.5">
              {parseInline(text)}
            </h2>
          );
        } else {
          nodes.push(
            <h3 key={`h3-${keyCount++}`} className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider mt-2 mb-1 flex items-center gap-1.5">
              {parseInline(text)}
            </h3>
          );
        }
        i++;
        continue;
      }
    }

    // 5. Blockquote (> quote)
    if (trimmed.startsWith('>')) {
      const quoteLines: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith('>')) {
        quoteLines.push(lines[i].trim().replace(/^>\s?/, ''));
        i++;
      }
      nodes.push(
        <div key={`quote-${keyCount++}`} className="my-2 border-l-2 border-emerald-500 bg-emerald-950/20 px-3 py-1.5 rounded-r-lg text-xs text-slate-300 italic">
          {quoteLines.map((ql, qIdx) => (
            <p key={qIdx}>{parseInline(ql)}</p>
          ))}
        </div>
      );
      continue;
    }

    // 6. Bullet lists (* item, - item)
    if (trimmed.startsWith('* ') || trimmed.startsWith('- ')) {
      const listItems: string[] = [];
      while (i < lines.length && (lines[i].trim().startsWith('* ') || lines[i].trim().startsWith('- '))) {
        listItems.push(lines[i].trim().replace(/^[\*\-]\s+/, ''));
        i++;
      }
      nodes.push(
        <ul key={`ul-${keyCount++}`} className="my-1.5 space-y-1 pl-1">
          {listItems.map((item, idx) => (
            <li key={idx} className="text-xs text-slate-200 flex items-start gap-2 leading-relaxed">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 flex-shrink-0" />
              <div className="flex-1">{parseInline(item)}</div>
            </li>
          ))}
        </ul>
      );
      continue;
    }

    // 7. Numbered list (1. item)
    if (/^\d+\.\s+/.test(trimmed)) {
      const listItems: string[] = [];
      while (i < lines.length && /^\d+\.\s+/.test(lines[i].trim())) {
        listItems.push(lines[i].trim().replace(/^\d+\.\s+/, ''));
        i++;
      }
      nodes.push(
        <ol key={`ol-${keyCount++}`} className="my-1.5 space-y-1 pl-1">
          {listItems.map((item, idx) => (
            <li key={idx} className="text-xs text-slate-200 flex items-start gap-2 leading-relaxed">
              <span className="w-4 h-4 rounded bg-slate-800 text-emerald-400 border border-slate-700 text-[10px] font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                {idx + 1}
              </span>
              <div className="flex-1">{parseInline(item)}</div>
            </li>
          ))}
        </ol>
      );
      continue;
    }

    // 8. Standard paragraph text
    nodes.push(
      <p key={`p-${keyCount++}`} className="text-xs text-slate-200 leading-relaxed my-1">
        {parseInline(line)}
      </p>
    );
    i++;
  }

  return <div className={`space-y-1 ${className}`}>{nodes}</div>;
};
