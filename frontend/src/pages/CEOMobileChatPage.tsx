import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, Mic, MicOff, Sparkles, RefreshCw, Maximize2, Minimize2, Bot,
  ArrowUpRight, CheckCircle2, Clock, Trash2, Check
} from 'lucide-react';
import { motion } from 'framer-motion';
import { ChatGPTMarkdownRenderer } from "@/components/chat/ChatGPTMarkdownRenderer";

interface StructuredData {
  intent?: string;
  decision?: string;
  summary?: string;
  markdown_answer?: string;
  workflow_id?: string;
  suggested_prompts?: string[];
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
  "Draft a job opening for Senior Frontend Engineer",
  "List active employees in our company"
];

export function CEOMobileChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [dynamicPrompts, setDynamicPrompts] = useState<string[]>(DEFAULT_PROMPTS);
  const [isFrameMode, setIsFrameMode] = useState(true);
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
            text: "Hello! I am your AI HR & Workforce Assistant connected directly to your live database. Ask me anything about headcount, attendance, payroll, or issue workflow commands.",
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

  const handleClearChat = async () => {
    try {
      await fetch('/api/v1/chat/messages', { method: 'DELETE' });
      await fetch('/api/v1/orchestration/clear', { method: 'POST' });
      setMessages([]);
      await fetchUnifiedMessages();
    } catch (e) {
      console.error('Failed to clear chat:', e);
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
    <div className="min-h-screen bg-slate-100 text-slate-800 flex flex-col items-center justify-center p-0 md:p-4 font-sans selection:bg-emerald-100 selection:text-emerald-900">
      <div className={`w-full ${isFrameMode ? 'max-w-md h-[92vh] border border-slate-200 rounded-3xl shadow-xl overflow-hidden' : 'h-screen'} bg-white flex flex-col relative`}>
        
        {/* Light Theme Header */}
        <div className="bg-white/95 backdrop-blur border-b border-slate-200 px-4 py-3 flex items-center justify-between z-10 shrink-0 shadow-xs">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-full bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="font-semibold text-sm tracking-tight text-slate-900">HRMS AI Assistant</span>
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              </div>
              <p className="text-[10px] text-slate-500 flex items-center gap-1">
                Database Live • Online
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-1">
            <button 
              onClick={() => fetchUnifiedMessages()}
              className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-500 hover:text-slate-800 transition"
              title="Sync Chat"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <button 
              onClick={handleClearChat}
              className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-red-600 transition"
              title="Clear History"
            >
              <Trash2 className="w-4 h-4" />
            </button>
            <button 
              onClick={() => setIsFrameMode(!isFrameMode)}
              className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-500 hover:text-slate-800 transition"
              title="Toggle Frame Mode"
            >
              {isFrameMode ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50">
          {messages.map((msg, idx) => {
            const isUser = msg.sender === 'user';
            const sData = msg.structured_data;
            const approvalReq = sData?.approval_request;
            const workflowId = sData?.workflow_id || approvalReq?.workflow_id;
            const isPendingApproval = approvalReq?.status === 'PENDING';

            return (
              <motion.div
                key={msg.id || idx}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`max-w-[92%] rounded-2xl px-4 py-3 text-xs leading-relaxed space-y-2 ${
                    isUser
                      ? 'bg-emerald-600 text-white rounded-br-xs shadow-xs'
                      : 'bg-white border border-slate-200 text-slate-800 rounded-bl-xs shadow-xs'
                  }`}
                >
                  {/* Clean conversational markdown */}
                  {isUser ? (
                    <div className="whitespace-pre-wrap leading-relaxed text-[13px]">{msg.text}</div>
                  ) : (
                    <div className="text-[13px] leading-relaxed text-slate-800">
                      <ChatGPTMarkdownRenderer content={msg.text} />
                    </div>
                  )}

                  {/* Clean Simple Inline HITL Approval Box */}
                  {!isUser && isPendingApproval && workflowId && (
                    <div className="mt-2.5 pt-2.5 border-t border-slate-200 flex flex-col gap-2 bg-slate-50 p-2.5 rounded-xl">
                      <div className="flex items-center justify-between text-[11px] text-amber-700 font-medium">
                        <span className="flex items-center gap-1.5">
                          <Clock className="w-3.5 h-3.5 animate-pulse text-amber-600" />
                          Approval Required: {approvalReq?.action_type || 'Workflow Action'}
                        </span>
                      </div>
                      
                      {revisingId === workflowId ? (
                        <div className="flex flex-col gap-2 bg-white p-2 rounded-lg border border-slate-200">
                          <input
                            type="text"
                            placeholder="Type revision notes..."
                            value={feedbackInput[workflowId] || ''}
                            onChange={(e) => setFeedbackInput({ ...feedbackInput, [workflowId]: e.target.value })}
                            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-emerald-500"
                          />
                          <div className="flex gap-1.5 justify-end">
                            <button
                              onClick={() => setRevisingId(null)}
                              className="px-2 py-1 rounded-md bg-slate-100 text-slate-600 hover:text-slate-900 text-[11px]"
                            >
                              Cancel
                            </button>
                            <button
                              onClick={() => handleRevise(workflowId, feedbackInput[workflowId] || '')}
                              className="px-2.5 py-1 rounded-md bg-amber-600 hover:bg-amber-500 text-white font-medium text-[11px]"
                            >
                              Submit Revision
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2 pt-0.5">
                          <button
                            onClick={() => handleApprove(workflowId)}
                            className="flex-1 py-1.5 px-3 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-[11px] flex items-center justify-center gap-1.5 transition shadow-xs"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            Approve Action
                          </button>
                          <button
                            onClick={() => setRevisingId(workflowId)}
                            className="py-1.5 px-3 rounded-lg bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 font-medium text-[11px] flex items-center justify-center gap-1.5 transition shadow-xs"
                          >
                            Request Revision
                          </button>
                        </div>
                      )}
                    </div>
                  )}

                  <div className={`text-[10px] pt-1 text-right ${isUser ? 'text-emerald-100' : 'text-slate-400'}`}>
                    {msg.timestamp}
                  </div>
                </div>
              </motion.div>
            );
          })}

          {isLoading && (
            <div className="flex items-center space-x-2 text-xs text-slate-500 bg-white border border-slate-200 rounded-xl px-3 py-2 w-fit shadow-xs">
              <Sparkles className="w-3.5 h-3.5 animate-spin text-emerald-600" />
              <span>Thinking...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Prompts Bar */}
        <div className="px-3 py-2 bg-white border-t border-slate-200 overflow-x-auto scrollbar-none flex items-center gap-1.5 shrink-0">
          <span className="text-[9px] font-semibold text-slate-500 uppercase tracking-wider whitespace-nowrap flex items-center gap-1">
            <Sparkles className="w-2.5 h-2.5 text-emerald-600" /> Suggestions:
          </span>
          {dynamicPrompts.map((prompt, i) => (
            <button
              key={i}
              onClick={() => handleSend(prompt)}
              className="text-[11px] whitespace-nowrap bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-700 hover:text-slate-900 rounded-full px-3 py-1 transition flex items-center gap-1 shadow-xs"
            >
              <span>{prompt}</span>
              <ArrowUpRight className="w-2.5 h-2.5 text-slate-400" />
            </button>
          ))}
        </div>

        {/* Light Theme Input Bar */}
        <div className="p-3 bg-white border-t border-slate-200 flex items-center space-x-2 shrink-0">
          <button
            onClick={toggleListening}
            className={`p-2.5 rounded-full transition ${
              isListening ? 'bg-red-500 text-white animate-pulse' : 'bg-slate-100 text-slate-600 hover:text-slate-900'
            }`}
          >
            {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
          </button>

          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder={isListening ? 'Listening...' : 'Type a message...'}
            className="flex-1 bg-slate-50 border border-slate-200 rounded-full px-4 py-2 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-emerald-500 focus:bg-white transition"
          />

          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || isLoading}
            className="p-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white rounded-full transition shadow-xs"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>

      </div>
    </div>
  );
}
