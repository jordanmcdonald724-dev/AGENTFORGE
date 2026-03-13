import { useState, useEffect, useRef, useCallback } from "react";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { 
  ArrowLeft,
  Send,
  Bot,
  Code2,
  Layers,
  Users,
  Shield,
  Zap,
  Plus,
  Loader2,
  FileCode,
  ListTodo,
  MessageSquare,
  Folder,
  FolderOpen,
  ChevronRight,
  ChevronDown,
  Save,
  Download,
  Trash2,
  Palette,
  Copy,
  Check,
  X,
  Image,
  Sparkles,
  ArrowRightCircle
} from "lucide-react";
import { API } from "@/App";

const PHASE_CONFIG = {
  clarification: { label: "Clarification", color: "bg-amber-500/20 text-amber-400", icon: MessageSquare },
  planning: { label: "Planning", color: "bg-blue-500/20 text-blue-400", icon: Layers },
  development: { label: "Development", color: "bg-emerald-500/20 text-emerald-400", icon: Code2 },
  review: { label: "Review", color: "bg-purple-500/20 text-purple-400", icon: Shield }
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

const ProjectWorkspace = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);
  
  const [project, setProject] = useState(null);
  const [agents, setAgents] = useState([]);
  const [messages, setMessages] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [files, setFiles] = useState([]);
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [chatInput, setChatInput] = useState("");
  const [sending, setSending] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [streamingAgent, setStreamingAgent] = useState(null);
  const [selectedAgent, setSelectedAgent] = useState(null);
  
  const [selectedFile, setSelectedFile] = useState(null);
  const [editorContent, setEditorContent] = useState("");
  const [unsavedChanges, setUnsavedChanges] = useState(false);
  const [expandedFolders, setExpandedFolders] = useState(new Set([""]));
  
  const [activeTab, setActiveTab] = useState("chat");
  const [copiedCode, setCopiedCode] = useState(null);
  
  const [taskDialogOpen, setTaskDialogOpen] = useState(false);
  const [newTask, setNewTask] = useState({ title: "", description: "", priority: "medium", category: "general" });
  
  const [imageDialogOpen, setImageDialogOpen] = useState(false);
  const [imagePrompt, setImagePrompt] = useState("");
  const [imageCategory, setImageCategory] = useState("concept");
  const [generatingImage, setGeneratingImage] = useState(false);

  useEffect(() => {
    fetchProjectData();
  }, [projectId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  const fetchProjectData = async () => {
    try {
      const [projectRes, agentsRes, messagesRes, tasksRes, filesRes, imagesRes] = await Promise.all([
        axios.get(`${API}/projects/${projectId}`),
        axios.get(`${API}/agents`),
        axios.get(`${API}/messages?project_id=${projectId}`),
        axios.get(`${API}/tasks?project_id=${projectId}`),
        axios.get(`${API}/files?project_id=${projectId}`),
        axios.get(`${API}/images?project_id=${projectId}`).catch(() => ({ data: [] }))
      ]);
      setProject(projectRes.data);
      setAgents(agentsRes.data);
      setMessages(messagesRes.data);
      setTasks(tasksRes.data);
      setFiles(filesRes.data);
      setImages(imagesRes.data);
    } catch (error) {
      toast.error("Failed to load project");
      navigate("/dashboard");
    } finally {
      setLoading(false);
    }
  };

  const sendMessageStreaming = async () => {
    if (!chatInput.trim() || sending) return;
    
    setSending(true);
    const userMessage = chatInput;
    setChatInput("");
    setStreamingContent("");

    // Add user message
    const tempUserMsg = {
      id: `temp-user-${Date.now()}`,
      project_id: projectId,
      agent_id: "user",
      agent_name: "You",
      agent_role: "user",
      content: userMessage,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);

    try {
      const response = await fetch(`${API}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          message: userMessage,
          phase: project?.phase,
          delegate_to: selectedAgent ? agents.find(a => a.id === selectedAgent)?.name : null
        })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullContent = "";
      let currentAgent = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.type === 'start') {
                currentAgent = data.agent;
                setStreamingAgent(data.agent);
                setAgents(prev => prev.map(a => 
                  a.id === data.agent.id ? { ...a, status: "thinking" } : a
                ));
              } else if (data.type === 'content') {
                fullContent += data.content;
                setStreamingContent(fullContent);
              } else if (data.type === 'done') {
                // Add completed message
                const agentMsg = {
                  id: `agent-${Date.now()}`,
                  project_id: projectId,
                  agent_id: currentAgent?.id,
                  agent_name: currentAgent?.name,
                  agent_role: currentAgent?.role,
                  content: fullContent,
                  code_blocks: data.code_blocks || [],
                  delegations: data.delegations || [],
                  timestamp: new Date().toISOString()
                };
                setMessages(prev => [...prev, agentMsg]);
                setStreamingContent("");
                setStreamingAgent(null);

                // Auto-save code blocks
                if (data.code_blocks?.length > 0) {
                  await saveCodeBlocks(data.code_blocks, currentAgent);
                }

                // Handle delegations
                if (data.delegations?.length > 0) {
                  for (const delegation of data.delegations) {
                    toast.info(`COMMANDER delegated to ${delegation.agent}`);
                  }
                }

                setAgents(prev => prev.map(a => ({ ...a, status: "idle" })));
              } else if (data.type === 'error') {
                toast.error(data.error);
              }
            } catch (e) {
              // Ignore parse errors
            }
          }
        }
      }
    } catch (error) {
      toast.error("Failed to send message");
      setStreamingContent("");
      setStreamingAgent(null);
    } finally {
      setSending(false);
      setAgents(prev => prev.map(a => ({ ...a, status: "idle" })));
    }
  };

  const executeDelegation = async (agentName, task) => {
    try {
      const res = await axios.post(`${API}/delegate`, {
        project_id: projectId,
        message: task,
        delegate_to: agentName
      });

      const agentMsg = {
        id: `delegate-${Date.now()}`,
        project_id: projectId,
        agent_id: res.data.agent.id,
        agent_name: res.data.agent.name,
        agent_role: res.data.agent.role,
        content: res.data.response,
        code_blocks: res.data.code_blocks || [],
        delegated_to: agentName,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, agentMsg]);

      if (res.data.code_blocks?.length > 0) {
        await saveCodeBlocks(res.data.code_blocks, res.data.agent);
      }

      toast.success(`${agentName} completed the task`);
    } catch (error) {
      toast.error(`Delegation to ${agentName} failed`);
    }
  };

  const saveCodeBlocks = async (codeBlocks, agent) => {
    const validBlocks = codeBlocks.filter(b => b.filepath);
    if (validBlocks.length === 0) return;

    try {
      await axios.post(`${API}/files/from-chat`, {
        project_id: projectId,
        code_blocks: validBlocks,
        agent_id: agent?.id,
        agent_name: agent?.name
      });
      
      const filesRes = await axios.get(`${API}/files?project_id=${projectId}`);
      setFiles(filesRes.data);
      toast.success(`Saved ${validBlocks.length} file(s)`);
    } catch (error) {
      console.error("Failed to save code blocks", error);
    }
  };

  const generateImage = async () => {
    if (!imagePrompt.trim()) return;
    setGeneratingImage(true);

    try {
      const res = await axios.post(`${API}/images/generate`, {
        project_id: projectId,
        prompt: imagePrompt,
        category: imageCategory
      });

      setImages(prev => [res.data, ...prev]);
      setImagePrompt("");
      setImageDialogOpen(false);
      toast.success("Image generated!");
    } catch (error) {
      toast.error("Image generation failed");
    } finally {
      setGeneratingImage(false);
    }
  };

  const saveFile = async () => {
    if (!selectedFile || !unsavedChanges) return;
    try {
      await axios.patch(`${API}/files/${selectedFile.id}`, { content: editorContent });
      setFiles(files.map(f => f.id === selectedFile.id ? { ...f, content: editorContent } : f));
      setSelectedFile({ ...selectedFile, content: editorContent });
      setUnsavedChanges(false);
      toast.success("File saved");
    } catch (error) {
      toast.error("Failed to save");
    }
  };

  const exportProject = async () => {
    try {
      const response = await axios.get(`${API}/projects/${projectId}/export`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${project?.name?.replace(/\s+/g, '_') || 'project'}.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success("Project exported!");
    } catch (error) {
      toast.error("Export failed");
    }
  };

  const copyCode = (code, id) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const createTask = async () => {
    if (!newTask.title.trim()) return;
    try {
      const res = await axios.post(`${API}/tasks`, { ...newTask, project_id: projectId });
      setTasks([res.data, ...tasks]);
      setNewTask({ title: "", description: "", priority: "medium", category: "general" });
      setTaskDialogOpen(false);
      toast.success("Task created");
    } catch (error) {
      toast.error("Failed to create task");
    }
  };

  const updateTaskStatus = async (taskId, status) => {
    await axios.patch(`${API}/tasks/${taskId}`, { status });
    setTasks(tasks.map(t => t.id === taskId ? { ...t, status } : t));
  };

  const deleteTask = async (taskId) => {
    await axios.delete(`${API}/tasks/${taskId}`);
    setTasks(tasks.filter(t => t.id !== taskId));
  };

  const deleteFile = async (fileId) => {
    await axios.delete(`${API}/files/${fileId}`);
    setFiles(files.filter(f => f.id !== fileId));
    if (selectedFile?.id === fileId) {
      setSelectedFile(null);
      setEditorContent("");
    }
  };

  const buildFileTree = () => {
    const tree = {};
    files.forEach(file => {
      const parts = file.filepath.split('/').filter(Boolean);
      let current = tree;
      parts.forEach((part, idx) => {
        if (idx === parts.length - 1) {
          current[part] = file;
        } else {
          if (!current[part]) current[part] = {};
          current = current[part];
        }
      });
    });
    return tree;
  };

  const toggleFolder = (path) => {
    const newExpanded = new Set(expandedFolders);
    newExpanded.has(path) ? newExpanded.delete(path) : newExpanded.add(path);
    setExpandedFolders(newExpanded);
  };

  const renderFileTree = (node, path = "", depth = 0) => {
    return Object.entries(node).map(([name, value]) => {
      const fullPath = path ? `${path}/${name}` : name;
      const isFile = value?.id;
      const isExpanded = expandedFolders.has(fullPath);
      
      if (isFile) {
        return (
          <div
            key={value.id}
            className={`flex items-center gap-2 px-2 py-1.5 cursor-pointer hover:bg-zinc-800 rounded text-sm group ${
              selectedFile?.id === value.id ? 'bg-blue-500/20 text-blue-400' : 'text-zinc-400'
            }`}
            style={{ paddingLeft: `${depth * 12 + 8}px` }}
            onClick={() => {
              setSelectedFile(value);
              setEditorContent(value.content);
              setUnsavedChanges(false);
            }}
          >
            <FileCode className="w-4 h-4 flex-shrink-0" />
            <span className="truncate flex-1">{name}</span>
            <Button variant="ghost" size="icon" className="h-6 w-6 opacity-0 group-hover:opacity-100"
              onClick={(e) => { e.stopPropagation(); deleteFile(value.id); }}>
              <Trash2 className="w-3 h-3 text-red-400" />
            </Button>
          </div>
        );
      }
      
      return (
        <div key={fullPath}>
          <div
            className="flex items-center gap-2 px-2 py-1.5 cursor-pointer hover:bg-zinc-800 rounded text-sm text-zinc-300"
            style={{ paddingLeft: `${depth * 12 + 8}px` }}
            onClick={() => toggleFolder(fullPath)}
          >
            {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            {isExpanded ? <FolderOpen className="w-4 h-4 text-amber-400" /> : <Folder className="w-4 h-4 text-amber-400" />}
            <span>{name}</span>
          </div>
          {isExpanded && renderFileTree(value, fullPath, depth + 1)}
        </div>
      );
    });
  };

  const getAgentIcon = (role) => AGENTS[role]?.icon || Bot;
  const getAgentColor = (role) => AGENTS[role]?.color || "text-zinc-400";
  const getStatusColor = (status) => ({
    idle: "bg-zinc-500", thinking: "bg-amber-500 animate-pulse", working: "bg-blue-500 animate-pulse", completed: "bg-emerald-500"
  }[status] || "bg-zinc-500");
  
  const getPriorityColor = (priority) => ({
    critical: "border-l-red-500 bg-red-500/5", high: "border-l-amber-500 bg-amber-500/5",
    medium: "border-l-blue-500 bg-blue-500/5", low: "border-l-zinc-500 bg-zinc-500/5"
  }[priority] || "border-l-zinc-500");

  const renderCodeBlock = (block, index, messageId) => {
    const blockId = `${messageId}-${index}`;
    return (
      <div key={blockId} className="my-3 rounded-lg overflow-hidden border border-zinc-700">
        <div className="flex items-center justify-between px-3 py-2 bg-zinc-800/50 border-b border-zinc-700">
          <div className="flex items-center gap-2">
            <FileCode className="w-4 h-4 text-blue-400" />
            <span className="text-xs text-zinc-400 font-mono">{block.filepath || block.filename}</span>
            <Badge variant="outline" className="text-[10px] border-zinc-600">{block.language}</Badge>
          </div>
          <div className="flex items-center gap-1">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => copyCode(block.content, blockId)}>
                    {copiedCode === blockId ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Copy</TooltipContent>
              </Tooltip>
            </TooltipProvider>
            {block.filepath && (
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button variant="ghost" size="icon" className="h-7 w-7"
                      onClick={() => {
                        const existingFile = files.find(f => f.filepath === block.filepath);
                        if (existingFile) {
                          setSelectedFile(existingFile);
                          setEditorContent(existingFile.content);
                          setActiveTab("code");
                        }
                      }}>
                      <FileCode className="w-3 h-3" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>Open in editor</TooltipContent>
                </Tooltip>
              </TooltipProvider>
            )}
          </div>
        </div>
        <SyntaxHighlighter language={LANGUAGE_MAP[block.language] || block.language} style={vscDarkPlus}
          customStyle={{ margin: 0, padding: '12px', fontSize: '12px', background: '#0d0d0f', maxHeight: '400px' }} showLineNumbers>
          {block.content}
        </SyntaxHighlighter>
      </div>
    );
  };

  const parseMessageContent = (content, messageId, delegations = []) => {
    const codeBlockRegex = /```(\w+)?(?::([^\n]+))?\n([\s\S]*?)```/g;
    const delegationRegex = /\[DELEGATE:(\w+)\]([\s\S]*?)\[\/DELEGATE\]/g;
    
    // Remove delegation blocks from display (they're shown separately)
    let cleanContent = content.replace(delegationRegex, '');
    
    const parts = [];
    let lastIndex = 0;
    let match;
    let blockIndex = 0;

    while ((match = codeBlockRegex.exec(cleanContent)) !== null) {
      if (match.index > lastIndex) {
        parts.push({ type: 'text', content: cleanContent.slice(lastIndex, match.index) });
      }
      parts.push({
        type: 'code', language: match[1] || 'text', filepath: match[2] || '',
        filename: match[2]?.split('/').pop() || '', content: match[3].trim(), index: blockIndex++
      });
      lastIndex = match.index + match[0].length;
    }
    
    if (lastIndex < cleanContent.length) {
      parts.push({ type: 'text', content: cleanContent.slice(lastIndex) });
    }

    return (
      <>
        {parts.map((part, idx) => {
          if (part.type === 'code') return renderCodeBlock(part, part.index, messageId);
          return <p key={idx} className="whitespace-pre-wrap text-sm text-zinc-200">{part.content}</p>;
        })}
        {delegations?.length > 0 && (
          <div className="mt-3 space-y-2">
            {delegations.map((d, idx) => (
              <div key={idx} className="flex items-center gap-2 p-2 rounded bg-blue-500/10 border border-blue-500/30">
                <ArrowRightCircle className="w-4 h-4 text-blue-400" />
                <span className="text-xs text-blue-400">Delegated to {d.agent}</span>
                <Button size="sm" className="ml-auto h-6 text-xs bg-blue-500 hover:bg-blue-600"
                  onClick={() => executeDelegation(d.agent, d.task)}>
                  Execute
                </Button>
              </div>
            ))}
          </div>
        )}
      </>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#09090b] flex items-center justify-center">
        <Loader2 className="w-10 h-10 text-blue-400 animate-spin" />
      </div>
    );
  }

  const phaseConfig = PHASE_CONFIG[project?.phase] || PHASE_CONFIG.clarification;
  const PhaseIcon = phaseConfig.icon;
  const tasksByStatus = {
    backlog: tasks.filter(t => t.status === "backlog"),
    todo: tasks.filter(t => t.status === "todo"),
    in_progress: tasks.filter(t => t.status === "in_progress"),
    review: tasks.filter(t => t.status === "review"),
    done: tasks.filter(t => t.status === "done")
  };

  return (
    <div className="h-screen bg-[#09090b] flex flex-col overflow-hidden">
      {/* Header */}
      <header className="flex-shrink-0 bg-[#0d0d0f]/95 backdrop-blur-lg border-b border-zinc-800 z-50">
        <div className="px-4 py-2 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate("/dashboard")} data-testid="back-btn">
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="font-rajdhani text-lg font-bold text-white flex items-center gap-2">
                {project?.name}
                <Badge className={`${phaseConfig.color} text-xs`}>
                  <PhaseIcon className="w-3 h-3 mr-1" />{phaseConfig.label}
                </Badge>
              </h1>
              <p className="text-xs text-zinc-500">{project?.type?.replace('_', ' ')} {project?.engine_version && `• ${project.engine_version}`}</p>
            </div>
          </div>
          
          {/* Agent pills */}
          <div className="hidden lg:flex items-center gap-2">
            {agents.map((agent) => {
              const AgentIcon = getAgentIcon(agent.role);
              const isSelected = selectedAgent === agent.id;
              return (
                <TooltipProvider key={agent.id}>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button
                        data-testid={`agent-pill-${agent.name.toLowerCase()}`}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded-full border transition-all ${
                          isSelected ? 'bg-blue-500/20 border-blue-500/50 text-blue-400' : 'bg-zinc-800/50 border-zinc-700 text-zinc-400 hover:border-zinc-600'
                        }`}
                        onClick={() => setSelectedAgent(isSelected ? null : agent.id)}
                      >
                        <div className={`w-2 h-2 rounded-full ${getStatusColor(agent.status)}`} />
                        <AgentIcon className="w-3.5 h-3.5" />
                        <span className="text-xs font-medium">{agent.name}</span>
                      </button>
                    </TooltipTrigger>
                    <TooltipContent>Chat directly with {agent.name}</TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              );
            })}
          </div>

          <div className="flex items-center gap-2">
            <Dialog open={imageDialogOpen} onOpenChange={setImageDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="outline" size="sm" className="border-zinc-700" data-testid="generate-image-btn">
                  <Image className="w-4 h-4 mr-2" />Generate Image
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-[#18181b] border-zinc-700" aria-describedby="img-desc">
                <DialogHeader>
                  <DialogTitle className="font-rajdhani text-white">Generate Game Asset</DialogTitle>
                  <p id="img-desc" className="sr-only">Generate an image for your project</p>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <Textarea
                    placeholder="Describe the image you want to generate..."
                    value={imagePrompt}
                    onChange={(e) => setImagePrompt(e.target.value)}
                    className="bg-zinc-900 border-zinc-700 min-h-[100px]"
                  />
                  <Select value={imageCategory} onValueChange={setImageCategory}>
                    <SelectTrigger className="bg-zinc-900 border-zinc-700">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-zinc-900 border-zinc-700">
                      <SelectItem value="concept">Concept Art</SelectItem>
                      <SelectItem value="character">Character</SelectItem>
                      <SelectItem value="environment">Environment</SelectItem>
                      <SelectItem value="ui">UI Element</SelectItem>
                      <SelectItem value="texture">Texture</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <DialogFooter>
                  <Button onClick={generateImage} disabled={generatingImage || !imagePrompt.trim()} className="bg-blue-500 hover:bg-blue-600">
                    {generatingImage ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Sparkles className="w-4 h-4 mr-2" />}
                    Generate
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
            <Button variant="outline" size="sm" className="border-zinc-700" onClick={exportProject} data-testid="export-btn">
              <Download className="w-4 h-4 mr-2" />Export
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <ResizablePanelGroup direction="horizontal">
          {/* Left Panel */}
          <ResizablePanel defaultSize={45} minSize={30}>
            <div className="h-full flex flex-col bg-[#0a0a0c]">
              <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
                <TabsList className="flex-shrink-0 bg-transparent border-b border-zinc-800 rounded-none px-4 h-11">
                  <TabsTrigger value="chat" className="data-[state=active]:bg-zinc-800" data-testid="chat-tab">
                    <MessageSquare className="w-4 h-4 mr-2" />Chat
                  </TabsTrigger>
                  <TabsTrigger value="tasks" className="data-[state=active]:bg-zinc-800" data-testid="tasks-tab">
                    <ListTodo className="w-4 h-4 mr-2" />Tasks
                    {tasks.length > 0 && <Badge variant="secondary" className="ml-2 text-xs">{tasks.length}</Badge>}
                  </TabsTrigger>
                  <TabsTrigger value="images" className="data-[state=active]:bg-zinc-800" data-testid="images-tab">
                    <Image className="w-4 h-4 mr-2" />Images
                    {images.length > 0 && <Badge variant="secondary" className="ml-2 text-xs">{images.length}</Badge>}
                  </TabsTrigger>
                </TabsList>

                {/* Chat Tab */}
                <TabsContent value="chat" className="flex-1 flex flex-col m-0 overflow-hidden">
                  <ScrollArea className="flex-1 p-4">
                    <div className="space-y-4">
                      {messages.length === 0 && !streamingContent ? (
                        <div className="text-center py-16">
                          <Sparkles className="w-12 h-12 mx-auto mb-4 text-blue-400/50" />
                          <h3 className="font-rajdhani text-xl text-white mb-2">Ready to Build</h3>
                          <p className="text-sm text-zinc-500 max-w-md mx-auto">
                            Describe your project to COMMANDER. I'll ask clarifying questions before we start building.
                          </p>
                        </div>
                      ) : (
                        <>
                          {messages.map((msg) => {
                            const isUser = msg.agent_role === "user";
                            const AgentIcon = getAgentIcon(msg.agent_role);
                            const agent = agents.find(a => a.id === msg.agent_id);
                            
                            return (
                              <motion.div key={msg.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                                className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
                                {!isUser && (
                                  <Avatar className="w-8 h-8 border border-zinc-700 flex-shrink-0 mt-1">
                                    <AvatarImage src={agent?.avatar} />
                                    <AvatarFallback className="bg-zinc-800">
                                      <AgentIcon className={`w-4 h-4 ${getAgentColor(msg.agent_role)}`} />
                                    </AvatarFallback>
                                  </Avatar>
                                )}
                                <div className={`max-w-[85%] ${isUser ? 'ml-auto' : ''}`}>
                                  {!isUser && (
                                    <div className="flex items-center gap-2 mb-1">
                                      <span className="font-rajdhani font-bold text-sm text-blue-400">{msg.agent_name}</span>
                                      <Badge variant="outline" className="text-[10px] border-zinc-700 text-zinc-500">{msg.agent_role}</Badge>
                                      {msg.delegated_to && (
                                        <Badge className="text-[10px] bg-purple-500/20 text-purple-400">delegated</Badge>
                                      )}
                                    </div>
                                  )}
                                  <div className={`rounded-lg px-4 py-3 ${isUser ? 'bg-blue-500 text-white' : 'bg-zinc-800/50 border border-zinc-700/50'}`}>
                                    {isUser ? (
                                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                                    ) : (
                                      parseMessageContent(msg.content, msg.id, msg.delegations)
                                    )}
                                  </div>
                                </div>
                              </motion.div>
                            );
                          })}
                          
                          {/* Streaming message */}
                          {streamingContent && streamingAgent && (
                            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-3">
                              <Avatar className="w-8 h-8 border border-zinc-700 flex-shrink-0 mt-1">
                                <AvatarImage src={streamingAgent.avatar} />
                                <AvatarFallback className="bg-zinc-800">
                                  <Bot className="w-4 h-4 text-blue-400 animate-pulse" />
                                </AvatarFallback>
                              </Avatar>
                              <div className="max-w-[85%]">
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="font-rajdhani font-bold text-sm text-blue-400">{streamingAgent.name}</span>
                                  <Badge className="text-[10px] bg-amber-500/20 text-amber-400 animate-pulse">streaming</Badge>
                                </div>
                                <div className="bg-zinc-800/50 border border-zinc-700/50 rounded-lg px-4 py-3">
                                  {parseMessageContent(streamingContent, 'streaming')}
                                </div>
                              </div>
                            </motion.div>
                          )}
                        </>
                      )}
                      
                      {sending && !streamingContent && (
                        <div className="flex gap-3">
                          <div className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center">
                            <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                          </div>
                          <div className="bg-zinc-800/50 rounded-lg px-4 py-3">
                            <div className="typing-indicator"><span></span><span></span><span></span></div>
                          </div>
                        </div>
                      )}
                      <div ref={chatEndRef} />
                    </div>
                  </ScrollArea>

                  {/* Chat Input */}
                  <div className="flex-shrink-0 p-4 border-t border-zinc-800">
                    {selectedAgent && (
                      <div className="mb-2 flex items-center gap-2">
                        <span className="text-xs text-zinc-500">Speaking to:</span>
                        <Badge className="bg-blue-500/20 text-blue-400 border-0">
                          {agents.find(a => a.id === selectedAgent)?.name}
                        </Badge>
                        <Button variant="ghost" size="sm" className="h-5 px-2" onClick={() => setSelectedAgent(null)}>
                          <X className="w-3 h-3" />
                        </Button>
                      </div>
                    )}
                    <div className="flex gap-2">
                      <Textarea ref={inputRef} data-testid="chat-input"
                        placeholder={project?.phase === "clarification" ? "Describe your project..." : "What should I build next?"}
                        value={chatInput} onChange={(e) => setChatInput(e.target.value)}
                        onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessageStreaming(); }}}
                        className="bg-zinc-900 border-zinc-700 min-h-[80px] resize-none text-sm"
                      />
                      <Button data-testid="send-btn" onClick={sendMessageStreaming} disabled={sending || !chatInput.trim()}
                        className="bg-blue-500 hover:bg-blue-600 px-4 self-end">
                        {sending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                      </Button>
                    </div>
                  </div>
                </TabsContent>

                {/* Tasks Tab */}
                <TabsContent value="tasks" className="flex-1 m-0 overflow-hidden flex flex-col">
                  <div className="flex-shrink-0 p-3 border-b border-zinc-800 flex items-center justify-between">
                    <h3 className="font-rajdhani font-bold text-white text-sm">Task Board</h3>
                    <Dialog open={taskDialogOpen} onOpenChange={setTaskDialogOpen}>
                      <DialogTrigger asChild>
                        <Button size="sm" className="bg-blue-500 hover:bg-blue-600 h-8" data-testid="add-task-btn">
                          <Plus className="w-3 h-3 mr-1" />Add
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="bg-[#18181b] border-zinc-700" aria-describedby="task-desc">
                        <DialogHeader>
                          <DialogTitle className="font-rajdhani text-white">New Task</DialogTitle>
                          <p id="task-desc" className="sr-only">Create a task</p>
                        </DialogHeader>
                        <div className="space-y-3 py-4">
                          <Input placeholder="Task title" value={newTask.title} onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                            className="bg-zinc-900 border-zinc-700" />
                          <Textarea placeholder="Description" value={newTask.description} onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                            className="bg-zinc-900 border-zinc-700" />
                          <div className="grid grid-cols-2 gap-3">
                            <Select value={newTask.priority} onValueChange={(v) => setNewTask({ ...newTask, priority: v })}>
                              <SelectTrigger className="bg-zinc-900 border-zinc-700"><SelectValue /></SelectTrigger>
                              <SelectContent className="bg-zinc-900 border-zinc-700">
                                <SelectItem value="low">Low</SelectItem>
                                <SelectItem value="medium">Medium</SelectItem>
                                <SelectItem value="high">High</SelectItem>
                                <SelectItem value="critical">Critical</SelectItem>
                              </SelectContent>
                            </Select>
                            <Select value={newTask.category} onValueChange={(v) => setNewTask({ ...newTask, category: v })}>
                              <SelectTrigger className="bg-zinc-900 border-zinc-700"><SelectValue /></SelectTrigger>
                              <SelectContent className="bg-zinc-900 border-zinc-700">
                                <SelectItem value="general">General</SelectItem>
                                <SelectItem value="architecture">Architecture</SelectItem>
                                <SelectItem value="coding">Coding</SelectItem>
                                <SelectItem value="assets">Assets</SelectItem>
                                <SelectItem value="testing">Testing</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </div>
                        <DialogFooter>
                          <Button onClick={createTask} className="bg-blue-500 hover:bg-blue-600">Create</Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  </div>
                  
                  <ScrollArea className="flex-1">
                    <div className="p-3 flex gap-3 min-w-max">
                      {Object.entries(tasksByStatus).map(([status, statusTasks]) => (
                        <div key={status} className="w-56 flex-shrink-0 bg-zinc-900/50 rounded-lg border border-zinc-800">
                          <div className="p-2 border-b border-zinc-800">
                            <h4 className="font-rajdhani font-bold text-xs text-white uppercase">{status.replace('_', ' ')}</h4>
                            <span className="text-xs text-zinc-500">{statusTasks.length}</span>
                          </div>
                          <div className="p-2 space-y-2 min-h-[200px]">
                            {statusTasks.map((task) => (
                              <div key={task.id} className={`p-2 rounded bg-zinc-800/50 border-l-2 ${getPriorityColor(task.priority)} text-xs`}>
                                <h5 className="text-white font-medium line-clamp-2 mb-1">{task.title}</h5>
                                {task.description && <p className="text-zinc-500 line-clamp-2 mb-2">{task.description}</p>}
                                <div className="flex items-center justify-between">
                                  <Select value={task.status} onValueChange={(v) => updateTaskStatus(task.id, v)}>
                                    <SelectTrigger className="h-6 w-20 text-[10px] bg-transparent border-zinc-700"><SelectValue /></SelectTrigger>
                                    <SelectContent className="bg-zinc-900 border-zinc-700">
                                      <SelectItem value="backlog">Backlog</SelectItem>
                                      <SelectItem value="todo">To Do</SelectItem>
                                      <SelectItem value="in_progress">In Progress</SelectItem>
                                      <SelectItem value="review">Review</SelectItem>
                                      <SelectItem value="done">Done</SelectItem>
                                    </SelectContent>
                                  </Select>
                                  <Button variant="ghost" size="icon" className="h-5 w-5" onClick={() => deleteTask(task.id)}>
                                    <Trash2 className="w-3 h-3 text-red-400" />
                                  </Button>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </TabsContent>

                {/* Images Tab */}
                <TabsContent value="images" className="flex-1 m-0 p-4 overflow-auto">
                  {images.length === 0 ? (
                    <div className="text-center py-16">
                      <Image className="w-12 h-12 mx-auto mb-4 text-zinc-700" />
                      <h3 className="font-rajdhani text-lg text-white mb-2">No Images Yet</h3>
                      <p className="text-sm text-zinc-500 mb-4">Generate concept art, characters, and assets</p>
                      <Button onClick={() => setImageDialogOpen(true)} className="bg-blue-500 hover:bg-blue-600">
                        <Sparkles className="w-4 h-4 mr-2" />Generate Image
                      </Button>
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 gap-4">
                      {images.map((img) => (
                        <div key={img.id} className="rounded-lg overflow-hidden border border-zinc-800 group">
                          <img src={img.url} alt={img.prompt} className="w-full aspect-square object-cover" />
                          <div className="p-3 bg-zinc-900">
                            <Badge variant="outline" className="text-xs border-zinc-700 mb-2">{img.category}</Badge>
                            <p className="text-xs text-zinc-400 line-clamp-2">{img.prompt}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            </div>
          </ResizablePanel>

          <ResizableHandle withHandle className="bg-zinc-800" />

          {/* Right Panel - Code Editor */}
          <ResizablePanel defaultSize={55} minSize={30}>
            <div className="h-full flex flex-col bg-[#0d0d0f]">
              <div className="flex-shrink-0 flex items-center justify-between px-4 py-2 border-b border-zinc-800 bg-[#0a0a0c]">
                <div className="flex items-center gap-2">
                  <Code2 className="w-4 h-4 text-blue-400" />
                  <span className="font-rajdhani font-bold text-white text-sm">Code Editor</span>
                  {files.length > 0 && <Badge variant="secondary" className="text-xs">{files.length} files</Badge>}
                </div>
                {selectedFile && (
                  <div className="flex items-center gap-2">
                    {unsavedChanges && <Badge className="bg-amber-500/20 text-amber-400 text-xs">Unsaved</Badge>}
                    <Button size="sm" variant="outline" className="h-7 border-zinc-700" onClick={saveFile} disabled={!unsavedChanges}>
                      <Save className="w-3 h-3 mr-1" />Save
                    </Button>
                  </div>
                )}
              </div>

              <ResizablePanelGroup direction="horizontal" className="flex-1">
                <ResizablePanel defaultSize={25} minSize={15} maxSize={40}>
                  <div className="h-full flex flex-col bg-[#0a0a0c] border-r border-zinc-800">
                    <div className="flex-shrink-0 px-3 py-2 border-b border-zinc-800">
                      <h4 className="text-xs text-zinc-500 uppercase tracking-wider">Files</h4>
                    </div>
                    <ScrollArea className="flex-1">
                      <div className="py-2">
                        {files.length === 0 ? (
                          <div className="px-4 py-8 text-center">
                            <Folder className="w-8 h-8 mx-auto mb-2 text-zinc-700" />
                            <p className="text-xs text-zinc-600">No files yet</p>
                          </div>
                        ) : renderFileTree(buildFileTree())}
                      </div>
                    </ScrollArea>
                  </div>
                </ResizablePanel>

                <ResizableHandle className="bg-zinc-800" />

                <ResizablePanel defaultSize={75}>
                  <div className="h-full flex flex-col">
                    {selectedFile ? (
                      <>
                        <div className="flex-shrink-0 px-4 py-2 border-b border-zinc-800 bg-[#0d0d0f] flex items-center gap-2">
                          <FileCode className="w-4 h-4 text-zinc-500" />
                          <span className="text-sm text-zinc-300 font-mono">{selectedFile.filepath}</span>
                          <Badge variant="outline" className="text-[10px] border-zinc-700 ml-auto">v{selectedFile.version || 1}</Badge>
                        </div>
                        <div className="flex-1">
                          <Editor height="100%" language={LANGUAGE_MAP[selectedFile.language] || selectedFile.language}
                            value={editorContent} onChange={(v) => { setEditorContent(v || ""); setUnsavedChanges(v !== selectedFile.content); }}
                            theme="vs-dark" options={{ minimap: { enabled: true }, fontSize: 13, fontFamily: "'JetBrains Mono', monospace",
                              lineNumbers: 'on', scrollBeyondLastLine: false, automaticLayout: true, tabSize: 2, wordWrap: 'on', padding: { top: 12 }}}
                          />
                        </div>
                      </>
                    ) : (
                      <div className="h-full flex items-center justify-center text-center">
                        <div>
                          <FileCode className="w-16 h-16 mx-auto mb-4 text-zinc-800" />
                          <h3 className="font-rajdhani text-lg text-zinc-600 mb-2">No File Selected</h3>
                          <p className="text-sm text-zinc-700">Select a file or ask an agent to generate code</p>
                        </div>
                      </div>
                    )}
                  </div>
                </ResizablePanel>
              </ResizablePanelGroup>
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </div>
  );
};

export default ProjectWorkspace;
