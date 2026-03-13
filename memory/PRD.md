# AgentForge - Personal AI Development Studio

## Original Problem Statement
Build a personal AI development studio with 6 specialized agents that can create AAA games (Unreal Engine, Unity, Godot), web apps, mobile apps - everything a full development team can do. Agents do ALL the work. Emergent-style workflow: clarify → plan → build. User stays in complete control.

## Architecture
- **Frontend**: React 19, Tailwind CSS, Shadcn UI, Framer Motion, Monaco Editor
- **Backend**: FastAPI with Motor (async MongoDB)
- **AI Integration**: fal.ai OpenRouter API (Google Gemini 2.5 Flash)
- **Database**: MongoDB

## Agent Team (6 Agents)
1. **COMMANDER** - Lead/Project Director - Clarifies, coordinates, delegates
2. **ATLAS** - Architect - System design, patterns, UE5/Unity expertise
3. **FORGE** - Developer - C++, C#, Blueprints, full-stack code
4. **SENTINEL** - Reviewer - Code quality, security, best practices
5. **PROBE** - Tester - QA, test automation, coverage
6. **PRISM** - Artist - UI/UX, shaders, VFX specs

## Core Features (Implemented)
- [x] 6-agent AI team with fal.ai integration
- [x] Monaco code editor with file tree
- [x] Syntax highlighting in chat (Prism.js)
- [x] Auto-save code blocks from agent responses
- [x] Project export to ZIP
- [x] Kanban task board
- [x] Project types: Unreal, Unity, Godot, Web, Mobile
- [x] Engine version selection
- [x] Phase workflow: Clarification → Planning → Development → Review
- [x] Agent status indicators
- [x] Message persistence

## Workflow
1. User describes project to COMMANDER
2. COMMANDER asks clarifying questions
3. User approves plan before any coding
4. Agents build, user stays in control
5. Export project when ready

## What's Been Implemented (Jan 2026)
- Full 6-agent AI team
- Monaco code editor with VS Code features
- File tree with folder expansion
- Code syntax highlighting in chat messages
- Copy code button per block
- Auto-save code to files
- Project export as ZIP
- Resizable panels
- Dark theme throughout

## P1 Features (Next)
- Streaming responses (SSE)
- Agent delegation (COMMANDER → FORGE)
- Image generation with fal.ai
- GitHub push integration
- Project templates (FPS, RPG, Platformer)

## P2 Features
- Live preview for web projects
- Multi-file refactoring
- Agent memory/learning
- Team activity feed
