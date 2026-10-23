import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, Mic, MicOff, Sparkles, RefreshCw, Maximize2, Minimize2, Bot,
  TrendingUp, TrendingDown, Minus, ArrowUpRight, CheckCircle2, User, Building2, Zap, Clock,
  Table as TableIcon, Search, Download, FileText, Briefcase
} from 'lucide-react';
import { AIMarkdownRenderer, MobileTableOrCards } from './components/AIMarkdownRenderer';

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

interface ArtifactContent {
  role_title?: string;
  department?: string;
  employment_type?: string;
  salary_range?: string;
  location?: string;
  about_role?: string;
  responsibilities?: string[];
  requirements?: string[];
  nice_to_have?: string[];
  // Payroll fields
  period?: string;
  total_net_payout?: string;
  employee_count?: number;
  [key: string]: any;
}

interface ArtifactModel {
  id: string;
  type: string;
  title: string;
  version: number;
  content: ArtifactContent;
  raw_markdown?: string;
  status: string;
  created_at?: string;
}

interface ApprovalRequest {
  id: string;
  workflow_id: string;
  artifact_id?: string;
  status: string;
  action_required?: string;
  [key: string]: any;
}

interface StructuredData {
  intent?: string;
  decision?: string;
  summary?: string;
  markdown_answer?: string;
  key_metrics?: KeyMetric[];
  entities_detected?: DetectedEntity[];
  recommended_actions?: RecommendedAction[];
  data_table?: DataTableStructure;
  suggested_prompts?: string[];
  artifact?: ArtifactModel;
  approval_request?: ApprovalRequest;
}

interface Message {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  structured_data?: StructuredData;
  suggested_prompts?: string[];
  timestamp: string;
  isStreaming?: boolean;
}

function MobileInteractiveTable({ table }: { table: DataTableStructure }) {
  if (!table || !table.columns || !table.rows || table.rows.length === 0) return null;
  const headers = table.columns;
  const rows = table.rows.map(r => table.columns.map(c => String(r[c] ?? '--')));
  return <MobileTableOrCards headers={headers} rows={rows} />;
}

