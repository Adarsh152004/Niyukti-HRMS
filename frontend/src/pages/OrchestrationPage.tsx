import React, { useState, useEffect } from 'react';
import {
  Trash2,
  Cpu, Terminal, Brain, Database, Sparkles, RefreshCw, Search,
  ChevronDown, ChevronRight, CheckCircle2, Clock, Copy, Check,
  Code, Activity, Zap, Layers, Filter, Bot, ArrowRight
} from 'lucide-react';

export interface WorkflowNode {
  id: string;
  label: string;
  subtitle?: string;
  type: 'input' | 'agent' | 'tool' | 'database' | 'approval' | 'output';
  status: 'completed' | 'active' | 'running' | 'waiting' | 'upcoming' | 'failed' | string;
  execution_time_ms?: number;
  agent_role?: string;
  handoff_to?: string;
  inputs?: Record<string, any>;
  outputs?: Record<string, any>;
  logs?: string[];
}

export interface WorkflowData {
  query_id: string;
  query: string;
  initiator: string;
  channel: string;
  timestamp: string;
  status: string;
  duration_ms: number;
  llm_provider?: string;
  decision?: string;
  collaboration_chain?: string[];
  nodes: WorkflowNode[];
}

export function OrchestrationPage() {
  const [history, setHistory] = useState<any[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowData | null>(null);
  const [expandedNodes, setExpandedNodes] = useState<Record<string, boolean>>({});
  const [searchQuery, setSearchQuery] = useState('');
  const [channelFilter, setChannelFilter] = useState('ALL');
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [isExecutingWorkflow, setIsExecutingWorkflow] = useState(false);

  // Launch prebuilt autonomous workflow
  const handleLaunchWorkflow = async (queryText: string) => {
    setIsExecutingWorkflow(true);
    try {
      const res = await fetch('/api/v1/orchestration/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: queryText,
          initiator: 'CEO / Executive Partner',
          channel: 'ORCHESTRATION_DAG'
        })
      });
      if (res.ok) {
        const data = await res.json();
        await fetchHistory();
        if (data.run_id) {
          await fetchWorkflowDetails(data.run_id);
        }
      }
    } catch (e) {
      console.error('Failed to trigger workflow', e);
    } finally {
      setIsExecutingWorkflow(false);
    }
  };

  // Human-in-the-loop approval execution
  const handleApproveWorkflow = async (workflowId: string) => {
    try {
      const res = await fetch(`/api/v1/orchestration/workflows/${workflowId}/approve`, {
        method: 'POST'
      });
      if (res.ok) {
        await fetchWorkflowDetails(workflowId);
        await fetchHistory();
      }
    } catch (e) {
      console.error('Approve failed', e);
    }
  };

  // Fetch real workflow runs history
  const fetchHistory = async () => {
    try {
      const res = await fetch('/api/v1/orchestration/history');
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data)) {
          setHistory(data);
          if (data.length > 0 && !selectedWorkflow) {
            fetchWorkflowDetails(data[0].query_id);
          }
        }
      }
    } catch (e) {
      console.error('Failed to fetch orchestration history', e);
    }
  };

  // Fetch full node details for a selected run
  const fetchWorkflowDetails = async (queryId: string) => {
    try {
      const res = await fetch(`/api/v1/orchestration/workflows/${queryId}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedWorkflow(data);
        // Start all collapsed by default
        setExpandedNodes({});
      }
    } catch (e) {
      console.error('Failed to fetch workflow details', e);
    }
  };

  useEffect(() => {
    fetchHistory();
    const interval = setInterval(fetchHistory, 4000);
    return () => clearInterval(interval);
  }, []);

  const toggleNodeExpand = (nodeId: string) => {
    setExpandedNodes((prev) => ({
      ...prev,
      [nodeId]: !prev[nodeId],
    }));
  };

  const copyPayload = (nodeId: string, payload: any) => {
    navigator.clipboard.writeText(JSON.stringify(payload, null, 2));
    setCopiedId(nodeId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const filteredHistory = history.filter((item) => {
    const matchesChannel = channelFilter === 'ALL' || item.channel === channelFilter;
    const matchesSearch =
      !searchQuery.trim() ||
      item.query.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.query_id.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesChannel && matchesSearch;
  });

  const getNodeTheme = (type: string) => {
    switch (type) {
      case 'input':
        return {
          icon: <Terminal className="w-4 h-4 text-sky-400" />,
          dotBg: 'bg-sky-400',
          dotRing: 'ring-sky-400/30',
          border: 'border-sky-500/20',
        };
      case 'agent':
        return {
          icon: <Brain className="w-4 h-4 text-indigo-400" />,
          dotBg: 'bg-indigo-400',
          dotRing: 'ring-indigo-400/30',
          border: 'border-indigo-500/20',
        };
      case 'database':
        return {
          icon: <Database className="w-4 h-4 text-emerald-400" />,
          dotBg: 'bg-emerald-400',
          dotRing: 'ring-emerald-400/30',
          border: 'border-emerald-500/20',
        };
      case 'output':
        return {
          icon: <Sparkles className="w-4 h-4 text-purple-400" />,
          dotBg: 'bg-purple-400',
          dotRing: 'ring-purple-400/30',
          border: 'border-purple-500/20',
        };
      default:
        return {
          icon: <Zap className="w-4 h-4 text-amber-400" />,
          dotBg: 'bg-amber-400',
          dotRing: 'ring-amber-400/30',
          border: 'border-amber-500/20',
        };
    }
  };

  return (
    <div className="space-y-4 pb-12 max-w-7xl mx-auto px-4 sm:px-6">
      
      {/* 1. Sleek Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface p-4 rounded-xl border border-border">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-500 shrink-0">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-text-primary tracking-tight">
              Agent Orchestration
            </h1>
            <p className="text-[11px] text-text-muted">
              Live multi-agent decision telemetry and step-by-step pipeline execution.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <button
            onClick={() => {
              setLoading(true);
              fetchHistory().finally(() => setLoading(false));
            }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-secondary hover:bg-surface-tertiary text-xs font-semibold text-text-secondary border border-border transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>

          <button
            onClick={async () => {
              try {
                const res = await fetch('/api/v1/orchestration/history', { method: 'DELETE' });
                if (res.ok) {
                  setHistory([]);
                  setSelectedWorkflow(null);
                  setExpandedNodes({});
                }
              } catch (err) {
                console.error('Failed to clear orchestration history', err);
              }
            }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-xs font-semibold text-rose-500 border border-rose-500/20 transition"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear History</span>
          </button>
        </div>
      </div>

      {/* Quick Autonomous Workflow Launcher Bar */}
      <div className="p-3 bg-surface border border-border rounded-xl shadow-xs space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-amber-500" />
            <span className="text-xs font-bold text-text-primary">Instant Multi-Agent Autonomous Triggers</span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-500 border border-indigo-500/20 font-mono">
              Live DAG Execution
            </span>
          </div>
          {isExecutingWorkflow && (
            <div className="flex items-center gap-1.5 text-xs text-indigo-500 font-semibold animate-pulse">
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              <span>Orchestrating agents...</span>
            </div>
          )}
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">
          {[
            { label: 'Deterministic Payroll Run', query: 'Run monthly payroll for all employees', icon: Activity, desc: '5-node audit & CEO sign-off gate' },
            { label: 'Job Description Requisition', query: 'Create job description for senior platform engineer', icon: Bot, desc: 'Recruitment lead & JD builder chain' },
            { label: 'Attendance Compliance Audit', query: 'Run attendance compliance audit', icon: Clock, desc: 'Biometric & punch verification' },
            { label: 'Workforce Headcount Sync', query: 'Check active headcount breakdown', icon: Layers, desc: 'Live SQLite ledger distribution' },
          ].map((wf, idx) => {
            const Icon = wf.icon;
            return (
              <button
                key={idx}
                disabled={isExecutingWorkflow}
                onClick={() => handleLaunchWorkflow(wf.query)}
                className="p-2.5 rounded-lg bg-surface-secondary/70 hover:bg-surface-secondary border border-border hover:border-indigo-500/50 text-left transition group disabled:opacity-50"
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-1.5">
                    <Icon className="w-3.5 h-3.5 text-indigo-500 group-hover:scale-110 transition-transform" />
                    <span className="text-xs font-bold text-text-primary group-hover:text-indigo-500 transition-colors">{wf.label}</span>
                  </div>
                  <ArrowRight className="w-3 h-3 text-text-muted group-hover:text-indigo-500 transition-colors" />
                </div>
                <p className="text-[10px] text-text-muted">{wf.desc}</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* 2. Main 2-Column Split */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start">
        
        {/* Left Column: Query History Explorer (4 of 12 Cols) */}
        <div className="lg:col-span-4 bg-surface p-3.5 rounded-xl border border-border space-y-2.5">
          <div className="flex items-center justify-between pb-0.5">
            <h2 className="text-[11px] font-bold text-text-muted uppercase tracking-wider flex items-center gap-1.5">
              <Clock className="w-3 h-3 text-indigo-500" />
              <span>Query History ({filteredHistory.length})</span>
            </h2>
          </div>

          {/* Search Input */}
          <div className="relative">
            <Search className="absolute left-2.5 top-2 w-3.5 h-3.5 text-text-muted" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter queries..."
              className="w-full pl-7.5 pr-2.5 py-1.5 rounded-lg bg-surface-secondary border border-border text-xs text-text-primary placeholder-text-muted focus:outline-none focus:ring-1 focus:ring-accent"
            />
          </div>

          {/* Channel Filters */}
          <div className="flex items-center gap-1 bg-surface-secondary p-0.5 rounded-lg border border-border">
            {['ALL', 'AI_WORKSPACE', 'CEO_MOBILE'].map((ch) => (
              <button
                key={ch}
                onClick={() => setChannelFilter(ch)}
                className={`flex-1 py-1 rounded-md text-[10px] font-bold transition ${
                  channelFilter === ch
                    ? 'bg-accent text-white'
                    : 'text-text-muted hover:text-text-primary'
                }`}
              >
                {ch === 'ALL' ? 'ALL' : ch === 'AI_WORKSPACE' ? 'WORKSPACE' : 'MOBILE'}
              </button>
            ))}
          </div>

          {/* Compact Query Cards List */}
          <div className="space-y-1.5 max-h-[580px] overflow-y-auto pr-0.5">
            {filteredHistory.length > 0 ? (
              filteredHistory.map((item) => {
                const isSelected = selectedWorkflow?.query_id === item.query_id;
                return (
                  <div
                    key={item.query_id}
                    onClick={() => fetchWorkflowDetails(item.query_id)}
                    className={`p-2.5 rounded-lg border transition-all cursor-pointer space-y-1 ${
                      isSelected
                        ? 'bg-indigo-500/10 border-indigo-500/50 border-l-3 border-l-indigo-500'
                        : 'bg-surface hover:bg-surface-secondary/60 border-border'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-1">
                      <span className="font-mono text-[9px] font-bold text-text-muted">
                        {item.query_id}
                      </span>
                      <span className="text-[10px] font-mono font-bold text-emerald-500">
                        {item.duration_ms} ms
                      </span>
                    </div>

                    <p className="text-xs font-semibold text-text-primary line-clamp-2 leading-tight">
                      "{item.query}"
                    </p>

                    <div className="flex items-center justify-between text-[10px] text-text-muted pt-1 border-t border-border/30">
                      <span className="text-indigo-400 font-medium">{item.llm_provider || 'Mistral-Small'}</span>
                      <span>{new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="text-center py-8 text-text-muted text-xs">
                No queries found.
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Continuous Connected Timeline Spine (8 of 12 Cols) */}
        <div className="lg:col-span-8 space-y-3">
          {selectedWorkflow ? (
            <div className="space-y-3">
              
              {/* Query Summary Banner */}
              <div className="bg-surface p-4 rounded-xl border border-border space-y-2">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                      {selectedWorkflow.query_id}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-surface-secondary text-text-secondary border border-border">
                      {selectedWorkflow.llm_provider || 'Mistral-Small'}
                    </span>
                  </div>

                  {selectedWorkflow.status === 'WAITING_FOR_APPROVAL' ? (
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
                      <span>Awaiting Approval ({selectedWorkflow.duration_ms} ms)</span>
                    </span>
                  ) : selectedWorkflow.status === 'REVISION_REQUESTED' ? (
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-sky-500/10 text-sky-400 border border-sky-500/20 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-sky-400" />
                      <span>Revision Requested</span>
                    </span>
                  ) : (
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                      <span>Completed ({selectedWorkflow.duration_ms} ms)</span>
                    </span>
                  )}
                </div>

                <div>
                  <h2 className="text-sm font-bold text-text-primary leading-snug">
                    "{selectedWorkflow.query}"
                  </h2>
                </div>

                <div className="flex items-center gap-3 text-[10px] text-text-muted pt-1 border-t border-border/40">
                  <span>Initiator: <strong className="text-text-primary font-medium">{selectedWorkflow.initiator}</strong></span>
                  <span>•</span>
                  <span>Channel: <strong className="text-text-primary font-medium">{selectedWorkflow.channel}</strong></span>
                </div>

                {/* Multi-Agent Collaboration & Delegation Chain Banner (Option 3) */}
                {selectedWorkflow.collaboration_chain && selectedWorkflow.collaboration_chain.length > 0 && (
                  <div className="mt-3 p-3 rounded-xl bg-surface-secondary/50 border border-border flex flex-col gap-2">
                    <div className="flex items-center gap-1.5 text-[10px] font-bold text-indigo-500 uppercase tracking-wider">
                      <Bot className="w-3.5 h-3.5 text-indigo-500" />
                      <span>Multi-Agent Collaboration & Delegation Chain</span>
                    </div>
                    <div className="flex items-center gap-1.5 overflow-x-auto pb-0.5">
                      {selectedWorkflow.collaboration_chain.map((agent, aIdx) => (
                        <React.Fragment key={aIdx}>
                          <div className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-surface border border-border shrink-0 shadow-2xs">
                            <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                            <span className="text-[11px] font-semibold text-text-primary whitespace-nowrap">{agent}</span>
                          </div>
                          {aIdx < (selectedWorkflow.collaboration_chain?.length || 0) - 1 && (
                            <ArrowRight className="w-3 h-3 text-text-muted shrink-0" />
                          )}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Continuous Timeline Spine Flow */}
              <div className="relative pl-6 space-y-3 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-[2px] before:bg-gradient-to-b before:from-sky-500/50 before:via-indigo-500/50 before:to-purple-500/50">
                {selectedWorkflow.nodes?.map((node, idx) => {
                  const nodeId = node.id || `${idx}`;
                  const isExpanded = !!expandedNodes[nodeId];
                  const theme = getNodeTheme(node.type);

                  return (
                    <div key={nodeId} className="relative">
                      
                      {/* Connected Spine Node Indicator */}
                      <div className={`absolute -left-6 top-3 w-5 h-5 rounded-full bg-surface border border-border flex items-center justify-center ring-4 ${
                        node.status === 'waiting'
                          ? 'ring-amber-400/40 bg-amber-500/10'
                          : node.status === 'upcoming'
                          ? 'ring-border/40 bg-surface'
                          : theme.dotRing
                      } z-10`}>
                        <div className={`w-2 h-2 rounded-full ${
                          node.status === 'waiting'
                            ? 'bg-amber-400 animate-pulse'
                            : node.status === 'upcoming'
                            ? 'bg-text-muted/40'
                            : theme.dotBg
                        }`} />
                      </div>

                      {/* Step Card */}
                      <div className={`bg-surface rounded-xl border transition-all duration-150 overflow-hidden ${
                        isExpanded ? 'border-indigo-500/50 ring-1 ring-indigo-500/20' : 'border-border hover:border-indigo-500/30'
                      }`}>
                        
                        {/* Header (Click to Expand / Collapse) */}
                        <div
                          onClick={() => toggleNodeExpand(nodeId)}
                          className="p-3 flex items-center justify-between gap-2.5 cursor-pointer hover:bg-surface-secondary/40 transition"
                        >
                          <div className="flex items-center gap-2.5">
                            <div className="p-1.5 rounded-lg bg-surface-secondary border border-border shrink-0">
                              {theme.icon}
                            </div>
                            <div>
                              <div className="flex items-center gap-1.5 flex-wrap">
                                <span className="text-[10px] font-mono font-bold text-text-muted uppercase">
                                  STEP 0{idx + 1}
                                </span>
                                <span className="text-xs font-bold text-text-primary">
                                  {node.label}
                                </span>
                                {node.agent_role && (
                                  <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-indigo-500/10 text-indigo-500 border border-indigo-500/20 flex items-center gap-1">
                                    <Bot className="w-2.5 h-2.5" />
                                    <span>{node.agent_role}</span>
                                  </span>
                                )}
                                {node.handoff_to && (
                                  <span className="px-1.5 py-0.5 rounded text-[9px] font-mono text-text-muted bg-surface-secondary border border-border flex items-center gap-1">
                                    <ArrowRight className="w-2.5 h-2.5 text-indigo-400" />
                                    <span>Handoff: {node.handoff_to}</span>
                                  </span>
                                )}
                              </div>
                              <p className="text-[10px] text-text-muted mt-0.5">
                                {node.subtitle || node.type.toUpperCase()}
                              </p>
                            </div>
                          </div>

                          <div className="flex items-center gap-2.5">
                            <span className="text-[10px] font-mono font-bold text-text-primary px-2 py-0.5 rounded bg-surface-secondary border border-border">
                              {node.execution_time_ms} ms
                            </span>
                            <div className="text-text-muted">
                              {isExpanded ? <ChevronDown className="w-4 h-4 text-indigo-400" /> : <ChevronRight className="w-4 h-4" />}
                            </div>
                          </div>
                        </div>

                        {/* Collapsible Content */}
                        {isExpanded && (
                          <div className="p-3 border-t border-border bg-surface-secondary/20 space-y-2.5 text-xs animate-in fade-in duration-150">
                            
                            {/* Outputs JSON */}
                            <div className="space-y-1">
                              <div className="flex items-center justify-between">
                                <span className="text-[10px] font-bold uppercase tracking-wider text-text-muted flex items-center gap-1">
                                  <Code className="w-3 h-3 text-emerald-500" />
                                  <span>Outputs & Data Payload</span>
                                </span>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    copyPayload(nodeId, node.outputs);
                                  }}
                                  className="flex items-center gap-1 text-[10px] font-semibold text-text-muted hover:text-text-primary px-2 py-0.5 rounded bg-surface border border-border transition hover:bg-surface-secondary"
                                >
                                  {copiedId === nodeId ? <Check className="w-3 h-3 text-emerald-500" /> : <Copy className="w-3 h-3" />}
                                  <span>{copiedId === nodeId ? 'Copied' : 'Copy JSON'}</span>
                                </button>
                              </div>

                              <pre className="p-2.5 rounded-lg bg-surface font-mono text-[10px] text-emerald-600 dark:text-emerald-400 border border-border overflow-x-auto max-h-44 leading-relaxed">
                                {JSON.stringify(node.outputs || {}, null, 2)}
                              </pre>
                            </div>

                            {/* Reasoning Logs */}
                            {node.logs && node.logs.length > 0 && (
                              <div className="space-y-1 pt-0.5">
                                <span className="text-[10px] font-bold uppercase tracking-wider text-text-muted flex items-center gap-1">
                                  <Activity className="w-3 h-3 text-indigo-500" />
                                  <span>Agent Reasoning Logs</span>
                                </span>
                                <div className="p-2.5 rounded-lg bg-surface border border-border space-y-1 max-h-32 overflow-y-auto">
                                  {node.logs.map((log: string, lIdx: number) => (
                                    <div key={lIdx} className="flex items-start gap-1.5 text-[11px] text-text-secondary leading-snug">
                                      <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-1 shrink-0" />
                                      <span>{log}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Inline Human-in-the-loop Approval Action Gate */}
                            {node.status === 'waiting' && (
                              <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-between gap-3">
                                <div className="flex items-center gap-2">
                                  <Clock className="w-4 h-4 text-amber-500 animate-pulse" />
                                  <div>
                                    <p className="text-xs font-bold text-amber-500">Executive Approval Gate Active</p>
                                    <p className="text-[10px] text-text-muted">Human reviewer review required to execute subsequent delegation steps.</p>
                                  </div>
                                </div>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleApproveWorkflow(selectedWorkflow.query_id);
                                  }}
                                  className="px-3 py-1.5 rounded-md bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-xs transition flex items-center gap-1.5 cursor-pointer"
                                >
                                  <CheckCircle2 className="w-3.5 h-3.5" />
                                  <span>Sign-Off & Execute</span>
                                </button>
                              </div>
                            )}

                          </div>
                        )}

                      </div>
                    </div>
                  );
                })}
              </div>

            </div>
          ) : (
            <div className="h-56 flex flex-col items-center justify-center bg-surface rounded-xl border border-border text-text-muted p-6 text-center space-y-2">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-500">
                <Cpu className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-xs font-bold text-text-primary">No Query Selected</h3>
                <p className="text-[11px] text-text-muted max-w-xs mx-auto mt-0.5">
                  Select a record from the history list to inspect its decision flow.
                </p>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}

export default OrchestrationPage;
