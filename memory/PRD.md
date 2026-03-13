# AgentForge - AI Development Studio

## Original Problem Statement
Build a web application that functions as an "AI agent dev team" backed by fal.ai. A platform for building full web pages, applications, and AAA-quality games with a team of specialized AI agents under user control. Features include Git repository management, high-level code editor, and Ubisoft studio-style workflow.

## Product Overview
AgentForge is a personal AI Development Studio with 6 specialized agents that work together to build projects. Now featuring overnight autonomous builds with scheduling, simulation mode, and comprehensive open world game systems.

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

### v2.3 - Advanced Features
- [x] Multi-file refactoring (find & replace across files)
- [x] Agent memory persistence (context across sessions)
- [x] Project duplication (clone with files)
- [x] Custom Quick Actions (user-defined automation)

### v3.0 - Autonomous Builds & Simulation
- [x] **Simulation Mode (Dry Run)** - Predicts build time, file count, size, warnings before building
- [x] **AI War Room** - Dedicated tab showing real-time agent communications
- [x] **Autonomous Builds** - Full builds with stage progress tracking
- [x] **Open World Game Systems** - 15 complete game systems for UE5 and Unity
- [x] **Modular File Generation** - Split large files into logical modules

### v3.1 - Overnight Scheduling (December 2025)
- [x] **Build Scheduling** - Schedule builds to start at specific time (before bed)
- [x] **Extended Build Time** - Minimum 12+ hours (now 15h 30m)
- [x] **Start Now / Cancel** - UI controls for scheduled builds
- [x] **COMMANDER Sleep Messages** - "Get some rest, I'll handle this"

## Build System

### Build Stages (8 stages, 15h 30m total)
1. Project Setup & Configuration (30m) - 6 tasks
2. Core Framework & Architecture (90m) - 8 tasks
3. Game Systems Implementation (180m) - 7 tasks
4. AI & NPC Systems (150m) - 9 tasks
5. UI/UX Framework (120m) - 10 tasks
6. World Building & Environment (150m) - 9 tasks
7. Audio & Effects Integration (90m) - 9 tasks
8. Polish, Testing & Documentation (120m) - 9 tasks

### Open World Systems (15 Total)
1. Terrain & World - Procedural terrain, biomes, world streaming
2. NPC Population - Spawning, schedules, factions
3. Quest System - Objectives, tracking, rewards
4. Vehicle System - Land, air, water vehicles with physics
5. Day/Night Cycle - Time, lighting, weather
6. Combat System - Melee, ranged, abilities
7. Crafting System - Resources, recipes, stations
8. Economy System - Currency, trading, shops
9. Stealth System - Visibility, sound, takedowns
10. Mount System - Rideable creatures, taming
11. Building System - Base building, snapping
12. Skill Tree - Progression, unlocks
13. Fast Travel - Discoverable locations
14. Photo Mode - Camera, filters, screenshots
15. Multiplayer - Networking, sessions, co-op

## API Endpoints

### Simulation & Builds
- `GET /api/systems/open-world` - List 15 game systems
- `GET /api/build-stages/{engine}` - Get build stages (930 minutes total)
- `POST /api/simulate` - Run simulation/dry run
- `POST /api/builds/start` - Start or schedule autonomous build
- `GET /api/builds/{project_id}/current` - Get current build
- `GET /api/builds/scheduled` - Get builds ready to start
- `POST /api/builds/{build_id}/start-scheduled` - Start scheduled build
- `POST /api/builds/{build_id}/pause` - Pause build
- `POST /api/builds/{build_id}/resume` - Resume build
- `POST /api/builds/{build_id}/cancel` - Cancel build

### War Room
- `GET /api/war-room/{project_id}` - Get agent communications
- `POST /api/war-room/message` - Post to war room
- `DELETE /api/war-room/{project_id}` - Clear war room

## Database Collections
- `projects`, `agents`, `files`, `messages`, `tasks`, `images`, `plans`, `memories`, `custom_actions`
- `simulations` - Simulation results
- `builds` - Autonomous build jobs (supports scheduled_at)
- `war_room` - Agent communications

## Environment Variables
- `MONGO_URL` - MongoDB connection
- `DB_NAME` - Database name
- `FAL_KEY` - fal.ai API key
- `GITHUB_TOKEN` - GitHub personal access token

## Testing Status
- v2.3: Backend 100% (24/24), Frontend 100%
- v3.0: Backend 100% (17/17), Frontend 100%
- v3.1: Backend 100% (10/10), Frontend 100%
- Total: 51+ tests passed

## Future/Backlog (P1/P2)
- [ ] Real-time collaboration (multiple users)
- [ ] Blueprint visual scripting for Unreal
- [ ] Project templates gallery
- [ ] AI-powered code review suggestions
- [ ] Version history with diff viewer
- [ ] Audio asset generation integration
- [ ] Deployment pipeline (one-click deploy)
- [ ] Email/Discord notifications for build completion
- [ ] Build queue (multiple scheduled builds)
