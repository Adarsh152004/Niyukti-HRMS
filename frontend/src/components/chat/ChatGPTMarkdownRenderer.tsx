import React from 'react';
import { AIMarkdownRenderer } from './AIMarkdownRenderer';

interface ChatGPTMarkdownRendererProps {
  content: string;
  className?: string;
}

/**
 * Enterprise-grade ChatGPT & Claude Markdown Renderer
 * Supports:
 * - Dynamic structural presentation (prose, numbered steps, tables, bullet lists, code blocks)
 * - Fenced code blocks with language badge, syntax highlighting, and 1-click copy button
 * - Responsive, horizontally scrollable tables with alignments
 * - Callout cards for notes, warnings, tips, and important announcements
 * - Sleek typography with font-sans and font-mono accents
 */
export const ChatGPTMarkdownRenderer: React.FC<ChatGPTMarkdownRendererProps> = ({
  content,
  className = '',
}) => {
  return <AIMarkdownRenderer content={content} className={className} />;
};

export default ChatGPTMarkdownRenderer;
