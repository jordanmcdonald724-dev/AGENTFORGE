import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import { toast } from "sonner";
import Editor from "@monaco-editor/react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger, DropdownMenuSub, DropdownMenuSubContent, DropdownMenuSubTrigger } from "@/components/ui/dropdown-menu";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable";
import { Progress } from "@/components/ui/progress";
import { Checkbox } from "@/components/ui/checkbox";
import { useTheme } from "@/context/ThemeContext";
import ThemeSelector from "@/components/ThemeSelector";
import { 
  ArrowLeft, Send, Bot, Code2, Layers, Users, Shield, Zap, Plus, Loader2, FileCode, ListTodo, MessageSquare,
  Folder, FolderOpen, ChevronRight, ChevronDown, Save, Download, Trash2, Palette, Copy, Check, X, Image,
  Sparkles, ArrowRightCircle, ArrowRight, Github, Play, Eye, Gamepad2, Package, Heart, Volume2, Layout, MessageCircle,
  Rocket, ChevronUp, RefreshCw, Brain, Wand2, CopyPlus, Search, Replace, Radio, AlertTriangle, Clock,
  Pause, Square, SkipForward, Swords, Mountain, Car, Sun, Map, Hammer, Coins, Ghost, Timer, Camera, Wifi,
  Joystick, Monitor, Globe, GitBranch, Calendar, Bell, Music, Terminal, Command, Settings, Moon, Menu
} from "lucide-react";
import { API } from "@/App";
import BlueprintEditor from "@/components/BlueprintEditor";
import CollaborationPanel from "@/components/CollaborationPanel";
import BuildQueuePanel from "@/components/BuildQueuePanel";
import NotificationsPanel from "@/components/NotificationsPanel";
import AudioGeneratorPanel from "@/components/AudioGeneratorPanel";
import DeploymentPanel from "@/components/DeploymentPanel";
import SandboxPanel from "@/components/SandboxPanel";
import AssetPipelinePanel from "@/components/AssetPipelinePanel";
import CommandCenter from "@/components/CommandCenter";
import GameEnginePanel from "@/components/GameEnginePanel";
import HardwarePanel from "@/components/HardwarePanel";
import ResearchPanel from "@/components/ResearchPanel";
import FileDropZone from "@/components/FileDropZone";
import WarRoomPanel from "@/pages/workspace/WarRoomPanel";
import WorkspaceChatPanel from "@/pages/workspace/WorkspaceChatPanel";
import WorkspaceCodeEditor from "@/pages/workspace/WorkspaceCodeEditor";
import WorkspaceDialogs from "@/pages/workspace/WorkspaceDialogs";

const PHASE_CONFIG = {
  clarification: { label: "Clarification", color: "bg-amber-500/20 text-amber-400", icon: MessageSquare },
  planning: { label: "Planning", color: "bg-blue-500/20 text-blue-400", icon: Layers },
  development: { label: "Development", color: "bg-emerald-500/20 text-emerald-400", icon: Code2 },
  review: { label: "Review", color: "bg-purple-500/20 text-purple-400", icon: Shield },
  building: { label: "Building", color: "bg-cyan-500/20 text-cyan-400 animate-pulse", icon: Rocket },
  scheduled: { label: "Scheduled", color: "bg-purple-500/20 text-purple-400", icon: Clock }
};

const LANGUAGE_MAP = {
  cpp: "cpp", "c++": "cpp", csharp: "csharp", "c#": "csharp", cs: "csharp",
  javascript: "javascript", js: "javascript", typescript: "typescript", ts: "typescript",
  python: "python", py: "python", json: "json", html: "html", css: "css",
  yaml: "yaml", yml: "yaml", markdown: "markdown", md: "markdown",
  gdscript: "python", blueprint: "json", hlsl: "cpp", glsl: "cpp"
};

const AGENTS = {
  lead: { icon: Users, color: "text-blue-400" },
  architect: { icon: Layers, color: "text-cyan-400" },
  developer: { icon: Code2, color: "text-emerald-400" },
  reviewer: { icon: Shield, color: "text-amber-400" },
  tester: { icon: Zap, color: "text-purple-400" },
  artist: { icon: Palette, color: "text-pink-400" }
};

const QUICK_ACTION_ICONS = {
  gamepad: Gamepad2, package: Package, save: Save, heart: Heart, bot: Bot,
  "message-square": MessageCircle, layout: Layout, "volume-2": Volume2, sparkles: Sparkles
};

// SYSTEM_ICONS lives in WorkspaceDialogs.jsx where it's actually used

// Panel configuration for grouped dropdown navigation
const PANEL_GROUPS = {
  core: {
    label: "Core",
    icon: MessageSquare,
    panels: [
      { id: "chat", label: "Chat", icon: MessageSquare },
      { id: "warroom", label: "War Room", icon: Radio },
      { id: "tasks", label: "Tasks", icon: ListTodo },
    ]
  },
  build: {
    label: "Build",
    icon: Code2,
    panels: [
      { id: "blueprints", label: "Blueprints", icon: GitBranch },
      { id: "queue", label: "Build Queue", icon: Calendar },
      { id: "sandbox", label: "Sandbox", icon: Terminal },
      { id: "command", label: "Command Center", icon: Command },
    ]
  },
  assets: {
    label: "Assets",
    icon: Package,
    panels: [
      { id: "images", label: "Images", icon: Image },
      { id: "audio", label: "Audio", icon: Music },
      { id: "assets", label: "Asset Pipeline", icon: Package },
    ]
  },
  advanced: {
    label: "Advanced",
    icon: Sparkles,
    panels: [
      { id: "game-engine", label: "Game Engine", icon: Gamepad2 },
      { id: "hardware", label: "Hardware", icon: Joystick },
      { id: "research", label: "Research", icon: Globe },
    ]
  },
  ops: {
    label: "Operations",
    icon: Rocket,
    panels: [
      { id: "deploy", label: "Deploy", icon: Rocket },
      { id: "collab", label: "Collaboration", icon: Users },
      { id: "notifications", label: "Alerts", icon: Bell },
    ]
  }
};

