# AgentForgeOS

AgentForgeOS is a clean, layered architecture for AI-assisted development. It rebuilds the previous system with minimal, modular components and clear separation of concerns.

## Layers
- **engine/**: FastAPI runtime, config loader, database bootstrap, worker system.
- **providers/**: Interfaces for LLM, image, and TTS providers.
- **services/**: Internal orchestration (agents, memory, embeddings, vector search, pattern extraction, project intelligence).
- **control/**: AI control layer (routing, file guard, supervision, permission matrix).
- **apps/**: Feature modules (studio, builds, research, assets, deployment, sandbox).
- **bridge/**: Local machine integrations.
- **knowledge/**: Shared knowledge utilities.
- **desktop/**: Tauri desktop wrapper placeholder.
- **frontend/**: Web UI placeholder (init with React/Vite).
- **config/**: Environment configuration.

## Quick Start
```bash
cd AgentForgeOS
python -m uvicorn engine.server:app --reload --port 8001
# frontend: initialize Vite/React in AgentForgeOS/frontend then npm run dev
```

## Documentation
- ARCHITECTURE.md
- SYSTEM_OVERVIEW.md
- DEVELOPMENT_GUIDE.md
- BOOTSTRAP_REPORT.md

## 🎯 Use Cases

**Game Development:**
- AAA action games
- RPG systems
- Multiplayer games
- Web-based games

**Web Applications:**
- SaaS platforms
- E-commerce sites
- Dashboards and admin panels
- Landing pages

**Mobile Apps:**
- React Native apps
- Progressive Web Apps

---

## 🌐 Access Methods

**Landing Page:** Main entry with sidebar navigation
**Dashboard:** Project management and selection
**Workspace:** Main development environment
**God Mode:** Autonomous build system (sidebar access)
**Research Lab:** Academic research tools (sidebar access)

---

## 💡 Tips for Best Results

1. **Be Specific:** The more detail you provide, the better the AI output
2. **Use God Mode:** For quick prototypes and complete features
3. **Normal Mode:** When you need control and collaboration
4. **Start Small:** Deploy simple projects first to test platforms
5. **Iterate:** AI learns from your feedback over time

---

## 🔐 Security

- API keys stored in environment variables
- Never commit keys to version control
- Secure token handling for deployments
- HTTPS enforced on all deployments

---

## 🎉 What Makes This Special

**100% Complete Output:**
- No "TODO: implement this"
- No placeholder code or stub functions
- Every feature fully implemented
- Production-ready from day one

**Luxury Quality:**
- Apple-level polish
- Ubisoft-level depth
- Linear's attention to detail
- Professional, enterprise-grade code

**Comprehensive Coverage:**
- Every discipline covered (code, art, audio, design, writing)
- Full deployment pipeline
- Local and cloud development
- Games and apps

---

## 📞 Support

For issues, questions, or feedback:
- Check documentation first
- Review deployment guide for platform-specific help
- Test with simplest platform (Surge.sh) first

---

**Built with ❤️ using AgentForge's own 12-agent team**
