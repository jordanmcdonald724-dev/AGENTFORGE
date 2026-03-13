# 🚀 AgentForge v4.5 - Local Setup Guide (Windows)

## Quick Start (3 Steps)

### 1️⃣ Download the Project
Download and extract the AgentForge folder to your desired location (e.g., `C:\AgentForge`)

### 2️⃣ Setup MongoDB (Choose One)

**Option A: Free Cloud MongoDB (Easiest - No Install)**
1. Go to https://www.mongodb.com/atlas
2. Sign up free (no credit card needed)
3. Create a free M0 cluster
4. Get your connection string
5. Paste it in `backend/.env` as `MONGO_URL`

**Option B: Local MongoDB**
1. Download: https://www.mongodb.com/try/download/community
2. Install with default settings
3. MongoDB runs automatically on `localhost:27017`

### 3️⃣ Launch AgentForge

```
1. Double-click INSTALL_DEPS.bat (first time only)
2. Double-click START_AGENTFORGE.bat
3. Open http://localhost:3000 in your browser
```

---

## 🎮 What You Get

- **Frontend:** http://localhost:3000 (React app)
- **Backend API:** http://localhost:8001 (FastAPI)
- **All 16 panels** working locally
- **Theme switching** (Dark/Light/Midnight/JARVIS)
- **Game Engine Builder** (UE5/Unity)
- **Hardware Integration** (Arduino/Pi/STM32)
- **Research Mode** (arXiv/HuggingFace)

---

## ⚠️ Requirements

| Software | Version | Download |
|----------|---------|----------|
| Node.js | 18+ | https://nodejs.org |
| Python | 3.10+ | https://python.org |
| Yarn | Latest | `npm install -g yarn` |
| MongoDB | 6+ | https://mongodb.com/try/download |

---

## 🔧 Troubleshooting

**"ECONNREFUSED" error:**
- MongoDB isn't running. Start it or use MongoDB Atlas (cloud)

**"Module not found" error:**
- Run `INSTALL_DEPS.bat` again

**Port already in use:**
- Change ports in `.env` files, or close other apps using 3000/8001

**Backend won't start:**
- Check Python: `python --version` (need 3.10+)
- Check pip: `pip --version`

---

## 📁 Folder Structure

```
AgentForge/
├── START_AGENTFORGE.bat    # Launch everything
├── INSTALL_DEPS.bat        # Install dependencies
├── backend/
│   ├── .env                # Backend config
│   ├── server.py           # Main server
│   ├── routes/             # API routes
│   └── requirements.txt    # Python packages
└── frontend/
    ├── .env                # Frontend config
    ├── src/                # React source
    └── package.json        # Node packages
```

---

## 🆓 Free Server Options (When Ready)

When you get a card or domain ready:
- **Oracle Cloud:** Free tier (forever free VM)
- **Google Cloud:** $300 free credits
- **Azure:** $200 free credits
- **Render.com:** Free tier available

---

Enjoy building with AgentForge! 🔥