const ProjectWorkspace = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const chatEndRef = useRef(null);
  
  const [project, setProject] = useState(null);
  const [agents, setAgents] = useState([]);
  const [messages, setMessages] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [files, setFiles] = useState([]);
  const [images, setImages] = useState([]);
  const [quickActions, setQuickActions] = useState([]);
  const [customActions, setCustomActions] = useState([]);
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // War Room & Builds
  const [warRoomMessages, setWarRoomMessages] = useState([]);
  const [openWorldSystems, setOpenWorldSystems] = useState([]);
  const [currentBuild, setCurrentBuild] = useState(null);
  const [simulationResult, setSimulationResult] = useState(null);
  const [currentDemo, setCurrentDemo] = useState(null);
  const [demoDialogOpen, setDemoDialogOpen] = useState(false);
  const [regeneratingDemo, setRegeneratingDemo] = useState(false);
  
  const [chatInput, setChatInput] = useState("");
  const [attachedFiles, setAttachedFiles] = useState([]);
  const [sending, setSending] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [streamingAgent, setStreamingAgent] = useState(null);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [chainProgress, setChainProgress] = useState(null);
  
  const [selectedFile, setSelectedFile] = useState(null);
  const [editorContent, setEditorContent] = useState("");
  const [unsavedChanges, setUnsavedChanges] = useState(false);
  const [expandedFolders, setExpandedFolders] = useState(new Set([""]));
  
  const [activeTab, setActiveTab] = useState("chat");
  const [rightTab, setRightTab] = useState("code");
  const [copiedCode, setCopiedCode] = useState(null);
  const [showQuickActions, setShowQuickActions] = useState(true);
  
  // Dialog states
  const [taskDialogOpen, setTaskDialogOpen] = useState(false);
  const [newTask, setNewTask] = useState({ title: "", description: "", priority: "medium", category: "general" });
  const [imageDialogOpen, setImageDialogOpen] = useState(false);
  const [imagePrompt, setImagePrompt] = useState("");
  const [imageCategory, setImageCategory] = useState("concept");
  const [generatingImage, setGeneratingImage] = useState(false);
  const [githubDialogOpen, setGithubDialogOpen] = useState(false);
  const [githubToken, setGithubToken] = useState("");
  const [githubRepoName, setGithubRepoName] = useState("");
  const [githubCreateNew, setGithubCreateNew] = useState(true);
  const [pushing, setPushing] = useState(false);
  const [previewHtml, setPreviewHtml] = useState("");
  
  // v2.3 states
  const [customActionDialog, setCustomActionDialog] = useState(false);
  const [newCustomAction, setNewCustomAction] = useState({ name: "", description: "", prompt: "", chain: ["COMMANDER", "FORGE"], icon: "sparkles", is_global: false });
  const [refactorDialog, setRefactorDialog] = useState(false);
  const [refactorData, setRefactorData] = useState({ type: "find_replace", target: "", new_value: "" });
  const [refactorPreview, setRefactorPreview] = useState(null);
  const [memoryDialog, setMemoryDialog] = useState(false);
  const [duplicateDialog, setDuplicateDialog] = useState(false);
  const [duplicateName, setDuplicateName] = useState("");
  
  // v3.0 states - Simulation & Build
  const [simulationDialog, setSimulationDialog] = useState(false);
  const [selectedSystems, setSelectedSystems] = useState([]);
  const [targetEngine, setTargetEngine] = useState("unreal");
  const [simulating, setSimulating] = useState(false);
  const [buildRunning, setBuildRunning] = useState(false);
  const [scheduleBuild, setScheduleBuild] = useState(false);
  const [scheduleTime, setScheduleTime] = useState("");

  // v3.3 states - Blueprints, Queue, Collaboration
  const [blueprints, setBlueprints] = useState([]);
  const [selectedBlueprint, setSelectedBlueprint] = useState(null);
  const [blueprintTemplates, setBlueprintTemplates] = useState({});
  const [currentUser] = useState({ id: `user_${Date.now()}`, username: "Developer" }); // Mock user for collab

  // Pipeline parallel status: { FORGE: 'working', ATLAS: 'done', ... }
  const [pipelineAgentStatus, setPipelineAgentStatus] = useState({});
  // Server-side pipeline run (persists after browser close)
  const [activePipelineId, setActivePipelineId] = useState(null);
  const [pipelineRunStatus, setPipelineRunStatus] = useState(null);

  useEffect(() => { fetchProjectData(); }, [projectId]);
  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, streamingContent]);

  // Auto-expand file tree: whenever files change, expand all parent paths so nested
  // files (e.g. AbyssalShores/Source/.../file.h) are visible without manual clicking
  useEffect(() => {
    if (files.length === 0) return;
    setExpandedFolders(prev => {
      const next = new Set(prev);
      files.forEach(f => {
        const parts = f.filepath.split('/').filter(Boolean);
        for (let i = 1; i < parts.length; i++) {
          next.add(parts.slice(0, i).join('/'));
        }
      });
      return next;
    });
  }, [files]);
  
  // Poll for war room and build updates
  useEffect(() => {
    if (activeTab === "warroom" || currentBuild?.status === "running") {
      const interval = setInterval(() => {
        fetchWarRoom();
        fetchCurrentBuild();
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [activeTab, currentBuild?.status]);

  // Poll server-side pipeline run: refresh messages + files + status every 4s
  useEffect(() => {
    if (!activePipelineId) return;
    const interval = setInterval(async () => {
      try {
        const [runRes, msgRes, filesRes] = await Promise.all([
          axios.get(`${API}/pipeline/run/${activePipelineId}`),
          axios.get(`${API}/messages?project_id=${projectId}&limit=500`),
          axios.get(`${API}/files?project_id=${projectId}&limit=500`)
        ]);
        const run = runRes.data;
        setPipelineRunStatus(run);
        setMessages(msgRes.data);
        setFiles(filesRes.data);
        // Update progress bar from server status
        if (run.agent_status) setPipelineAgentStatus(run.agent_status);
        // Stop polling on any terminal status
        const terminal = ['completed', 'failed', 'cancelled', 'interrupted'];
        if (terminal.includes(run.status)) {
          setActivePipelineId(null);
          setPipelineAgentStatus({});
          setSending(false);
          if (run.status === 'completed')    toast.success('Pipeline complete');
          else if (run.status === 'cancelled')  toast.info('Pipeline cancelled');
          else if (run.status === 'interrupted') toast.warning('Pipeline was interrupted (server restarted). You can re-run the build.');
          else toast.error(`Pipeline failed: ${run.error || 'unknown error'}`);
          await fetchWarRoom();
        }
      } catch (e) { /* polling errors are non-fatal */ }
    }, 4000);
    return () => clearInterval(interval);
  }, [activePipelineId, projectId]);

  const fetchProjectData = async () => {
    try {
      const [projectRes, agentsRes, messagesRes, tasksRes, filesRes, imagesRes, actionsRes, customRes, memRes, systemsRes] = await Promise.all([
        axios.get(`${API}/projects/${projectId}`),
        axios.get(`${API}/agents`),
        axios.get(`${API}/messages?project_id=${projectId}&limit=500`),
        axios.get(`${API}/tasks?project_id=${projectId}`),
        axios.get(`${API}/files?project_id=${projectId}`),
        axios.get(`${API}/images?project_id=${projectId}`).catch(() => ({ data: [] })),
        axios.get(`${API}/quick-actions`).catch(() => ({ data: [] })),
        axios.get(`${API}/custom-actions?project_id=${projectId}`).catch(() => ({ data: [] })),
        axios.get(`${API}/memory?project_id=${projectId}`).catch(() => ({ data: [] })),
        axios.get(`${API}/systems/open-world`).catch(() => ({ data: [] }))
      ]);
      setProject(projectRes.data);
      setAgents(agentsRes.data);
      setMessages(messagesRes.data);
      setTasks(tasksRes.data);
      setFiles(filesRes.data);
      setImages(imagesRes.data);
      setQuickActions(actionsRes.data);
      setCustomActions(customRes.data);
      setMemories(memRes.data);
      setOpenWorldSystems(systemsRes.data);
      setGithubRepoName(projectRes.data.name.toLowerCase().replace(/\s+/g, '-'));
      setDuplicateName(projectRes.data.name + " Copy");
      
      // Set default engine based on project type
      if (projectRes.data.type === "unity") setTargetEngine("unity");
      
      // Fetch war room, build, demo, and blueprints
      await fetchWarRoom();
      await fetchCurrentBuild();
      await fetchLatestDemo();
      await fetchBlueprints();
      await fetchBlueprintTemplates();

      // Auto-resume: check for an active server-side pipeline from a previous session
      try {
        const pipelineRes = await axios.get(`${API}/pipeline/run/project/${projectId}/latest`);
        const latestRun = pipelineRes.data;
        if (latestRun?.status === 'running') {
          // API returns 'id' field on GET (not 'run_id' which is only in POST response)
          const resumeId = latestRun.run_id || latestRun.id;
          setActivePipelineId(resumeId);
          setPipelineRunStatus(latestRun);
          // Populate agent status bar immediately (polling will refresh every 4s)
          if (latestRun.agent_status) setPipelineAgentStatus(latestRun.agent_status);
          toast.info('Resuming pipeline from previous session...');
        }
      } catch (e) { /* no previous pipeline — that's fine */ }
    } catch (error) {
      toast.error("Failed to load project");
      navigate("/dashboard");
    } finally {
      setLoading(false);
    }
  };

  const fetchWarRoom = async () => {
    try {
      const res = await axios.get(`${API}/war-room/${projectId}`);
      // Dedupe messages by content hash to prevent glitchy repeats
      const seen = new Set();
      const deduped = res.data.filter(msg => {
        // Create a unique key from agent + full content
        const key = `${msg.from_agent}-${msg.message_type}-${msg.content}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      });
      setWarRoomMessages(deduped);
    } catch (e) {}
  };

  const fetchBlueprints = async () => {
    try {
      const res = await axios.get(`${API}/blueprints?project_id=${projectId}`);
      setBlueprints(res.data);
    } catch (e) {}
  };

  const fetchBlueprintTemplates = async () => {
    try {
      const res = await axios.get(`${API}/blueprints/templates`);
      setBlueprintTemplates(res.data);
    } catch (e) {}
  };

  const createBlueprint = async (name, type = "logic") => {
    try {
      const res = await axios.post(`${API}/blueprints`, null, {
        params: { project_id: projectId, name, blueprint_type: type, target_engine: targetEngine }
      });
      setBlueprints([...blueprints, res.data]);
      setSelectedBlueprint(res.data);
      toast.success("Blueprint created!");
    } catch (e) { toast.error("Failed to create blueprint"); }
  };

  const updateBlueprint = async (data) => {
    if (!selectedBlueprint) return;
    try {
      await axios.patch(`${API}/blueprints/${selectedBlueprint.id}`, data);
      setSelectedBlueprint({ ...selectedBlueprint, ...data });
    } catch (e) {}
  };

  const generateCodeFromBlueprint = async () => {
    if (!selectedBlueprint) return;
    try {
      const res = await axios.post(`${API}/blueprints/${selectedBlueprint.id}/generate-code`);
      toast.success(`Generated code: ${res.data.filepath}`);
      fetchProjectData(); // Refresh files
    } catch (e) { toast.error("Code generation failed"); }
  };

  const syncBlueprintFromCode = async () => {
    if (!selectedBlueprint) return;
    try {
      const res = await axios.post(`${API}/blueprints/${selectedBlueprint.id}/sync-from-code`);
      toast.success(`Synced ${res.data.synced_nodes} nodes from code`);
      fetchBlueprints();
    } catch (e) { toast.error("Sync failed"); }
  };

  const fetchCurrentBuild = async () => {
    try {
      const res = await axios.get(`${API}/builds/${projectId}/current`);
      setCurrentBuild(res.data);
      // If build just completed, fetch the demo
      if (res.data?.status === "completed" && res.data?.demo_id) {
        await fetchLatestDemo();
      }
    } catch (e) {}
  };

  const fetchLatestDemo = async () => {
    try {
      const res = await axios.get(`${API}/demos/${projectId}/latest`);
      setCurrentDemo(res.data);
    } catch (e) {}
  };

  const regenerateDemo = async () => {
    setRegeneratingDemo(true);
    try {
      await axios.post(`${API}/demos/${projectId}/regenerate`);
      toast.success("Demo regeneration started!");
      // Poll for completion
      const checkDemo = setInterval(async () => {
        const res = await axios.get(`${API}/demos/${projectId}/latest`);
        if (res.data?.status === "ready") {
          setCurrentDemo(res.data);
          setRegeneratingDemo(false);
          clearInterval(checkDemo);
          toast.success("Demo ready!");
        }
      }, 5000);
    } catch (error) {
      toast.error("Failed to regenerate demo");
      setRegeneratingDemo(false);
    }
  };

  const openWebDemo = () => {
    if (currentDemo?.web_demo_html) {
      const newWindow = window.open("", "_blank");
      newWindow.document.write(currentDemo.web_demo_html);
      newWindow.document.close();
    } else {
      window.open(`${API}/demos/${projectId}/web`, "_blank");
    }
  };

  const sendMessageStreaming = async () => {
    if (!chatInput.trim() || sending) return;
    setSending(true);
    
    // Prepare message with files
    let userMessage = chatInput;
    if (attachedFiles.length > 0) {
      userMessage += '\n\n**Attached Files:**\n';
      attachedFiles.forEach(file => {
        userMessage += `\n**${file.name}** (${file.type}):\n\`\`\`\n${file.content}\n\`\`\`\n`;
      });
    }
    
    setChatInput("");
    setAttachedFiles([]);
    setStreamingContent("");

    const tempUserMsg = { id: `temp-user-${Date.now()}`, project_id: projectId, agent_id: "user", agent_name: "You", agent_role: "user", content: userMessage, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, tempUserMsg]);

    try {
      const response = await fetch(`${API}/chat/stream`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, message: userMessage, phase: project?.phase, delegate_to: selectedAgent ? agents.find(a => a.id === selectedAgent)?.name : null })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullContent = "";
      let currentAgent = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        for (const line of chunk.split('\n')) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === 'start') { currentAgent = data.agent; setStreamingAgent(data.agent); setAgents(prev => prev.map(a => a.id === data.agent.id ? { ...a, status: "thinking" } : a)); }
              else if (data.type === 'content') { fullContent += data.content; setStreamingContent(fullContent); }
              else if (data.type === 'done') {
                const agentMsg = { id: `agent-${Date.now()}`, project_id: projectId, agent_id: currentAgent?.id, agent_name: currentAgent?.name, agent_role: currentAgent?.role, content: fullContent, code_blocks: data.code_blocks || [], delegations: data.delegations || [], timestamp: new Date().toISOString() };
                setMessages(prev => [...prev, agentMsg]);
                setStreamingContent(""); setStreamingAgent(null);
                if (data.code_blocks?.length > 0) {
                  await saveCodeBlocks(data.code_blocks, currentAgent);
                  // Refresh files list
                  const filesRes = await axios.get(`${API}/files?project_id=${projectId}`);
                  setFiles(filesRes.data);
                }
                // Handle phase change
                if (data.new_phase) {
                  setProject(prev => ({ ...prev, phase: data.new_phase }));
                  toast.success(`Project advanced to ${data.new_phase} phase`);
                }
                // Auto-execute delegations from COMMANDER — isChainCall=true keeps sending=true throughout
                if (data.delegations && data.delegations.length > 0) {
                  console.log('[Pipeline] COMMANDER issued delegations:', data.delegations.map(d => d.agent));
                  await runPipelinePhased(data.delegations);
                  toast.success('Pipeline complete');
                }
                setAgents(prev => prev.map(a => ({ ...a, status: "idle" })));
              }
            } catch (e) {}
          }
        }
      }
    } catch (error) { toast.error("Failed to send message"); }
    finally { setSending(false); setAgents(prev => prev.map(a => ({ ...a, status: "idle" }))); }
  };

  const executeQuickAction = async (actionId, isCustom = false) => {
    setSending(true);
    setChainProgress({ action: actionId, step: 0, total: 0 });
    const endpoint = isCustom ? `${API}/custom-actions/${actionId}/execute/stream?project_id=${projectId}` : `${API}/quick-actions/execute/stream`;
    const body = isCustom ? {} : { project_id: projectId, action_id: actionId };

    try {
      const response = await fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let currentAgentContent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        for (const line of decoder.decode(value).split('\n')) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === 'agent_start') { setChainProgress({ action: actionId, step: data.step, total: data.total, agent: data.agent }); setStreamingAgent({ name: data.agent, role: data.role }); currentAgentContent = ""; setAgents(prev => prev.map(a => a.name === data.agent ? { ...a, status: "working" } : a)); }
              else if (data.type === 'content') { currentAgentContent += data.content; setStreamingContent(currentAgentContent); }
              else if (data.type === 'agent_done') { setMessages(prev => [...prev, { id: `chain-${Date.now()}-${data.agent}`, project_id: projectId, agent_name: data.agent, agent_role: "chain", content: currentAgentContent, code_blocks: data.code_blocks || [], timestamp: new Date().toISOString() }]); setStreamingContent(""); setAgents(prev => prev.map(a => a.name === data.agent ? { ...a, status: "idle" } : a)); }
              else if (data.type === 'chain_complete') { toast.success(`Saved ${data.saved_files?.length || 0} files`); fetchProjectData(); }
            } catch (e) {}
          }
        }
      }
    } catch (error) { toast.error("Action failed"); }
    finally { setSending(false); setChainProgress(null); setStreamingAgent(null); }
  };

  const saveCodeBlocks = async (codeBlocks, agent) => {
    const validBlocks = codeBlocks.filter(b => b.filepath);
    if (validBlocks.length === 0) return;
    try {
      await axios.post(`${API}/files/from-chat`, { project_id: projectId, code_blocks: validBlocks, agent_id: agent?.id, agent_name: agent?.name });
      const filesRes = await axios.get(`${API}/files?project_id=${projectId}`);
      setFiles(filesRes.data);
      toast.success(`Saved ${validBlocks.length} file(s)`);
    } catch (error) {}
  };

  // executeDelegation uses streaming to avoid proxy timeouts and provide real-time feedback
  // isChainCall=true means it's called mid-pipeline; don't toggle the global sending state
  const executeDelegation = async (agentName, task, isChainCall = false) => {
    console.log(`[Pipeline] → ${agentName}`);
    if (!isChainCall) setSending(true);
    
    try {
      const response = await fetch(`${API}/delegate/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, message: task, delegate_to: agentName })
      });
      
      if (!response.ok) {
        throw new Error(`${agentName} returned ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullContent = "";
      let currentAgent = null;

      // Show streaming for this delegate agent
      setStreamingAgent({ name: agentName, role: 'delegation' });
      setStreamingContent("");

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        for (const line of chunk.split('\n')) {
          if (!line.startsWith('data: ')) continue;
          try {
            const data = JSON.parse(line.slice(6));
            if (data.type === 'start') {
              currentAgent = data.agent;
              setStreamingAgent(data.agent);
              setAgents(prev => prev.map(a => a.id === data.agent.id ? { ...a, status: "working" } : a));
            } else if (data.type === 'content') {
              fullContent += data.content;
              setStreamingContent(fullContent);
            } else if (data.type === 'done') {
              setStreamingContent("");
              setStreamingAgent(null);

              // Extract delegations from response text as fallback if backend didn't find them
              const delegationRegex = /\[DELEGATE:(\w+)\]([\s\S]*?)\[\/DELEGATE\]/g;
              const parsedDelegations = [];
              let m;
              while ((m = delegationRegex.exec(fullContent)) !== null) {
                parsedDelegations.push({ agent: m[1].toUpperCase(), task: m[2].trim() });
              }
              const chainDelegations = data.delegations?.length > 0 ? data.delegations : parsedDelegations;

              const newMsg = {
                id: `delegate-${Date.now()}`,
                project_id: projectId,
                agent_id: currentAgent?.id,
                agent_name: currentAgent?.name || agentName,
                agent_role: currentAgent?.role,
                content: fullContent,
                code_blocks: data.code_blocks || [],
                delegations: chainDelegations,
                timestamp: new Date().toISOString()
              };
              setMessages(prev => [...prev, newMsg]);
              setAgents(prev => prev.map(a => ({ ...a, status: "idle" })));

              if (data.code_blocks?.length > 0) {
                await saveCodeBlocks(data.code_blocks, currentAgent);
                const filesRes = await axios.get(`${API}/files?project_id=${projectId}`);
                setFiles(filesRes.data);
              }

              // Auto-chain: continue pipeline if this agent issued more delegations
              if (chainDelegations.length > 0) {
                for (const delegation of chainDelegations) {
                  toast.info(`${agentName} → ${delegation.agent}`);
                  await executeDelegation(delegation.agent, delegation.task, true);
                }
              }
            } else if (data.type === 'error') {
              setStreamingContent("");
              setStreamingAgent(null);
              throw new Error(data.error);
            }
          } catch (parseErr) {
            // Silently skip malformed SSE lines
          }
        }
      }
    } catch (error) {
      console.error(`[Pipeline] ${agentName} error:`, error);
      setStreamingContent("");
      setStreamingAgent(null);
      toast.error(`${agentName} failed: ${error.message}`);
    } finally {
      if (!isChainCall) setSending(false);
    }
  };

  // ── Silent delegation: streams response without updating streaming UI ──────
  // Used for parallel agents so multiple can run without UI state conflicts.
  const executeDelegationSilent = async (agentName, task) => {
    setPipelineAgentStatus(prev => ({ ...prev, [agentName]: 'working' }));
    try {
      const response = await fetch(`${API}/delegate/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, message: task, delegate_to: agentName })
      });
      if (!response.ok) throw new Error(`${agentName} returned ${response.status}`);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullContent = "";
      let currentAgent = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        for (const line of decoder.decode(value).split('\n')) {
          if (!line.startsWith('data: ')) continue;
          try {
            const data = JSON.parse(line.slice(6));
            if (data.type === 'start') {
              currentAgent = data.agent;
              setAgents(prev => prev.map(a => a.id === data.agent.id ? { ...a, status: "working" } : a));
            } else if (data.type === 'content') {
              fullContent += data.content; // accumulate silently
            } else if (data.type === 'done') {
              const delegationRegex = /\[DELEGATE:(\w+)\]([\s\S]*?)\[\/DELEGATE\]/g;
              const parsed = [];
              let m;
              while ((m = delegationRegex.exec(fullContent)) !== null) {
                parsed.push({ agent: m[1].toUpperCase(), task: m[2].trim() });
              }
              const chainDelegations = data.delegations?.length > 0 ? data.delegations : parsed;

              setMessages(prev => [...prev, {
                id: `parallel-${Date.now()}-${agentName}`,
                project_id: projectId,
                agent_id: currentAgent?.id,
                agent_name: currentAgent?.name || agentName,
                agent_role: currentAgent?.role,
                content: fullContent,
                code_blocks: data.code_blocks || [],
                delegations: chainDelegations,
                timestamp: new Date().toISOString()
              }]);
              setAgents(prev => prev.map(a => a.id === currentAgent?.id ? { ...a, status: "idle" } : a));

              if (data.code_blocks?.length > 0) {
                await saveCodeBlocks(data.code_blocks, currentAgent);
              }

              // Post War Room build log entry for this agent's completion
              const fileCount = data.code_blocks?.length || 0;
              const summary = fileCount > 0
                ? `Completed parallel task — generated ${fileCount} file(s): ${data.code_blocks.map(b => b.filepath?.split('/').pop() || b.filename).filter(Boolean).slice(0, 3).join(', ')}${fileCount > 3 ? ` +${fileCount - 3} more` : ''}`
                : `Completed task: ${task.substring(0, 100)}${task.length > 100 ? '...' : ''}`;
              try {
                await axios.post(`${API}/war-room/message`, null, {
                  params: { project_id: projectId, from_agent: agentName, content: summary, message_type: "progress" }
                });
                // Refresh War Room so the new entry is visible
                const wr = await axios.get(`${API}/war-room/${projectId}`);
                const seen = new Set();
                const deduped = wr.data.filter(msg => {
                  const key = `${msg.from_agent}-${msg.message_type}-${msg.content}`;
                  if (seen.has(key)) return false;
                  seen.add(key);
                  return true;
                });
                setWarRoomMessages(deduped);
              } catch (e) { /* non-critical — war room log failure shouldn't break pipeline */ }
            } else if (data.type === 'error') {
              throw new Error(data.error);
            }
          } catch (e) { /* skip malformed lines */ }
        }
      }
      setPipelineAgentStatus(prev => ({ ...prev, [agentName]: 'done' }));
    } catch (error) {
      console.error(`[Parallel] ${agentName} failed:`, error);
      toast.error(`${agentName} failed: ${error.message}`);
      setPipelineAgentStatus(prev => ({ ...prev, [agentName]: 'error' }));
    }
  };

  // Cancel a running server-side pipeline
  const cancelPipeline = async () => {
    if (!activePipelineId) return;
    try {
      await axios.post(`${API}/pipeline/run/${activePipelineId}/cancel`);
      setActivePipelineId(null);
      setPipelineAgentStatus({});
      setPipelineRunStatus(null);
      setSending(false);
      toast.info('Pipeline cancelled');
    } catch (e) {
      toast.error('Could not cancel pipeline');
    }
  };

  // Phased pipeline: prefers server-side execution (pipeline persists after browser close).
  // Falls back to browser-side execution if server endpoint fails.
  const DESIGN_AGENTS = new Set(['NEXUS', 'ATLAS']);
  const REVIEW_AGENTS = new Set(['SENTINEL', 'PROBE']);

  const runPipelinePhased = async (delegations) => {
    // Try server-side first
    try {
      const res = await axios.post(`${API}/pipeline/run`, {
        project_id: projectId,
        delegations
      });
      setActivePipelineId(res.data.run_id);
      // Initialize agent status bar immediately so Cancel button is visible without waiting for first poll
      const initialStatus = Object.fromEntries(delegations.map(d => [d.agent.toUpperCase(), 'pending']));
      setPipelineAgentStatus(initialStatus);
      setPipelineRunStatus({ ...res.data, agent_status: initialStatus });
      setSending(true); // keep input locked while pipeline runs
      toast.info(`Pipeline running on server (${delegations.length} agents)...`);
      return; // polling useEffect takes over from here
    } catch (serverErr) {
      console.warn('[Pipeline] Server-side start failed, falling back to browser:', serverErr.message);
    }

    // Browser-side fallback (original phased approach)
    const phase1 = delegations.filter(d => DESIGN_AGENTS.has(d.agent.toUpperCase()));
    const phase3 = delegations.filter(d => REVIEW_AGENTS.has(d.agent.toUpperCase()));
    const phase2 = delegations.filter(d =>
      !DESIGN_AGENTS.has(d.agent.toUpperCase()) && !REVIEW_AGENTS.has(d.agent.toUpperCase())
    );

    for (const d of phase1) await executeDelegation(d.agent, d.task, true);

    if (phase2.length > 0) {
      const status = {};
      phase2.forEach(d => { status[d.agent] = 'pending'; });
      setPipelineAgentStatus(status);
      toast.info(`Running ${phase2.length} agents in parallel...`);
      const BATCH = 4;
      for (let i = 0; i < phase2.length; i += BATCH) {
        await Promise.all(phase2.slice(i, i + BATCH).map(d => executeDelegationSilent(d.agent, d.task)));
      }
      const filesRes = await axios.get(`${API}/files?project_id=${projectId}&limit=500`);
      setFiles(filesRes.data);
      setPipelineAgentStatus({});
    }

    for (const d of phase3) await executeDelegation(d.agent, d.task, true);
  };

  // ========== SIMULATION MODE ==========
  const runSimulation = async () => {
    if (selectedSystems.length === 0) { toast.error("Select at least one system"); return; }
    setSimulating(true);
    try {
      const res = await axios.post(`${API}/simulate`, {
        project_id: projectId,
        build_type: "full",
        target_engine: targetEngine,
        include_systems: selectedSystems
      });
      setSimulationResult(res.data);
      toast.success("Simulation complete!");
    } catch (error) { toast.error("Simulation failed"); }
    finally { setSimulating(false); }
  };

  const toggleSystem = (systemId) => {
    setSelectedSystems(prev => 
      prev.includes(systemId) 
        ? prev.filter(s => s !== systemId) 
        : [...prev, systemId]
    );
  };

  // ========== AUTONOMOUS BUILDS ==========
  const startAutonomousBuild = async (isScheduled = false) => {
    if (!simulationResult || !simulationResult.ready_to_build) {
      toast.error("Run simulation first and resolve all high-severity warnings");
      return;
    }
    
    if (isScheduled && !scheduleTime) {
      toast.error("Please select a time to schedule the build");
      return;
    }
    
    setBuildRunning(true);
    try {
      const buildData = {
        project_id: projectId,
        build_type: "full",
        target_engine: targetEngine,
        systems_to_build: selectedSystems
      };
      
      if (isScheduled && scheduleTime) {
        // Convert local time to ISO string
        const scheduledDate = new Date(scheduleTime);
        buildData.scheduled_at = scheduledDate.toISOString();
      }
      
      const res = await axios.post(`${API}/builds/start`, buildData);
      setCurrentBuild(res.data);
      setSimulationDialog(false);
      setActiveTab("warroom");
      
      if (isScheduled) {
        const scheduledDate = new Date(scheduleTime);
        toast.success(`Build scheduled for ${scheduledDate.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}! Sweet dreams 🌙`);
      } else {
        toast.success("Autonomous build started!");
        // Start running stages immediately
        await axios.post(`${API}/builds/${res.data.id}/run-full`);
      }
    } catch (error) { toast.error(error.response?.data?.detail || "Build failed to start"); }
    finally { setBuildRunning(false); setScheduleBuild(false); setScheduleTime(""); }
  };

  const startScheduledBuildNow = async () => {
    if (!currentBuild || currentBuild.status !== "scheduled") return;
    try {
      await axios.post(`${API}/builds/${currentBuild.id}/start-scheduled`);
      await fetchCurrentBuild();
      toast.success("Scheduled build started!");
    } catch (error) { toast.error("Failed to start scheduled build"); }
  };

  const pauseBuild = async () => {
    if (!currentBuild) return;
    await axios.post(`${API}/builds/${currentBuild.id}/pause`);
    await fetchCurrentBuild();
    toast.info("Build paused");
  };

  const resumeBuild = async () => {
    if (!currentBuild) return;
    await axios.post(`${API}/builds/${currentBuild.id}/resume`);
    await fetchCurrentBuild();
    toast.success("Build resumed");
  };

  const cancelBuild = async () => {
    if (!currentBuild) return;
    await axios.post(`${API}/builds/${currentBuild.id}/cancel`);
    await fetchCurrentBuild();
    toast.info("Build cancelled");
  };

  // Custom Actions, Refactoring, Memory, Duplicate (same as before)
  const createCustomAction = async () => {
    if (!newCustomAction.name || !newCustomAction.prompt) { toast.error("Name and prompt required"); return; }
    try {
      const res = await axios.post(`${API}/custom-actions`, { ...newCustomAction, project_id: projectId });
      setCustomActions([...customActions, res.data]);
      setNewCustomAction({ name: "", description: "", prompt: "", chain: ["COMMANDER", "FORGE"], icon: "sparkles", is_global: false });
      setCustomActionDialog(false);
      toast.success("Custom action created!");
    } catch (error) { toast.error("Failed to create action"); }
  };

  const deleteCustomAction = async (id) => {
    await axios.delete(`${API}/custom-actions/${id}`);
    setCustomActions(customActions.filter(a => a.id !== id));
  };

  const previewRefactor = async () => {
    if (!refactorData.target) { toast.error("Enter a search target"); return; }
    try {
      const res = await axios.post(`${API}/refactor/preview`, {
        project_id: projectId, refactor_type: refactorData.type,
        target: refactorData.target, new_value: refactorData.new_value
      });
      setRefactorPreview(res.data);
    } catch (error) { toast.error("Preview failed"); }
  };

  const applyRefactor = async () => {
    try {
      const res = await axios.post(`${API}/refactor/apply`, {
        project_id: projectId, refactor_type: refactorData.type,
        target: refactorData.target, new_value: refactorData.new_value
      });
      toast.success(`Updated ${res.data.files_updated} file(s)`);
      setRefactorDialog(false);
      setRefactorPreview(null);
      setRefactorData({ type: "find_replace", target: "", new_value: "" });
      fetchProjectData();
    } catch (error) { toast.error("Refactor failed"); }
  };

  const extractMemories = async () => {
    try {
      const res = await axios.post(`${API}/memory/auto-extract?project_id=${projectId}`);
      if (res.data.extracted > 0) {
        setMemories([...res.data.memories, ...memories]);
        toast.success(`Extracted ${res.data.extracted} memories`);
      } else { toast.info("No new memories found"); }
    } catch (error) { toast.error("Memory extraction failed"); }
  };

  const deleteMemory = async (id) => {
    await axios.delete(`${API}/memory/${id}`);
    setMemories(memories.filter(m => m.id !== id));
  };

  const duplicateProject = async () => {
    if (!duplicateName) { toast.error("Name required"); return; }
    try {
      const res = await axios.post(`${API}/projects/${projectId}/duplicate`, { project_id: projectId, new_name: duplicateName, include_files: true, include_tasks: false });
      setDuplicateDialog(false);
      toast.success(`Created "${res.data.project.name}" with ${res.data.files} files`);
      navigate(`/project/${res.data.project.id}`);
    } catch (error) { toast.error("Duplication failed"); }
  };

  // GitHub, Image, File operations
  const pushToGithub = async () => {
    if (!githubToken || !githubRepoName) { toast.error("Token and repo required"); return; }
    setPushing(true);
    try {
      const res = await axios.post(`${API}/github/push`, { project_id: projectId, github_token: githubToken, repo_name: githubRepoName, commit_message: `Update from AgentForge - ${new Date().toISOString()}`, create_repo: githubCreateNew });
      setProject({ ...project, repo_url: res.data.repo_url });
      setGithubDialogOpen(false);
      toast.success(`Pushed ${res.data.pushed_files.length} files!`);
    } catch (error) { toast.error(error.response?.data?.detail || "Push failed"); }
    finally { setPushing(false); }
  };

  const generateImage = async () => {
    if (!imagePrompt.trim()) return;
    setGeneratingImage(true);
    try {
      const res = await axios.post(`${API}/images/generate`, { project_id: projectId, prompt: imagePrompt, category: imageCategory });
      setImages([res.data, ...images]); setImagePrompt(""); setImageDialogOpen(false); toast.success("Image generated!");
    } catch (error) { toast.error("Generation failed"); }
    finally { setGeneratingImage(false); }
  };

  const saveFile = async () => {
    if (!selectedFile || !unsavedChanges) return;
    await axios.patch(`${API}/files/${selectedFile.id}`, { content: editorContent });
    setFiles(files.map(f => f.id === selectedFile.id ? { ...f, content: editorContent } : f));
    setSelectedFile({ ...selectedFile, content: editorContent }); setUnsavedChanges(false); toast.success("Saved");
  };

  const exportProject = async () => {
    const response = await axios.get(`${API}/projects/${projectId}/export`, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a'); link.href = url;
    link.setAttribute('download', `${project?.name?.replace(/\s+/g, '_') || 'project'}.zip`);
    document.body.appendChild(link); link.click(); link.remove();
    toast.success("Exported!");
  };

  const loadPreview = async () => {
    if (!['web_app', 'web_game'].includes(project?.type)) return;
    try {
      const res = await axios.get(`${API}/projects/${projectId}/preview-data`);
      let fullHtml = res.data.html[0]?.content || '<html><body><h1>No HTML</h1></body></html>';
      const css = res.data.css.map(f => f.content).join('\n');
      const js = res.data.js.map(f => f.content).join('\n');
      if (!fullHtml.includes('<style>') && css) fullHtml = fullHtml.replace('</head>', `<style>${css}</style></head>`);
      if (!fullHtml.includes('<script>') && js) fullHtml = fullHtml.replace('</body>', `<script>${js}</script></body>`);
      setPreviewHtml(fullHtml);
    } catch (error) {}
  };

  const copyCode = (code, id) => { navigator.clipboard.writeText(code); setCopiedCode(id); setTimeout(() => setCopiedCode(null), 2000); };
  const createTask = async () => { if (!newTask.title.trim()) return; const res = await axios.post(`${API}/tasks`, { ...newTask, project_id: projectId }); setTasks([res.data, ...tasks]); setNewTask({ title: "", description: "", priority: "medium", category: "general" }); setTaskDialogOpen(false); };
  const updateTaskStatus = async (taskId, status) => { await axios.patch(`${API}/tasks/${taskId}`, { status }); setTasks(tasks.map(t => t.id === taskId ? { ...t, status } : t)); };
  const deleteTask = async (taskId) => { await axios.delete(`${API}/tasks/${taskId}`); setTasks(tasks.filter(t => t.id !== taskId)); };
  const deleteFile = async (fileId) => { await axios.delete(`${API}/files/${fileId}`); setFiles(files.filter(f => f.id !== fileId)); if (selectedFile?.id === fileId) { setSelectedFile(null); setEditorContent(""); } };
  const toggleFolder = (path) => { const n = new Set(expandedFolders); n.has(path) ? n.delete(path) : n.add(path); setExpandedFolders(n); };

  // buildFileTree and renderFileTree live in WorkspaceCodeEditor now

  const getAgentIcon = (role) => AGENTS[role]?.icon || Bot;
  const getAgentColor = (role) => AGENTS[role]?.color || "text-zinc-400";
  const getStatusColor = (status) => ({ idle: "bg-zinc-500", thinking: "bg-amber-500 animate-pulse", working: "bg-blue-500 animate-pulse" }[status] || "bg-zinc-500");
  const getPriorityColor = (priority) => ({ critical: "border-l-red-500 bg-red-500/5", high: "border-l-amber-500 bg-amber-500/5", medium: "border-l-blue-500 bg-blue-500/5", low: "border-l-zinc-500 bg-zinc-500/5" }[priority] || "border-l-zinc-500");
  const getWarRoomTypeColor = (type) => ({ discussion: "text-zinc-400", handoff: "text-cyan-400", question: "text-amber-400", decision: "text-emerald-400", warning: "text-red-400", progress: "text-blue-400" }[type] || "text-zinc-400");

  const renderCodeBlock = (block, index, messageId) => {
    const blockId = `${messageId}-${index}`;
    return (<div key={blockId} className="my-3 rounded-lg overflow-hidden border border-zinc-700"><div className="flex items-center justify-between px-3 py-2 bg-zinc-800/50 border-b border-zinc-700"><div className="flex items-center gap-2"><FileCode className="w-4 h-4 text-blue-400" /><span className="text-xs text-zinc-400 font-mono">{block.filepath || block.filename}</span><Badge variant="outline" className="text-[10px] border-zinc-600">{block.language}</Badge></div><div className="flex gap-1"><Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => copyCode(block.content, blockId)}>{copiedCode === blockId ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}</Button>{block.filepath && <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => { const f = files.find(f => f.filepath === block.filepath); if (f) { setSelectedFile(f); setEditorContent(f.content); setRightTab("code"); }}}><FileCode className="w-3 h-3" /></Button>}</div></div><SyntaxHighlighter language={LANGUAGE_MAP[block.language] || block.language} style={vscDarkPlus} customStyle={{ margin: 0, padding: '12px', fontSize: '12px', background: '#0d0d0f', maxHeight: '400px' }} showLineNumbers>{block.content}</SyntaxHighlighter></div>);
  };

  const parseMessageContent = (content, messageId, delegations = []) => {
    const codeBlockRegex = /```(\w+)?(?::([^\n]+))?\n([\s\S]*?)```/g;
    let cleanContent = content.replace(/\[DELEGATE:(\w+)\]([\s\S]*?)\[\/DELEGATE\]/g, '');
    const parts = []; let lastIndex = 0, match, blockIndex = 0;
    while ((match = codeBlockRegex.exec(cleanContent)) !== null) {
      if (match.index > lastIndex) parts.push({ type: 'text', content: cleanContent.slice(lastIndex, match.index) });
      parts.push({ type: 'code', language: match[1] || 'text', filepath: match[2] || '', filename: match[2]?.split('/').pop() || '', content: match[3].trim(), index: blockIndex++ });
      lastIndex = match.index + match[0].length;
    }
    if (lastIndex < cleanContent.length) parts.push({ type: 'text', content: cleanContent.slice(lastIndex) });
    return (<>{parts.map((p, i) => p.type === 'code' ? renderCodeBlock(p, p.index, messageId) : <p key={i} className="whitespace-pre-wrap text-sm text-zinc-200">{p.content}</p>)}{delegations?.length > 0 && delegations.map((d, i) => (<div key={i} className="mt-3 flex items-center gap-2 p-2 rounded bg-blue-500/10 border border-blue-500/30"><ArrowRightCircle className="w-4 h-4 text-blue-400" /><span className="text-xs text-blue-400">Delegated to {d.agent}</span><Button size="sm" className="ml-auto h-6 text-xs bg-blue-500 hover:bg-blue-600" onClick={() => executeDelegation(d.agent, d.task)}>Execute</Button></div>))}</>);
  };

  if (loading) return <div className="min-h-screen bg-[#09090b] flex items-center justify-center"><Loader2 className="w-10 h-10 text-blue-400 animate-spin" /></div>;

  const phaseConfig = PHASE_CONFIG[project?.status === "building" ? "building" : project?.phase] || PHASE_CONFIG.clarification;
  const PhaseIcon = phaseConfig.icon;
  const tasksByStatus = { backlog: tasks.filter(t => t.status === "backlog"), todo: tasks.filter(t => t.status === "todo"), in_progress: tasks.filter(t => t.status === "in_progress"), review: tasks.filter(t => t.status === "review"), done: tasks.filter(t => t.status === "done") };
  const isWebProject = ['web_app', 'web_game'].includes(project?.type);
  const allActions = [...quickActions, ...customActions.map(a => ({ ...a, isCustom: true }))];

  return (
    <div className="h-screen flex flex-col overflow-hidden transition-colors duration-300" style={{ backgroundColor: 'var(--bg-primary)' }}>
      {/* Clean Header with Integrated Tabs */}
      <header className="flex-shrink-0 backdrop-blur-lg border-b z-50 transition-colors duration-300" style={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-color)' }}>
        <div className="px-4 py-2 flex items-center justify-between">
          {/* Left: Back + Project Info */}
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" onClick={() => navigate("/dashboard")} data-testid="back-btn" className="h-8 w-8">
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <div className="border-r pr-3" style={{ borderColor: 'var(--border-color)' }}>
              <h1 className="font-rajdhani text-sm font-bold flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
                {project?.name}
                <Badge className={`${phaseConfig.color} text-[10px]`}>
                  <PhaseIcon className="w-3 h-3 mr-1" />{phaseConfig.label}
                </Badge>
              </h1>
              <p className="text-[11px] flex items-center gap-2" style={{ color: 'var(--text-muted)' }}>
                {project?.type?.replace('_', ' ')}
                {(project?.type === 'unreal' || project?.type === 'unity' || project?.type === 'godot') && (
                  <Select
                    value={project?.engine_version || ''}
                    onValueChange={async (version) => {
                      try {
                        await axios.put(`${API}/projects/${projectId}`, { engine_version: version });
                        setProject({ ...project, engine_version: version });
                        toast.success(`Engine version updated to ${version}`);
                      } catch (e) {
                        toast.error('Failed to update engine version');
                      }
                    }}
                  >
                    <SelectTrigger className="h-5 w-auto min-w-[70px] px-2 text-[10px] bg-transparent border-zinc-700">
                      <SelectValue placeholder="Ver" />
                    </SelectTrigger>
                    <SelectContent className="bg-zinc-900 border-zinc-700">
                      {project?.type === 'unreal' && (
                        <>
                          <SelectItem value="5.7">UE 5.7</SelectItem>
                          <SelectItem value="5.6">UE 5.6</SelectItem>
                          <SelectItem value="5.5">UE 5.5</SelectItem>
                        </>
                      )}
                      {project?.type === 'unity' && (
                        <>
                          <SelectItem value="6000.0 LTS">Unity 6 LTS</SelectItem>
                          <SelectItem value="2023.3 LTS">2023.3 LTS</SelectItem>
                          <SelectItem value="2022.3 LTS">2022.3 LTS</SelectItem>
                        </>
                      )}
                      {project?.type === 'godot' && (
                        <>
                          <SelectItem value="4.3">Godot 4.3</SelectItem>
                          <SelectItem value="4.2">Godot 4.2</SelectItem>
                        </>
                      )}
                    </SelectContent>
                  </Select>
                )}
              </p>
            </div>
            
            {/* Center: Main Tabs */}
            <div className="flex items-center">
              {[
                { id: "chat", icon: MessageSquare, label: "Chat" },
                { id: "tasks", icon: ListTodo, label: "Tasks", badge: tasks.length },
                { id: "warroom", icon: Radio, label: "War Room", badge: warRoomMessages.length },
                { id: "blueprints", icon: GitBranch, label: "Blueprints", badge: blueprints.length },
              ].map(({ id, icon: Icon, label, badge }) => (
                <button
                  key={id}
                  onClick={() => setActiveTab(id)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium transition-all border-b-2 ${
                    activeTab === id 
                      ? 'border-blue-500 text-blue-400' 
                      : 'border-transparent text-zinc-400 hover:text-zinc-200'
                  }`}
                  data-testid={`tab-${id}`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {label}
                  {badge > 0 && (
                    <span className={`ml-1 px-1.5 py-0.5 text-[10px] rounded-full ${
                      activeTab === id ? 'bg-blue-500/20 text-blue-400' : 'bg-zinc-700 text-zinc-400'
                    }`}>
                      {badge}
                    </span>
                  )}
                </button>
              ))}
              
              {/* More dropdown for additional panels */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="flex items-center gap-1 px-3 py-1.5 text-xs text-zinc-400 hover:text-zinc-200 transition-colors">
                    <Menu className="w-3.5 h-3.5" />
                    More
                    <ChevronDown className="w-3 h-3" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-48" style={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-color)' }}>
                  {Object.entries(PANEL_GROUPS).filter(([key]) => !['core'].includes(key)).map(([groupKey, group]) => (
                    <div key={groupKey}>
                      <DropdownMenuLabel className="text-[10px] flex items-center gap-1.5" style={{ color: 'var(--text-muted)' }}>
                        <group.icon className="w-3 h-3" />
                        {group.label}
                      </DropdownMenuLabel>
                      {group.panels.map((panel) => (
                        <DropdownMenuItem
                          key={panel.id}
                          onClick={() => setActiveTab(panel.id)}
                          className="text-xs cursor-pointer"
                          style={{ color: activeTab === panel.id ? 'var(--accent)' : 'var(--text-secondary)' }}
                        >
                          <panel.icon className="w-3.5 h-3.5 mr-2" />
                          {panel.label}
                        </DropdownMenuItem>
                      ))}
                      <DropdownMenuSeparator style={{ backgroundColor: 'var(--border-color)' }} />
                    </div>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
          
          {/* Right: Actions */}
          <div className="flex items-center gap-2">
            <Button 
              variant="outline" 
              size="sm" 
              className="h-7 text-xs border-amber-500/30 text-amber-400 hover:bg-amber-500/10"
              onClick={() => navigate(`/project/${projectId}/god-mode`)}
              data-testid="god-mode-btn"
            >
              <Zap className="w-3.5 h-3.5 mr-1" />
              God Mode
            </Button>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="h-7 text-xs border-zinc-700">
                  <Settings className="w-3.5 h-3.5" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="bg-zinc-900 border-zinc-700" align="end">
                <DropdownMenuItem onClick={() => setSimulationDialog(true)}>
                  <Radio className="w-4 h-4 mr-2 text-cyan-400" />
                  Simulate Build
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setMemoryDialog(true)}>
                  <Brain className="w-4 h-4 mr-2 text-purple-400" />
                  View Memories
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setGithubDialogOpen(true)}>
                  <Github className="w-4 h-4 mr-2" />
                  Push to GitHub
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setImageDialogOpen(true)}>
                  <Image className="w-4 h-4 mr-2" />
                  Generate Asset
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setRefactorDialog(true)}>
                  <Search className="w-4 h-4 mr-2 text-orange-400" />
                  Find & Replace
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setDuplicateDialog(true)}>
                  <CopyPlus className="w-4 h-4 mr-2 text-blue-400" />
                  Duplicate Project
                </DropdownMenuItem>
                <DropdownMenuSeparator className="bg-zinc-700" />
                <DropdownMenuItem onClick={exportProject}>
                  <Download className="w-4 h-4 mr-2" />
                  Export Project
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      {/* Dialogs — extracted to WorkspaceDialogs component (rendered hidden, opened via dropdowns) */}
      <div style={{ display: 'contents' }}>
        <WorkspaceDialogs
          simulationDialog={simulationDialog} setSimulationDialog={setSimulationDialog}
          openWorldSystems={openWorldSystems} targetEngine={targetEngine} setTargetEngine={setTargetEngine}
          selectedSystems={selectedSystems} toggleSystem={toggleSystem} simulating={simulating}
          simulationResult={simulationResult} runSimulation={runSimulation}
          scheduleBuild={scheduleBuild} setScheduleBuild={setScheduleBuild}
          scheduleTime={scheduleTime} setScheduleTime={setScheduleTime}
          buildRunning={buildRunning} startAutonomousBuild={startAutonomousBuild}
          currentBuild={currentBuild} startScheduledBuildNow={startScheduledBuildNow}
          cancelBuild={cancelBuild} pauseBuild={pauseBuild}
          demoDialogOpen={demoDialogOpen} setDemoDialogOpen={setDemoDialogOpen}
          currentDemo={currentDemo} openWebDemo={openWebDemo} files={files}
          setRightTab={setRightTab} setSelectedFile={setSelectedFile} setEditorContent={setEditorContent}
          regenerateDemo={regenerateDemo} regeneratingDemo={regeneratingDemo}
          githubDialogOpen={githubDialogOpen} setGithubDialogOpen={setGithubDialogOpen}
          githubToken={githubToken} setGithubToken={setGithubToken}
          githubRepoName={githubRepoName} setGithubRepoName={setGithubRepoName}
          githubCreateNew={githubCreateNew} setGithubCreateNew={setGithubCreateNew}
          pushing={pushing} pushToGithub={pushToGithub} projectRepoUrl={project?.repo_url}
          imageDialogOpen={imageDialogOpen} setImageDialogOpen={setImageDialogOpen}
          imagePrompt={imagePrompt} setImagePrompt={setImagePrompt}
          imageCategory={imageCategory} setImageCategory={setImageCategory}
          generatingImage={generatingImage} generateImage={generateImage}
          memoryDialog={memoryDialog} setMemoryDialog={setMemoryDialog}
          memories={memories} extractMemories={extractMemories} deleteMemory={deleteMemory}
          duplicateDialog={duplicateDialog} setDuplicateDialog={setDuplicateDialog}
          duplicateName={duplicateName} setDuplicateName={setDuplicateName} duplicateProject={duplicateProject}
          refactorDialog={refactorDialog} setRefactorDialog={setRefactorDialog}
          refactorData={refactorData} setRefactorData={setRefactorData}
          refactorPreview={refactorPreview} setRefactorPreview={setRefactorPreview}
          previewRefactor={previewRefactor} applyRefactor={applyRefactor}
        />
      </div>

      {/* Main - Fully Resizable Layout */}
      <div className="flex-1 overflow-hidden min-h-0">
        <ResizablePanelGroup direction="horizontal">
          {/* Left Side - Quick Actions + Content */}
          <ResizablePanel defaultSize={55} minSize={30} maxSize={80}>
            <ResizablePanelGroup direction="vertical">
              {/* Quick Actions Panel - Resizable */}
              <ResizablePanel 
                defaultSize={showQuickActions ? 25 : 5} 
                minSize={5} 
                maxSize={50}
                collapsible={true}
                collapsedSize={5}
              >
                <div className="h-full flex flex-col border-b overflow-hidden" style={{ borderColor: 'var(--border-color)', backgroundColor: 'var(--bg-primary)' }}>
                  {showQuickActions ? (
                    <div className="p-3 h-full overflow-auto">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold text-sm flex items-center gap-2" style={{ color: 'var(--text-secondary)' }}>
                          <Sparkles className="w-4 h-4 text-blue-400" />
                          Quick Actions
                        </h3>
                        <div className="flex items-center gap-2">
                          <Dialog open={customActionDialog} onOpenChange={setCustomActionDialog}>
                            <DialogTrigger asChild><Button variant="ghost" size="sm" className="h-7 text-xs"><Plus className="w-3 h-3 mr-1" />Custom</Button></DialogTrigger>
                            <DialogContent className="border" style={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-color)' }}>
                              <DialogHeader><DialogTitle style={{ color: 'var(--text-primary)' }}>Create Custom Action</DialogTitle></DialogHeader>
                              <div className="space-y-3 py-4">
                                <Input placeholder="Action name" value={newCustomAction.name} onChange={(e) => setNewCustomAction({ ...newCustomAction, name: e.target.value })} className="border" style={{ backgroundColor: 'var(--bg-tertiary)', borderColor: 'var(--border-color)' }} />
                                <Input placeholder="Description" value={newCustomAction.description} onChange={(e) => setNewCustomAction({ ...newCustomAction, description: e.target.value })} className="border" style={{ backgroundColor: 'var(--bg-tertiary)', borderColor: 'var(--border-color)' }} />
                                <Textarea placeholder="Prompt template" value={newCustomAction.prompt} onChange={(e) => setNewCustomAction({ ...newCustomAction, prompt: e.target.value })} className="border min-h-[100px]" style={{ backgroundColor: 'var(--bg-tertiary)', borderColor: 'var(--border-color)' }} />
                              </div>
                              <DialogFooter><Button onClick={createCustomAction} className="bg-blue-500 hover:bg-blue-600">Create</Button></DialogFooter>
                            </DialogContent>
                          </Dialog>
                          <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={() => setShowQuickActions(false)}>
                            <ChevronUp className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                      <div className="grid grid-cols-4 gap-2">
                        {allActions.slice(0, 8).map((action) => {
                          const Icon = QUICK_ACTION_ICONS[action.icon] || Sparkles;
                          return (
                            <TooltipProvider key={action.id}><Tooltip><TooltipTrigger asChild>
                              <button onClick={() => executeQuickAction(action.id, action.isCustom)} disabled={sending}
                                className={`flex flex-col items-center gap-1 p-2 rounded-lg border transition-all text-center disabled:opacity-50 ${action.isCustom ? 'bg-purple-500/10 border-purple-500/30 hover:border-purple-500/50' : 'bg-zinc-800/50 border-zinc-700 hover:border-blue-500/50'}`}>
                                <Icon className={`w-5 h-5 ${action.isCustom ? 'text-purple-400' : 'text-blue-400'}`} />
                                <span className="text-[10px] text-zinc-400 line-clamp-1">{action.name}</span>
                              </button>
                            </TooltipTrigger><TooltipContent><p className="text-xs">{action.description}</p></TooltipContent></Tooltip></TooltipProvider>
                          );
                        })}
                      </div>
                    </div>
                  ) : (
                    <Button variant="ghost" size="sm" className="m-2 text-xs border border-zinc-700 text-zinc-400 hover:bg-zinc-800" onClick={() => setShowQuickActions(true)}>
                      <Sparkles className="w-4 h-4 mr-1" />Quick Actions
                      <ChevronDown className="w-3 h-3 ml-1" />
                    </Button>
                  )}
                </div>
              </ResizablePanel>
              
              <ResizableHandle withHandle className="bg-zinc-800 hover:bg-blue-500/50 transition-colors" />
              
              {/* Main Content Panel - Resizable */}
              <ResizablePanel defaultSize={75} minSize={30}>
                <div className="h-full flex flex-col overflow-hidden" style={{ backgroundColor: 'var(--bg-primary)' }}>
                  {chainProgress && <div className="px-4 py-2 border-b flex-shrink-0" style={{ backgroundColor: 'color-mix(in srgb, var(--accent) 10%, transparent)', borderColor: 'color-mix(in srgb, var(--accent) 30%, transparent)' }}><div className="flex items-center gap-2"><Loader2 className="w-4 h-4 animate-spin" style={{ color: 'var(--accent)' }} /><span className="text-xs" style={{ color: 'var(--accent)' }}>Step {chainProgress.step}/{chainProgress.total}: {chainProgress.agent}</span></div></div>}

                  {/* Pipeline progress bar — shows for both server-side and browser-side runs */}
                  {Object.keys(pipelineAgentStatus).length > 0 && (
                    <div className="px-4 py-2 border-b flex-shrink-0 bg-zinc-900/80">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-[10px] text-zinc-500 mr-1">
                          {activePipelineId ? 'Server pipeline:' : 'Parallel:'}
                        </span>
                        {pipelineRunStatus && activePipelineId && (
                          <span className="text-[10px] text-zinc-600 mr-1">
                            {pipelineRunStatus.completed_agents || 0}/{pipelineRunStatus.total_agents || 0}
                          </span>
                        )}
                        {Object.entries(pipelineAgentStatus).map(([agent, status]) => (
                          <div key={agent} className={`flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium transition-all ${
                            status === 'done'    ? 'bg-emerald-500/20 text-emerald-400' :
                            status === 'working' ? 'bg-blue-500/20 text-blue-400' :
                            status === 'error'   ? 'bg-red-500/20 text-red-400' :
                                                  'bg-zinc-800 text-zinc-500'
                          }`}>
                            {status === 'done'    && <Check className="w-2.5 h-2.5" />}
                            {status === 'working' && <Loader2 className="w-2.5 h-2.5 animate-spin" />}
                            {status === 'error'   && <span>✕</span>}
                            {agent}
                          </div>
                        ))}
                        {/* Cancel button — only for server-side runs */}
                        {activePipelineId && (
                          <button
                            onClick={cancelPipeline}
                            className="ml-auto px-2 py-0.5 rounded text-[10px] font-medium bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors"
                            data-testid="cancel-pipeline-btn"
                          >
                            ✕ Cancel
                          </button>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="flex-1 flex flex-col overflow-hidden">

                {/* Chat Panel - When active */}
                {activeTab === "chat" && (
                  <WorkspaceChatPanel
                    messages={messages}
                    streamingContent={streamingContent}
                    streamingAgent={streamingAgent}
                    sending={sending}
                    agents={agents}
                    project={project}
                    selectedAgent={selectedAgent}
                    chatInput={chatInput}
                    attachedFiles={attachedFiles}
                    chatEndRef={chatEndRef}
                    onSendMessage={sendMessageStreaming}
                    onSetAttachedFiles={setAttachedFiles}
                    onSetChatInput={setChatInput}
                    onClearSelectedAgent={() => setSelectedAgent(null)}
                    parseContent={parseMessageContent}
                  />
                )}

                {/* Other tabs - Using conditional rendering */}
                {activeTab === "warroom" && (
                  <div className="flex-1 flex flex-col overflow-hidden">
                    <WarRoomPanel
                      messages={warRoomMessages}
                      currentBuild={currentBuild}
                      onSimulate={() => setSimulationDialog(true)}
                      onPause={pauseBuild}
                      onResume={resumeBuild}
                      onCancel={cancelBuild}
                    />
                  </div>
                )}

                {/* Blueprints Tab */}
                {activeTab === "blueprints" && (
                  <div className="flex-1 flex flex-col overflow-hidden">
                    <div className="flex-shrink-0 p-3 border-b border-zinc-800 flex items-center justify-between">
                      <h3 className="font-rajdhani font-bold text-white text-sm flex items-center gap-2">
                        <GitBranch className="w-4 h-4 text-purple-400" />Visual Blueprints
                      </h3>
                      <div className="flex items-center gap-2">
                        <Select value={selectedBlueprint?.id || ""} onValueChange={(v) => setSelectedBlueprint(blueprints.find(b => b.id === v))}>
                          <SelectTrigger className="w-40 h-8 bg-zinc-900 border-zinc-700 text-xs">
                            <SelectValue placeholder="Select blueprint" />
                          </SelectTrigger>
                          <SelectContent className="bg-zinc-900 border-zinc-700">
                            {blueprints.map(bp => (
                              <SelectItem key={bp.id} value={bp.id}>{bp.name}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <Button size="sm" className="h-8 bg-purple-500 hover:bg-purple-600" onClick={() => {
                          const name = prompt("Blueprint name:");
                          if (name) createBlueprint(name);
                        }}>
                          <Plus className="w-3 h-3 mr-1" />New
                        </Button>
                      </div>
                    </div>
                    {selectedBlueprint ? (
                    <BlueprintEditor
                      blueprint={selectedBlueprint}
                      templates={blueprintTemplates}
                      onUpdate={updateBlueprint}
                      onGenerateCode={generateCodeFromBlueprint}
                      onSyncFromCode={syncBlueprintFromCode}
                    />
                  ) : (
                    <div className="flex-1 flex items-center justify-center">
                      <div className="text-center">
                        <GitBranch className="w-16 h-16 mx-auto mb-4 text-zinc-700" />
                        <h3 className="font-rajdhani text-lg text-white mb-2">No Blueprint Selected</h3>
                        <p className="text-sm text-zinc-500 mb-4">Create or select a blueprint to start visual scripting</p>
                        <Button className="bg-purple-500 hover:bg-purple-600" onClick={() => {
                          const name = prompt("Blueprint name:");
                          if (name) createBlueprint(name);
                        }}>
                          <Plus className="w-4 h-4 mr-2" />Create Blueprint
                        </Button>
                      </div>
                    </div>
                  )}
                  </div>
                )}

                {/* Other Tabs - Use Tabs wrapper */}
                {!["chat", "warroom", "blueprints"].includes(activeTab) && (
                <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col overflow-hidden">

                {/* Build Queue Tab */}
                <TabsContent value="queue" className="flex-1 m-0 overflow-hidden">
                  <BuildQueuePanel 
                    projectId={projectId} 
                    onBuildStart={(buildId) => { fetchCurrentBuild(); setActiveTab("warroom"); }}
                  />
                </TabsContent>

                {/* Collaboration Tab */}
                <TabsContent value="collab" className="flex-1 m-0 overflow-hidden">
                  <CollaborationPanel
                    projectId={projectId}
                    currentUser={currentUser}
                    activeFileId={selectedFile?.id}
                    onFileSelect={(fileId) => {
                      const file = files.find(f => f.id === fileId);
                      if (file) { setSelectedFile(file); setEditorContent(file.content); }
                    }}
                  />
                </TabsContent>

                {/* Tasks Tab */}
                <TabsContent value="tasks" className="flex-1 m-0 overflow-hidden flex flex-col">
                  <div className="flex-shrink-0 p-3 border-b border-zinc-800 flex items-center justify-between"><h3 className="font-rajdhani font-bold text-white text-sm">Task Board</h3><Dialog open={taskDialogOpen} onOpenChange={setTaskDialogOpen}><DialogTrigger asChild><Button size="sm" className="bg-blue-500 hover:bg-blue-600 h-8"><Plus className="w-3 h-3 mr-1" />Add</Button></DialogTrigger><DialogContent className="bg-[#18181b] border-zinc-700"><DialogHeader><DialogTitle className="font-rajdhani text-white">New Task</DialogTitle></DialogHeader><div className="space-y-3 py-4"><Input placeholder="Title" value={newTask.title} onChange={(e) => setNewTask({ ...newTask, title: e.target.value })} className="bg-zinc-900 border-zinc-700" /><Textarea placeholder="Description" value={newTask.description} onChange={(e) => setNewTask({ ...newTask, description: e.target.value })} className="bg-zinc-900 border-zinc-700" /><div className="grid grid-cols-2 gap-3"><Select value={newTask.priority} onValueChange={(v) => setNewTask({ ...newTask, priority: v })}><SelectTrigger className="bg-zinc-900 border-zinc-700"><SelectValue /></SelectTrigger><SelectContent className="bg-zinc-900 border-zinc-700"><SelectItem value="low">Low</SelectItem><SelectItem value="medium">Medium</SelectItem><SelectItem value="high">High</SelectItem><SelectItem value="critical">Critical</SelectItem></SelectContent></Select><Select value={newTask.category} onValueChange={(v) => setNewTask({ ...newTask, category: v })}><SelectTrigger className="bg-zinc-900 border-zinc-700"><SelectValue /></SelectTrigger><SelectContent className="bg-zinc-900 border-zinc-700"><SelectItem value="general">General</SelectItem><SelectItem value="architecture">Architecture</SelectItem><SelectItem value="coding">Coding</SelectItem><SelectItem value="assets">Assets</SelectItem><SelectItem value="testing">Testing</SelectItem></SelectContent></Select></div></div><DialogFooter><Button onClick={createTask} className="bg-blue-500 hover:bg-blue-600">Create</Button></DialogFooter></DialogContent></Dialog></div>
                  <ScrollArea className="flex-1"><div className="p-3 flex gap-3 min-w-max">{Object.entries(tasksByStatus).map(([status, statusTasks]) => (<div key={status} className="w-56 flex-shrink-0 bg-zinc-900/50 rounded-lg border border-zinc-800"><div className="p-2 border-b border-zinc-800"><h4 className="font-rajdhani font-bold text-xs text-white uppercase">{status.replace('_', ' ')}</h4><span className="text-xs text-zinc-500">{statusTasks.length}</span></div><div className="p-2 space-y-2 min-h-[200px]">{statusTasks.map((task) => (<div key={task.id} className={`p-2 rounded bg-zinc-800/50 border-l-2 ${getPriorityColor(task.priority)} text-xs`}><h5 className="text-white font-medium line-clamp-2 mb-1">{task.title}</h5>{task.description && <p className="text-zinc-500 line-clamp-2 mb-2">{task.description}</p>}<div className="flex items-center justify-between"><Select value={task.status} onValueChange={(v) => updateTaskStatus(task.id, v)}><SelectTrigger className="h-6 w-20 text-[10px] bg-transparent border-zinc-700"><SelectValue /></SelectTrigger><SelectContent className="bg-zinc-900 border-zinc-700"><SelectItem value="backlog">Backlog</SelectItem><SelectItem value="todo">To Do</SelectItem><SelectItem value="in_progress">In Progress</SelectItem><SelectItem value="review">Review</SelectItem><SelectItem value="done">Done</SelectItem></SelectContent></Select><Button variant="ghost" size="icon" className="h-5 w-5" onClick={() => deleteTask(task.id)}><Trash2 className="w-3 h-3 text-red-400" /></Button></div></div>))}</div></div>))}</div></ScrollArea>
                </TabsContent>

                {/* Images Tab */}
                <TabsContent value="images" className="flex-1 m-0 p-4 overflow-auto">{images.length === 0 ? (<div className="text-center py-12"><Image className="w-12 h-12 mx-auto mb-4 text-zinc-700" /><h3 className="font-rajdhani text-lg text-white mb-2">No Images</h3><Button onClick={() => setImageDialogOpen(true)} className="bg-blue-500 hover:bg-blue-600"><Sparkles className="w-4 h-4 mr-2" />Generate</Button></div>) : (<div className="grid grid-cols-2 gap-4">{images.map((img) => (<div key={img.id} className="rounded-lg overflow-hidden border border-zinc-800"><img src={img.url} alt={img.prompt} className="w-full aspect-square object-cover" /><div className="p-3 bg-zinc-900"><Badge variant="outline" className="text-xs border-zinc-700 mb-2">{img.category}</Badge><p className="text-xs text-zinc-400 line-clamp-2">{img.prompt}</p></div></div>))}</div>)}</TabsContent>

                {/* Audio Tab */}
                <TabsContent value="audio" className="flex-1 m-0 overflow-hidden">
                  <AudioGeneratorPanel projectId={projectId} />
                </TabsContent>

                {/* Assets Tab */}
                <TabsContent value="assets" className="flex-1 m-0 overflow-hidden">
                  <AssetPipelinePanel projectId={projectId} />
                </TabsContent>

                {/* Sandbox Tab */}
                <TabsContent value="sandbox" className="flex-1 m-0 overflow-hidden">
                  <SandboxPanel projectId={projectId} />
                </TabsContent>

                {/* Command Center Tab */}
                <TabsContent value="command" className="flex-1 m-0 overflow-hidden">
                  <CommandCenter projectId={projectId} projectName={project?.name} onNavigate={(path) => window.location.href = path} />
                </TabsContent>

                {/* Deploy Tab */}
                <TabsContent value="deploy" className="flex-1 m-0 overflow-hidden">
                  <DeploymentPanel projectId={projectId} projectName={project?.name} />
                </TabsContent>

                {/* Notifications Tab */}
                <TabsContent value="notifications" className="flex-1 m-0 overflow-hidden">
                  <NotificationsPanel projectId={projectId} />
                </TabsContent>

                <TabsContent value="game-engine" className="flex-1 m-0 overflow-hidden">
                  <GameEnginePanel />
                </TabsContent>

                <TabsContent value="hardware" className="flex-1 m-0 overflow-hidden">
                  <HardwarePanel />
                </TabsContent>

                <TabsContent value="research" className="flex-1 m-0 overflow-hidden">
                  <ResearchPanel />
                </TabsContent>
              </Tabs>
              )}
                  </div>
                </div>
              </ResizablePanel>
            </ResizablePanelGroup>
          </ResizablePanel>

          <ResizableHandle withHandle className="bg-zinc-800 hover:bg-blue-500/50 transition-colors" />

          {/* Right Panel - Files/Code */}
          <ResizablePanel defaultSize={45} minSize={25} maxSize={70}>
            <WorkspaceCodeEditor
              files={files}
              selectedFile={selectedFile}
              editorContent={editorContent}
              unsavedChanges={unsavedChanges}
              rightTab={rightTab}
              previewHtml={previewHtml}
              isWebProject={isWebProject}
              expandedFolders={expandedFolders}
              onFileSelect={(f) => { setSelectedFile(f); setEditorContent(f.content); setUnsavedChanges(false); }}
              onEditorChange={(v) => { setEditorContent(v); setUnsavedChanges(v !== selectedFile?.content); }}
              onSave={saveFile}
              onDeleteFile={deleteFile}
              onLoadPreview={loadPreview}
              setRightTab={setRightTab}
              toggleFolder={toggleFolder}
            />
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </div>
  );
};

export default ProjectWorkspace;
