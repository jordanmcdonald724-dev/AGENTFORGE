/**
 * ProjectWorkspace Constants & Configuration
 * ==========================================
 * Extracted from ProjectWorkspace.jsx for better maintainability
 */

import {
  MessageSquare, Radio, GitBranch, ListTodo, Layers, Palette,
  Music, Package, Box, Terminal, Server, Rocket
} from 'lucide-react';

export const PHASE_CONFIG = {
  clarification: { label: "Clarification", color: "bg-blue-500/20 text-blue-400", icon: "MessageSquare" },
  architecture: { label: "Architecture", color: "bg-purple-500/20 text-purple-400", icon: "Layers" },
  approved: { label: "Approved", color: "bg-green-500/20 text-green-400", icon: "Check" },
  building: { label: "Building", color: "bg-yellow-500/20 text-yellow-400", icon: "Hammer" },
  complete: { label: "Complete", color: "bg-emerald-500/20 text-emerald-400", icon: "CheckCircle" },
};

export const LANGUAGE_MAP = {
  cpp: "C++", h: "C++ Header", js: "JavaScript", jsx: "React JSX",
  ts: "TypeScript", tsx: "React TSX", py: "Python", cs: "C#",
  ini: "Config", json: "JSON", md: "Markdown", txt: "Text"
};

export const AGENTS = {
  COMMANDER: { color: "from-amber-500 to-orange-600" },
  ATLAS: { color: "from-blue-500 to-cyan-600" },
  FORGE: { color: "from-emerald-500 to-green-600" },
  SENTINEL: { color: "from-red-500 to-rose-600" },
  PRISM: { color: "from-violet-500 to-purple-600" },
  PROBE: { color: "from-pink-500 to-rose-600" },
};

export const QUICK_ACTION_ICONS = {
  layout: Layers, gamepad: Package, package: Package,
  save: Package, heart: Package, bot: Package
};

export const SYSTEM_ICONS = {
  GameFramework: Layers, Characters: Package, Vehicles: Package,
  AI: Package, World: Package, UI: Palette,
  Networking: Server, Audio: Music, Core: Package
};

export const PANEL_GROUPS = {
  core: {
    label: "Core",
    icon: MessageSquare,
    panels: [
      { id: "chat", label: "Chat", icon: MessageSquare },
      { id: "warroom", label: "War Room", icon: Radio },
      { id: "blueprints", label: "Blueprints", icon: GitBranch },
    ]
  },
  build: {
    label: "Build",
    icon: Layers,
    panels: [
      { id: "tasks", label: "Tasks", icon: ListTodo },
      { id: "queue", label: "Build Queue", icon: Layers },
      { id: "sandbox", label: "Sandbox", icon: Box },
    ]
  },
  assets: {
    label: "Assets",
    icon: Palette,
    panels: [
      { id: "images", label: "Images", icon: Palette },
      { id: "audio", label: "Audio", icon: Music },
      { id: "assets", label: "3D Assets", icon: Package },
    ]
  },
  advanced: {
    label: "Advanced",
    icon: Terminal,
    panels: [
      { id: "command", label: "Command Center", icon: Terminal },
      { id: "collab", label: "Collaboration", icon: Radio },
    ]
  },
  operations: {
    label: "Operations",
    icon: Server,
    panels: [
      { id: "deploy", label: "Deploy", icon: Rocket },
    ]
  }
};
