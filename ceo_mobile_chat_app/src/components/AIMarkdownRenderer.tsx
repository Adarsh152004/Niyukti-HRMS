import React from 'react';

interface AIMarkdownRendererProps {
  content: string;
  className?: string;
}

// Parses inline Markdown elements (bold, italic, code, links)
export function parseInline(text: string): React.ReactNode {
  if (!text) return null;

  // Regex for inline elements
  // 1: `code`
  // 2: **bold**
  // 3: *italic*
  // 4: [text](url)
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

    // 3. Markdown Table (| header | header |)
    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      const tableLines: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith('|') && lines[i].trim().endsWith('|')) {
        tableLines.push(lines[i].trim());
        i++;
      }

      if (tableLines.length >= 2) {
        // Parse header
        const rawHeaders = tableLines[0]
          .split('|')
          .slice(1, -1)
          .map((c) => c.trim());

        // Parse rows (skipping index 1 delimiter row)
        const rows: string[][] = [];
        for (let r = 2; r < tableLines.length; r++) {
          const cells = tableLines[r]
            .split('|')
            .slice(1, -1)
            .map((c) => c.trim());
          rows.push(cells);
        }

        nodes.push(
          <div key={`tbl-${keyCount++}`} className="my-2.5 overflow-hidden rounded-xl border border-slate-700/80 bg-slate-900/90 shadow-md">
            <div className="overflow-x-auto no-scrollbar">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-800/80 border-b border-slate-700 text-slate-300 font-semibold tracking-wide">
                    {rawHeaders.map((th, thIdx) => (
                      <th key={thIdx} className="py-2 px-3 text-[11px] font-semibold tracking-wider text-slate-300 uppercase whitespace-nowrap">
                        {parseInline(th)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {rows.map((row, rIdx) => (
                    <tr
                      key={rIdx}
                      className={`transition-colors duration-150 ${
                        rIdx % 2 === 0 ? 'bg-transparent' : 'bg-slate-800/30'
                      } hover:bg-slate-800/60`}
                    >
                      {row.map((cell, cIdx) => (
                        <td key={cIdx} className="py-2 px-3 text-slate-200 text-xs leading-relaxed whitespace-nowrap">
                          {parseInline(cell)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
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
            <h1 key={`h1-${keyCount++}`} className="text-base font-bold text-white mt-3 mb-1.5 flex items-center gap-1.5 border-b border-slate-700/60 pb-1">
              {parseInline(text)}
            </h1>
          );
        } else if (level === 2) {
          nodes.push(
            <h2 key={`h2-${keyCount++}`} className="text-sm font-bold text-white mt-2.5 mb-1 flex items-center gap-1.5">
              {parseInline(text)}
            </h2>
          );
        } else {
          nodes.push(
            <h3 key={`h3-${keyCount++}`} className="text-xs font-bold text-emerald-400 uppercase tracking-wider mt-2 mb-1 flex items-center gap-1.5">
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
