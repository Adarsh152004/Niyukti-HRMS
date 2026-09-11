/**
 * AI Agent Router — /api/v1/agent/*
 * 
 * Dedicated agent-access endpoints for the HRMS AI Agent.
 * Provides full CRUD control over Jobs, Applications, and read access to Inquiries.
 * All routes are authenticated by the X-Agent-Key header.
 */

import express from 'express';
import {
  getAgentCapabilities,
  getAgentDashboard,
  agentListJobs,
  agentCreateJob,
  agentUpdateJob,
  agentDeleteJob,
  agentToggleJobStatus,
  agentListApplications,
  agentUpdateApplicationStatus,
  agentBulkUpdateStatus,
  agentAddReviewerNote,
  agentListInquiries,
  agentReseedJobs,
} from '../controllers/agentController.mjs';

const agentRouter = express.Router();

// ─── Simple Agent Auth Middleware ─────────────────────────────────────────────
// The key is read from AGENT_API_KEY env var (or defaults to dev key for local dev)
const AGENT_KEY = process.env.AGENT_API_KEY || 'azyntrix-agent-dev-key-2026';

// ─── Rate Limiter (Sliding Window: 120 req / minute per IP) ────────────────────
const rateLimitMap = new Map();
const RATE_LIMIT_WINDOW_MS = 60 * 1000; // 1 minute
const RATE_LIMIT_MAX_REQUESTS = 120;

// Periodic cleanup of stale rate-limit buckets every 5 minutes
setInterval(() => {
  const now = Date.now();
  for (const [ip, data] of rateLimitMap.entries()) {
    if (now - data.windowStart > RATE_LIMIT_WINDOW_MS) {
      rateLimitMap.delete(ip);
    }
  }
}, 5 * 60 * 1000).unref();

function agentRateLimiter(req, res, next) {
  const ip = req.ip || req.connection.remoteAddress || '127.0.0.1';
  const now = Date.now();

  let clientData = rateLimitMap.get(ip);
  if (!clientData || (now - clientData.windowStart > RATE_LIMIT_WINDOW_MS)) {
    clientData = { windowStart: now, count: 0 };
    rateLimitMap.set(ip, clientData);
  }

  clientData.count += 1;
  const remaining = Math.max(0, RATE_LIMIT_MAX_REQUESTS - clientData.count);
  const resetSeconds = Math.ceil((clientData.windowStart + RATE_LIMIT_WINDOW_MS - now) / 1000);

  res.setHeader('X-RateLimit-Limit', RATE_LIMIT_MAX_REQUESTS);
  res.setHeader('X-RateLimit-Remaining', remaining);
  res.setHeader('X-RateLimit-Reset', resetSeconds);

  if (clientData.count > RATE_LIMIT_MAX_REQUESTS) {
    return res.status(429).json({
      success: false,
      error: 'Too Many Requests: Rate limit exceeded on Agent API.',
      retryAfterSeconds: resetSeconds,
    });
  }

  next();
}

// ─── Audit Logger Middleware ──────────────────────────────────────────────────
function agentAuditLogger(req, res, next) {
  const startTime = Date.now();
  const clientIp = req.ip || req.connection.remoteAddress || 'unknown';
  
  res.on('finish', () => {
    const duration = Date.now() - startTime;
    const logEntry = `[AGENT AUDIT] ${new Date().toISOString()} | IP: ${clientIp} | ${req.method} ${req.originalUrl} | Status: ${res.statusCode} | Duration: ${duration}ms`;
    console.log(logEntry);
  });

  next();
}

function agentAuth(req, res, next) {
  const providedKey = req.headers['x-agent-key'] || req.query.agentKey;
  if (!providedKey || providedKey !== AGENT_KEY) {
    return res.status(401).json({
      success: false,
      error: 'Unauthorized: Missing or invalid X-Agent-Key header.',
      hint: 'Set X-Agent-Key header or agentKey query param. Dev key is: azyntrix-agent-dev-key-2026',
    });
  }
  next();
}

// Apply rate limiting, audit logging, and auth to all agent routes
agentRouter.use(agentRateLimiter);
agentRouter.use(agentAuditLogger);
agentRouter.use(agentAuth);

// ─── Agent System Info ────────────────────────────────────────────────────────
// GET /api/v1/agent
agentRouter.get('/', getAgentCapabilities);

// ─── Analytics Dashboard ──────────────────────────────────────────────────────
// GET /api/v1/agent/dashboard
agentRouter.get('/dashboard', getAgentDashboard);

// ─── Jobs: Full CRUD ──────────────────────────────────────────────────────────
// GET    /api/v1/agent/jobs             — list all (with filters)
// POST   /api/v1/agent/jobs             — create new job posting
// PUT    /api/v1/agent/jobs/:jobId      — update job (any field)
// DELETE /api/v1/agent/jobs/:jobId      — soft-delete (close) or hard-delete
// PATCH  /api/v1/agent/jobs/:jobId/toggle — flip active/closed status
agentRouter.get('/jobs', agentListJobs);
agentRouter.post('/jobs', agentCreateJob);
agentRouter.put('/jobs/:jobId', agentUpdateJob);
agentRouter.delete('/jobs/:jobId', agentDeleteJob);
agentRouter.patch('/jobs/:jobId/toggle', agentToggleJobStatus);

// ─── Applications: Pipeline Management ───────────────────────────────────────
// GET   /api/v1/agent/applications              — list all (with filters)
// PATCH /api/v1/agent/applications/:ref/status  — update pipeline status + optional note
// POST  /api/v1/agent/applications/bulk-status  — bulk update status for multiple refs
// POST  /api/v1/agent/applications/:ref/note    — add reviewer note only
agentRouter.get('/applications', agentListApplications);
agentRouter.patch('/applications/:referenceId/status', agentUpdateApplicationStatus);
agentRouter.post('/applications/bulk-status', agentBulkUpdateStatus);
agentRouter.post('/applications/:referenceId/note', agentAddReviewerNote);

// ─── Inquiries (read) ─────────────────────────────────────────────────────────
// GET /api/v1/agent/inquiries
agentRouter.get('/inquiries', agentListInquiries);

// ─── System Ops ───────────────────────────────────────────────────────────────
// POST /api/v1/agent/reseed
agentRouter.post('/reseed', agentReseedJobs);

export default agentRouter;
