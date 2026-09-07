import React, { useState } from 'react';
import { Check, Copy, Sparkles, ThumbsUp, ThumbsDown } from 'lucide-react';
import { AIMarkdownRenderer } from './AIMarkdownRenderer';
import { ArtifactCard, ArtifactData } from './ArtifactCard';

export interface AIMessageProps {
  content: string;
  role?: 'assistant' | 'user' | 'system';
  provider?: string;
  timestamp?: string;
  artifacts?: ArtifactData[];
  onApproveArtifact?: (art: ArtifactData, workflowId?: string) => Promise<void> | void;
  onReviseArtifact?: (art: ArtifactData, workflowId?: string, feedback?: string) => Promise<void> | void;
  className?: string;
}

export const AIMessage: React.FC<AIMessageProps> = ({
  content,
  role = 'assistant',
  provider,
  timestamp,
  artifacts = [],
  onApproveArtifact,
  onReviseArtifact,
  className = '',
}) => {
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(null);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isAssistant = role === 'assistant';

  if (!isAssistant) {
    return (
      <div className={`flex justify-end my-3 ${className}`}>
        <div className="max-w-[760px] rounded-2xl bg-indigo-600 px-4 py-2.5 text-[14px] text-white shadow-md shadow-indigo-950/20">
          <p className="whitespace-pre-wrap leading-relaxed">{content}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`my-4 flex items-start gap-3 max-w-[820px] w-full ${className}`}>
      {/* Assistant Avatar */}
      <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500/20 via-purple-500/20 to-pink-500/20 border border-indigo-500/30 text-indigo-400 shadow-sm">
        <Sparkles className="h-4 w-4" />
      </div>

      {/* Message Body */}
      <div className="flex-1 min-w-0 space-y-2">
        {/* Header Metadata */}
        <div className="flex items-center space-x-2 text-[11px] text-zinc-400 select-none">
          <span className="font-semibold text-zinc-200 tracking-wide">Nova Assistant</span>
          {provider && (
            <span className="rounded-full bg-zinc-800/80 px-2 py-0.5 text-[10px] text-zinc-400 border border-zinc-700/50">
              {provider}
            </span>
          )}
          {timestamp && <span className="text-zinc-500">{timestamp}</span>}
        </div>

        {/* Markdown Prose & Formatted Elements */}
        <div className="rounded-2xl border border-zinc-800/80 bg-zinc-900/60 p-4 shadow-md backdrop-blur-sm">
          <AIMarkdownRenderer content={content} />

          {/* Interactive Actionable Artifacts (JDs, Offers, Payroll runs) */}
          {artifacts && artifacts.length > 0 && (
            <div className="mt-4 space-y-3 pt-3 border-t border-zinc-800/80">
              {artifacts.map((art, idx) => (
                <ArtifactCard
                  key={art.id || idx}
                  artifact={art}
                  workflowId={art.id}
                  onApprove={async (wfId) => {
                    if (onApproveArtifact) await onApproveArtifact(art, wfId);
                  }}
                  onRevise={async (wfId, fb) => {
                    if (onReviseArtifact) await onReviseArtifact(art, wfId, fb);
                  }}
                />
              ))}
            </div>
          )}

          {/* Bottom Message Action Bar */}
          <div className="mt-3 flex items-center justify-between border-t border-zinc-800/50 pt-2.5 text-xs text-zinc-400">
            <div className="flex items-center space-x-2">
              <button
                onClick={handleCopy}
                className="flex items-center space-x-1 rounded-md px-2 py-1 hover:bg-zinc-800 hover:text-zinc-200 transition-colors text-[11px]"
                title="Copy entire response"
              >
                {copied ? (
                  <>
                    <Check className="h-3.5 w-3.5 text-emerald-400" />
                    <span className="text-emerald-400">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="h-3.5 w-3.5" />
                    <span>Copy</span>
                  </>
                )}
              </button>
            </div>

            <div className="flex items-center space-x-1">
              <button
                onClick={() => setFeedback('up')}
                className={`p-1 rounded hover:bg-zinc-800 transition-colors ${
                  feedback === 'up' ? 'text-emerald-400' : 'hover:text-zinc-200'
                }`}
                title="Good response"
              >
                <ThumbsUp className="h-3.5 w-3.5" />
              </button>
              <button
                onClick={() => setFeedback('down')}
                className={`p-1 rounded hover:bg-zinc-800 transition-colors ${
                  feedback === 'down' ? 'text-rose-400' : 'hover:text-zinc-200'
                }`}
                title="Needs improvement"
              >
                <ThumbsDown className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
