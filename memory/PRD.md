# AgentForge - AI Development Studio

## Original Problem Statement
Build a web application that functions as an "AI agent dev team" backed by fal.ai. A platform for building full web pages, applications, and AAA-quality games with a team of specialized AI agents under user control. Features include Git repository management, high-level code editor, and Ubisoft studio-style workflow.

## Product Overview
AgentForge is a personal AI Development Studio with 6 specialized agents that work together to build projects.

## Tech Stack
- **Backend:** FastAPI, MongoDB (motor), Python
- **Frontend:** React, TailwindCSS, Shadcn UI
- **AI/LLM:** fal.ai (OpenRouter for LLM, fal-client for image generation)
- **Code Editor:** Monaco Editor
- **Version Control:** PyGithub for GitHub integration

## Agent Team
1. **COMMANDER** - Lead Agent, Project Director, Coordinates team
2. **ATLAS** - System Architect, Design patterns
3. **FORGE** - Senior Developer, Code generation
4. **SENTINEL** - Code Reviewer, Quality assurance
5. **PROBE** - QA/Testing Agent
6. **PRISM** - Technical Artist, UI/Shaders/VFX

## Core Features (All Implemented & Tested)

### v1.0 - Initial Platform
- [x] 6-Agent team with specialized roles
- [x] Project management (create/list/delete)
- [x] fal.ai LLM integration for agent responses
- [x] Basic chat interface

### v2.0 - Studio Expansion
- [x] Monaco Editor integration
- [x] File management system
- [x] Task board (Kanban style)
- [x] Agent status indicators

### v2.1 - Streaming & Delegation
- [x] Streaming chat responses (SSE)
- [x] Agent delegation (COMMANDER -> specialists)
- [x] fal.ai image generation for assets

### v2.2 - GitHub & Actions
- [x] GitHub push integration
- [x] Agent conversation chains
- [x] Live preview for web projects
- [x] Quick Actions panel (8 predefined)

### v2.3 - Advanced Features (December 2025)
- [x] Multi-file refactoring (find & replace across files)
- [x] Agent memory persistence (context across sessions)
- [x] Project duplication (clone with files)
- [x] Custom Quick Actions (user-defined automation)

## API Endpoints

### Core
- `GET /api/` - API info
- `GET /api/health` - Health check
- `GET /api/agents` - List agents
- `POST/GET/DELETE /api/projects` - Project CRUD

### Chat & Streaming
- `POST /api/chat` - Non-streaming chat
- `POST /api/chat/stream` - SSE streaming chat
- `POST /api/delegate` - Execute delegation
- `POST /api/chain` - Agent chain execution
- `POST /api/chain/stream` - Streaming chain execution

### Files & Tasks
- `POST/GET/PATCH/DELETE /api/files` - File CRUD
- `POST /api/files/from-chat` - Auto-save code blocks
- `POST/GET/PATCH/DELETE /api/tasks` - Task CRUD

### v2.3 Features
- `POST/GET/DELETE /api/custom-actions` - Custom actions CRUD
- `POST /api/custom-actions/{id}/execute/stream` - Execute custom action
- `POST/GET/DELETE /api/memory` - Agent memory CRUD
- `POST /api/memory/auto-extract` - Extract memories from conversation
- `POST /api/refactor/preview` - Preview refactoring changes
- `POST /api/refactor/apply` - Apply refactoring
- `POST /api/projects/{id}/duplicate` - Duplicate project

### Integrations
- `POST /api/github/push` - Push to GitHub
- `POST /api/images/generate` - Generate images via fal.ai
- `GET /api/projects/{id}/preview` - Live preview HTML
- `GET /api/projects/{id}/export` - Export as ZIP

## Database Collections
- `projects` - Project metadata
- `agents` - Agent configurations
- `files` - Project files
- `messages` - Chat history
- `tasks` - Task board items
- `images` - Generated images
- `plans` - Project plans
- `memories` - Agent persistent memory
- `custom_actions` - User-defined quick actions

## Environment Variables
- `MONGO_URL` - MongoDB connection
- `DB_NAME` - Database name
- `FAL_KEY` - fal.ai API key
- `GITHUB_TOKEN` - GitHub personal access token

## Testing Status
- Backend: 100% (24/24 tests passed)
- Frontend: 100% (All features functional)
- Test file: `/app/backend/tests/test_v23_features.py`

## Future/Backlog (P1/P2)
- [ ] Real-time collaboration (multiple users)
- [ ] Blueprint visual scripting for Unreal
- [ ] Project templates gallery
- [ ] AI-powered code review suggestions
- [ ] Version history with diff viewer
- [ ] Audio asset generation integration
- [ ] Deployment pipeline (one-click deploy)
