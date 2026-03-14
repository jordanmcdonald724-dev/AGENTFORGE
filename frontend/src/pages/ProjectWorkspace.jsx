import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import { toast } from "sonner";
import Editor from "@monaco-editor/react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { 
  ArrowLeft, Send, Code2, Layers, Users, Shield, Zap, Loader2, FileCode, ListTodo, MessageSquare,
  Folder, FolderOpen, ChevronRight, ChevronDown, Download, Copy, Check, Image,
  Sparkles, Github, Play, Package, Volume2, Rocket, Brain, Terminal, Settings, 
  PanelLeftClose, PanelLeft, Plus, MoreHorizontal, Palette, BookOpen
} from "lucide-react";
import { API } from "@/App";

const LANGUAGE_MAP = {
  cpp: "cpp", "c++": "cpp", csharp: "csharp", "c#": "csharp", cs: "csharp",
  javascript: "javascript", js: "javascript", typescript: "typescript", ts: "typescript",
  python: "python", py: "python", json: "json", html: "html", css: "css",
  yaml: "yaml", yml: "yaml", markdown: "markdown", md: "markdown",
  gdscript: "python", blueprint: "json", hlsl: "cpp", glsl: "cpp"
};

const AGENTS = {
  COMMANDER: { icon: Users, color: "#3b82f6", label: "Lead" },
  ATLAS: { icon: Layers, color: "#06b6d4", label: "Architect" },
  FORGE: { icon: Code2, color: "#10b981", label: "Developer" },
  SENTINEL: { icon: Shield, color: "#f97316", label: "Reviewer" },
  PROBE: { icon: Zap, color: "#8b5cf6", label: "Tester" },
  PRISM: { icon: Palette, color: "#ec4899", label: "Artist" },
};

