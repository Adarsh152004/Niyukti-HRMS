import React, { useState } from 'react';
import { Check, Copy } from 'lucide-react';

interface CodeBlockProps {
  code: string;
  language?: string;
}

// Tokenize a single line of code into syntax-highlighted spans
function highlightLine(line: string, language: string): React.ReactNode[] {
  const lang = (language || '').toLowerCase();

  // Comments
  if ((lang === 'python' || lang === 'py' || lang === 'bash' || lang === 'sh' || lang === 'dockerfile') && line.trim().startsWith('#')) {
    return [<span key="c" className="text-zinc-500 italic">{line}</span>];
  }
  if (lang === 'sql' && line.trim().startsWith('--')) {
    return [<span key="c" className="text-zinc-500 italic">{line}</span>];
  }
  if (line.trim().startsWith('//')) {
    return [<span key="c" className="text-zinc-500 italic">{line}</span>];
  }

  // Keywords
  const jsKeywords = 'const|let|var|function|return|import|export|from|default|if|else|switch|case|break|for|while|do|try|catch|finally|throw|new|typeof|instanceof|async|await|class|extends|super|this|interface|type|enum|implements|as|is';
  const pyKeywords = 'def|class|return|import|from|as|if|elif|else|for|while|try|except|finally|with|raise|yield|lambda|pass|break|continue|async|await|in|is|not|and|or|global|nonlocal';
  const sqlKeywords = 'SELECT|FROM|WHERE|INSERT|INTO|VALUES|UPDATE|SET|DELETE|CREATE|TABLE|ALTER|DROP|INDEX|JOIN|INNER|LEFT|RIGHT|FULL|OUTER|ON|GROUP|BY|ORDER|HAVING|LIMIT|OFFSET|UNION|ALL|AND|OR|NOT|IN|EXISTS|BETWEEN|LIKE|IS|NULL|AS|CASE|WHEN|THEN|ELSE|END|COUNT|SUM|AVG|MIN|MAX|DISTINCT';
  const bashKeywords = 'echo|cd|ls|mkdir|rm|cp|mv|cat|grep|sed|awk|chmod|chown|curl|wget|git|npm|npx|pnpm|yarn|node|python|docker|kubectl|sudo|export|source|exit|if|then|else|fi|for|do|done';

  let kwPattern = jsKeywords;
  if (lang === 'python' || lang === 'py') kwPattern = pyKeywords;
  else if (lang === 'sql') kwPattern = sqlKeywords;
  else if (lang === 'bash' || lang === 'sh' || lang === 'zsh' || lang === 'shell') kwPattern = bashKeywords;

  // Safe token regex
  const tokenRegex = new RegExp(
    "(\/\/.*$|#.*$|--.*$)|" + // Comment (group 1)
    "(\"[^\"]*\"|'[^']*'|`[^`]*`)|" + // String (group 2)
    "\\b(" + kwPattern + ")\\b|" + // Keyword (group 3)
    "\\b(true|false|null|undefined|None|True|False)\\b|" + // Literal (group 4)
    "\\b([A-Z][a-zA-Z0-9_]*)\\b|" + // Type / Class (group 5)
    "\\b(\\d+(?:\\.\\d+)?)\\b|" + // Number (group 6)
    "([a-zA-Z_$][a-zA-Z0-9_$]*)(?=\\()|" + // Function call (group 7)
    "([=><!+\-*\/&|?:^~%]+)", // Operator (group 8)
    lang === 'sql' ? 'i' : ''
  );

  const parts: React.ReactNode[] = [];
  let remaining = line;
  let idx = 0;

  while (remaining.length > 0) {
    const match = remaining.match(tokenRegex);
    if (!match || match.index === undefined) {
      parts.push(<span key={idx++} className="text-zinc-200">{remaining}</span>);
      break;
    }

    if (match.index > 0) {
      parts.push(<span key={idx++} className="text-zinc-200">{remaining.slice(0, match.index)}</span>);
    }

    const [full, comment, str, kw, literal, typeName, num, fnName, op] = match;
    if (comment) {
      parts.push(<span key={idx++} className="text-zinc-500 italic">{comment}</span>);
    } else if (str) {
      parts.push(<span key={idx++} className="text-emerald-300">{str}</span>);
    } else if (kw) {
      parts.push(<span key={idx++} className="text-purple-400 font-medium">{kw}</span>);
    } else if (literal) {
      parts.push(<span key={idx++} className="text-amber-400">{literal}</span>);
    } else if (typeName) {
      parts.push(<span key={idx++} className="text-yellow-300">{typeName}</span>);
    } else if (num) {
      parts.push(<span key={idx++} className="text-orange-300">{num}</span>);
    } else if (fnName) {
      parts.push(<span key={idx++} className="text-sky-300">{fnName}</span>);
    } else if (op) {
      parts.push(<span key={idx++} className="text-pink-400">{op}</span>);
    } else {
      parts.push(<span key={idx++} className="text-zinc-200">{full}</span>);
    }

    remaining = remaining.slice(match.index + full.length);
  }

  return parts.length > 0 ? parts : [<span key="empty">{" "}</span>];
}

export const CodeBlock: React.FC<CodeBlockProps> = ({ code, language = 'text' }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const cleanLang = (language || 'code').trim().toLowerCase();
  const displayLang = cleanLang.toUpperCase();
  const lines = code.trimEnd().split('\n');
  const showLineNumbers = lines.length > 3;

  return (
    <div className="my-4 overflow-hidden rounded-xl border border-zinc-800/90 bg-[#0d0d12] shadow-xl shadow-black/40">
      {/* Top Header Bar */}
      <div className="flex items-center justify-between border-b border-zinc-800/80 bg-zinc-900/90 px-4 py-2 text-xs select-none">
        <div className="flex items-center space-x-2">
          <div className="flex space-x-1.5 mr-2">
            <div className="w-2.5 h-2.5 rounded-full bg-red-500/70"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-amber-500/70"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/70"></div>
          </div>
          <span className="font-mono font-semibold tracking-wider text-zinc-400 text-[11px]">
            {displayLang}
          </span>
        </div>

        <button
          onClick={handleCopy}
          className="flex items-center space-x-1.5 rounded-md px-2.5 py-1 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/80 transition-colors active:scale-95"
          title="Copy code to clipboard"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-emerald-400 font-medium text-[11px]">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span className="text-[11px]">Copy</span>
            </>
          )}
        </button>
      </div>

      {/* Code Body */}
      <div className="relative overflow-x-auto p-4 font-mono text-[13px] leading-relaxed">
        <table className="border-collapse w-full">
          <tbody>
            {lines.map((line, idx) => (
              <tr key={idx} className="hover:bg-zinc-800/20 transition-colors">
                {showLineNumbers && (
                  <td className="select-none pr-4 text-right text-zinc-600 text-xs w-8 align-top font-mono">
                    {idx + 1}
                  </td>
                )}
                <td className="whitespace-pre font-mono text-zinc-200">
                  {highlightLine(line, cleanLang)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
