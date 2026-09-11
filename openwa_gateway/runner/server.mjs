import makeWASocket, { useMultiFileAuthState, DisconnectReason } from '@whiskeysockets/baileys';
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
      res.end(`<!DOCTYPE html>
<html>
<head>
  <title>WhatsApp Direct QR - Niyukti HRMS</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0a0f1d; color: #f8fafc; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 20px; box-sizing: border-box;">
  <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 24px; padding: 36px; max-width: 440px; width: 100%; text-align: center; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7); backdrop-filter: blur(12px);">
    <div style="font-size: 32px; margin-bottom: 12px;">📲</div>
    <h1 style="font-size: 22px; font-weight: 700; margin: 0 0 8px 0; background: linear-gradient(135deg, #34d399, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Link WhatsApp Executive Bot</h1>
    <p style="color: #94a3b8; font-size: 14px; margin: 0 0 24px 0;">Open WhatsApp &gt; Settings &gt; Linked Devices &gt; Link a Device</p>
    
    <div style="background: #ffffff; padding: 20px; border-radius: 16px; display: inline-block; box-shadow: 0 8px 20px rgba(0,0,0,0.4);">
      <img src="${qrDataUrl}" width="260" height="260" style="display: block;" alt="WhatsApp QR Code" />
    </div>

    <div style="margin-top: 24px; padding: 12px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 12px;">
      <span style="display: inline-block; width: 8px; height: 8px; background: #10b981; border-radius: 50%; margin-right: 6px; animation: pulse 1.5s infinite;"></span>
      <span style="color: #34d399; font-size: 13px; font-weight: 500;">Live QR Code Active • Auto-refreshes</span>
    </div>
  </div>
  <script>
    setTimeout(() => location.reload(), 15000);
  </script>
</body>
</html>`);
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
  console.log(`\n🚀 WhatsApp Gateway REST Server listening on http://localhost:${PORT}`);
  console.log(`🌐 View Direct QR Code in browser at: http://localhost:${PORT}/qr\n`);
  startWhatsApp().catch((err) => console.error('Failed to start WhatsApp socket:', err));
});
