import * as React from 'react';
import { 
  Send, Bot, Loader2, RefreshCw, Trash2, Sparkles, 
  ArrowUpRight, CheckCircle2, Clock, Compass, ShieldCheck
} from 'lucide-react';
import { PageHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useLocation, useNavigate } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { ChatGPTMarkdownRenderer } from "@/components/chat/ChatGPTMarkdownRenderer";

interface StructuredData {
  intent?: string;
  decision?: string;
  summary?: string;
  markdown_answer?: string;
  suggested_prompts?: string[];
  workflow_id?: string;
  approval_request?: {
    id: string;
    workflow_id: string;
    status: string;
    action_type?: string;
    action_required?: string;
  };
  artifact?: {
    id: string;
    title: string;
    type: string;
    version: number;
    content: any;
    status: string;
  };
}

interface ChatMessageItem {
  id?: string;
  role: 'user' | 'assistant';
  content: string;
  structured_data?: StructuredData;
  suggested_prompts?: string[];
  channel?: string;
  timestamp: string;
  workflow_id?: string;
  isStreaming?: boolean;
}

export function AIAssistantPage() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [input, setInput] = React.useState('');
  const [isSending, setIsSending] = React.useState(false);
  const [pendingUserQuery, setPendingUserQuery] = React.useState<string | null>(null);
  const [feedbackInput, setFeedbackInput] = React.useState<{ [workflowId: string]: string }>({});
  const [revisingId, setRevisingId] = React.useState<string | null>(null);
  const messagesEndRef = React.useRef<HTMLDivElement>(null);
  const location = useLocation();

  // Dynamic starter suggestions
  const { data: dynamicStarterInfo } = useQuery({
    queryKey: ['dynamic-suggestions-starter'],
    queryFn: async () => {
      const res = await fetch('/api/v1/orchestration/suggestions');
      if (!res.ok) return null;
      return res.json();
    },
    staleTime: 60_000,
  });

  // Unified Chat Messages
  const { data: messages = [], isLoading, refetch } = useQuery<ChatMessageItem[]>({
    queryKey: ['unified-chat-messages'],
    queryFn: async () => {
      const res = await fetch('/api/v1/chat/messages');
      if (!res.ok) return [];
      const data = await res.json();
      return (data || []).map((m: any, idx: number) => ({
        id: m.id || `msg-${idx}`,
        role: m.role,
        content: m.content,
        structured_data: m.structured_data,
        suggested_prompts: m.suggested_prompts,
        timestamp: m.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        workflow_id: m.structured_data?.workflow_id || m.workflow_id
      }));
    },
    refetchInterval: 3000,
  });

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending, pendingUserQuery]);

  const handleApprove = async (workflowId: string) => {
    try {
      const res = await fetch(`/api/v1/orchestration/workflows/${workflowId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      if (res.ok) {
        queryClient.invalidateQueries({ queryKey: ['unified-chat-messages'] });
      }
    } catch (e) {
      console.error('Failed to approve workflow:', e);
    }
  };

  const handleRevise = async (workflowId: string, feedback: string) => {
    try {
      const res = await fetch(`/api/v1/orchestration/workflows/${workflowId}/revise`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feedback })
      });
      if (res.ok) {
        setRevisingId(null);
        queryClient.invalidateQueries({ queryKey: ['unified-chat-messages'] });
      }
    } catch (e) {
      console.error('Failed to revise workflow:', e);
    }
  };

  const handleClearChat = async () => {
    try {
      await fetch('/api/v1/chat/messages', { method: 'DELETE' });
      await fetch('/api/v1/orchestration/clear', { method: 'POST' });
      queryClient.setQueryData(['unified-chat-messages'], []);
      queryClient.invalidateQueries({ queryKey: ['unified-chat-messages'] });
    } catch (e) {
      console.error('Failed to clear chat:', e);
    }
  };

  const handleSend = async (textToSend?: string) => {
    const query = (textToSend || input).trim();
    if (!query || isSending) return;

    setInput('');
    setPendingUserQuery(query);
    setIsSending(true);

    try {
      const res = await fetch('/api/v1/orchestration/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          initiator: 'HR Executive',
          channel: 'AI_WORKSPACE',
        }),
      });

      if (res.ok) {
        await queryClient.refetchQueries({ queryKey: ['unified-chat-messages'] });
      }
    } catch (err) {
      console.error('Failed to send message:', err);
    } finally {
      setPendingUserQuery(null);
      setIsSending(false);
      queryClient.refetchQueries({ queryKey: ['unified-chat-messages'] });
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const latestAiMessage = [...messages].reverse().find(m => m.role === 'assistant');
  const activeSuggestedPrompts = latestAiMessage?.suggested_prompts?.length 
    ? latestAiMessage.suggested_prompts 
    : (dynamicStarterInfo?.suggested_prompts || [
        "Check headcount distribution across all departments",
        "Show attendance summary for today",
        "Draft a job opening for Senior Frontend Engineer",
        "List all employees in our company"
      ]);

  return (
    <div className="flex flex-col h-[calc(100vh-8.5rem)] space-y-3.5">
      <PageHeader
        title="AI Workforce Assistant"
        description="Conversational assistant connected directly to your live database records."
        actions={
          <div className="flex items-center gap-2">
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
              onClick={handleClearChat}
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
              <h3 className="font-semibold text-text-primary text-base">HRMS AI Assistant Active</h3>
              <p className="text-xs text-text-muted mt-1 leading-relaxed">
                Direct live database connection. Ask questions about headcount, attendance, payroll, or issue workflow commands.
              </p>
            </div>

            {/* Starter Suggestions */}
            <div className="w-full space-y-2 pt-2">
              <div className="flex items-center justify-center gap-1.5 text-2xs font-semibold uppercase tracking-wider text-text-muted">
                <Compass className="w-3.5 h-3.5 text-accent" />
                <span>Quick Prompts</span>
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
            const approvalReq = sData?.approval_request;
            const workflowId = sData?.workflow_id || msg.workflow_id || approvalReq?.workflow_id;
            const isPendingApproval = approvalReq?.status === 'PENDING';

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
                  {/* Clean natural markdown answer */}
                  {isUser ? (
                    <div className="whitespace-pre-wrap leading-relaxed text-xs sm:text-sm">
                      {msg.content?.trim()}
                    </div>
                  ) : (
                    <div className="text-xs sm:text-sm leading-relaxed">
                      <ChatGPTMarkdownRenderer content={msg.content || ""} />
                    </div>
                  )}

                  {/* Clean inline HITL Approval bar when action is required */}
                  {!isUser && isPendingApproval && workflowId && (
                    <div className="mt-3 pt-3 border-t border-border flex flex-col gap-2 bg-surface/60 p-3 rounded-xl">
                      <div className="flex items-center justify-between text-xs text-amber-600 font-medium">
                        <span className="flex items-center gap-1.5">
                          <Clock className="w-3.5 h-3.5 animate-pulse" />
                          Approval Required: {approvalReq?.action_type || 'Workflow Action'}
                        </span>
                      </div>
                      
                      {revisingId === workflowId ? (
                        <div className="flex flex-col gap-2 bg-surface p-2.5 rounded-lg border border-border">
                          <input
                            type="text"
                            placeholder="Type revision notes..."
                            value={feedbackInput[workflowId] || ''}
                            onChange={(e) => setFeedbackInput({ ...feedbackInput, [workflowId]: e.target.value })}
                            className="w-full bg-surface-secondary border border-border rounded-lg px-2.5 py-1.5 text-xs text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-1 focus:ring-accent"
                          />
                          <div className="flex gap-1.5 justify-end">
                            <button
                              onClick={() => setRevisingId(null)}
                              className="px-2.5 py-1 rounded-lg bg-surface-secondary text-text-muted hover:text-text-primary text-xs"
                            >
                              Cancel
                            </button>
                            <button
                              onClick={() => handleRevise(workflowId, feedbackInput[workflowId] || '')}
                              className="px-2.5 py-1 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-medium text-xs"
                            >
                              Submit Revision
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2 pt-1">
                          <Button
                            size="sm"
                            variant="primary"
                            onClick={() => handleApprove(workflowId)}
                            className="text-xs h-8 gap-1.5"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            Approve Action
                          </Button>
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => setRevisingId(workflowId)}
                            className="text-xs h-8 gap-1.5"
                          >
                            Request Revision
                          </Button>
                        </div>
                      )}
                    </div>
                  )}

                  <div className={`text-[10px] text-right ${isUser ? 'text-white/70' : 'text-text-muted'}`}>
                    {msg.timestamp}
                  </div>
                </div>
              </div>
            );
          })
        )}

        {pendingUserQuery && (
          <div className="flex gap-3 max-w-[90%] md:max-w-[85%] ml-auto flex-row-reverse">
            <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-xs font-bold bg-accent text-white shadow-xs">
              U
            </div>
            <div className="rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-xs bg-accent text-white rounded-tr-none">
              <div className="whitespace-pre-wrap leading-relaxed text-xs sm:text-sm">
                {pendingUserQuery}
              </div>
              <div className="text-[10px] text-right text-white/70 mt-1">
                Sending...
              </div>
            </div>
          </div>
        )}

        {isSending && (
          <div className="flex gap-3 max-w-[85%] mr-auto">
            <div className="w-8 h-8 rounded-full bg-surface-secondary border border-border text-accent flex items-center justify-center shrink-0">
              <Bot className="h-4 w-4 animate-spin" />
            </div>
            <div className="bg-surface-secondary border border-border text-text-muted rounded-2xl rounded-tl-none px-4 py-3 text-xs flex items-center gap-2">
              <Loader2 className="h-3.5 w-3.5 animate-spin text-accent" />
              <span>Synthesizing response...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompts */}
      {activeSuggestedPrompts.length > 0 && (
        <div className="flex items-center gap-1.5 overflow-x-auto py-1 scrollbar-none shrink-0">
          <span className="text-[10px] font-semibold text-text-muted uppercase tracking-wider whitespace-nowrap pl-1 flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-accent" /> Quick Prompts:
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
          placeholder="Ask workforce query or issue command (e.g. 'Show attendance summary', 'Draft a job opening')..."
          rows={1}
          className="flex-1 resize-none bg-surface border border-border rounded-xl px-4 py-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent shadow-xs"
        />
        <Button
          variant="primary"
          onClick={() => handleSend()}
          disabled={!input.trim() || isSending}
          className="px-5 shrink-0"
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
