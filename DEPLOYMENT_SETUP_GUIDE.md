# 🚀 FREE DEPLOYMENT PLATFORMS - API KEY SETUP GUIDE

## Quick Overview
Get API keys for 9 FREE deployment platforms (takes ~20 minutes total)

---

## 1️⃣ VERCEL (Web Apps, Static Sites)

**Time: 2 minutes**

### Steps:
1. Go to https://vercel.com/signup
2. Sign up with GitHub/GitLab/Email
3. Click your avatar (bottom left) → **Settings**
4. Go to **Tokens** tab
5. Click **Create Token**
   - Name: `AgentForge`
   - Scope: `Full Account`
6. Click **Create** → Copy the token

### Add to AgentForge:
- Paste token in deployment panel when deploying
- Or add to backend `.env`: `VERCEL_TOKEN=your_token_here`

**Free Tier:**
- Unlimited deployments
- 100GB bandwidth/month
- Automatic HTTPS

---

## 2️⃣ RAILWAY (Full-Stack Apps + Database)

**Time: 2 minutes**

### Steps:
1. Go to https://railway.app/
2. Click **Login** → Sign in with GitHub
3. Click your avatar (top right) → **Account Settings**
4. Go to **Tokens** tab
5. Click **Create Token**
   - Name: `AgentForge`
6. Copy the token

### Add to AgentForge:
- Paste in deployment panel
- Or add to backend `.env`: `RAILWAY_TOKEN=your_token_here`

**Free Tier:**
- $5 credit per month
- 500 hours execution time
- PostgreSQL, MySQL, Redis included

---

## 3️⃣ NETLIFY (Web Apps, Static Sites)

**Time: 2 minutes**

### Steps:
1. Go to https://app.netlify.com/signup
2. Sign up with GitHub/GitLab/Email
3. Click your avatar (top right) → **User settings**
4. Go to **Applications** → **Personal access tokens**
5. Click **New access token**
   - Description: `AgentForge`
6. Click **Generate token** → Copy it

### Add to AgentForge:
- Paste in deployment panel
- Or add to backend `.env`: `NETLIFY_TOKEN=your_token_here`

**Free Tier:**
- 100GB bandwidth/month
- 300 build minutes/month
- Unlimited sites

---

## 4️⃣ RENDER (Full-Stack Apps + Database)

**Time: 2 minutes**

### Steps:
1. Go to https://dashboard.render.com/register
2. Sign up with GitHub/GitLab/Email
3. Click your avatar (top right) → **Account Settings**
4. Scroll to **API Keys** section
5. Click **Create API Key**
   - Name: `AgentForge`
6. Copy the key

### Add to AgentForge:
- Paste in deployment panel
- Or add to backend `.env`: `RENDER_API_KEY=your_key_here`

**Free Tier:**
- 750 hours/month
- PostgreSQL database included
- Automatic HTTPS

---

## 5️⃣ GITHUB PAGES (Static Sites - Unlimited FREE)

**Time: 3 minutes**

### Steps:
1. Go to https://github.com/settings/tokens
2. Click **Generate new token** → **Generate new token (classic)**
3. Give it a name: `AgentForge`
4. Select scopes:
   - ✅ `repo` (all repo permissions)
   - ✅ `workflow`
