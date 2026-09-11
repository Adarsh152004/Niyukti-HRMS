import { makeWASocket, useMultiFileAuthState, DisconnectReason } from '@whiskeysockets/baileys';
import QRCode from 'qrcode';
import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SESSIONS_DIR = path.join(__dirname, 'data', 'sessions', 'default');
if (!fs.existsSync(SESSIONS_DIR)) {
  fs.mkdirSync(SESSIONS_DIR, { recursive: true });
}

const PORT = process.env.PORT || 2785;
const WEBHOOK_URL = process.env.WEBHOOK_URL || 'http://localhost:8000/api/whatsapp/webhook';

let currentQR = null;
let sock = null;
let isConnected = false;
let userJid = null;

async function startWhatsApp() {
  const { state, saveCreds } = await useMultiFileAuthState(SESSIONS_DIR);

  sock = makeWASocket({
    auth: state,
    printQRInTerminal: false,
    syncFullHistory: false,
  });

  sock.ev.on('creds.update', saveCreds);

  sock.ev.on('connection.update', async (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      currentQR = qr;
      console.log('\n' + '='.repeat(60));
      console.log('📲 SCAN THIS DIRECT QR CODE TO LINK YOUR WHATSAPP ACCOUNT:');
      console.log('='.repeat(60) + '\n');
      
      try {
        const asciiQR = await QRCode.toString(qr, { type: 'terminal', small: true });
        console.log(asciiQR);
      } catch (err) {
        console.error('Error generating terminal QR:', err);
      }
      
      console.log('\n' + '='.repeat(60));
      console.log(`🌐 Alternatively view QR in browser: http://localhost:${PORT}/qr`);
      console.log('='.repeat(60) + '\n');
    }

    if (connection === 'close') {
      const shouldReconnect =
        lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
      console.log('⚠️ Connection closed. Reconnecting:', shouldReconnect);
      isConnected = false;
      if (shouldReconnect) {
        setTimeout(startWhatsApp, 3000);
      }
    } else if (connection === 'open') {
      isConnected = true;
      currentQR = null;
      userJid = sock.user?.id;
      console.log('\n' + '🎉'.repeat(20));
      console.log(`✅ WhatsApp successfully connected! Linked ID: ${userJid}`);
      console.log(`📡 Ready to receive CEO commands & dispatch autonomous HR briefings.`);
      console.log('🎉'.repeat(20) + '\n');
    }
  });

  sock.ev.on('messages.upsert', async (m) => {
    if (m.type === 'notify') {
      for (const msg of m.messages) {
        if (!msg.key.fromMe && msg.message) {
          const sender = msg.key.remoteJid;
          const text =
            msg.message.conversation ||
            msg.message.extendedTextMessage?.text ||
            msg.message.imageMessage?.caption ||
            '';

          console.log(`📩 Inbound WhatsApp message from ${sender}: "${text}"`);

          // Forward to HRMS Backend Webhook
          try {
            await fetch(WEBHOOK_URL, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                from: sender,
                to: userJid || 'HRMS-BOT',
                body: text,
                timestamp: msg.messageTimestamp,
                id: msg.key.id,
              }),
            });
          } catch (err) {
            console.error('Failed to dispatch webhook to HRMS backend:', err.message);
          }
        }
      }
    }
  });
}

// Start HTTP REST API for OpenWA compatibility
const server = http.createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Agent-Key');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  // Health / Status endpoint
  if (req.url === '/api/default/status' || req.url === '/status' || req.url === '/api/status') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(
      JSON.stringify({
        status: isConnected ? 'CONNECTED' : 'DISCONNECTED',
        state: isConnected ? 'CONNECTED' : (currentQR ? 'SCAN_QR' : 'INITIALIZING'),
        phone: userJid,
        session: 'default',
      })
    );
    return;
  }

  // QR endpoint for browser
  if (req.url === '/qr' || req.url === '/api/default/qr') {
    if (!currentQR) {
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(`<html><body style="font-family:sans-serif;text-align:center;padding:40px;background:#0d1117;color:#fff;">
        <h2>${isConnected ? '✅ WhatsApp is already connected!' : '⏳ Generating QR Code...'}</h2>
        <p>${isConnected ? `Connected as: ${userJid}` : 'Please refresh in a moment.'}</p>
      </body></html>`);
      return;
    }

    try {
      const qrDataUrl = await QRCode.toDataURL(currentQR);
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(`<html><body style="font-family:sans-serif;text-align:center;padding:40px;background:#0b0f19;color:#fff;">
        <h1 style="color:#10b981;">📲 Link WhatsApp with OpenWA Gateway</h1>
        <p style="color:#94a3b8;font-size:16px;">Open WhatsApp > Settings > Linked Devices > Link a Device</p>
        <div style="background:#fff;padding:24px;display:inline-block;border-radius:16px;margin-top:20px;box-shadow:0 10px 25px rgba(0,0,0,0.5);">
          <img src="${qrDataUrl}" width="300" height="300" alt="QR Code" />
        </div>
        <p style="color:#64748b;margin-top:24px;font-size:14px;">Auto-refreshing every 10 seconds...</p>
        <script>setTimeout(() => location.reload(), 10000);</script>
      </body></html>`);
    } catch (err) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: err.message }));
    }
    return;
  }

  // Outbound Send Message endpoints
  if (
    (req.url === '/api/default/send-message' ||
      req.url === '/api/sendText' ||
      req.url === '/api/messages/send') &&
    req.method === 'POST'
  ) {
    let body = '';
    req.on('data', (chunk) => (body += chunk));
    req.on('end', async () => {
      try {
        const data = JSON.parse(body || '{}');
        const to = data.to || data.chatId || data.number;
        const text = data.text || data.message || data.body;

        if (!isConnected || !sock) {
          res.writeHead(503, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ success: false, error: 'WhatsApp is not connected yet. Scan QR first.' }));
          return;
        }

        const jid = to.includes('@') ? to : `${to.replace(/\D/g, '')}@s.whatsapp.net`;
        const result = await sock.sendMessage(jid, { text });

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(
          JSON.stringify({
            success: true,
            id: result.key.id,
            timestamp: result.messageTimestamp,
            to: jid,
          })
        );
      } catch (err) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: false, error: err.message }));
      }
    });
    return;
  }

  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Endpoint not found' }));
});

server.listen(PORT, () => {
  console.log(`\n🚀 OpenWA Gateway REST Server listening on http://localhost:${PORT}`);
  console.log(`🌐 View QR Code anytime at: http://localhost:${PORT}/qr\n`);
  startWhatsApp().catch((err) => console.error('Failed to start WhatsApp socket:', err));
});
