import { ChatGPTMarkdownRenderer } from "@/components/chat/ChatGPTMarkdownRenderer";
import { WidgetRegistry } from '@/components/chat/widgets/WidgetRegistry';
import { ArtifactCard, ArtifactData, ApprovalRequestData } from '@/components/chat/ArtifactCard';
import * as React from 'react';
import { 
  Send, Bot, Loader2, RefreshCw, Trash2, Sparkles, 
  TrendingUp, TrendingDown, Minus, ArrowUpRight, CheckCircle2, 
  AlertCircle, Shield, User, Building2, Zap, Clock, Compass, Layers,
  Table as TableIcon, Search, ArrowUpDown, Download, ChevronDown, ChevronUp
} from 'lucide-react';
import { PageHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useLocation, useNavigate } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';

interface KeyMetric {
  label: string;
  value: string;
  trend?: 'up' | 'down' | 'stable';
  status?: 'normal' | 'success' | 'warning' | 'danger';
}

interface DetectedEntity {
  type: string;
  name: string;
  id?: string;
  department?: string;
  headcount?: number;
}

interface RecommendedAction {
  id: string;
  label: string;
  action_type: 'NAVIGATE' | 'QUERY' | 'TRIGGER_WORKFLOW';
  target: string;
}

interface DataTableStructure {
  title?: string;
  columns: string[];
  rows: Record<string, any>[];
}

interface StructuredData {
  intent?: string;
  decision?: 'INFORMATIONAL' | 'WORKFLOW_TRIGGERED' | 'ACTION_REQUIRED' | 'DATA_INSIGHT' | 'APPROVAL_GATE' | string;
  summary?: string;
  markdown_answer?: string;
  key_metrics?: KeyMetric[];
  entities_detected?: DetectedEntity[];
  recommended_actions?: RecommendedAction[];
  data_table?: DataTableStructure;
  suggested_prompts?: string[];
  artifact?: ArtifactData;
  approval_request?: ApprovalRequestData;
  workflow_id?: string;
  widgets?: any[];
}

interface ChatMessageItem {
  id?: string;
  role: 'user' | 'assistant';
  content: string;
  structured_data?: StructuredData;
  suggested_prompts?: string[];
  channel?: string;
  timestamp: string;
  artifact?: ArtifactData;
  approval_request?: ApprovalRequestData;
  workflow_id?: string;
  widgets?: any[];
  isStreaming?: boolean;
}