const SIDEBAR_SECTIONS = [
  {
    title: "Project",
    items: [
      { id: "chat", label: "Chat", icon: MessageSquare },
      { id: "tasks", label: "Tasks", icon: ListTodo },
      { id: "files", label: "Files", icon: FileCode },
    ]
  },
  {
    title: "Build",
    items: [
      { id: "queue", label: "Build Queue", icon: Terminal },
      { id: "blueprints", label: "Blueprints", icon: Layers },
    ]
  },
  {
    title: "Assets",
    items: [
      { id: "images", label: "Images", icon: Image },
      { id: "audio", label: "Audio", icon: Volume2 },
    ]
  },
  {
    title: "Operations",
    items: [
      { id: "deploy", label: "Deploy", icon: Rocket },
      { id: "github", label: "GitHub", icon: Github },
    ]
  }
];

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
  const [loading, setLoading] = useState(true);
  
  const [chatInput, setChatInput] = useState("");
  const [sending, setSending] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [streamingAgent, setStreamingAgent] = useState(null);
  
  const [selectedFile, setSelectedFile] = useState(null);
  const [editorContent, setEditorContent] = useState("");
  const [expandedFolders, setExpandedFolders] = useState(new Set([""]));
  
  const [activePanel, setActivePanel] = useState("chat");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [copiedCode, setCopiedCode] = useState(null);

  useEffect(() => { fetchProjectData(); }, [projectId]);
  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, streamingContent]);

  const fetchProjectData = async () => {
    try {
      const [projectRes, agentsRes, messagesRes, tasksRes, filesRes, imagesRes] = await Promise.all([
        axios.get(`${API}/projects/${projectId}`),
        axios.get(`${API}/agents`),
        axios.get(`${API}/messages?project_id=${projectId}`),
        axios.get(`${API}/tasks?project_id=${projectId}`),
        axios.get(`${API}/files?project_id=${projectId}`),
        axios.get(`${API}/images?project_id=${projectId}`).catch(() => ({ data: [] })),
      ]);
      setProject(projectRes.data);
      setAgents(agentsRes.data);
      setMessages(messagesRes.data);
      setTasks(tasksRes.data);
      setFiles(filesRes.data);
      setImages(imagesRes.data);
    } catch (error) {
      toast.error("Failed to load project");
      navigate("/studio");
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!chatInput.trim() || sending) return;
    
    const userMsg = { role: "user", content: chatInput, agent: "user", created_at: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    setChatInput("");
    setSending(true);
    setStreamingContent("");
    setStreamingAgent("COMMANDER");

    try {
      const response = await fetch(`${API}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: projectId, message: chatInput, agent: "COMMANDER" })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullContent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");
        
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.content) {
                fullContent += data.content;
                setStreamingContent(fullContent);
              }
              if (data.agent) setStreamingAgent(data.agent);
              if (data.done) {
                setMessages(prev => [...prev, { role: "assistant", content: fullContent, agent: data.agent || "COMMANDER", created_at: new Date().toISOString() }]);
                setStreamingContent("");
                setStreamingAgent(null);
              }
            } catch (e) {}
          }
        }
      }
    } catch (error) {
      toast.error("Failed to send message");
    } finally {
      setSending(false);
    }
  };

  const selectFile = (file) => {
    setSelectedFile(file);
    setEditorContent(file.content || "");
  };

  const copyCode = (code, id) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const buildFileTree = (files) => {
    const tree = {};
    files.forEach(file => {
      const parts = file.filepath.split("/").filter(Boolean);
      let current = tree;
      parts.forEach((part, idx) => {
        if (idx === parts.length - 1) {
          current[part] = { ...file, isFile: true };
        } else {
          if (!current[part]) current[part] = {};
          current = current[part];
        }
      });
    });
    return tree;
  };

  const toggleFolder = (path) => {
    setExpandedFolders(prev => {
      const next = new Set(prev);
      if (next.has(path)) next.delete(path);
      else next.add(path);
      return next;
    });
  };

  const renderFileTree = (node, path = "", depth = 0) => {
    return Object.entries(node).map(([name, value]) => {
      const fullPath = path ? `${path}/${name}` : name;
      const isFile = value.isFile;
      const isExpanded = expandedFolders.has(fullPath);

      if (isFile) {
        return (
          <button
            key={fullPath}
            onClick={() => selectFile(value)}
            className={`w-full flex items-center gap-2 px-3 py-1.5 text-sm rounded-lg transition-colors ${
              selectedFile?.filepath === value.filepath
                ? "bg-blue-500/10 text-blue-400"
                : "text-zinc-400 hover:bg-white/5 hover:text-white"
            }`}
            style={{ paddingLeft: `${12 + depth * 16}px` }}
          >
            <FileCode className="w-4 h-4 flex-shrink-0" />
            <span className="truncate">{name}</span>
          </button>
        );
      }

      return (
        <div key={fullPath}>
          <button
            onClick={() => toggleFolder(fullPath)}
            className="w-full flex items-center gap-2 px-3 py-1.5 text-sm text-zinc-400 hover:bg-white/5 hover:text-white rounded-lg transition-colors"
            style={{ paddingLeft: `${12 + depth * 16}px` }}
          >
            {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            {isExpanded ? <FolderOpen className="w-4 h-4 text-blue-400" /> : <Folder className="w-4 h-4" />}
            <span className="truncate">{name}</span>
          </button>
          {isExpanded && renderFileTree(value, fullPath, depth + 1)}
        </div>
      );
    });
  };

  const AgentIcon = ({ agent, size = 5 }) => {
    const config = AGENTS[agent] || { icon: Brain, color: "#fff" };
    const Icon = config.icon;
    return <Icon className={`w-${size} h-${size}`} style={{ color: config.color }} />;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#09090b] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  const fileTree = buildFileTree(files);

  return (
    <div className="h-screen bg-[#09090b] flex flex-col overflow-hidden">
      {/* Header */}
      <header className="flex-shrink-0 h-14 border-b border-white/5 bg-[#09090b]/80 backdrop-blur-xl z-50">
        <div className="h-full px-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button onClick={() => navigate("/studio")} className="p-2 rounded-lg hover:bg-white/5 transition-colors">
              <ArrowLeft className="w-5 h-5 text-zinc-400" />
            </button>
            <div>
              <h1 className="text-sm font-semibold text-white">{project?.name}</h1>
              <p className="text-xs text-zinc-500">{project?.type} • {files.length} files</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              onClick={() => navigate(`/project/${projectId}/god-mode`)}
              size="sm"
              className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-black font-medium gap-2"
            >
              <Zap className="w-4 h-4" />
              God Mode
            </Button>
            <Button onClick={() => navigate("/research")} variant="ghost" size="sm" className="text-zinc-400 hover:text-white">
              <BookOpen className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <motion.aside
          initial={false}
          animate={{ width: sidebarCollapsed ? 48 : 220 }}
          className="flex-shrink-0 border-r border-white/5 bg-[#0c0c0e] flex flex-col"
        >
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="p-3 text-zinc-500 hover:text-white transition-colors"
          >
            {sidebarCollapsed ? <PanelLeft className="w-5 h-5" /> : <PanelLeftClose className="w-5 h-5" />}
          </button>

          <ScrollArea className="flex-1">
            <nav className="p-2">
              {!sidebarCollapsed && SIDEBAR_SECTIONS.map((section, idx) => (
                <div key={section.title} className={idx > 0 ? "mt-6" : ""}>
                  <p className="px-3 mb-2 text-[10px] font-medium text-zinc-600 uppercase tracking-wider">
                    {section.title}
                  </p>
                  {section.items.map(item => (
                    <button
                      key={item.id}
                      onClick={() => setActivePanel(item.id)}
                      className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all ${
                        activePanel === item.id
                          ? "bg-white/5 text-white"
                          : "text-zinc-500 hover:text-white hover:bg-white/[0.02]"
                      }`}
                    >
                      <item.icon className="w-4 h-4 flex-shrink-0" />
                      <span>{item.label}</span>
                    </button>
                  ))}
                </div>
              ))}
              {sidebarCollapsed && (
                <TooltipProvider>
                  {SIDEBAR_SECTIONS.flatMap(s => s.items).map(item => (
                    <Tooltip key={item.id}>
                      <TooltipTrigger asChild>
                        <button
                          onClick={() => setActivePanel(item.id)}
                          className={`w-full p-3 rounded-lg transition-colors ${
                            activePanel === item.id
                              ? "bg-white/5 text-white"
                              : "text-zinc-500 hover:text-white hover:bg-white/[0.02]"
                          }`}
                        >
                          <item.icon className="w-5 h-5 mx-auto" />
                        </button>
                      </TooltipTrigger>
                      <TooltipContent side="right">{item.label}</TooltipContent>
                    </Tooltip>
                  ))}
                </TooltipProvider>
              )}
            </nav>
          </ScrollArea>
        </motion.aside>

        {/* Main Panel */}
        <main className="flex-1 flex overflow-hidden">
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Chat Panel */}
            {activePanel === "chat" && (
              <>
                <ScrollArea className="flex-1 p-4">
                  <div className="max-w-3xl mx-auto space-y-4">
                    {messages.length === 0 && !streamingContent ? (
                      <div className="text-center py-20">
                        <MessageSquare className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-zinc-400 mb-2">Start a conversation</h3>
                        <p className="text-sm text-zinc-600">Describe what you want to build</p>
                      </div>
                    ) : (
                      <>
                        {messages.map((msg, idx) => (
                          <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}
                          >
                            {msg.role !== "user" && (
                              <div 
                                className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                                style={{ backgroundColor: `${AGENTS[msg.agent]?.color || '#3b82f6'}15` }}
                              >
                                <AgentIcon agent={msg.agent} size={4} />
                              </div>
                            )}
                            <div className={`max-w-[80%] ${msg.role === "user" ? "order-first" : ""}`}>
                              {msg.role !== "user" && (
                                <p className="text-xs text-zinc-500 mb-1">{msg.agent}</p>
                              )}
                              <div className={`p-4 rounded-2xl ${
                                msg.role === "user" 
                                  ? "bg-blue-500 text-white rounded-br-sm"
                                  : "bg-white/5 text-zinc-300 rounded-bl-sm"
                              }`}>
                                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                              </div>
                            </div>
                          </motion.div>
                        ))}
                        
                        {/* Streaming Response */}
                        {streamingContent && (
                          <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="flex gap-3"
                          >
                            <div 
                              className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                              style={{ backgroundColor: `${AGENTS[streamingAgent]?.color || '#3b82f6'}15` }}
                            >
                              <AgentIcon agent={streamingAgent} size={4} />
                            </div>
                            <div className="max-w-[80%]">
                              <p className="text-xs text-zinc-500 mb-1">{streamingAgent}</p>
                              <div className="p-4 rounded-2xl bg-white/5 text-zinc-300 rounded-bl-sm">
                                <p className="text-sm whitespace-pre-wrap">{streamingContent}</p>
                                <span className="inline-block w-2 h-4 bg-blue-400 animate-pulse ml-1" />
                              </div>
                            </div>
                          </motion.div>
                        )}
                      </>
                    )}
                    <div ref={chatEndRef} />
                  </div>
                </ScrollArea>

                {/* Chat Input */}
                <div className="flex-shrink-0 p-4 border-t border-white/5">
                  <div className="max-w-3xl mx-auto flex gap-3">
                    <Input
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
                      placeholder="What would you like to build?"
                      className="flex-1 bg-white/5 border-white/10 focus:border-blue-500"
                      disabled={sending}
                    />
                    <Button 
                      onClick={sendMessage} 
                      disabled={!chatInput.trim() || sending}
                      className="bg-blue-500 hover:bg-blue-600"
                    >
                      {sending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                    </Button>
                  </div>
                </div>
              </>
            )}

            {/* Tasks Panel */}
            {activePanel === "tasks" && (
              <ScrollArea className="flex-1 p-4">
                <div className="max-w-3xl mx-auto">
                  <h2 className="text-lg font-semibold text-white mb-4">Tasks</h2>
                  {tasks.length === 0 ? (
                    <div className="text-center py-20">
                      <ListTodo className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-zinc-400 mb-2">No tasks yet</h3>
                      <p className="text-sm text-zinc-600">Tasks will appear as you build</p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {tasks.map(task => (
                        <div key={task.id} className="p-4 rounded-xl bg-white/[0.02] border border-white/5">
                          <h3 className="font-medium text-white">{task.title}</h3>
                          <p className="text-sm text-zinc-500 mt-1">{task.description}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </ScrollArea>
            )}

            {/* Files Panel */}
            {activePanel === "files" && (
              <div className="flex-1 flex overflow-hidden">
                {/* File Tree */}
                <div className="w-64 border-r border-white/5 overflow-hidden flex flex-col">
                  <div className="p-3 border-b border-white/5">
                    <h3 className="text-sm font-medium text-white">Files</h3>
                    <p className="text-xs text-zinc-500">{files.length} files</p>
                  </div>
                  <ScrollArea className="flex-1">
                    <div className="p-2">
                      {files.length === 0 ? (
                        <p className="text-sm text-zinc-600 text-center py-8">No files yet</p>
                      ) : (
                        renderFileTree(fileTree)
                      )}
                    </div>
                  </ScrollArea>
                </div>

                {/* Code Editor */}
                <div className="flex-1 flex flex-col overflow-hidden">
                  {selectedFile ? (
                    <>
                      <div className="p-3 border-b border-white/5 flex items-center justify-between">
                        <div>
                          <h3 className="text-sm font-medium text-white">{selectedFile.filename}</h3>
                          <p className="text-xs text-zinc-500">{selectedFile.filepath}</p>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => copyCode(editorContent, selectedFile.id)}
                          className="text-zinc-400 hover:text-white"
                        >
                          {copiedCode === selectedFile.id ? (
                            <Check className="w-4 h-4 text-emerald-400" />
                          ) : (
                            <Copy className="w-4 h-4" />
                          )}
                        </Button>
                      </div>
                      <div className="flex-1">
                        <Editor
                          height="100%"
                          language={LANGUAGE_MAP[selectedFile.language] || "cpp"}
                          value={editorContent}
                          theme="vs-dark"
                          options={{
                            readOnly: true,
                            fontSize: 13,
                            minimap: { enabled: false },
                            scrollBeyondLastLine: false,
                            padding: { top: 16 }
                          }}
                        />
                      </div>
                    </>
                  ) : (
                    <div className="flex-1 flex items-center justify-center">
                      <div className="text-center">
                        <FileCode className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-zinc-400 mb-2">Select a file</h3>
                        <p className="text-sm text-zinc-600">Choose a file from the tree to view</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Images Panel */}
            {activePanel === "images" && (
              <ScrollArea className="flex-1 p-4">
                <div className="max-w-4xl mx-auto">
                  <h2 className="text-lg font-semibold text-white mb-4">Images</h2>
                  {images.length === 0 ? (
                    <div className="text-center py-20">
                      <Image className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-zinc-400 mb-2">No images yet</h3>
                      <p className="text-sm text-zinc-600">Generate images through chat</p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-3 gap-4">
                      {images.map(img => (
                        <div key={img.id} className="rounded-xl overflow-hidden bg-white/5">
                          <img src={img.url} alt={img.prompt} className="w-full aspect-square object-cover" />
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </ScrollArea>
            )}

            {/* Build Queue Panel */}
            {activePanel === "queue" && (
              <ScrollArea className="flex-1 p-4">
                <div className="max-w-3xl mx-auto">
                  <h2 className="text-lg font-semibold text-white mb-4">Build Queue</h2>
                  <div className="text-center py-20">
                    <Terminal className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-zinc-400 mb-2">No builds in queue</h3>
                    <p className="text-sm text-zinc-600 mb-6">Use God Mode for autonomous builds</p>
                    <Button
                      onClick={() => navigate(`/project/${projectId}/god-mode`)}
                      className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-black"
                    >
                      <Zap className="w-4 h-4 mr-2" />
                      Launch God Mode
                    </Button>
                  </div>
                </div>
              </ScrollArea>
            )}

            {/* Blueprints Panel */}
            {activePanel === "blueprints" && (
              <ScrollArea className="flex-1 p-4">
                <div className="max-w-3xl mx-auto">
                  <h2 className="text-lg font-semibold text-white mb-4">Blueprints</h2>
                  <div className="text-center py-20">
                    <Layers className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-zinc-400 mb-2">No blueprints yet</h3>
                    <p className="text-sm text-zinc-600">Create architecture blueprints for your project</p>
                  </div>
                </div>
              </ScrollArea>
            )}

            {/* Audio Panel */}
            {activePanel === "audio" && (
              <ScrollArea className="flex-1 p-4">
                <div className="max-w-3xl mx-auto">
                  <h2 className="text-lg font-semibold text-white mb-4">Audio</h2>
                  <div className="text-center py-20">
                    <Volume2 className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-zinc-400 mb-2">No audio files yet</h3>
                    <p className="text-sm text-zinc-600">Generate audio through chat</p>
                  </div>
                </div>
              </ScrollArea>
            )}

            {/* Deploy Panel */}
            {activePanel === "deploy" && (
              <ScrollArea className="flex-1 p-4">
                <div className="max-w-3xl mx-auto">
                  <h2 className="text-lg font-semibold text-white mb-4">Deploy</h2>
                  <div className="grid gap-4">
                    <div className="p-6 rounded-xl bg-white/[0.02] border border-white/5">
                      <Download className="w-8 h-8 text-blue-400 mb-4" />
                      <h3 className="font-medium text-white mb-2">Download as ZIP</h3>
                      <p className="text-sm text-zinc-500 mb-4">Export your project files as a ZIP archive</p>
                      <Button className="bg-blue-500 hover:bg-blue-600">
                        <Download className="w-4 h-4 mr-2" />
                        Download
                      </Button>
                    </div>
                  </div>
                </div>
              </ScrollArea>
            )}

            {/* GitHub Panel */}
            {activePanel === "github" && (
              <ScrollArea className="flex-1 p-4">
                <div className="max-w-3xl mx-auto">
                  <h2 className="text-lg font-semibold text-white mb-4">GitHub</h2>
                  <div className="p-6 rounded-xl bg-white/[0.02] border border-white/5">
                    <Github className="w-8 h-8 text-white mb-4" />
                    <h3 className="font-medium text-white mb-2">Push to GitHub</h3>
                    <p className="text-sm text-zinc-500 mb-4">Push your project to a GitHub repository</p>
                    <Button className="bg-white text-black hover:bg-zinc-200">
                      <Github className="w-4 h-4 mr-2" />
                      Connect GitHub
                    </Button>
                  </div>
                </div>
              </ScrollArea>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default ProjectWorkspace;
