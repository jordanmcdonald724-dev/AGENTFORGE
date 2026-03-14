# 🚀 AGENTFORGE DEPLOYMENT CONFIGURATION

## Deployment Strategy: Personal User Setup

### Core Philosophy:
AgentForge deploys with minimal required credentials. Users add their own deployment platform tokens in Settings for personal use.

---

## ✅ EMERGENT DEPLOYMENT VARIABLES (Set in Emergent)

```bash
# Database (Auto-configured by Emergent)
MONGO_URL=<emergent-managed>

# Core Application
DB_NAME=agentforge
CORS_ORIGINS=*

# AI Services (Required for agents to work)
FAL_KEY=premium-os-ui:114c9ab5a4bbd94c1cac728820cf60e0
EMERGENT_LLM_KEY=sk-emergent-93a44EcAbB7E68aE7B
```

---

## 🔧 USER-CONFIGURED TOKENS (Set in AgentForge Settings)

Users will configure these in the AgentForge UI Settings page when they want to deploy projects:

### Web Hosting:
- Vercel Token
- Railway Token  
- Netlify Token
- Render API Key
- GitHub Token
- Cloudflare API Token
- Fly.io API Token
- Surge credentials

### Game Distribution:
- Itch.io API Key + Username

### Optional Services:
- SendGrid API Key (emails)
- Resend API Key (emails)
- Discord Webhook URL

---

## 🔐 How It Works:

**1. User opens Settings in AgentForge**
   - Goes to Settings → Deployment Platforms
   - Adds their personal API tokens
   - Tokens stored in their user profile (MongoDB)

**2. User deploys a project**
   - Clicks "Deploy" on their project
   - Selects platform (Vercel, Netlify, etc.)
   - AgentForge uses THEIR saved token
   - Project deploys to THEIR account

**3. Local Bridge (Unreal/Unity)**
   - Browser extension + native app installed on user's computer
   - Connects safely via local bridge
   - Code pushed directly to local game engine folders
   - No cloud tokens needed - direct local connection

---

## ✅ Benefits:

- **Security:** Users control their own API keys
- **Privacy:** Tokens stored per-user, not globally
- **Flexibility:** Each user can use different platforms
- **Simple Deployment:** AgentForge deploys with minimal config
- **No Shared Credentials:** Every user brings their own

---

## 📋 Deployment Checklist:

✅ Set 4 required env vars in Emergent
✅ Deploy AgentForge
✅ Users sign up / create accounts
✅ Users add their personal tokens in Settings
✅ Users can deploy projects to their accounts
✅ Local bridge works for game engine integration

---

## 🎯 Ready to Deploy!

**Command:** Hit "Deploy" in Emergent with these variables:
```
DB_NAME=agentforge
CORS_ORIGINS=*
FAL_KEY=premium-os-ui:114c9ab5a4bbd94c1cac728820cf60e0
EMERGENT_LLM_KEY=sk-emergent-93a44EcAbB7E68aE7B
```

**Result:** 
- AgentForge live at `https://agentforge.emergent.host`
- Users configure their own deployment tokens
- Local bridge ready for safe OS-level connections
- Complete luxury dev studio operational! 🚀
