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
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable";
import { Progress } from "@/components/ui/progress";
import { Checkbox } from "@/components/ui/checkbox";
import { 
  ArrowLeft, Send, Bot, Code2, Layers, Users, Shield, Zap, Plus, Loader2, FileCode, ListTodo, MessageSquare,
  Folder, FolderOpen, ChevronRight, ChevronDown, Save, Download, Trash2, Palette, Copy, Check, X, Image,
  Sparkles, ArrowRightCircle, Github, Play, Eye, Gamepad2, Package, Heart, Volume2, Layout, MessageCircle,
  Rocket, ChevronUp, RefreshCw, Brain, Wand2, CopyPlus, Search, Replace, Radio, AlertTriangle, Clock,
  Pause, Square, SkipForward, Swords, Mountain, Car, Sun, Map, Hammer, Coins, Ghost, Timer, Camera, Wifi,
  Joystick, Monitor, Globe, GitBranch, Calendar, Bell, Music, Terminal, Command, FlaskConical, Cpu, Mic
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
import LabsPanel from "@/components/LabsPanel";
import OSFeaturesPanel from "@/components/OSFeaturesPanel";
import VoiceControlPanel from "@/components/VoiceControlPanel";

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

const SYSTEM_ICONS = {
  terrain: Mountain, npc_population: Users, quest_system: Map, vehicle_system: Car,
  day_night_cycle: Sun, combat_system: Swords, crafting_system: Hammer, economy_system: Coins,
  stealth_system: Ghost, mount_system: Gamepad2, building_system: Layers, skill_tree: Sparkles,
  fast_travel: Timer, photo_mode: Camera, multiplayer: Wifi
};

const ProjectWorkspace = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const chatEndRef = useRef(null);
  const warRoomEndRef = useRef(null);
  
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
  const [buildDialog, setBuildDialog] = useState(false);
  const [buildRunning, setBuildRunning] = useState(false);
  const [scheduleBuild, setScheduleBuild] = useState(false);
  const [scheduleTime, setScheduleTime] = useState("");

  // v3.3 states - Blueprints, Queue, Collaboration
  const [blueprints, setBlueprints] = useState([]);
  const [selectedBlueprint, setSelectedBlueprint] = useState(null);
  const [blueprintTemplates, setBlueprintTemplates] = useState({});
  const [currentUser] = useState({ id: `user_${Date.now()}`, username: "Developer" }); // Mock user for collab

  useEffect(() => { fetchProjectData(); }, [projectId]);
  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, streamingContent]);
  useEffect(() => { warRoomEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [warRoomMessages]);
  
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

  const fetchProjectData = async () => {
    try {
      const [projectRes, agentsRes, messagesRes, tasksRes, filesRes, imagesRes, actionsRes, customRes, memRes, systemsRes] = await Promise.all([
        axios.get(`${API}/projects/${projectId}`),
        axios.get(`${API}/agents`),
        axios.get(`${API}/messages?project_id=${projectId}`),
        axios.get(`${API}/tasks?project_id=${projectId}`),
        axios.get(`${API}/files?project_id=${projectId}`),
        axios.get(`${API}/images?project_id=${projectId}`).catch(() => ({ data: [] })),
        axios.get(`${API}/quick-actions`).catch(() => ({ data: [] })),
        axios.get(`${API}/custom-actions?project_id=${projectId}`).catch(() => ({ data: [] })),
        axios.get(`${API}/memory?project_id=${projectId}`).catch(() => ({ data: [] })),
        axios.get(`${API}/refactor/systems/open-world`).catch(() => ({ data: [] }))
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
      setOpenWorldSystems(Object.entries(systemsRes.data).map(([id, system]) => ({ id, ...system })));
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
    } catch (error) {
      toast.error("Failed to load project");
      navigate("/dashboard");
    } finally {
      setLoading(false);
    }
  };

  const fetchWarRoom = async () => {
    try {
      const res = await axios.get(`${API}/war-room/${projectId}/messages`);
      setWarRoomMessages(res.data);
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
      const res = await axios.get(`${API}/builds/${projectId}/latest`);
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
    const userMessage = chatInput;
    setChatInput("");
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
                if (data.code_blocks?.length > 0) await saveCodeBlocks(data.code_blocks, currentAgent);
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

  const executeDelegation = async (agentName, task) => {
    try {
      const res = await axios.post(`${API}/delegate`, { project_id: projectId, message: task, delegate_to: agentName });
      setMessages(prev => [...prev, { id: `delegate-${Date.now()}`, project_id: projectId, agent_id: res.data.agent.id, agent_name: res.data.agent.name, agent_role: res.data.agent.role, content: res.data.response, code_blocks: res.data.code_blocks || [], timestamp: new Date().toISOString() }]);
      if (res.data.code_blocks?.length > 0) await saveCodeBlocks(res.data.code_blocks, res.data.agent);
      toast.success(`${agentName} completed`);
    } catch (error) { toast.error(`Delegation failed`); }
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
      setBuildDialog(false);
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
    if (!refactorData.target) { toast.error("Target required"); return; }
    try {
      const res = await axios.post(`${API}/refactor/preview`, { project_id: projectId, refactor_type: refactorData.type, target: refactorData.target, new_value: refactorData.new_value });
      setRefactorPreview(res.data);
    } catch (error) { toast.error("Preview failed"); }
  };

  const applyRefactor = async () => {
    try {
      const res = await axios.post(`${API}/refactor/apply`, { project_id: projectId, refactor_type: refactorData.type, target: refactorData.target, new_value: refactorData.new_value });
      toast.success(`Refactored ${res.data.files_updated} files`);
      setRefactorDialog(false);
      setRefactorPreview(null);
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

  const buildFileTree = () => { const tree = {}; files.forEach(f => { const parts = f.filepath.split('/').filter(Boolean); let cur = tree; parts.forEach((p, i) => { if (i === parts.length - 1) cur[p] = f; else { if (!cur[p]) cur[p] = {}; cur = cur[p]; }}); }); return tree; };

  const renderFileTree = (node, path = "", depth = 0) => Object.entries(node).map(([name, value]) => {
    const fullPath = path ? `${path}/${name}` : name;
    const isFile = value?.id;
    if (isFile) return (<div key={value.id} className={`flex items-center gap-2 px-2 py-1.5 cursor-pointer hover:bg-zinc-800 rounded text-sm group ${selectedFile?.id === value.id ? 'bg-blue-500/20 text-blue-400' : 'text-zinc-400'}`} style={{ paddingLeft: `${depth * 12 + 8}px` }} onClick={() => { setSelectedFile(value); setEditorContent(value.content); setUnsavedChanges(false); }}><FileCode className="w-4 h-4" /><span className="truncate flex-1">{name}</span><Button variant="ghost" size="icon" className="h-6 w-6 opacity-0 group-hover:opacity-100" onClick={(e) => { e.stopPropagation(); deleteFile(value.id); }}><Trash2 className="w-3 h-3 text-red-400" /></Button></div>);
    return (<div key={fullPath}><div className="flex items-center gap-2 px-2 py-1.5 cursor-pointer hover:bg-zinc-800 rounded text-sm text-zinc-300" style={{ paddingLeft: `${depth * 12 + 8}px` }} onClick={() => toggleFolder(fullPath)}>{expandedFolders.has(fullPath) ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}{expandedFolders.has(fullPath) ? <FolderOpen className="w-4 h-4 text-amber-400" /> : <Folder className="w-4 h-4 text-amber-400" />}<span>{name}</span></div>{expandedFolders.has(fullPath) && renderFileTree(value, fullPath, depth + 1)}</div>);
  });

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
    <div className="h-screen bg-[#09090b] flex flex-col overflow-hidden">
      {/* Header */}
      <header className="flex-shrink-0 bg-[#0d0d0f]/95 backdrop-blur-lg border-b border-zinc-800 z-50">
        <div className="px-4 py-2 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate("/dashboard")} data-testid="back-btn"><ArrowLeft className="w-5 h-5" /></Button>
            <div>
              <h1 className="font-rajdhani text-lg font-bold text-white flex items-center gap-2">{project?.name}<Badge className={`${phaseConfig.color} text-xs`}><PhaseIcon className="w-3 h-3 mr-1" />{phaseConfig.label}</Badge>{project?.repo_url && <a href={project.repo_url} target="_blank" rel="noopener noreferrer"><Badge className="bg-zinc-800 text-zinc-400 hover:bg-zinc-700"><Github className="w-3 h-3 mr-1" />GitHub</Badge></a>}</h1>
              <p className="text-xs text-zinc-500">{project?.type?.replace('_', ' ')} {project?.engine_version && `• ${project.engine_version}`}</p>
            </div>
          </div>
          
          <div className="hidden lg:flex items-center gap-2">
            {agents.map((agent) => {
              const AgentIcon = getAgentIcon(agent.role);
              return (<button key={agent.id} className={`flex items-center gap-2 px-3 py-1.5 rounded-full border transition-all ${selectedAgent === agent.id ? 'bg-blue-500/20 border-blue-500/50 text-blue-400' : 'bg-zinc-800/50 border-zinc-700 text-zinc-400 hover:border-zinc-600'}`} onClick={() => setSelectedAgent(selectedAgent === agent.id ? null : agent.id)}><div className={`w-2 h-2 rounded-full ${getStatusColor(agent.status)}`} /><AgentIcon className="w-3.5 h-3.5" /><span className="text-xs font-medium">{agent.name}</span></button>);
            })}
          </div>

          <div className="flex items-center gap-2">
            {/* Simulation Mode Button */}
            <Dialog open={simulationDialog} onOpenChange={setSimulationDialog}>
              <DialogTrigger asChild><Button variant="outline" size="sm" className="border-cyan-700 text-cyan-400 hover:bg-cyan-500/10" data-testid="simulation-btn"><Radio className="w-4 h-4 mr-1" />Simulate</Button></DialogTrigger>
              <DialogContent className="bg-[#18181b] border-zinc-700 max-w-3xl max-h-[90vh] overflow-y-auto">
                <DialogHeader><DialogTitle className="font-rajdhani text-white flex items-center gap-2"><Radio className="w-5 h-5 text-cyan-400" />Build Simulation (Dry Run)</DialogTitle></DialogHeader>
                <div className="py-4 space-y-4">
                  {/* Engine Selection */}
                  <div className="flex gap-4">
                    <Button variant={targetEngine === "unreal" ? "default" : "outline"} className={targetEngine === "unreal" ? "bg-blue-500" : "border-zinc-700"} onClick={() => setTargetEngine("unreal")}>Unreal Engine 5</Button>
                    <Button variant={targetEngine === "unity" ? "default" : "outline"} className={targetEngine === "unity" ? "bg-blue-500" : "border-zinc-700"} onClick={() => setTargetEngine("unity")}>Unity</Button>
                  </div>

                  {/* System Selection */}
                  <div>
                    <h4 className="text-sm font-medium text-white mb-3">Select Game Systems</h4>
                    <div className="grid grid-cols-3 gap-2">
                      {openWorldSystems.map((system) => {
                        const Icon = SYSTEM_ICONS[system.id] || Sparkles;
                        const isSelected = selectedSystems.includes(system.id);
                        return (
                          <button key={system.id} onClick={() => toggleSystem(system.id)}
                            className={`p-3 rounded-lg border text-left transition-all ${isSelected ? 'bg-cyan-500/20 border-cyan-500/50' : 'bg-zinc-900 border-zinc-700 hover:border-zinc-600'}`}>
                            <div className="flex items-center gap-2 mb-1">
                              <Icon className={`w-4 h-4 ${isSelected ? 'text-cyan-400' : 'text-zinc-500'}`} />
                              <span className={`text-sm font-medium ${isSelected ? 'text-cyan-400' : 'text-zinc-300'}`}>{system.name}</span>
                            </div>
                            <p className="text-[10px] text-zinc-500 line-clamp-1">{system.description}</p>
                            <div className="flex gap-2 mt-2 text-[10px] text-zinc-600">
                              <span>{system.files_estimate} files</span>
                              <span>~{system.time_estimate_minutes}m</span>
                            </div>
                          </button>
                        );
                      })}
                    </div>
                    <p className="text-xs text-zinc-500 mt-2">{selectedSystems.length} systems selected</p>
                  </div>

                  {/* Run Simulation Button */}
                  <Button onClick={runSimulation} disabled={simulating || selectedSystems.length === 0} className="w-full bg-cyan-500 hover:bg-cyan-600">
                    {simulating ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Simulating...</> : <><Radio className="w-4 h-4 mr-2" />Run Simulation</>}
                  </Button>

                  {/* Simulation Results */}
                  {simulationResult && (
                    <div className="space-y-4 border-t border-zinc-700 pt-4">
                      <h4 className="font-rajdhani font-bold text-white">Simulation Results</h4>
                      
                      {/* Stats Grid */}
                      <div className="grid grid-cols-4 gap-3">
                        <div className="p-3 rounded bg-zinc-900 border border-zinc-800">
                          <Clock className="w-5 h-5 text-blue-400 mb-1" />
                          <p className="text-lg font-bold text-white">{simulationResult.estimated_build_time}</p>
                          <p className="text-[10px] text-zinc-500">Build Time</p>
                        </div>
                        <div className="p-3 rounded bg-zinc-900 border border-zinc-800">
                          <FileCode className="w-5 h-5 text-emerald-400 mb-1" />
                          <p className="text-lg font-bold text-white">{simulationResult.file_count}</p>
                          <p className="text-[10px] text-zinc-500">Files</p>
                        </div>
                        <div className="p-3 rounded bg-zinc-900 border border-zinc-800">
                          <Package className="w-5 h-5 text-amber-400 mb-1" />
                          <p className="text-lg font-bold text-white">{simulationResult.total_size_kb}KB</p>
                          <p className="text-[10px] text-zinc-500">Total Size</p>
                        </div>
                        <div className="p-3 rounded bg-zinc-900 border border-zinc-800">
                          <Sparkles className="w-5 h-5 text-purple-400 mb-1" />
                          <p className="text-lg font-bold text-white">{simulationResult.feasibility_score}%</p>
                          <p className="text-[10px] text-zinc-500">Feasibility</p>
                        </div>
                      </div>

                      {/* Warnings */}
                      {simulationResult.warnings.length > 0 && (
                        <div className="space-y-2">
                          <h5 className="text-sm font-medium text-amber-400 flex items-center gap-2"><AlertTriangle className="w-4 h-4" />Warnings ({simulationResult.warnings.length})</h5>
                          {simulationResult.warnings.map((warning, i) => (
                            <div key={i} className={`p-3 rounded border ${warning.severity === 'high' ? 'bg-red-500/10 border-red-500/30' : warning.severity === 'medium' ? 'bg-amber-500/10 border-amber-500/30' : 'bg-zinc-800 border-zinc-700'}`}>
                              <p className="text-sm text-zinc-200">{warning.message}</p>
                              <p className="text-xs text-zinc-500 mt-1">{warning.suggestion}</p>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Architecture Summary */}
                      <div className="p-3 rounded bg-zinc-900 border border-zinc-800">
                        <h5 className="text-sm font-medium text-white mb-2">Architecture Summary</h5>
                        <p className="text-xs text-zinc-400">{simulationResult.architecture_summary}</p>
                      </div>

                      {/* Schedule Build Option */}
                      {simulationResult.ready_to_build && (
                        <div className="p-4 rounded-lg bg-gradient-to-r from-purple-500/10 to-blue-500/10 border border-purple-500/30">
                          <div className="flex items-center gap-2 mb-3">
                            <input type="checkbox" id="schedule-build" checked={scheduleBuild} onChange={(e) => setScheduleBuild(e.target.checked)} className="rounded" />
                            <label htmlFor="schedule-build" className="text-sm text-white flex items-center gap-2">
                              <Clock className="w-4 h-4 text-purple-400" />
                              Schedule for tonight (12+ hour build)
                            </label>
                          </div>
                          {scheduleBuild && (
                            <div className="mt-3">
                              <label className="text-xs text-zinc-400 mb-2 block">Start build at:</label>
                              <Input 
                                type="datetime-local" 
                                value={scheduleTime} 
                                onChange={(e) => setScheduleTime(e.target.value)} 
                                className="bg-zinc-900 border-zinc-700" 
                                data-testid="schedule-time-input"
                              />
                              <p className="text-[10px] text-zinc-500 mt-2">💤 Set it before bed and wake up to a complete project!</p>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Start Build Buttons */}
                      <div className="flex gap-2">
                        {scheduleBuild ? (
                          <Button onClick={() => startAutonomousBuild(true)} disabled={!simulationResult.ready_to_build || buildRunning || !scheduleTime}
                            className={`flex-1 ${simulationResult.ready_to_build && scheduleTime ? 'bg-purple-500 hover:bg-purple-600' : 'bg-zinc-700 cursor-not-allowed'}`}>
                            {buildRunning ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Scheduling...</> : 
                              <><Clock className="w-4 h-4 mr-2" />Schedule Overnight Build</>}
                          </Button>
                        ) : (
                          <Button onClick={() => startAutonomousBuild(false)} disabled={!simulationResult.ready_to_build || buildRunning}
                            className={`flex-1 ${simulationResult.ready_to_build ? 'bg-emerald-500 hover:bg-emerald-600' : 'bg-zinc-700 cursor-not-allowed'}`}>
                            {buildRunning ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Starting Build...</> : 
                              simulationResult.ready_to_build ? <><Rocket className="w-4 h-4 mr-2" />Start Build Now</> :
                              <><AlertTriangle className="w-4 h-4 mr-2" />Resolve Warnings First</>}
                          </Button>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </DialogContent>
            </Dialog>

            {/* Current Build Status */}
            {currentBuild && currentBuild.status === "scheduled" && (
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-purple-500/20 border border-purple-500/50">
                <Clock className="w-4 h-4 text-purple-400" />
                <span className="text-xs text-purple-400">Scheduled {currentBuild.scheduled_at ? new Date(currentBuild.scheduled_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : ''}</span>
                <Button variant="ghost" size="icon" className="h-5 w-5" onClick={startScheduledBuildNow} title="Start Now"><Play className="w-3 h-3" /></Button>
                <Button variant="ghost" size="icon" className="h-5 w-5" onClick={cancelBuild} title="Cancel"><X className="w-3 h-3" /></Button>
              </div>
            )}
            {currentBuild && currentBuild.status === "running" && (
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/20 border border-blue-500/50">
                <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                <span className="text-xs text-blue-400">Building {currentBuild.progress_percent}%</span>
                <Button variant="ghost" size="icon" className="h-5 w-5" onClick={pauseBuild}><Pause className="w-3 h-3" /></Button>
              </div>
            )}

            {/* Playable Demo Button */}
            {currentDemo && currentDemo.status === "ready" && (
              <Dialog open={demoDialogOpen} onOpenChange={setDemoDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline" size="sm" className="border-emerald-700 text-emerald-400 hover:bg-emerald-500/10" data-testid="demo-btn">
                    <Gamepad2 className="w-4 h-4 mr-1" />Play Demo
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-[#18181b] border-zinc-700 max-w-2xl">
                  <DialogHeader>
                    <DialogTitle className="font-rajdhani text-white flex items-center gap-2">
                      <Gamepad2 className="w-5 h-5 text-emerald-400" />Playable Demo Ready!
                    </DialogTitle>
                  </DialogHeader>
                  <div className="py-4 space-y-4">
                    {/* Demo Options */}
                    <div className="grid grid-cols-2 gap-4">
                      {/* Web Demo */}
                      <div className="p-4 rounded-lg bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/30">
                        <div className="flex items-center gap-2 mb-3">
                          <Globe className="w-6 h-6 text-blue-400" />
                          <h4 className="font-rajdhani font-bold text-white">Web Demo</h4>
                        </div>
                        <p className="text-xs text-zinc-400 mb-4">Play instantly in your browser. HTML5/WebGL based.</p>
                        <Button onClick={openWebDemo} className="w-full bg-blue-500 hover:bg-blue-600">
                          <Play className="w-4 h-4 mr-2" />Play in Browser
                        </Button>
                      </div>
                      
                      {/* Executable Demo */}
                      <div className="p-4 rounded-lg bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/30">
                        <div className="flex items-center gap-2 mb-3">
                          <Monitor className="w-6 h-6 text-purple-400" />
                          <h4 className="font-rajdhani font-bold text-white">Executable</h4>
                        </div>
                        <p className="text-xs text-zinc-400 mb-4">Download build configs for {currentDemo.target_engine?.toUpperCase() || 'UE5'}.</p>
                        <Button variant="outline" className="w-full border-purple-500 text-purple-400" onClick={() => { setRightTab("code"); setDemoDialogOpen(false); const demoFile = files.find(f => f.filepath?.includes("demo/")); if (demoFile) { setSelectedFile(demoFile); setEditorContent(demoFile.content); } }}>
                          <FileCode className="w-4 h-4 mr-2" />View Demo Files
                        </Button>
                      </div>
                    </div>

                    {/* Demo Features */}
                    {currentDemo.demo_features?.length > 0 && (
                      <div className="p-3 rounded bg-zinc-900 border border-zinc-800">
                        <h5 className="text-sm font-medium text-white mb-2">Demo Features</h5>
                        <div className="flex flex-wrap gap-2">
                          {currentDemo.demo_features.map((feature, i) => (
                            <Badge key={i} variant="outline" className="text-xs border-zinc-700 text-zinc-400">{feature}</Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Controls Guide */}
                    {currentDemo.controls_guide && (
                      <div className="p-3 rounded bg-zinc-900 border border-zinc-800">
                        <h5 className="text-sm font-medium text-white mb-2">Controls</h5>
                        <pre className="text-xs text-zinc-400 whitespace-pre-wrap max-h-32 overflow-y-auto">{currentDemo.controls_guide.slice(0, 500)}</pre>
                      </div>
                    )}

                    {/* Regenerate Button */}
                    <Button variant="outline" className="w-full border-zinc-700" onClick={regenerateDemo} disabled={regeneratingDemo}>
                      {regeneratingDemo ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Regenerating...</> : <><RefreshCw className="w-4 h-4 mr-2" />Regenerate Demo</>}
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            )}

            {/* Other header buttons */}
            <Dialog open={refactorDialog} onOpenChange={setRefactorDialog}>
              <DialogTrigger asChild><Button variant="outline" size="sm" className="border-zinc-700"><Replace className="w-4 h-4 mr-1" />Refactor</Button></DialogTrigger>
              <DialogContent className="bg-[#18181b] border-zinc-700 max-w-lg">
                <DialogHeader><DialogTitle className="font-rajdhani text-white flex items-center gap-2"><Wand2 className="w-5 h-5 text-blue-400" />Multi-File Refactor</DialogTitle></DialogHeader>
                <div className="space-y-4 py-4">
                  <Select value={refactorData.type} onValueChange={(v) => setRefactorData({ ...refactorData, type: v })}><SelectTrigger className="bg-zinc-900 border-zinc-700"><SelectValue /></SelectTrigger><SelectContent className="bg-zinc-900 border-zinc-700"><SelectItem value="find_replace">Find & Replace</SelectItem><SelectItem value="rename">Rename Symbol</SelectItem></SelectContent></Select>
                  <Input placeholder="Find what..." value={refactorData.target} onChange={(e) => setRefactorData({ ...refactorData, target: e.target.value })} className="bg-zinc-900 border-zinc-700" />
                  <Input placeholder="Replace with..." value={refactorData.new_value} onChange={(e) => setRefactorData({ ...refactorData, new_value: e.target.value })} className="bg-zinc-900 border-zinc-700" />
                  <Button variant="outline" className="w-full border-zinc-700" onClick={previewRefactor}><Search className="w-4 h-4 mr-2" />Preview Changes</Button>
                  {refactorPreview && (<div className="p-3 rounded bg-zinc-900 border border-zinc-700"><p className="text-sm text-zinc-400 mb-2">{refactorPreview.files_affected} files will be modified</p>{refactorPreview.changes?.slice(0, 3).map((c, i) => (<div key={i} className="text-xs text-zinc-500">• {c.filepath} ({c.occurrences} occurrences)</div>))}</div>)}
                </div>
                <DialogFooter><Button onClick={applyRefactor} disabled={!refactorPreview?.files_affected} className="bg-blue-500 hover:bg-blue-600">Apply Refactor</Button></DialogFooter>
              </DialogContent>
            </Dialog>

            <Dialog open={memoryDialog} onOpenChange={setMemoryDialog}>
              <DialogTrigger asChild><Button variant="outline" size="sm" className="border-zinc-700"><Brain className="w-4 h-4 mr-1" />Memory</Button></DialogTrigger>
              <DialogContent className="bg-[#18181b] border-zinc-700 max-w-lg">
                <DialogHeader><DialogTitle className="font-rajdhani text-white flex items-center gap-2"><Brain className="w-5 h-5 text-purple-400" />Agent Memories ({memories.length})</DialogTitle></DialogHeader>
                <div className="py-4">
                  <Button variant="outline" className="w-full mb-4 border-zinc-700" onClick={extractMemories}><Sparkles className="w-4 h-4 mr-2" />Extract Memories from Conversation</Button>
                  <ScrollArea className="h-[300px]">
                    {memories.length === 0 ? <p className="text-center text-zinc-500 py-8">No memories yet</p> : (
                      <div className="space-y-2">{memories.map((m) => (<div key={m.id} className="p-3 rounded bg-zinc-900 border border-zinc-800 group"><div className="flex items-center justify-between mb-1"><Badge variant="outline" className="text-[10px] border-zinc-700">{m.agent_name}</Badge><Badge className={`text-[10px] ${m.importance >= 7 ? 'bg-amber-500/20 text-amber-400' : 'bg-zinc-800 text-zinc-500'}`}>imp: {m.importance}</Badge></div><p className="text-sm text-zinc-300">{m.content}</p><Button variant="ghost" size="sm" className="h-6 mt-2 opacity-0 group-hover:opacity-100" onClick={() => deleteMemory(m.id)}><Trash2 className="w-3 h-3 text-red-400 mr-1" />Delete</Button></div>))}</div>
                    )}
                  </ScrollArea>
                </div>
              </DialogContent>
            </Dialog>

            <Dialog open={duplicateDialog} onOpenChange={setDuplicateDialog}>
              <DialogTrigger asChild><Button variant="outline" size="sm" className="border-zinc-700"><CopyPlus className="w-4 h-4" /></Button></DialogTrigger>
              <DialogContent className="bg-[#18181b] border-zinc-700">
                <DialogHeader><DialogTitle className="font-rajdhani text-white">Duplicate Project</DialogTitle></DialogHeader>
                <div className="py-4"><Input placeholder="New project name" value={duplicateName} onChange={(e) => setDuplicateName(e.target.value)} className="bg-zinc-900 border-zinc-700" /></div>
                <DialogFooter><Button onClick={duplicateProject} className="bg-blue-500 hover:bg-blue-600"><CopyPlus className="w-4 h-4 mr-2" />Duplicate with Files</Button></DialogFooter>
              </DialogContent>
            </Dialog>

            <Dialog open={githubDialogOpen} onOpenChange={setGithubDialogOpen}><DialogTrigger asChild><Button variant="outline" size="sm" className="border-zinc-700"><Github className="w-4 h-4 mr-1" />Push</Button></DialogTrigger><DialogContent className="bg-[#18181b] border-zinc-700"><DialogHeader><DialogTitle className="font-rajdhani text-white"><Github className="w-5 h-5 inline mr-2" />Push to GitHub</DialogTitle></DialogHeader><div className="space-y-4 py-4"><div><label className="text-sm text-zinc-400 mb-2 block">GitHub Token</label><Input type="password" placeholder="ghp_xxxx" value={githubToken} onChange={(e) => setGithubToken(e.target.value)} className="bg-zinc-900 border-zinc-700" /></div><div><label className="text-sm text-zinc-400 mb-2 block">Repo Name</label><Input value={githubRepoName} onChange={(e) => setGithubRepoName(e.target.value)} className="bg-zinc-900 border-zinc-700" /></div><div className="flex items-center gap-2"><input type="checkbox" id="create-new" checked={githubCreateNew} onChange={(e) => setGithubCreateNew(e.target.checked)} /><label htmlFor="create-new" className="text-sm text-zinc-400">Create new if not exists</label></div></div><DialogFooter><Button onClick={pushToGithub} disabled={pushing} className="bg-blue-500 hover:bg-blue-600">{pushing ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Rocket className="w-4 h-4 mr-2" />}Push</Button></DialogFooter></DialogContent></Dialog>

            <Dialog open={imageDialogOpen} onOpenChange={setImageDialogOpen}><DialogTrigger asChild><Button variant="outline" size="sm" className="border-zinc-700"><Image className="w-4 h-4" /></Button></DialogTrigger><DialogContent className="bg-[#18181b] border-zinc-700"><DialogHeader><DialogTitle className="font-rajdhani text-white">Generate Asset</DialogTitle></DialogHeader><div className="space-y-4 py-4"><Textarea placeholder="Describe..." value={imagePrompt} onChange={(e) => setImagePrompt(e.target.value)} className="bg-zinc-900 border-zinc-700 min-h-[100px]" /><Select value={imageCategory} onValueChange={setImageCategory}><SelectTrigger className="bg-zinc-900 border-zinc-700"><SelectValue /></SelectTrigger><SelectContent className="bg-zinc-900 border-zinc-700"><SelectItem value="concept">Concept Art</SelectItem><SelectItem value="character">Character</SelectItem><SelectItem value="environment">Environment</SelectItem><SelectItem value="ui">UI</SelectItem><SelectItem value="texture">Texture</SelectItem></SelectContent></Select></div><DialogFooter><Button onClick={generateImage} disabled={generatingImage} className="bg-blue-500 hover:bg-blue-600">{generatingImage ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Sparkles className="w-4 h-4 mr-2" />}Generate</Button></DialogFooter></DialogContent></Dialog>

            <Button variant="outline" size="sm" className="border-zinc-700" onClick={exportProject}><Download className="w-4 h-4" /></Button>
          </div>
        </div>
      </header>

      {/* Main */}
      <div className="flex-1 overflow-hidden">
        <ResizablePanelGroup direction="horizontal">
          <ResizablePanel defaultSize={45} minSize={30}>
            <div className="h-full flex flex-col bg-[#0a0a0c]">
              {/* Quick Actions */}
              <AnimatePresence>
                {showQuickActions && (
                  <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="border-b border-zinc-800 overflow-hidden">
                    <div className="p-3">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-rajdhani font-bold text-white text-sm flex items-center gap-2"><Rocket className="w-4 h-4 text-blue-400" />Quick Actions</h3>
                        <div className="flex gap-2">
                          <Dialog open={customActionDialog} onOpenChange={setCustomActionDialog}>
                            <DialogTrigger asChild><Button variant="ghost" size="icon" className="h-6 w-6"><Plus className="w-4 h-4" /></Button></DialogTrigger>
                            <DialogContent className="bg-[#18181b] border-zinc-700">
                              <DialogHeader><DialogTitle className="font-rajdhani text-white">Create Custom Action</DialogTitle></DialogHeader>
                              <div className="space-y-3 py-4">
                                <Input placeholder="Action name" value={newCustomAction.name} onChange={(e) => setNewCustomAction({ ...newCustomAction, name: e.target.value })} className="bg-zinc-900 border-zinc-700" />
                                <Input placeholder="Description" value={newCustomAction.description} onChange={(e) => setNewCustomAction({ ...newCustomAction, description: e.target.value })} className="bg-zinc-900 border-zinc-700" />
                                <Textarea placeholder="Prompt template (use {engine_type} for variables)" value={newCustomAction.prompt} onChange={(e) => setNewCustomAction({ ...newCustomAction, prompt: e.target.value })} className="bg-zinc-900 border-zinc-700 min-h-[100px]" />
                                <div className="flex items-center gap-2"><input type="checkbox" id="global" checked={newCustomAction.is_global} onChange={(e) => setNewCustomAction({ ...newCustomAction, is_global: e.target.checked })} /><label htmlFor="global" className="text-sm text-zinc-400">Available in all projects</label></div>
                              </div>
                              <DialogFooter><Button onClick={createCustomAction} className="bg-blue-500 hover:bg-blue-600">Create Action</Button></DialogFooter>
                            </DialogContent>
                          </Dialog>
                          <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => setShowQuickActions(false)}><ChevronUp className="w-4 h-4" /></Button>
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
                            </TooltipTrigger><TooltipContent><p className="text-xs">{action.description}</p>{action.isCustom && <Button variant="ghost" size="sm" className="h-5 mt-1 text-red-400" onClick={(e) => { e.stopPropagation(); deleteCustomAction(action.id); }}><Trash2 className="w-3 h-3 mr-1" />Delete</Button>}</TooltipContent></Tooltip></TooltipProvider>
                          );
                        })}
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
              {!showQuickActions && <Button variant="ghost" size="sm" className="mx-3 mt-2 text-xs text-zinc-500" onClick={() => setShowQuickActions(true)}><ChevronDown className="w-3 h-3 mr-1" />Show Quick Actions</Button>}
              {chainProgress && <div className="px-4 py-2 bg-blue-500/10 border-b border-blue-500/30"><div className="flex items-center gap-2"><Loader2 className="w-4 h-4 text-blue-400 animate-spin" /><span className="text-xs text-blue-400">Step {chainProgress.step}/{chainProgress.total}: {chainProgress.agent}</span></div></div>}

              <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
                <TabsList className="flex-shrink-0 bg-transparent border-b border-zinc-800 rounded-none px-4 h-11 overflow-x-auto">
                  <TabsTrigger value="chat" className="data-[state=active]:bg-zinc-800"><MessageSquare className="w-4 h-4 mr-2" />Chat</TabsTrigger>
                  <TabsTrigger value="warroom" className="data-[state=active]:bg-zinc-800" data-testid="warroom-tab"><Radio className="w-4 h-4 mr-2" />War Room{warRoomMessages.length > 0 && <Badge variant="secondary" className="ml-2 text-xs bg-cyan-500/20 text-cyan-400">{warRoomMessages.length}</Badge>}</TabsTrigger>
                  <TabsTrigger value="blueprints" className="data-[state=active]:bg-zinc-800" data-testid="blueprints-tab"><GitBranch className="w-4 h-4 mr-2" />Blueprints{blueprints.length > 0 && <Badge variant="secondary" className="ml-2 text-xs bg-purple-500/20 text-purple-400">{blueprints.length}</Badge>}</TabsTrigger>
                  <TabsTrigger value="queue" className="data-[state=active]:bg-zinc-800" data-testid="queue-tab"><Calendar className="w-4 h-4 mr-2" />Queue</TabsTrigger>
                  <TabsTrigger value="collab" className="data-[state=active]:bg-zinc-800" data-testid="collab-tab"><Users className="w-4 h-4 mr-2" />Collab</TabsTrigger>
                  <TabsTrigger value="tasks" className="data-[state=active]:bg-zinc-800"><ListTodo className="w-4 h-4 mr-2" />Tasks{tasks.length > 0 && <Badge variant="secondary" className="ml-2 text-xs">{tasks.length}</Badge>}</TabsTrigger>
                  <TabsTrigger value="images" className="data-[state=active]:bg-zinc-800"><Image className="w-4 h-4 mr-2" />Images</TabsTrigger>
                  <TabsTrigger value="audio" className="data-[state=active]:bg-zinc-800" data-testid="audio-tab"><Music className="w-4 h-4 mr-2" />Audio</TabsTrigger>
                  <TabsTrigger value="assets" className="data-[state=active]:bg-zinc-800" data-testid="assets-tab"><Package className="w-4 h-4 mr-2" />Assets</TabsTrigger>
                  <TabsTrigger value="sandbox" className="data-[state=active]:bg-zinc-800" data-testid="sandbox-tab"><Terminal className="w-4 h-4 mr-2" />Sandbox</TabsTrigger>
                  <TabsTrigger value="command" className="data-[state=active]:bg-zinc-800" data-testid="command-tab"><Command className="w-4 h-4 mr-2" />Command</TabsTrigger>
                  <TabsTrigger value="deploy" className="data-[state=active]:bg-zinc-800" data-testid="deploy-tab"><Rocket className="w-4 h-4 mr-2" />Deploy</TabsTrigger>
                  <TabsTrigger value="notifications" className="data-[state=active]:bg-zinc-800" data-testid="notifications-tab"><Bell className="w-4 h-4 mr-2" />Alerts</TabsTrigger>
                  <TabsTrigger value="labs" className="data-[state=active]:bg-violet-900/50 text-violet-400" data-testid="labs-tab"><FlaskConical className="w-4 h-4 mr-2" />Labs<Badge variant="secondary" className="ml-2 text-xs bg-violet-500/20 text-violet-400">NEW</Badge></TabsTrigger>
                  <TabsTrigger value="os" className="data-[state=active]:bg-cyan-900/50 text-cyan-400" data-testid="os-tab"><Cpu className="w-4 h-4 mr-2" />OS</TabsTrigger>
                  <TabsTrigger value="voice" className="data-[state=active]:bg-cyan-900/50 text-cyan-400" data-testid="voice-tab"><Mic className="w-4 h-4 mr-2" />Voice</TabsTrigger>
                </TabsList>

                {/* Chat Tab */}
                <TabsContent value="chat" className="flex-1 flex flex-col m-0 overflow-hidden">
                  <ScrollArea className="flex-1 p-4"><div className="space-y-4">
                    {messages.length === 0 && !streamingContent ? (<div className="text-center py-12"><Sparkles className="w-12 h-12 mx-auto mb-4 text-blue-400/50" /><h3 className="font-rajdhani text-xl text-white mb-2">Ready to Build</h3><p className="text-sm text-zinc-500 max-w-md mx-auto mb-4">Describe your project or use Quick Actions above.</p></div>) : (<>
                      {messages.map((msg) => {
                        const isUser = msg.agent_role === "user";
                        const AgentIcon = getAgentIcon(msg.agent_role);
                        const agent = agents.find(a => a.id === msg.agent_id);
                        return (<motion.div key={msg.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>{!isUser && <Avatar className="w-8 h-8 border border-zinc-700 flex-shrink-0 mt-1"><AvatarImage src={agent?.avatar} /><AvatarFallback className="bg-zinc-800"><AgentIcon className={`w-4 h-4 ${getAgentColor(msg.agent_role)}`} /></AvatarFallback></Avatar>}<div className={`max-w-[85%] ${isUser ? 'ml-auto' : ''}`}>{!isUser && <div className="flex items-center gap-2 mb-1"><span className="font-rajdhani font-bold text-sm text-blue-400">{msg.agent_name}</span><Badge variant="outline" className="text-[10px] border-zinc-700 text-zinc-500">{msg.agent_role}</Badge></div>}<div className={`rounded-lg px-4 py-3 ${isUser ? 'bg-blue-500 text-white' : 'bg-zinc-800/50 border border-zinc-700/50'}`}>{isUser ? <p className="text-sm whitespace-pre-wrap">{msg.content}</p> : parseMessageContent(msg.content, msg.id, msg.delegations)}</div></div></motion.div>);
                      })}
                      {streamingContent && streamingAgent && (<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-3"><Avatar className="w-8 h-8 border border-zinc-700 mt-1"><AvatarFallback className="bg-zinc-800"><Bot className="w-4 h-4 text-blue-400 animate-pulse" /></AvatarFallback></Avatar><div className="max-w-[85%]"><div className="flex items-center gap-2 mb-1"><span className="font-rajdhani font-bold text-sm text-blue-400">{streamingAgent.name}</span><Badge className="text-[10px] bg-amber-500/20 text-amber-400 animate-pulse">streaming</Badge></div><div className="bg-zinc-800/50 border border-zinc-700/50 rounded-lg px-4 py-3">{parseMessageContent(streamingContent, 'streaming')}</div></div></motion.div>)}
                    </>)}
                    {sending && !streamingContent && <div className="flex gap-3"><div className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center"><Loader2 className="w-4 h-4 text-blue-400 animate-spin" /></div><div className="bg-zinc-800/50 rounded-lg px-4 py-3"><div className="typing-indicator"><span></span><span></span><span></span></div></div></div>}
                    <div ref={chatEndRef} />
                  </div></ScrollArea>
                  <div className="flex-shrink-0 p-4 border-t border-zinc-800">
                    {selectedAgent && <div className="mb-2 flex items-center gap-2"><span className="text-xs text-zinc-500">Speaking to:</span><Badge className="bg-blue-500/20 text-blue-400 border-0">{agents.find(a => a.id === selectedAgent)?.name}</Badge><Button variant="ghost" size="sm" className="h-5 px-2" onClick={() => setSelectedAgent(null)}><X className="w-3 h-3" /></Button></div>}
                    <div className="flex gap-2"><Textarea placeholder={project?.phase === "clarification" ? "Describe your project..." : "What next?"} value={chatInput} onChange={(e) => setChatInput(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessageStreaming(); }}} className="bg-zinc-900 border-zinc-700 min-h-[80px] resize-none text-sm" data-testid="chat-input" /><Button onClick={sendMessageStreaming} disabled={sending || !chatInput.trim()} className="bg-blue-500 hover:bg-blue-600 px-4 self-end" data-testid="send-btn">{sending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}</Button></div>
                  </div>
                </TabsContent>

                {/* War Room Tab */}
                <TabsContent value="warroom" className="flex-1 flex flex-col m-0 overflow-hidden">
                  <div className="flex-shrink-0 p-3 border-b border-zinc-800 flex items-center justify-between bg-gradient-to-r from-cyan-500/10 to-transparent">
                    <h3 className="font-rajdhani font-bold text-white text-sm flex items-center gap-2"><Radio className="w-4 h-4 text-cyan-400" />Agent War Room</h3>
                    {currentBuild && (
                      <div className="flex items-center gap-2">
                        <Badge className={`text-xs ${currentBuild.status === 'running' ? 'bg-blue-500/20 text-blue-400' : currentBuild.status === 'completed' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-zinc-800 text-zinc-400'}`}>
                          {currentBuild.status}
                        </Badge>
                        {currentBuild.status === "running" && (
                          <>
                            <Progress value={currentBuild.progress_percent} className="w-24 h-2" />
                            <span className="text-xs text-zinc-400">{currentBuild.progress_percent}%</span>
                            <Button variant="ghost" size="icon" className="h-6 w-6" onClick={pauseBuild}><Pause className="w-3 h-3" /></Button>
                            <Button variant="ghost" size="icon" className="h-6 w-6" onClick={cancelBuild}><Square className="w-3 h-3" /></Button>
                          </>
                        )}
                        {currentBuild.status === "paused" && (
                          <Button variant="ghost" size="sm" className="h-6 text-xs" onClick={resumeBuild}><Play className="w-3 h-3 mr-1" />Resume</Button>
                        )}
                      </div>
                    )}
                  </div>
                  
                  {/* Build Stages */}
                  {currentBuild && currentBuild.stages && (
                    <div className="flex-shrink-0 p-3 border-b border-zinc-800 bg-zinc-900/50">
                      <div className="flex gap-2 overflow-x-auto pb-2">
                        {currentBuild.stages.map((stage, i) => (
                          <div key={i} className={`flex-shrink-0 px-3 py-2 rounded border text-xs ${stage.status === 'completed' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : stage.status === 'in_progress' ? 'bg-blue-500/10 border-blue-500/30 text-blue-400 animate-pulse' : stage.status === 'failed' ? 'bg-red-500/10 border-red-500/30 text-red-400' : 'bg-zinc-800/50 border-zinc-700 text-zinc-500'}`}>
                            <div className="font-medium">{stage.name}</div>
                            {stage.files_created?.length > 0 && <div className="text-[10px] mt-1">{stage.files_created.length} files</div>}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <ScrollArea className="flex-1 p-4">
                    <div className="space-y-3">
                      {warRoomMessages.length === 0 ? (
                        <div className="text-center py-12">
                          <Radio className="w-12 h-12 mx-auto mb-4 text-cyan-400/30" />
                          <h3 className="font-rajdhani text-lg text-white mb-2">War Room Empty</h3>
                          <p className="text-sm text-zinc-500 mb-4">Start a simulation to see agents communicate</p>
                          <Button onClick={() => setSimulationDialog(true)} className="bg-cyan-500 hover:bg-cyan-600"><Radio className="w-4 h-4 mr-2" />Open Simulation</Button>
                        </div>
                      ) : (
                        warRoomMessages.map((msg) => (
                          <motion.div key={msg.id} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="flex gap-3">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${msg.message_type === 'warning' ? 'bg-red-500/20' : msg.message_type === 'handoff' ? 'bg-cyan-500/20' : 'bg-zinc-800'}`}>
                              <Bot className={`w-4 h-4 ${getWarRoomTypeColor(msg.message_type)}`} />
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <span className="font-rajdhani font-bold text-sm text-cyan-400">{msg.from_agent}</span>
                                {msg.to_agent && <><ArrowRightCircle className="w-3 h-3 text-zinc-600" /><span className="text-xs text-zinc-500">{msg.to_agent}</span></>}
                                <Badge variant="outline" className={`text-[10px] border-zinc-700 ${getWarRoomTypeColor(msg.message_type)}`}>{msg.message_type}</Badge>
                              </div>
                              <p className="text-sm text-zinc-300">{msg.content}</p>
                            </div>
                          </motion.div>
                        ))
                      )}
                      <div ref={warRoomEndRef} />
                    </div>
                  </ScrollArea>
                </TabsContent>

                {/* Blueprints Tab */}
                <TabsContent value="blueprints" className="flex-1 m-0 overflow-hidden flex flex-col">
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
                </TabsContent>

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

                <TabsContent value="labs" className="flex-1 m-0 overflow-hidden">
                  <LabsPanel projectId={projectId} />
                </TabsContent>
                <TabsContent value="os" className="flex-1 m-0 overflow-hidden">
                  <OSFeaturesPanel projectId={projectId} />
                </TabsContent>
                <TabsContent value="voice" className="flex-1 m-0 overflow-hidden">
                  <VoiceControlPanel projectId={projectId} />
                </TabsContent>
              </Tabs>
            </div>
          </ResizablePanel>

          <ResizableHandle withHandle className="bg-zinc-800" />

          {/* Right Panel */}
          <ResizablePanel defaultSize={55} minSize={30}>
            <div className="h-full flex flex-col bg-[#0d0d0f]">
              <div className="flex-shrink-0 border-b border-zinc-800 bg-[#0a0a0c]"><div className="flex items-center justify-between px-4 py-2"><Tabs value={rightTab} onValueChange={setRightTab} className="w-full"><TabsList className="bg-transparent"><TabsTrigger value="code" className="data-[state=active]:bg-zinc-800"><Code2 className="w-4 h-4 mr-2" />Code{files.length > 0 && <Badge variant="secondary" className="ml-2 text-xs">{files.length}</Badge>}</TabsTrigger>{isWebProject && <TabsTrigger value="preview" className="data-[state=active]:bg-zinc-800" onClick={loadPreview}><Eye className="w-4 h-4 mr-2" />Preview</TabsTrigger>}</TabsList></Tabs>{selectedFile && rightTab === "code" && <div className="flex items-center gap-2">{unsavedChanges && <Badge className="bg-amber-500/20 text-amber-400 text-xs">Unsaved</Badge>}<Button size="sm" variant="outline" className="h-7 border-zinc-700" onClick={saveFile} disabled={!unsavedChanges}><Save className="w-3 h-3 mr-1" />Save</Button></div>}</div></div>

              {rightTab === "code" ? (
                <ResizablePanelGroup direction="horizontal" className="flex-1">
                  <ResizablePanel defaultSize={25} minSize={15} maxSize={40}><div className="h-full flex flex-col bg-[#0a0a0c] border-r border-zinc-800"><div className="flex-shrink-0 px-3 py-2 border-b border-zinc-800"><h4 className="text-xs text-zinc-500 uppercase tracking-wider">Files</h4></div><ScrollArea className="flex-1"><div className="py-2">{files.length === 0 ? <div className="px-4 py-8 text-center"><Folder className="w-8 h-8 mx-auto mb-2 text-zinc-700" /><p className="text-xs text-zinc-600">No files</p></div> : renderFileTree(buildFileTree())}</div></ScrollArea></div></ResizablePanel>
                  <ResizableHandle className="bg-zinc-800" />
                  <ResizablePanel defaultSize={75}><div className="h-full flex flex-col">{selectedFile ? (<><div className="flex-shrink-0 px-4 py-2 border-b border-zinc-800 bg-[#0d0d0f] flex items-center gap-2"><FileCode className="w-4 h-4 text-zinc-500" /><span className="text-sm text-zinc-300 font-mono">{selectedFile.filepath}</span><Badge variant="outline" className="text-[10px] border-zinc-700 ml-auto">v{selectedFile.version || 1}</Badge></div><div className="flex-1"><Editor height="100%" language={LANGUAGE_MAP[selectedFile.language] || selectedFile.language} value={editorContent} onChange={(v) => { setEditorContent(v || ""); setUnsavedChanges(v !== selectedFile.content); }} theme="vs-dark" options={{ minimap: { enabled: true }, fontSize: 13, fontFamily: "'JetBrains Mono', monospace", lineNumbers: 'on', scrollBeyondLastLine: false, automaticLayout: true, tabSize: 2, wordWrap: 'on', padding: { top: 12 }}} /></div></>) : (<div className="h-full flex items-center justify-center text-center"><div><FileCode className="w-16 h-16 mx-auto mb-4 text-zinc-800" /><h3 className="font-rajdhani text-lg text-zinc-600 mb-2">No File Selected</h3><p className="text-sm text-zinc-700">Select a file or use Quick Actions</p></div></div>)}</div></ResizablePanel>
                </ResizablePanelGroup>
              ) : (
                <div className="flex-1 flex flex-col"><div className="flex-shrink-0 px-4 py-2 border-b border-zinc-800 flex items-center justify-between"><span className="text-sm text-zinc-400">Live Preview</span><Button size="sm" variant="outline" className="h-7 border-zinc-700" onClick={loadPreview}><Play className="w-3 h-3 mr-1" />Refresh</Button></div><div className="flex-1 bg-white">{previewHtml ? <iframe srcDoc={previewHtml} className="w-full h-full border-0" sandbox="allow-scripts" title="Preview" /> : <div className="h-full flex items-center justify-center bg-zinc-900"><p className="text-zinc-500">Click Refresh</p></div>}</div></div>
              )}
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </div>
  );
};

export default ProjectWorkspace;