5. Click **Generate token** → Copy immediately (can't see again!)

### Add to AgentForge:
- Paste in deployment panel
- Or add to backend `.env`: `GITHUB_TOKEN=your_token_here`

**Free Tier:**
- Unlimited sites
- Unlimited bandwidth
- Custom domains free
- Perfect for portfolios, docs, static sites

---

## 6️⃣ CLOUDFLARE PAGES (Unlimited Sites - FREE Forever)

**Time: 3 minutes**

### Steps:
1. Go to https://dash.cloudflare.com/sign-up
2. Sign up with email
3. After login, go to https://dash.cloudflare.com/profile/api-tokens
4. Click **Create Token**
5. Use template: **Edit Cloudflare Workers**
6. Or create custom with:
   - Zone: `DNS:Edit`, `Zone:Read`
   - Account: `Cloudflare Pages:Edit`
7. Click **Continue to summary** → **Create Token**
8. Copy the token

### Add to AgentForge:
- Paste in deployment panel
- Or add to backend `.env`: `CLOUDFLARE_API_TOKEN=your_token_here`

**Free Tier:**
- Unlimited sites
- Unlimited requests
- 500 builds/month
- Fastest global CDN

---

## 7️⃣ FLY.IO (Modern Cloud Platform)

**Time: 3 minutes**

### Steps:
1. Go to https://fly.io/app/sign-up
2. Sign up with GitHub/Email
3. After signup, go to https://fly.io/user/personal_access_tokens
4. Click **Create token**
   - Name: `AgentForge`
   - Expiry: Never (or custom)
5. Copy the token

### Add to AgentForge:
- Paste in deployment panel
- Or add to backend `.env`: `FLY_API_TOKEN=your_token_here`

**Free Tier:**
- 3 shared VMs (256MB RAM each)
- 160GB bandwidth/month
- Global deployment
- Great for full-stack apps

---

## 8️⃣ SURGE.SH (Simple Static Sites - FREE Forever)

**Time: 1 minute**

### Steps:
1. **NO API KEY NEEDED!** 
2. Install surge CLI: `npm install -g surge`
3. Run `surge login` in terminal
4. Create account with email
5. Done! Surge uses email/password directly

### Add to AgentForge:
- No token needed
- Or for automation, add to `.env`: `SURGE_EMAIL=your@email.com` and `SURGE_PASSWORD=yourpassword`

**Free Tier:**
- Unlimited sites
- Unlimited bandwidth
- Custom domains
- Simplest deployment ever

---

## 9️⃣ ITCH.IO (Game Distribution - FREE)

**Time: 2 minutes**

### Steps:
1. Go to https://itch.io/register
2. Create account
3. After login, go to https://itch.io/user/settings/api-keys
4. Click **Generate new API key**
5. Copy the key
6. Your username is visible at top right

### Add to AgentForge:
- Add to backend `.env`:
  ```
  ITCH_API_KEY=your_api_key_here
  ITCH_USERNAME=your_username_here
  ```

**Free Tier:**
- Unlimited games
- Pay-what-you-want pricing
- Analytics included
- Community features

---

## 🎯 QUICK SETUP SUMMARY

### Required for Backend (.env file):
```bash
# Add these to /app/backend/.env

# Web Hosting
VERCEL_TOKEN=vercel_xxxxx
RAILWAY_TOKEN=railway_xxxxx
NETLIFY_TOKEN=netlify_xxxxx
RENDER_API_KEY=render_xxxxx
GITHUB_TOKEN=ghp_xxxxx
CLOUDFLARE_API_TOKEN=cloudflare_xxxxx
FLY_API_TOKEN=fly_xxxxx

# Game Distribution
ITCH_API_KEY=itch_xxxxx
ITCH_USERNAME=your_username
```

### Testing Deployment:
1. Create a simple project in AgentForge
2. Click **Push** button in workspace
3. Select a platform (start with **Surge.sh** - easiest)
4. Enter project name
5. Click **Deploy**
6. Get live URL in ~30 seconds!

---

## 💡 RECOMMENDED ORDER (Easiest First):

1. **Surge.sh** - No token needed, instant
2. **GitHub Pages** - You probably have GitHub already
3. **Vercel** - Most popular, great UX
4. **Netlify** - Vercel alternative
5. **Railway** - If you need databases
6. **Render** - Railway alternative
7. **Cloudflare Pages** - Fastest CDN
8. **Fly.io** - Most powerful free tier
9. **Itch.io** - Only if deploying games

---

## 🔒 SECURITY TIPS:

1. **Never commit API keys to GitHub**
2. **Use environment variables** (backend/.env)
3. **Rotate keys every 6 months**
4. **Delete unused tokens**
5. **Use read-only tokens when possible**

---

## ❓ TROUBLESHOOTING:

**"Invalid token" error:**
- Check token hasn't expired
- Verify correct permissions/scopes
- Regenerate token

**"Deployment failed":**
- Check platform status page
- Verify free tier limits not exceeded
- Try different platform

**"Rate limit exceeded":**
- Wait 1 hour and retry
- Upgrade to paid tier (optional)

---

## 🎉 DONE!

You now have access to **9 FREE deployment platforms** covering:
- ✅ Static sites (GitHub Pages, Surge, Cloudflare)
- ✅ Web apps (Vercel, Netlify)
- ✅ Full-stack (Railway, Render, Fly.io)
- ✅ Games (Itch.io)

**All platforms are FREE with no credit card required!**