// Interactive Rich Data Table Component for Chat
function InteractiveChatTable({ table }: { table: DataTableStructure }) {
  const [searchTerm, setSearchTerm] = React.useState('');
  const [sortCol, setSortCol] = React.useState<string | null>(null);
  const [sortAsc, setSortAsc] = React.useState(true);

    // Filter out dummy/empty rows
  const validRows = (table?.rows || []).filter(r => {
    const vals = Object.values(r || {});
    return vals.some(v => v !== null && v !== undefined && String(v).trim() !== '' && String(v).trim() !== '--' && String(v).trim() !== '-');
  });

  if (!table || !table.columns || table.columns.length === 0 || validRows.length === 0) return null;

  const handleSort = (col: string) => {
    if (sortCol === col) {
      setSortAsc(!sortAsc);
    } else {
      setSortCol(col);
      setSortAsc(true);
    }
  };

  const filteredRows = table.rows.filter(row => {
    if (!searchTerm.trim()) return true;
    const term = searchTerm.toLowerCase();
    return Object.values(row).some(v => String(v).toLowerCase().includes(term));
  });

  const sortedRows = [...filteredRows].sort((a, b) => {
    if (!sortCol) return 0;
    const valA = a[sortCol] ?? '';
    const valB = b[sortCol] ?? '';
    if (typeof valA === 'number' && typeof valB === 'number') {
      return sortAsc ? valA - valB : valB - valA;
    }
    return sortAsc ? String(valA).localeCompare(String(valB)) : String(valB).localeCompare(String(valA));
  });

  const exportCSV = () => {
    const headers = table.columns.join(',');
    const rows = sortedRows.map(r => table.columns.map(c => `"${String(r[c] ?? '').replace(/"/g, '""')}"`).join(','));
    const csvContent = "data:text/csv;charset=utf-8," + [headers, ...rows].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `${table.title || 'export'}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const renderCellBadge = (val: any) => {
    const s = String(val).toUpperCase();
    if (['ACTIVE', 'PRESENT', 'ON_TIME', 'APPROVED', 'COMPLETED', 'OPTIMAL', 'OPEN'].includes(s)) {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
          {val}
        </span>
      );
    }
    if (['PENDING', 'IN_PROGRESS', 'REVIEW', 'WARNING'].includes(s)) {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/30">
          {val}
        </span>
      );
    }
    if (['ABSENT', 'REJECTED', 'FAILED', 'HIRING REQUIRED'].includes(s)) {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-red-500/15 text-red-400 border border-red-500/30">
          {val}
        </span>
      );
    }
    return String(val);
  };

  return (
    <div className="mt-3 bg-surface border border-border rounded-xl overflow-hidden shadow-xs">
      {/* Table Header Controls */}
      <div className="p-2.5 bg-surface-secondary/70 border-b border-border flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-1.5">
          <TableIcon className="w-3.5 h-3.5 text-accent" />
          <span className="text-xs font-semibold text-text-primary">{table.title || 'Structured Data Records'}</span>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-surface border border-border text-text-muted font-mono">
            {sortedRows.length} rows
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Search bar inside table */}
          <div className="relative">
            <Search className="w-3 h-3 absolute left-2 top-1/2 -translate-y-1/2 text-text-muted" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Filter rows..."
              className="h-6 pl-6 pr-2 text-2xs bg-surface border border-border rounded-md text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-1 focus:ring-accent"
            />
          </div>

          <button
            onClick={exportCSV}
            title="Export to CSV"
            className="p-1 rounded hover:bg-surface border border-transparent hover:border-border text-text-muted hover:text-text-primary transition"
          >
            <Download className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Table Body */}
      <div className="overflow-x-auto max-h-64 scrollbar-thin">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-surface-secondary/40 border-b border-border sticky top-0 backdrop-blur">
              {table.columns.map((col, cIdx) => (
                <th
                  key={cIdx}
                  onClick={() => handleSort(col)}
                  className="px-3 py-2 text-[10px] font-semibold text-text-muted uppercase tracking-wider cursor-pointer hover:text-text-primary select-none whitespace-nowrap"
                >
                  <div className="flex items-center gap-1">
                    <span>{col}</span>
                    {sortCol === col ? (
                      sortAsc ? <ChevronUp className="w-3 h-3 text-accent" /> : <ChevronDown className="w-3 h-3 text-accent" />
                    ) : (
                      <ArrowUpDown className="w-2.5 h-2.5 opacity-40" />
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border/60">
            {sortedRows.map((row, rIdx) => (
              <tr
                key={rIdx}
                className="hover:bg-accent-soft/30 transition-colors even:bg-surface-secondary/20"
              >
                {table.columns.map((col, cIdx) => (
                  <td key={cIdx} className="px-3 py-2 text-text-primary whitespace-nowrap text-xs">
                    {renderCellBadge(row[col] ?? '--')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function AIAssistantPage() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [input, setInput] = React.useState('');
  const [isSending, setIsSending] = React.useState(false);
  const messagesEndRef = React.useRef<HTMLDivElement>(null);
  const location = useLocation();

  // Dynamic starter suggestions based on time of day
  const { data: dynamicStarterInfo } = useQuery({
    queryKey: ['dynamic-suggestions-starter'],
    queryFn: async () => {
      const res = await fetch('/api/v1/orchestration/suggestions');
      if (!res.ok) return null;
      return res.json();
    },
    staleTime: 60_000,
  });

  // Unified Chat Messages from Supabase Cloud DB
  const { data: messages = [], isLoading, refetch } = useQuery<ChatMessageItem[]>({
    queryKey: ['unified-chat-messages'],
    queryFn: async () => {
      const res = await fetch('/api/v1/chat/messages');
      if (!res.ok) return [];
      return res.json();
    },
    refetchInterval: 3000,
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [messages, isSending]);

  React.useEffect(() => {
    if (location.state && (location.state as any).query) {
      setInput((location.state as any).query);
    }
  }, [location]);

  const handleApprove = async (workflowId: string) => {
    try {
      const res = await fetch(`/api/v1/orchestration/workflows/${workflowId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      if (res.ok) {
        const data = await res.json();
        queryClient.setQueryData<ChatMessageItem[]>(['unified-chat-messages'], (old = []) => {
          return old.map(m => {
            if (m.workflow_id === workflowId && m.artifact) {
              return {
                ...m,
                artifact: { ...m.artifact, status: 'APPROVED' },
                approval_request: m.approval_request ? { ...m.approval_request, status: 'APPROVED' } : undefined
              };
            }
            return m;
          });
        });

        if (data.next_message) {
          const nextMsg: ChatMessageItem = {
            id: `next-${Date.now()}`,
            role: 'assistant',
            content: data.next_message,
            channel: 'AI_WORKSPACE',
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          };
          queryClient.setQueryData<ChatMessageItem[]>(['unified-chat-messages'], (old = []) => [...old, nextMsg]);
        }
      }
    } catch (err) {
      console.error('Approve failed:', err);
    }
  };

  const handleRevise = async (workflowId: string, feedback: string) => {
    try {
      const userFeedbackMsg: ChatMessageItem = {
        id: `feedback-${Date.now()}`,
        role: 'user',
        content: feedback,
        channel: 'AI_WORKSPACE',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      queryClient.setQueryData<ChatMessageItem[]>(['unified-chat-messages'], (old = []) => [...old, userFeedbackMsg]);

      const res = await fetch(`/api/v1/orchestration/workflows/${workflowId}/revise`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feedback })
      });
      if (res.ok) {
        const data = await res.json();
        const revisedAssistantMsg: ChatMessageItem = {
          id: `revised-${Date.now()}`,
          role: 'assistant',
          content: data.next_message,
          channel: 'AI_WORKSPACE',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          artifact: data.artifact,
          approval_request: data.approval_request,
          workflow_id: workflowId
        };
        queryClient.setQueryData<ChatMessageItem[]>(['unified-chat-messages'], (old = []) => [...old, revisedAssistantMsg]);
      }
    } catch (err) {
      console.error('Revise failed:', err);
    }
  };

  const handleSend = async (queryOverride?: string) => {
    const textToSend = (queryOverride || input).trim();
    if (!textToSend || isSending) return;
    
    const tempUserMsg: ChatMessageItem = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: textToSend,
      channel: 'AI_WORKSPACE',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    const streamMsgId = `stream-${Date.now()}`;
    const initialAssistantMsg: ChatMessageItem = {
      id: streamMsgId,
      role: 'assistant',
      content: '',
      isStreaming: true,
      channel: 'AI_WORKSPACE',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    // Optimistically update query client cache
    queryClient.setQueryData<ChatMessageItem[]>(['unified-chat-messages'], (old = []) => [...old, tempUserMsg, initialAssistantMsg]);

    setInput('');
    setIsSending(true);

    try {
      const res = await fetch('/api/v1/orchestration/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: textToSend,
          initiator: 'AI Workspace User',
          channel: 'AI_WORKSPACE',
        }),
      });

      if (res.ok && res.body) {
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let accumulatedText = '';
        let structuredData: any = null;
        let artifactData: any = null;
        let approvalReqData: any = null;
        let workflowId = streamMsgId;
        let widgetsData: any[] = [];
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const blocks = buffer.split('\n\n');
          buffer = blocks.pop() || '';

          for (const block of blocks) {
            const blockLines = block.split('\n');
            let eventType = '';
            let dataStr = '';

            for (const line of blockLines) {
              if (line.startsWith('event: ')) {
                eventType = line.slice(7).trim();
              } else if (line.startsWith('data: ')) {
                dataStr = line.slice(6).trim();
              }
            }

            if (!dataStr) continue;

            if (eventType === 'metadata') {
              try {
                const meta = JSON.parse(dataStr);
                if (meta.run_id) workflowId = meta.run_id;
                if (meta.artifact) artifactData = meta.artifact;
                if (meta.approval_request) approvalReqData = meta.approval_request;
              } catch (_) {}
            } else if (eventType === 'token') {
              try {
                const parsed = JSON.parse(dataStr);
                accumulatedText += parsed.token;
                queryClient.setQueryData<ChatMessageItem[]>(['unified-chat-messages'], (old = []) =>
                  old.map(m => m.id === streamMsgId ? { ...m, content: accumulatedText, isStreaming: true, workflow_id: workflowId } : m)
                );
              } catch (_) {}
            } else if (eventType === 'complete') {
              try {
                const comp = JSON.parse(dataStr);
                structuredData = comp.structured_response || comp.envelope;
                if (comp.run_id) workflowId = comp.run_id;
                if (comp.structured_response?.artifact) artifactData = comp.structured_response.artifact;
                if (comp.structured_response?.approval_request) approvalReqData = comp.structured_response.approval_request;
                if (comp.structured_response?.widgets) widgetsData = comp.structured_response.widgets;
              } catch (_) {}
            }
          }
        }

        // Finalize message
        const finalMsg: ChatMessageItem = {
          id: workflowId,
          role: 'assistant',
          content: accumulatedText.trim() || 'Processed your request.',
          isStreaming: false,
          channel: 'AI_WORKSPACE',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          structured_data: structuredData,
          artifact: artifactData,
          approval_request: approvalReqData,
          workflow_id: workflowId,
          widgets: widgetsData,
        };

        queryClient.setQueryData<ChatMessageItem[]>(['unified-chat-messages'], (old = []) => {
          const map = new Map<string, ChatMessageItem>();
          old.forEach(m => {
            if (m.id === streamMsgId) {
              map.set(finalMsg.id || streamMsgId, finalMsg);
            } else if (m?.id) {
              map.set(m.id, m);
            }
          });
          return Array.from(map.values());
        });
      } else {
        // Fallback to execute
        const fallbackRes = await fetch('/api/v1/orchestration/execute', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: textToSend, channel: 'AI_WORKSPACE' }),
        });
        if (fallbackRes.ok) {
          const data = await fallbackRes.json();
          const assistantText = data.envelope?.text || data.markdown_answer || 'Processed your request.';
          const assistantMsg: ChatMessageItem = {
            id: data.run_id || streamMsgId,
            role: 'assistant',
            content: assistantText,
            isStreaming: false,
            channel: 'AI_WORKSPACE',
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            structured_data: data.structured_response || data.envelope,
            artifact: data.structured_response?.artifact,
            approval_request: data.structured_response?.approval_request,
            workflow_id: data.run_id,
            widgets: data.structured_response?.widgets || [],
          };
          queryClient.setQueryData<ChatMessageItem[]>(['unified-chat-messages'], (old = []) =>
            old.map(m => m.id === streamMsgId ? assistantMsg : m)
          );
        }
      }
    } catch (err) {
      console.error('Failed to send message:', err);
      queryClient.setQueryData<ChatMessageItem[]>(['unified-chat-messages'], (old = []) =>
        old.filter(m => m.id !== streamMsgId)
      );
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleActionClick = (action: RecommendedAction) => {
    if (action.action_type === 'NAVIGATE') {
      navigate(action.target);
    } else if (action.action_type === 'QUERY') {
      handleSend(action.target);
    } else {
      navigate('/workflows');
    }
  };

  // Get active suggested prompts
  const latestAiMessage = [...messages].reverse().find(m => m.role === 'assistant');
  const activeSuggestedPrompts = latestAiMessage?.suggested_prompts?.length 
    ? latestAiMessage.suggested_prompts 
    : (dynamicStarterInfo?.suggested_prompts || [
        "Check headcount distribution across all departments",
        "Show attendance of Priya",
        "Recruit a new senior backend engineer for HealthPulse",
        "List all employees in our company"
      ]);

  return (
    <div className="flex flex-col h-[calc(100vh-8.5rem)] space-y-3.5">
      <PageHeader
        title="AI Workforce Intelligence"
        description="Structured Multi-Agent Reasoning grounded in Supabase, MongoDB Atlas, and Enterprise HR data."
        actions={
          <div className="flex items-center gap-2">
            {dynamicStarterInfo?.time_context && (
              <div className="hidden md:flex items-center gap-1.5 px-3 py-1 bg-surface-secondary border border-border rounded-full text-2xs text-text-muted">
                <Clock className="w-3 h-3 text-accent" />
                <span className="capitalize font-medium text-text-primary">{dynamicStarterInfo.time_context.period} Mode</span>
                <span>•</span>
                
              </div>
            )}
            <Button
              variant="secondary"
              size="sm"
              onClick={() => refetch()}
              className="flex items-center gap-1.5"
            >
              <RefreshCw className="h-3.5 w-3.5" /> Sync
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={async () => {
                await fetch('/api/v1/chat/messages', { method: 'DELETE' });
                queryClient.invalidateQueries({ queryKey: ['unified-chat-messages'] });
              }}
              className="flex items-center gap-1.5 text-text-muted hover:text-danger"
            >
              <Trash2 className="h-3.5 w-3.5" /> Clear History
            </Button>
          </div>
        }
      />

      {/* Main Chat Conversation Window */}
      <div className="flex-1 bg-surface border border-border rounded-xl p-5 overflow-y-auto space-y-4 shadow-sm">
        {isLoading && messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <Loader2 className="h-6 w-6 text-accent animate-spin" />
          </div>
        ) : messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center max-w-lg mx-auto space-y-4">
            <div className="w-14 h-14 rounded-2xl bg-accent-soft text-accent flex items-center justify-center shadow-xs">
              <Sparkles className="h-7 w-7" />
            </div>
            <div>
              <h3 className="font-semibold text-text-primary text-base">Nova Workforce Intelligence Connected</h3>
              <p className="text-xs text-text-muted mt-1 leading-relaxed">
                Structured decision reasoning engine live-synced with Supabase & MongoDB Atlas. Ask questions or trigger automated workflows.
              </p>
            </div>

            {/* Starter Suggestions */}
            <div className="w-full space-y-2 pt-2">
              <div className="flex items-center justify-center gap-1.5 text-2xs font-semibold uppercase tracking-wider text-text-muted">
                <Compass className="w-3.5 h-3.5 text-accent" />
                <span>Suggested Queries for {dynamicStarterInfo?.time_context?.period || 'today'}</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-left">
                {activeSuggestedPrompts.slice(0, 4).map((prompt: string, idx: number) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(prompt)}
                    className="p-2.5 rounded-xl bg-surface-secondary hover:bg-surface-secondary/80 border border-border hover:border-accent/40 text-xs text-text-primary transition flex items-center justify-between group text-left"
                  >
                    <span className="line-clamp-2 pr-2">{prompt}</span>
                    <ArrowUpRight className="w-3.5 h-3.5 text-text-muted group-hover:text-accent shrink-0 transition" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => {
            const isUser = msg.role === 'user';
            const sData = msg.structured_data;

            return (
              <div
                key={msg.id || idx}
                className={`flex gap-3 max-w-[90%] md:max-w-[85%] ${
                  isUser ? 'ml-auto flex-row-reverse' : 'mr-auto'
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-xs font-bold ${
                    isUser
                      ? 'bg-accent text-white shadow-xs'
                      : 'bg-surface-secondary border border-border text-accent shadow-xs'
                  }`}
                >
                  {isUser ? 'U' : <Bot className="h-4 w-4" />}
                </div>

                <div
                  className={`rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-xs ${
                    isUser
                      ? 'bg-accent text-white rounded-tr-none'
                      : 'bg-surface-secondary border border-border text-text-primary rounded-tl-none space-y-3'
                  }`}
                >
                  {/* Structured Decision Badge for AI */}




                  {/* Message Content (Claude & ChatGPT Style Rich Markdown) */}
                  {isUser ? (
                    <div className="whitespace-pre-wrap leading-relaxed text-xs sm:text-sm">
                      {msg.content?.trim()}
                    </div>
                  ) : (
                    <div className="relative">
                      <ChatGPTMarkdownRenderer content={msg.content || ""} />
                      {msg.isStreaming && (
                        <span className="inline-block w-1.5 h-3.5 bg-accent ml-1 rounded-xs animate-pulse align-middle" />
                      )}
                    </div>
                  )}

                  {/* Interactive Structured Widgets */}
                  {!isUser && (((msg as any).widgets && (msg as any).widgets.length > 0) || (sData?.widgets && sData.widgets.length > 0)) && (
                    <div className="space-y-3 mt-3 text-left w-full">
                      {((msg as any).widgets || sData?.widgets || []).map((w: any, wIdx: number) => (
                        <WidgetRegistry key={wIdx} widget={w} />
                      ))}
                    </div>
                  )}

                  {/* Artifact Card (Job Descriptions, Offers, Plans with Approval Gates) */}
                  {!isUser && (msg.artifact || sData?.artifact) && (
                    <div className="mt-3">
                      <ArtifactCard
                        artifact={msg.artifact || (sData?.artifact as any)}
                        approvalRequest={msg.approval_request || (sData?.approval_request as any)}
                        workflowId={msg.workflow_id || (sData as any)?.workflow_id}
                        onApprove={handleApprove}
                        onRevise={handleRevise}
                      />
                    </div>
                  )}



                  {/* Recommended Action Buttons */}
                  {!isUser && sData?.recommended_actions && sData.recommended_actions.length > 0 && (
                    <div className="flex flex-wrap gap-2 pt-2 border-t border-border/50">
                      {sData.recommended_actions.map((act) => (
                        <Button
                          key={act.id}
                          variant="secondary"
                          size="sm"
                          onClick={() => handleActionClick(act)}
                          className="text-xs h-7 px-2.5 gap-1.5 bg-surface hover:bg-accent hover:text-white border-border transition"
                        >
                          <Zap className="w-3 h-3 text-accent group-hover:text-white" />
                          <span>{act.label}</span>
                          <ArrowUpRight className="w-3 h-3" />
                        </Button>
                      ))}
                    </div>
                  )}


                </div>
              </div>
            );
          })
        )}

        {isSending && (
          <div className="flex gap-3 max-w-[85%] mr-auto">
            <div className="w-8 h-8 rounded-full bg-surface-secondary border border-border text-accent flex items-center justify-center shrink-0">
              <Bot className="h-4 w-4 animate-spin" />
            </div>
            <div className="bg-surface-secondary border border-border text-text-muted rounded-2xl rounded-tl-none px-4 py-3 text-xs flex items-center gap-2">
              <Loader2 className="h-3.5 w-3.5 animate-spin text-accent" />
              <span>Multi-agent reasoning & domain synthesis in progress...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Dynamic Contextual Query Suggestions Bar */}
      {activeSuggestedPrompts.length > 0 && (
        <div className="flex items-center gap-1.5 overflow-x-auto py-1 scrollbar-none shrink-0">
          <span className="text-[10px] font-semibold text-text-muted uppercase tracking-wider whitespace-nowrap pl-1 flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-accent" /> Suggested:
          </span>
          {activeSuggestedPrompts.map((prompt: string, i: number) => (
            <button
              key={i}
              onClick={() => handleSend(prompt)}
              className="text-2xs whitespace-nowrap bg-surface hover:bg-surface-secondary border border-border hover:border-accent/50 text-text-secondary hover:text-text-primary rounded-full px-3 py-1.5 transition shadow-xs flex items-center gap-1"
            >
              <span>{prompt}</span>
              <ArrowUpRight className="w-2.5 h-2.5 text-text-muted" />
            </button>
          ))}
        </div>
      )}

      {/* Query Input Bar */}
      <div className="flex gap-2 shrink-0">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask workforce query or command autonomous fleet (e.g. 'Show attendance of Priya', 'List all employees')..."
          rows={1}
          className="flex-1 resize-none bg-surface border border-border rounded-xl px-4 py-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent shadow-xs"
        />
        <Button
          variant="primary"
          onClick={() => handleSend()}
          disabled={!input.trim() || isSending}
          className="px-5 shrink-0"
        >
          {isSending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
        </Button>
      </div>
    </div>
  );
}
