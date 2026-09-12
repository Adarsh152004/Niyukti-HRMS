import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, Mic, MicOff, Sparkles, RefreshCw, Maximize2, Minimize2, Bot,
  ArrowUpRight, CheckCircle2, User, Building2, Zap, Clock
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChatGPTMarkdownRenderer } from "@/components/chat/ChatGPTMarkdownRenderer";
import { ArtifactCard, ArtifactData, ApprovalRequestData } from '@/components/chat/ArtifactCard';
import { WidgetRegistry } from '@/components/chat/widgets/WidgetRegistry';

interface StructuredData {
  intent?: string;
  decision?: string;
  summary?: string;
  markdown_answer?: string;
  widgets?: any[];
  artifact?: ArtifactData;
  approval_request?: ApprovalRequestData;
  workflow_id?: string;
  suggested_prompts?: string[];
}

interface Message {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  structured_data?: StructuredData;
  suggested_prompts?: string[];
  timestamp: string;
}

const DEFAULT_PROMPTS = [
  "Check headcount distribution across all departments",
  "Show attendance summary for today",
  "Recruit a senior engineer for engineering team",
  "List active employees in our company"
];

export function CEOMobileChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [dynamicPrompts, setDynamicPrompts] = useState<string[]>(DEFAULT_PROMPTS);
  const [isFrameMode, setIsFrameMode] = useState(true);
  const [timeContext, setTimeContext] = useState<any>(null);
  const [feedbackInput, setFeedbackInput] = useState<{ [workflowId: string]: string }>({});
  const [revisingId, setRevisingId] = useState<string | null>(null);

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
    try {
      const res = await fetch('/api/v1/chat/messages');
      if (res.ok) {
        const data = await res.json();
        if (data && data.length > 0) {
          const formatted: Message[] = data.map((m: any, idx: number) => ({
            id: m.id || String(idx),
            sender: m.role === 'user' ? 'user' : 'ai',
            text: m.content,
            structured_data: m.structured_data,
            suggested_prompts: m.suggested_prompts,
            timestamp: m.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }));

          setMessages(prev => {
            if (prev.length === 0) return formatted;
            const map = new Map<string, Message>();
            prev.forEach(m => map.set(m.id, m));
            formatted.forEach(m => map.set(m.id, m));
            return Array.from(map.values());
          });

          const latestAi = [...formatted].reverse().find(m => m.sender === 'ai');
          if (latestAi?.suggested_prompts?.length) {
            setDynamicPrompts(latestAi.suggested_prompts);
          }
        } else if (messages.length === 0) {
          setMessages([{
            id: 'welcome-1',
            sender: 'ai',
            text: "Hello! I am your AI Executive Workforce Assistant connected directly to your live database. Ask me anything about headcount, attendance, payroll, hiring, or issue workflow commands.",
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
    const interval = setInterval(fetchUnifiedMessages, 3000);
    return () => clearInterval(interval);
  }, []);

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
    try {
      const res = await fetch(`/api/v1/orchestration/workflows/${workflowId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      if (res.ok) {
        await fetchUnifiedMessages();
      }
    } catch (e) {
      console.error('Failed to approve workflow in mobile chat:', e);
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
        await fetchUnifiedMessages();
      }
    } catch (e) {
      console.error('Failed to revise workflow in mobile chat:', e);
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

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/orchestration/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          initiator: 'CEO Mobile User',
          channel: 'CEO_MOBILE'
        })
      });

      const data = await response.json();
      
      const assistantText = data.envelope?.text || data.markdown_answer || data.text || "Processed your request.";
      const assistantMsg: Message = {
        id: data.envelope?.message_id || Date.now().toString(),
        sender: 'ai',
        text: assistantText,
        structured_data: data.structured_response || data.envelope,
        suggested_prompts: data.suggested_prompts || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, assistantMsg]);

      if (data.suggested_prompts?.length) {
        setDynamicPrompts(data.suggested_prompts);
      }

    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-0 md:p-4 font-sans selection:bg-emerald-500 selection:text-black">
      <div className={`w-full ${isFrameMode ? 'max-w-md h-[92vh] border border-slate-800 rounded-3xl shadow-2xl overflow-hidden' : 'h-screen'} bg-slate-900 flex flex-col relative`}>
        
        {/* Header */}
        <div className="bg-slate-900/90 backdrop-blur border-b border-slate-800 px-4 py-3 flex items-center justify-between z-10 shrink-0">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="font-semibold text-sm tracking-tight text-white">HRMS AI Assistant</span>
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              </div>
              <p className="text-[10px] text-slate-400 flex items-center gap-1">
                {timeContext?.period ? <span className="capitalize text-emerald-400 font-medium">{timeContext.period} Sync</span> : 'Live Sync'} • Database Active
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
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, idx) => {
            const isUser = msg.sender === 'user';
            const sData = msg.structured_data;
            const approvalReq = sData?.approval_request || (msg as any).approval_request;
            const workflowId = sData?.workflow_id || (msg as any).workflow_id || approvalReq?.workflow_id;
            const isPendingApproval = approvalReq?.status === 'PENDING';

            return (
              <motion.div
                key={msg.id || idx}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`max-w-[94%] rounded-2xl px-4 py-3 text-xs leading-relaxed space-y-2 ${
                    isUser
                      ? 'bg-emerald-600 text-white rounded-br-xs shadow-md'
                      : 'bg-slate-800/90 border border-slate-700/60 text-slate-200 rounded-bl-xs shadow-md'
                  }`}
                >
                  {/* Clean humanoid markdown answer */}
                  {isUser ? (
                    <div className="whitespace-pre-wrap leading-relaxed text-[13px]">{msg.text}</div>
                  ) : (
                    <div className="text-[13px] leading-relaxed">
                      <ChatGPTMarkdownRenderer content={msg.text} />
                    </div>
                  )}

                  {/* Clean inline HITL Approval bar when action is required */}
                  {!isUser && isPendingApproval && workflowId && (
                    <div className="mt-3 pt-3 border-t border-slate-700/60 flex flex-col gap-2">
                      <div className="flex items-center justify-between text-[11px] text-amber-400 font-medium">
                        <span className="flex items-center gap-1.5">
                          <Clock className="w-3.5 h-3.5 animate-pulse" />
                          Approval Required: {approvalReq?.action_type || 'Workflow Action'}
                        </span>
                      </div>
                      
                      {revisingId === workflowId ? (
                        <div className="flex flex-col gap-2 bg-slate-900/80 p-2.5 rounded-xl border border-slate-700">
                          <input
                            type="text"
                            placeholder="Type revision notes..."
                            value={feedbackInput[workflowId] || ''}
                            onChange={(e) => setFeedbackInput({ ...feedbackInput, [workflowId]: e.target.value })}
                            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-emerald-500"
                          />
                          <div className="flex gap-1.5 justify-end">
                            <button
                              onClick={() => setRevisingId(null)}
                              className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-400 hover:text-slate-200 text-[11px]"
                            >
                              Cancel
                            </button>
                            <button
                              onClick={() => handleRevise(workflowId, feedbackInput[workflowId] || '')}
                              className="px-2.5 py-1 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-medium text-[11px]"
                            >
                              Submit Revision
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleApprove(workflowId)}
                            className="flex-1 py-1.5 px-3 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-[11px] flex items-center justify-center gap-1.5 transition shadow-xs"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            Approve Action
                          </button>
                          <button
                            onClick={() => setRevisingId(workflowId)}
                            className="py-1.5 px-3 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-200 font-medium text-[11px] flex items-center justify-center gap-1.5 transition"
                          >
                            Request Revision
                          </button>
                        </div>
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
                  {!isUser && (sData?.artifact || (msg as any).artifact) && (
                    <div className="mt-3 text-left">
                      <ArtifactCard
                        artifact={sData?.artifact || (msg as any).artifact}
                        approvalRequest={sData?.approval_request || (msg as any).approval_request}
                        workflowId={sData?.workflow_id || (msg as any).workflow_id}
                        onApprove={handleApprove}
                        onRevise={handleRevise}
                      />
                    </div>
                  )}

                  <div className={`text-[9px] pt-1 text-right ${isUser ? 'text-emerald-200/80' : 'text-slate-400'}`}>
                    {msg.timestamp}
                  </div>
                </div>
              </motion.div>
            );
          })}

          {isLoading && (
            <div className="flex items-center space-x-2 text-xs text-slate-400 bg-slate-800/50 border border-slate-700/40 rounded-xl px-3 py-2 w-fit">
              <Sparkles className="w-3.5 h-3.5 animate-spin text-emerald-400" />
              <span>Synthesizing response...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Prompts */}
        <div className="px-3 py-2 bg-slate-900/95 border-t border-slate-800 overflow-x-auto scrollbar-none flex items-center gap-1.5 shrink-0">
          <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider whitespace-nowrap flex items-center gap-1">
            <Sparkles className="w-2.5 h-2.5 text-emerald-400" /> Quick Prompts:
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
            placeholder={isListening ? 'Listening...' : 'Type your message...'}
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
