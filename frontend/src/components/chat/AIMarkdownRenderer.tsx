import React from 'react';
import { CodeBlock } from './CodeBlock';
import { TableRenderer, TableData } from './TableRenderer';
import { Callout, CalloutType } from './Callout';

interface AIMarkdownRendererProps {
  content: string;
  className?: string;
}

// Parses inline Markdown elements (bold, italic, code, links, strikethrough)
export function parseInlineMarkdown(text: string): React.ReactNode {
  if (!text) return null;

  // Regex for inline elements
  // Group 1: `code`
  // Group 2: **bold** or __bold__
  // Group 3: *italic* or _italic_
  // Group 4: ~~strikethrough~~
  // Group 5: [text](url)
  const regex = /(`[^`]+`)|(\*\*[^*]+\*\*|__[^_]+__)|(\*[^*]+\*|_[^_]+_)|(~~[^~]+~~)|(\[([^\]]+)\]\(([^\)]+)\))/g;

  const parts: React.ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  let keyIdx = 0;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }

    const [full, codeMatch, boldMatch, italicMatch, strikeMatch, linkMatch, linkText, linkUrl] = match;

    if (codeMatch) {
      const codeStr = codeMatch.slice(1, -1);
      parts.push(
        <code
          key={keyIdx++}
          className="rounded px-1.5 py-0.5 bg-surface-secondary text-accent font-mono text-[12px] border border-border"
        >
          {codeStr}
        </code>
      );
    } else if (boldMatch) {
      const boldText = boldMatch.slice(2, -2);
      parts.push(
        <strong key={keyIdx++} className="font-semibold text-text-primary">
          {parseInlineMarkdown(boldText)}
        </strong>
      );
    } else if (italicMatch) {
      const italicText = italicMatch.slice(1, -1);
      parts.push(
        <em key={keyIdx++} className="italic text-text-secondary">
          {parseInlineMarkdown(italicText)}
        </em>
      );
    } else if (strikeMatch) {
      const strikeText = strikeMatch.slice(2, -2);
      parts.push(
        <del key={keyIdx++} className="line-through text-text-muted">
          {parseInlineMarkdown(strikeText)}
        </del>
      );
    } else if (linkMatch) {
      parts.push(
        <a
          key={keyIdx++}
          href={linkUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="text-accent hover:underline underline-offset-2 transition-colors inline-flex items-center gap-0.5 font-medium"
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
        <CodeBlock key={`code-${keyCount++}`} code={codeLines.join('\n')} language={lang} />
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

        // Parse delimiter row (:---, :---:, ---:)
        const delimiterCols = tableLines[1]
          .split('|')
          .slice(1, -1)
          .map((c) => c.trim());

        const alignments: ('left' | 'center' | 'right')[] = delimiterCols.map((col) => {
          const starts = col.startsWith(':');
          const ends = col.endsWith(':');
          if (starts && ends) return 'center';
          if (ends) return 'right';
          return 'left';
        });

        // Parse rows
        const rows: string[][] = [];
        for (let r = 2; r < tableLines.length; r++) {
          const cells = tableLines[r]
            .split('|')
            .slice(1, -1)
            .map((c) => c.trim());
          rows.push(cells);
        }

        const tableData: TableData = {
          headers: rawHeaders,
          alignments,
          rows,
        };

        nodes.push(
          <TableRenderer
            key={`tbl-${keyCount++}`}
            table={tableData}
            parseInline={parseInlineMarkdown}
          />
        );
        continue;
      }
    }

    // 4. Horizontal rule (--- or ***)
    if (/^(\-{3,}|\*{3,}|_{3,})$/.test(trimmed)) {
      nodes.push(<hr key={`hr-${keyCount++}`} className="my-5 border-t border-border" />);
      i++;
      continue;
    }

    // 5. Headings (#, ##, ###, ####)
    if (trimmed.startsWith('#')) {
      const headingMatch = trimmed.match(/^(#{1,6})\s+(.*)$/);
      if (headingMatch) {
        const level = headingMatch[1].length;
        const text = headingMatch[2];

        if (level === 1) {
          nodes.push(
            <h1
              key={`h1-${keyCount++}`}
              className="text-xl font-bold tracking-tight text-text-primary mt-6 mb-3 border-b border-border pb-2"
            >
              {parseInlineMarkdown(text)}
            </h1>
          );
        } else if (level === 2) {
          nodes.push(
            <h2
              key={`h2-${keyCount++}`}
              className="text-lg font-bold tracking-tight text-text-primary mt-5 mb-2.5"
            >
              {parseInlineMarkdown(text)}
            </h2>
          );
        } else if (level === 3) {
          nodes.push(
            <h3
              key={`h3-${keyCount++}`}
              className="text-base font-semibold tracking-tight text-text-primary mt-4 mb-2"
            >
              {parseInlineMarkdown(text)}
            </h3>
          );
        } else {
          nodes.push(
            <h4
              key={`h4-${keyCount++}`}
              className="text-sm font-semibold tracking-tight text-text-secondary mt-3 mb-1.5"
            >
              {parseInlineMarkdown(text)}
            </h4>
          );
        }
        i++;
        continue;
      }
    }

    // 6. Blockquote or Callout (> ...)
    if (trimmed.startsWith('>')) {
      const quoteLines: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith('>')) {
        quoteLines.push(lines[i].trim().replace(/^>\s?/, ''));
        i++;
      }
      const quoteText = quoteLines.join('\n');

      // Check for Callout pattern (> **Note:**, > [!NOTE], etc.)
      const calloutMatch = quoteText.match(
        /^(?:\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]|\*\*(Note|Tip|Warning|Important|Success)\:\*\*)\s*(.*)$/is
      );

      if (calloutMatch) {
        const typeRaw = (calloutMatch[1] || calloutMatch[2] || 'note').toLowerCase();
        let cType: CalloutType = 'note';
        if (typeRaw === 'tip') cType = 'tip';
        else if (typeRaw === 'warning' || typeRaw === 'caution') cType = 'warning';
        else if (typeRaw === 'important') cType = 'important';
        else if (typeRaw === 'success') cType = 'success';

        const body = calloutMatch[3] || quoteText;

        nodes.push(
          <Callout key={`callout-${keyCount++}`} type={cType}>
            {parseInlineMarkdown(body)}
          </Callout>
        );
      } else {
        nodes.push(
          <blockquote
            key={`quote-${keyCount++}`}
            className="my-3 border-l-4 border-accent/60 pl-3.5 py-1 text-text-secondary bg-surface-secondary/40 rounded-r-lg italic text-[13.5px]"
          >
            {parseInlineMarkdown(quoteText)}
          </blockquote>
        );
      }
      continue;
    }

    // 7. Numbered / Ordered List (1. item, 2. item)
    if (/^\d+\.\s+/.test(trimmed)) {
      const listItems: { num: string; text: string; subItems?: string[] }[] = [];
      while (i < lines.length) {
        const curr = lines[i];
        const numMatch = curr.trim().match(/^(\d+)\.\s+(.*)$/);
        if (numMatch) {
          listItems.push({ num: numMatch[1], text: numMatch[2], subItems: [] });
          i++;
        } else if (
          (curr.startsWith('   ') || curr.startsWith('\t')) &&
          listItems.length > 0 &&
          (curr.trim().startsWith('- ') || curr.trim().startsWith('* '))
        ) {
          listItems[listItems.length - 1].subItems?.push(curr.trim().slice(2));
          i++;
        } else if (curr.trim() === '') {
          // lookahead
          if (i + 1 < lines.length && /^\d+\.\s+/.test(lines[i + 1].trim())) {
            i++;
          } else {
            break;
          }
        } else {
          break;
        }
      }

      nodes.push(
        <ol key={`ol-${keyCount++}`} className="space-y-2.5 my-3 pl-1 text-[13.5px]">
          {listItems.map((item, idx) => (
            <li key={idx} className="flex flex-col text-text-primary">
              <div className="flex items-start">
                <span className="select-none font-mono font-semibold text-accent text-xs w-6 shrink-0 mt-0.5">
                  {item.num}.
                </span>
                <div className="flex-1 leading-relaxed">{parseInlineMarkdown(item.text)}</div>
              </div>
              {item.subItems && item.subItems.length > 0 && (
                <ul className="pl-6 mt-1.5 space-y-1">
                  {item.subItems.map((sub, sIdx) => (
                    <li key={sIdx} className="flex items-start text-xs text-text-secondary">
                      <span className="w-1.5 h-1.5 rounded-full bg-text-muted mr-2 mt-1.5 shrink-0" />
                      <span className="leading-relaxed">{parseInlineMarkdown(sub)}</span>
                    </li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ol>
      );
      continue;
    }

    // 8. Bulleted List (- item or * item)
    if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      const listItems: string[] = [];
      while (
        i < lines.length &&
        (lines[i].trim().startsWith('- ') || lines[i].trim().startsWith('* '))
      ) {
        listItems.push(lines[i].trim().slice(2));
        i++;
      }

      nodes.push(
        <ul key={`ul-${keyCount++}`} className="space-y-2 my-2.5 pl-1 text-[13.5px]">
          {listItems.map((item, idx) => (
            <li key={idx} className="flex items-start text-text-primary">
              <span className="w-1.5 h-1.5 rounded-full bg-accent mr-2.5 mt-2 shrink-0" />
              <div className="flex-1 leading-relaxed">{parseInlineMarkdown(item)}</div>
            </li>
          ))}
        </ul>
      );
      continue;
    }

    // 9. Standard Paragraph
    const paragraphLines: string[] = [];
    while (
      i < lines.length &&
      lines[i].trim() !== '' &&
      !lines[i].trim().startsWith('```') &&
      !lines[i].trim().startsWith('#') &&
      !lines[i].trim().startsWith('>') &&
      !lines[i].trim().startsWith('- ') &&
      !lines[i].trim().startsWith('* ') &&
      !/^\d+\.\s+/.test(lines[i].trim()) &&
      !(lines[i].trim().startsWith('|') && lines[i].trim().endsWith('|'))
    ) {
      paragraphLines.push(lines[i]);
      i++;
    }

    if (paragraphLines.length > 0) {
      const paraText = paragraphLines.join(' ');
      nodes.push(
        <p
          key={`p-${keyCount++}`}
          className="text-[14px] leading-relaxed text-text-primary mb-3 last:mb-0"
        >
          {parseInlineMarkdown(paraText)}
        </p>
      );
    }
  }

  return <div className={`ai-markdown-content leading-relaxed ${className}`}>{nodes}</div>;
};

export default AIMarkdownRenderer;
