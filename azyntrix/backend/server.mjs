import express from 'express';
import cors from 'cors';
import { connectDB } from './src/config/db.mjs';
import { seedDatabase } from './src/seed/seedData.mjs';
import apiRouter from './src/routes/api.mjs';
import agentRouter from './src/routes/agent.mjs';

const app = express();
const PORT = process.env.AZYNTRIX_PORT || 5050;

// Enable CORS for frontend
app.use(cors({
  origin: '*',
  credentials: true,
}));

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Static uploads route
app.use('/uploads', express.static('uploads'));

// AI Agent Control Routes (secured by X-Agent-Key header) - MUST be before generic apiRouter
app.use('/api/v1/agent', agentRouter);

// Public API Routes
app.use('/api/v1', apiRouter);

// Root fallback
app.get('/', (req, res) => {
  res.json({
    service: 'Azyntrix Backend API Engine',
    version: '2.4.0',
    documentation: '/api/v1/health',
    endpoints: [
      '--- Public Endpoints ---',
      'GET  /api/v1/health',
      'GET  /api/v1/jobs',
      'GET  /api/v1/jobs/:jobId',
      'POST /api/v1/applications',
      'GET  /api/v1/applications',
      'POST /api/v1/inquiries',
      'GET  /api/v1/inquiries',
      '--- AI Agent Endpoints (X-Agent-Key required) ---',
      'GET  /api/v1/agent',
      'GET  /api/v1/agent/dashboard',
      'GET  /api/v1/agent/jobs',
      'POST /api/v1/agent/jobs',
      'PUT  /api/v1/agent/jobs/:jobId',
      'DELETE /api/v1/agent/jobs/:jobId',
      'PATCH /api/v1/agent/jobs/:jobId/toggle',
      'GET  /api/v1/agent/applications',
      'PATCH /api/v1/agent/applications/:ref/status',
      'POST /api/v1/agent/applications/bulk-status',
      'POST /api/v1/agent/applications/:ref/note',
      'GET  /api/v1/agent/inquiries',
      'POST /api/v1/agent/reseed',
    ]
  });
});

async function startServer() {
  const server = app.listen(PORT, '0.0.0.0', () => {
    console.log(`[Azyntrix Backend] 🚀 Server running on http://localhost:${PORT}`);
    console.log(`[Azyntrix Backend] 📡 API Root: http://localhost:${PORT}/api/v1`);
  });

  // Connect to MongoDB asynchronously & seed
  connectDB().then(() => {
    seedDatabase().catch(err => console.warn('[Azyntrix Seed Error]:', err));
  }).catch(err => {
    console.warn('[Azyntrix DB Connect Error]:', err);
  });
}

startServer();