/** Renders the full JD content from an artifact */
function JDContentCard({ artifact }: { artifact: ArtifactModel }) {
  const c = artifact.content;
  const [expanded, setExpanded] = React.useState(false);

  return (
    <div className="mt-2 border border-slate-700/60 rounded-xl overflow-hidden bg-slate-950/70">
      {/* JD Header */}
      <div className="flex items-center justify-between px-3 py-2 bg-slate-800/80 border-b border-slate-700/60">
        <div className="flex items-center gap-2">
          <Briefcase className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-xs font-bold text-white">{artifact.title || c.role_title}</span>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-[10px] text-emerald-400 hover:text-emerald-300 transition"
        >
          {expanded ? '▲ Collapse' : '▼ View Full JD'}
        </button>
      </div>

      {/* Quick info always visible */}
      <div className="px-3 py-2 grid grid-cols-2 gap-1.5">
        {c.role_title && (
          <div className="text-[10px]">
            <span className="text-slate-500">Role</span>
            <div className="text-slate-200 font-medium">{c.role_title}</div>
          </div>
        )}
        {c.department && (
          <div className="text-[10px]">
            <span className="text-slate-500">Department</span>
            <div className="text-slate-200 font-medium">{c.department}</div>
          </div>
        )}
        {c.salary_range && (
          <div className="text-[10px]">
            <span className="text-slate-500">Salary</span>
            <div className="text-emerald-400 font-bold">{c.salary_range}</div>
          </div>
        )}
        {c.employment_type && (
          <div className="text-[10px]">
            <span className="text-slate-500">Type</span>
            <div className="text-slate-200">{c.employment_type}</div>
          </div>
        )}
        {c.location && (
          <div className="col-span-2 text-[10px]">
            <span className="text-slate-500">Location</span>
            <div className="text-slate-300">{c.location}</div>
          </div>
        )}
      </div>

      {/* Expanded full JD */}
      {expanded && (
        <div className="px-3 pb-3 space-y-2.5 border-t border-slate-700/40 pt-2">
          {c.about_role && (
            <div>
              <div className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider mb-1">About the Role</div>
              <p className="text-[11px] text-slate-300 leading-relaxed">{c.about_role}</p>
            </div>
          )}
          {c.responsibilities && c.responsibilities.length > 0 && (
            <div>
              <div className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider mb-1">Responsibilities</div>
              <ul className="space-y-1">
                {c.responsibilities.map((r, i) => (
                  <li key={i} className="text-[11px] text-slate-300 flex gap-1.5">
                    <span className="text-emerald-500 mt-0.5">•</span>
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {c.requirements && c.requirements.length > 0 && (
            <div>
              <div className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider mb-1">Requirements</div>
              <ul className="space-y-1">
                {c.requirements.map((r, i) => (
                  <li key={i} className="text-[11px] text-slate-300 flex gap-1.5">
                    <span className="text-emerald-500 mt-0.5">•</span>
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {c.nice_to_have && c.nice_to_have.length > 0 && (
            <div>
              <div className="text-[10px] font-bold text-amber-400 uppercase tracking-wider mb-1">Nice to Have</div>
              <ul className="space-y-1">
                {c.nice_to_have.map((r, i) => (
                  <li key={i} className="text-[11px] text-slate-400 flex gap-1.5">
                    <span className="text-amber-500 mt-0.5">◆</span>
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

const DEFAULT_PROMPTS = [
  "Check headcount distribution across all departments",
  "Show attendance of Priya",
  "Recruit a new senior backend engineer for HealthPulse",
  "List all employees in our company"
];

export function CEOMobileChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [dynamicPrompts, setDynamicPrompts] = useState<string[]>(DEFAULT_PROMPTS);
  const [isFrameMode, setIsFrameMode] = useState(true);
  const [timeContext, setTimeContext] = useState<any>(null);
  const [isStreamingActive, setIsStreamingActive] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  const fetchStarterSuggestions = async () => {
    try {
      const res = await fetch('/api/v1/orchestration/suggestions');
      if (res.ok) {
        const data = await res.json();
        if (data.suggested_prompts?.length) {
          setDynamicPrompts(data.suggested_prompts);
        }
        if (data.time_context) {
          setTimeContext(data.time_context);
        }
      }
    } catch (e) {
      console.error('Failed to fetch starter suggestions:', e);
    }
  };

  const fetchUnifiedMessages = async () => {
    if (isStreamingActive) return;
    try {
      const res = await fetch('/api/v1/chat/messages');
      if (res.ok) {
        const data = await res.json();
        if (data && data.length > 0) {
          const formatted: Message[] = data.map((m: any, idx: number) => {
            // Merge top-level artifact/approval_request into structured_data so the JD card renders
            const sd = m.structured_data || {};
            const mergedStructuredData = {
              ...sd,
              artifact: sd.artifact || m.artifact || null,
              approval_request: sd.approval_request || m.approval_request || null,
            };
            return {
              id: m.id || String(idx),
              sender: m.role === 'user' ? 'user' : 'ai',
              text: m.content,
              structured_data: mergedStructuredData,
              suggested_prompts: m.suggested_prompts || sd.suggested_prompts,
              timestamp: m.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            };
          });
          setMessages(formatted);

          const latestAi = [...formatted].reverse().find(m => m.sender === 'ai');
          if (latestAi?.suggested_prompts?.length) {
            setDynamicPrompts(latestAi.suggested_prompts);
          }
        } else if (messages.length === 0) {
          setMessages([{
            id: '1',
            sender: 'ai',
            text: "Good day, CEO. Executive Workforce AI is synchronized with Supabase & MongoDB Atlas. What command would you like to issue?",
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            suggested_prompts: dynamicPrompts
          }]);
        }
      }
    } catch (e) {
      console.error('Failed to fetch unified chat:', e);
    }
  };

  useEffect(() => {
    fetchStarterSuggestions();
    fetchUnifiedMessages();
    const interval = setInterval(() => {
      if (!isStreamingActive) fetchUnifiedMessages();
    }, 3000);
    return () => clearInterval(interval);
  }, [isStreamingActive]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onresult = (event: any) => {
          const transcript = Array.from(event.results)
            .map((result: any) => result[0].transcript)
            .join('');
          setInput(transcript);
        };

        recognition.onerror = () => setIsListening(false);
        recognition.onend = () => setIsListening(false);
        recognitionRef.current = recognition;
      }
    }
  }, []);

  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in this browser.');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      setInput('');
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const handleApprove = async (workflowId: string) => {
    if (!workflowId) return;
    try {
      const res = await fetch(`/api/v1/orchestration/workflows/${workflowId}/approve`, {
        method: 'POST',
      });
      if (res.ok) {
        const data = await res.json();
        setMessages(prev =>
          prev.map(m => {
            if (m.id === workflowId || m.structured_data?.approval_request?.workflow_id === workflowId) {
              const updatedSData = {
                ...m.structured_data,
                artifact: m.structured_data?.artifact ? { ...m.structured_data.artifact, status: 'APPROVED' } : undefined,
                approval_request: m.structured_data?.approval_request ? { ...m.structured_data.approval_request, status: 'APPROVED' } : undefined,
              };
              return { ...m, structured_data: updatedSData };
            }
            return m;
          })
        );
        if (data.next_message) {
          const nextMsg: Message = {
            id: 'next-' + Date.now(),
            sender: 'ai',
            text: data.next_message,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          };
          setMessages(prev => [...prev, nextMsg]);
        }
      }
    } catch (e) {
      console.error('Approve failed:', e);
    }
  };

  const handleRevise = async (workflowId: string, feedback: string) => {
    if (!workflowId || !feedback) return;
    try {
      const userFeedbackMsg: Message = {
        id: 'feedback-' + Date.now(),
        sender: 'user',
        text: feedback,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages(prev => [...prev, userFeedbackMsg]);

      const res = await fetch(`/api/v1/orchestration/workflows/${workflowId}/revise`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feedback }),
      });
      if (res.ok) {
        const data = await res.json();
        const revisedMsg: Message = {
          id: 'revised-' + Date.now(),
          sender: 'ai',
          text: data.next_message || 'Revised proposal based on your feedback.',
          structured_data: {
            artifact: data.artifact,
            approval_request: data.approval_request,
          },
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages(prev => [...prev, revisedMsg]);
      }
    } catch (e) {
      console.error('Revise failed:', e);
    }
  };

  const handleSend = async (textToSend?: string) => {
    const query = (textToSend || input).trim();
    if (!query || isLoading) return;

    const userMsgId = Date.now().toString();
    const userMessage: Message = {
      id: userMsgId,
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    const streamMsgId = 'stream-' + Date.now();
    const initialAssistantMsg: Message = {
      id: streamMsgId,
      sender: 'ai',
      text: '',
      isStreaming: true,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    // Immediately display user message and streaming placeholder in chat
    setMessages(prev => [...prev, userMessage, initialAssistantMsg]);
    setInput('');
    setIsLoading(true);
    setIsStreamingActive(true);

    try {
      const response = await fetch('/api/v1/orchestration/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          initiator: 'CEO Mobile User',
          channel: 'CEO_MOBILE'
        })
      });

      if (response.ok && response.body) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let accumulatedText = '';
        let structuredData: any = null;
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

            if (eventType === 'token') {
              try {
                const parsed = JSON.parse(dataStr);
                accumulatedText += parsed.token;
                setMessages(prev =>
                  prev.map(m => m.id === streamMsgId ? { ...m, text: accumulatedText, isStreaming: true } : m)
                );
              } catch (_) {}
            } else if (eventType === 'complete') {
              try {
                const comp = JSON.parse(dataStr);
                const sr = comp.structured_response || {};
                // Merge structured_response fields into structuredData so artifact/approval_request are captured
                structuredData = {
                  ...(sr),
                  artifact: sr.artifact || comp.envelope?.artifact || null,
                  approval_request: sr.approval_request || comp.envelope?.approval_request || null,
                  decision: sr.decision || comp.decision,
                };
                if (sr.suggested_prompts?.length) {
                  setDynamicPrompts(sr.suggested_prompts);
                }
              } catch (_) {}
            }
          }
        }

        setMessages(prev =>
          prev.map(m => m.id === streamMsgId ? {
            ...m,
            text: accumulatedText.trim() || 'Processed your request.',
            structured_data: structuredData,
            isStreaming: false
          } : m)
        );
      } else {
        const fallbackRes = await fetch('/api/v1/orchestration/execute', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: query,
            initiator: 'CEO Mobile User',
            channel: 'CEO_MOBILE'
          })
        });
        const data = await fallbackRes.json();
        setMessages(prev =>
          prev.map(m => m.id === streamMsgId ? {
            ...m,
            text: data.envelope?.text || data.markdown_answer || 'Processed your request.',
            structured_data: data.structured_response,
            isStreaming: false
          } : m)
        );
      }
    } catch (err) {
      console.error(err);
      setMessages(prev => prev.filter(m => m.id !== streamMsgId));
    } finally {
      setIsLoading(false);
      setIsStreamingActive(false);
      setTimeout(fetchUnifiedMessages, 1000);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-0 md:p-4 font-sans">
      <div className={`w-full ${isFrameMode ? 'max-w-md h-[92vh] border border-slate-800 rounded-3xl shadow-2xl overflow-hidden' : 'h-screen'} bg-slate-900 flex flex-col relative`}>
        
        {/* Header */}
        <div className="bg-slate-900/90 backdrop-blur border-b border-slate-800 px-4 py-3 flex items-center justify-between z-10 shrink-0">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="font-semibold text-sm tracking-tight text-white">CEO Autonomous AI</span>
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              </div>
              <p className="text-[10px] text-slate-400 flex items-center gap-1">
                {timeContext?.period ? <span className="capitalize text-emerald-400 font-medium">{timeContext.period} Sync</span> : 'Live Sync'} • Supabase & Atlas
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-1">
            <button 
              onClick={() => fetchUnifiedMessages()}
              className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition"
              title="Sync Chat"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <button 
              onClick={() => setIsFrameMode(!isFrameMode)}
              className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition"
              title="Toggle Frame Mode"
            >
              {isFrameMode ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3.5">
          {messages.map((msg, idx) => {
            const isUser = msg.sender === 'user';
            const sData = msg.structured_data;

            return (
              <div
                key={msg.id || idx}
                className={`flex flex-col animate-in fade-in duration-150 ${isUser ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`max-w-[92%] rounded-2xl px-3.5 py-2.5 text-xs leading-relaxed space-y-2 ${
                    isUser
                      ? 'bg-emerald-600 text-white rounded-br-none shadow-sm'
                      : 'bg-slate-800/90 border border-slate-700/60 text-slate-200 rounded-bl-none shadow-sm'
                  }`}
                >
                  {/* Structured Decision Badge */}
                  {!isUser && sData?.decision && (
                    <div className="flex items-center gap-1.5 pb-1 border-b border-slate-700/60">
                      <span className="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                        {sData.decision.replace('_', ' ')}
                      </span>
                      {sData.intent && (
                        <span className="text-[9px] text-slate-400 uppercase">[{sData.intent}]</span>
                      )}
                    </div>
                  )}

                  {/* Summary Callout */}
                  {!isUser && sData?.summary && (
                    <div className="bg-slate-900/60 border-l-2 border-emerald-500 px-2.5 py-1 text-[11px] text-slate-300 rounded-r">
                      <span className="font-semibold text-emerald-400">Takeaway: </span>
                      {sData.summary}
                    </div>
                  )}

                  {/* Content */}
                  {isUser ? (
                    <div className="whitespace-pre-wrap leading-relaxed text-white text-xs">{msg.text}</div>
                  ) : (
                    <div className="relative">
                      <AIMarkdownRenderer content={msg.text} />
                      {msg.isStreaming && (
                        <span className="inline-block w-1.5 h-3.5 bg-emerald-400 ml-1 rounded-xs animate-pulse align-middle" />
                      )}
                    </div>
                  )}

                  {/* Mobile Data Table */}
                  {!isUser && sData?.data_table && (
                    <MobileInteractiveTable table={sData.data_table} />
                  )}

                  {/* Key Metrics */}
                  {!isUser && sData?.key_metrics && sData.key_metrics.length > 0 && (
                    <div className="grid grid-cols-2 gap-1.5 pt-1">
                      {sData.key_metrics.map((m, mIdx) => (
                        <div key={mIdx} className="bg-slate-900/80 border border-slate-700/50 rounded-lg p-1.5 flex flex-col justify-between">
                          <span className="text-[9px] text-slate-400 truncate">{m.label}</span>
                          <div className="flex items-center justify-between mt-0.5">
                            <span className="text-xs font-bold text-white">{m.value}</span>
                            {m.trend === 'up' && <TrendingUp className="w-3 h-3 text-emerald-400" />}
                            {m.trend === 'down' && <TrendingDown className="w-3 h-3 text-red-400" />}
                            {m.trend === 'stable' && <Minus className="w-3 h-3 text-slate-400" />}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Detected Entities */}
                  {!isUser && sData?.entities_detected && sData.entities_detected.length > 0 && (
                    <div className="flex flex-wrap gap-1 pt-1">
                      {sData.entities_detected.map((e, eIdx) => (
                        <span key={eIdx} className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-slate-900 border border-slate-700 text-[9px] text-slate-300">
                          {e.type === 'EMPLOYEE' ? <User className="w-2.5 h-2.5 text-emerald-400" /> : <Building2 className="w-2.5 h-2.5 text-emerald-400" />}
                          <span>{e.name}</span>
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Recommended Actions */}
                  {!isUser && sData?.recommended_actions && sData.recommended_actions.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-1 border-t border-slate-700/50">
                      {sData.recommended_actions.map((act) => (
                        <button
                          key={act.id}
                          onClick={() => act.action_type === 'QUERY' ? handleSend(act.target) : window.open(act.target, '_self')}
                          className="px-2 py-1 rounded bg-slate-900 hover:bg-emerald-600 hover:text-white border border-slate-700 text-[10px] text-emerald-300 transition flex items-center gap-1"
                        >
                          <Zap className="w-2.5 h-2.5" />
                          <span>{act.label}</span>
                          <ArrowUpRight className="w-2.5 h-2.5" />
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Mobile HITL Approval Gate Card */}
                  {!isUser && (sData?.artifact || sData?.approval_request) && (() => {
                    const art = sData.artifact;
                    const appr = sData.approval_request;
                    const isApproved = art?.status === 'APPROVED' || appr?.status === 'APPROVED';
                    const isJD = art?.type === 'JOB_DESCRIPTION';
                    const isPayroll = art?.type === 'PAYROLL_RUN';

                    return (
                      <div className="mt-2.5 rounded-xl bg-slate-900 border border-emerald-500/40 shadow-sm overflow-hidden">
                        {/* Card Header */}
                        <div className="flex items-center justify-between px-3 py-2 bg-gradient-to-r from-slate-800 to-slate-900 border-b border-slate-700/60">
                          <div className="flex items-center gap-1.5">
                            {isJD ? <FileText className="w-3.5 h-3.5 text-emerald-400" /> : <Briefcase className="w-3.5 h-3.5 text-amber-400" />}
                            <span className={`w-1.5 h-1.5 rounded-full ${isApproved ? 'bg-emerald-400' : 'bg-amber-400 animate-ping'}`} />
                            <span className="text-[11px] font-bold text-white uppercase tracking-wider">
                              {isApproved ? '✓ Authorized' : isJD ? 'JD Review Gate' : 'Approval Gate'}
                            </span>
                          </div>
                          <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 font-mono">
                            {art?.type || 'APPROVAL'}
                          </span>
                        </div>

                        <div className="p-3 space-y-2.5">
                          {/* Action Required label */}
                          <div className="text-xs font-semibold text-slate-100">
                            {appr?.action_required || art?.title || 'Executive Authorization Required'}
                          </div>

                          {/* JD Content Block */}
                          {isJD && art && <JDContentCard artifact={art} />}

                          {/* Payroll Content Block */}
                          {isPayroll && art?.content?.total_net_payout && (
                            <div className="text-[11px] text-slate-300 bg-slate-950/60 p-2 rounded border border-slate-800 space-y-1">
                              <div><strong>Period:</strong> {art.content.period}</div>
                              <div><strong>Net Disbursed:</strong> {art.content.total_net_payout} ({art.content.employee_count} staff)</div>
                            </div>
                          )}

                          {/* Generic artifact (salary_range shown for other types) */}
                          {!isJD && !isPayroll && art?.content?.salary_range && (
                            <div className="text-[11px] text-slate-300 bg-slate-950/60 p-2 rounded border border-slate-800 space-y-1">
                              <div><strong>Role:</strong> {art.content.role_title} ({art.content.department})</div>
                              <div><strong>Band:</strong> {art.content.salary_range}</div>
                            </div>
                          )}

                          {/* Approve / Revise buttons */}
                          {!isApproved ? (
                            <div className="flex items-center gap-2 pt-1">
                              <button
                                onClick={() => handleApprove(appr?.workflow_id || appr?.id || msg.id)}
                                className="flex-1 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow transition flex items-center justify-center gap-1.5"
                              >
                                <CheckCircle2 className="w-3.5 h-3.5" />
                                <span>{isJD ? '✓ Approve & Post JD' : isPayroll ? '✓ Authorize & Disburse' : '✓ Approve'}</span>
                              </button>
                              <button
                                onClick={() => {
                                  const feedback = prompt(isJD ? 'Request changes to the JD (e.g., add specific skills, change salary):' : 'Enter your feedback for revision:');
                                  if (feedback) handleRevise(appr?.workflow_id || msg.id, feedback);
                                }}
                                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs border border-slate-700 transition"
                              >
                                Revise
                              </button>
                            </div>
                          ) : (
                            <div className="text-[11px] text-emerald-400 font-medium flex items-center gap-1.5 pt-1">
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              <span>{isJD ? 'JD approved and posted to Azyntrix Careers!' : 'Execution authorized and downstream actions dispatched.'}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })()}

                  <div className={`text-[9px] mt-1 ${isUser ? 'text-emerald-200/70 text-right' : 'text-slate-400'}`}>
                    {msg.timestamp}
                  </div>
                </div>
              </div>
            );
          })}

          {isLoading && (
            <div className="flex items-center space-x-2 text-xs text-slate-400 bg-slate-800/50 border border-slate-700/40 rounded-xl px-3 py-2 w-fit">
              <Sparkles className="w-3.5 h-3.5 animate-spin text-emerald-400" />
              <span>Multi-agent reasoning & domain synthesis...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Dynamic Contextual Suggested Prompts Bar */}
        <div className="px-3 py-2 bg-slate-900/95 border-t border-slate-800 overflow-x-auto scrollbar-none flex items-center gap-1.5 shrink-0">
          <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider whitespace-nowrap flex items-center gap-1">
            <Sparkles className="w-2.5 h-2.5 text-emerald-400" /> Suggestions:
          </span>
          {dynamicPrompts.map((prompt, i) => (
            <button
              key={i}
              onClick={() => handleSend(prompt)}
              className="text-[11px] whitespace-nowrap bg-slate-800 hover:bg-slate-700 border border-slate-700/80 text-slate-300 hover:text-white rounded-full px-3 py-1 transition flex items-center gap-1 shadow-xs"
            >
              <span>{prompt}</span>
              <ArrowUpRight className="w-2.5 h-2.5 text-slate-400" />
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div className="p-3 bg-slate-900 border-t border-slate-800 flex items-center space-x-2 shrink-0">
          <button
            onClick={toggleListening}
            className={`p-2.5 rounded-full transition ${
              isListening ? 'bg-red-500 text-white animate-pulse' : 'bg-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
          </button>

          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder={isListening ? 'Listening...' : 'Command AI fleet...'}
            className="flex-1 bg-slate-800 border border-slate-700 rounded-full px-4 py-2 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-emerald-500"
          />

          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || isLoading}
            className="p-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white rounded-full transition shadow-sm"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>

      </div>
    </div>
  );
}

export default CEOMobileChatPage;
