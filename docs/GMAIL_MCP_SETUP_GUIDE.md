# Real Google Workspace & Gmail MCP Integration Guide

This guide walks you through connecting **HRMS Autonomous AI Agents** directly to your **Real Google Gmail Account** using official Google Cloud OAuth2 credentials and MCP (Model Context Protocol).

---

## 1. Google Cloud Console Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g. `HRMS-Autonomous-Agents`) or select an existing project.
3. In the sidebar, navigate to **APIs & Services > Library**.
4. Search for **Gmail API** and click **Enable**.

---

## 2. Configure OAuth Consent Screen

1. In the sidebar, navigate to **APIs & Services > OAuth consent screen**.
2. Select User Type: **External** (or **Internal** if using Google Workspace).
3. Fill in:
   - **App Name**: `HRMS AI Assistant`
   - **User support email**: `your-email@gmail.com`
   - **Developer contact email**: `your-email@gmail.com`
4. Under **Scopes**, click **Add or Remove Scopes** and add:
   - `https://www.googleapis.com/auth/gmail.readonly` (Read incoming emails)
   - `https://www.googleapis.com/auth/gmail.send` (Send emails on behalf of HR)
   - `https://www.googleapis.com/auth/gmail.modify` (Mark unread/read)
5. Under **Test Users**, add your Gmail address (e.g., `your-email@gmail.com`).
6. Click **Save and Continue**.

---

## 3. Create OAuth Client Credentials

1. In the sidebar, navigate to **APIs & Services > Credentials**.
2. Click **+ Create Credentials > OAuth client ID**.
3. Application type: **Web application** (or **Desktop app**).
4. For Web application, set Authorized redirect URIs:
   - `https://developers.google.com/oauthplayground`
5. Click **Create**. Copy your **Client ID** and **Client Secret**.

---

## 4. Generate Refresh Token via Google OAuth Playground

1. Go to the [Google OAuth 2.0 Playground](https://developers.google.com/oauthplayground/).
2. In the top-right corner, click the **Settings (Gear Icon)**:
   - Check **Use your own OAuth credentials**.
   - Enter your **OAuth Client ID** and **OAuth Client Secret**.
3. In Step 1 (Select & authorize APIs), scroll down to **Gmail API v1** and select:
   - `https://www.googleapis.com/auth/gmail.modify`
   - `https://www.googleapis.com/auth/gmail.send`
4. Click **Authorize APIs** and log in with your Google account.
5. In Step 2 (Exchange authorization code for tokens), click **Exchange authorization code for tokens**.
6. Copy the generated **Refresh Token**.

---

## 5. Configure HRMS `.env`

Add the following variables into your `backend/.env` file:

```env
# Real Gmail Integration
GMAIL_CLIENT_ID=your_client_id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REFRESH_TOKEN=your_refresh_token
GMAIL_SENDER_EMAIL=your_email@gmail.com
```

---

## 6. How the HRMS AI Uses Real Gmail

- **Autonomous Background Polling**: The `EmailIntelligenceAgent` periodically scans your actual unread emails for critical keywords (`offer acceptance`, `resignation`, `compliance notice`, `urgent`).
- **Live CEO Briefings**: When critical messages arrive, the AI analyzes business impact and pushes real-time executive alerts to the CEO Mobile and Desktop chat channels.
- **Interactive Dispatch**: In chat, you can issue commands like:
  - *"Send an email to candidate@domain.com welcoming them to the team"*
  - *"Search my inbox for recent emails about statutory compliance"*
  - *"Read email thread msg-12345"*
