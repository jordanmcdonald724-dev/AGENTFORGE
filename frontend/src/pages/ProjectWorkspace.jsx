import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import { toast } from "sonner";
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
  DialogClose
} from "@/components/ui/dialog";
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
  GripVertical,
  MoreVertical,
  Trash2
} from "lucide-react";
import { API } from "@/App";

const ProjectWorkspace = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const chatEndRef = useRef(null);
  
  const [project, setProject] = useState(null);
  const [agents, setAgents] = useState([]);
  const [messages, setMessages] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [chatInput, setChatInput] = useState("");
  const [sending, setSending] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [activeTab, setActiveTab] = useState("chat");
  
  // Task dialog state
  const [taskDialogOpen, setTaskDialogOpen] = useState(false);
  const [newTask, setNewTask] = useState({
    title: "",
    description: "",
    priority: "medium"
  });

  useEffect(() => {
    fetchProjectData();
  }, [projectId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchProjectData = async () => {
    try {
      const [projectRes, agentsRes, messagesRes, tasksRes, filesRes] = await Promise.all([
        axios.get(`${API}/projects/${projectId}`),
        axios.get(`${API}/agents`),
        axios.get(`${API}/messages?project_id=${projectId}`),
        axios.get(`${API}/tasks?project_id=${projectId}`),
        axios.get(`${API}/files?project_id=${projectId}`)
      ]);
      setProject(projectRes.data);
      setAgents(agentsRes.data);
      setMessages(messagesRes.data);
      setTasks(tasksRes.data);
      setFiles(filesRes.data);
    } catch (error) {
      toast.error("Failed to load project");
      navigate("/dashboard");
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!chatInput.trim() || sending) return;
    
    setSending(true);
    const userMessage = chatInput;
    setChatInput("");

    // Add user message to UI immediately
    const tempUserMsg = {
      id: `temp-${Date.now()}`,
      project_id: projectId,
      agent_id: "user",
      agent_name: "You",
      agent_role: "user",
      content: userMessage,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);

    try {
      // Update agent status to thinking
      const pm = agents.find(a => a.role === "project_manager");
      if (pm) {
        setAgents(prev => prev.map(a => 
          a.id === pm.id ? { ...a, status: "thinking" } : a
        ));
      }

      const endpoint = selectedAgent 
        ? `${API}/agents/${selectedAgent}/call`
        : `${API}/chat`;
      
      const res = await axios.post(endpoint, {
        project_id: projectId,
        message: userMessage
      });

      // Add agent response
      const agentMsg = {
        id: `agent-${Date.now()}`,
        project_id: projectId,
        agent_id: res.data.agent.id,
        agent_name: res.data.agent.name,
        agent_role: res.data.agent.role,
        content: res.data.response,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, agentMsg]);

      // Reset agent status
      setAgents(prev => prev.map(a => ({ ...a, status: "idle" })));
    } catch (error) {
      toast.error("Failed to send message");
      setAgents(prev => prev.map(a => ({ ...a, status: "idle" })));
    } finally {
      setSending(false);
    }
  };

  const createTask = async () => {
    if (!newTask.title.trim()) {
      toast.error("Task title is required");
      return;
    }
    try {
      const res = await axios.post(`${API}/tasks`, {
        ...newTask,
        project_id: projectId
      });
      setTasks([res.data, ...tasks]);
      setNewTask({ title: "", description: "", priority: "medium" });
      setTaskDialogOpen(false);
      toast.success("Task created");
    } catch (error) {
      toast.error("Failed to create task");
    }
  };

  const updateTaskStatus = async (taskId, status) => {
    try {
      await axios.patch(`${API}/tasks/${taskId}`, { status });
      setTasks(tasks.map(t => t.id === taskId ? { ...t, status } : t));
    } catch (error) {
      toast.error("Failed to update task");
    }
  };

  const deleteTask = async (taskId) => {
    try {
      await axios.delete(`${API}/tasks/${taskId}`);
      setTasks(tasks.filter(t => t.id !== taskId));
      toast.success("Task deleted");
    } catch (error) {
      toast.error("Failed to delete task");
    }
  };

  const getAgentIcon = (role) => {
    switch (role) {
      case "project_manager": return Users;
      case "architect": return Layers;
      case "developer": return Code2;
      case "reviewer": return Shield;
      case "tester": return Zap;
      default: return Bot;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "idle": return "bg-zinc-500";
      case "thinking": return "bg-amber-500 animate-pulse";
      case "working": return "bg-blue-500 animate-pulse";
      case "completed": return "bg-emerald-500";
      default: return "bg-zinc-500";
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case "critical": return "border-l-red-500 bg-red-500/5";
      case "high": return "border-l-amber-500 bg-amber-500/5";
      case "medium": return "border-l-blue-500 bg-blue-500/5";
      case "low": return "border-l-zinc-500 bg-zinc-500/5";
      default: return "border-l-zinc-500";
    }
  };

  const tasksByStatus = {
    backlog: tasks.filter(t => t.status === "backlog"),
    todo: tasks.filter(t => t.status === "todo"),
    in_progress: tasks.filter(t => t.status === "in_progress"),
    review: tasks.filter(t => t.status === "review"),
    done: tasks.filter(t => t.status === "done")
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#09090b] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#09090b] flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-[#0d0d0f]/80 backdrop-blur-lg border-b border-zinc-800">
        <div className="px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              size="icon"
              onClick={() => navigate("/dashboard")}
              data-testid="back-to-dashboard-btn"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="font-rajdhani text-lg font-bold text-white">
                {project?.name}
              </h1>
              <p className="text-xs text-zinc-500 capitalize">
                {project?.type?.replace('_', ' ')}
              </p>
            </div>
          </div>
          
          {/* Agent Status Pills */}
          <div className="hidden md:flex items-center gap-2">
            {agents.map((agent) => {
              const AgentIcon = getAgentIcon(agent.role);
              return (
                <div
                  key={agent.id}
                  data-testid={`workspace-agent-status-${agent.name.toLowerCase()}`}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-full bg-zinc-800/50 border border-zinc-700 cursor-pointer hover:border-blue-500/50 transition-colors ${selectedAgent === agent.id ? 'border-blue-500 bg-blue-500/10' : ''}`}
                  onClick={() => setSelectedAgent(selectedAgent === agent.id ? null : agent.id)}
                >
                  <div className={`w-2 h-2 rounded-full ${getStatusColor(agent.status)}`} />
                  <AgentIcon className="w-3 h-3 text-zinc-400" />
                  <span className="text-xs text-zinc-300">{agent.name}</span>
                </div>
              );
            })}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Chat Panel */}
        <div className="flex-1 flex flex-col border-r border-zinc-800">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
            <TabsList className="bg-transparent border-b border-zinc-800 rounded-none px-4 h-12">
              <TabsTrigger 
                value="chat" 
                data-testid="chat-tab"
                className="data-[state=active]:bg-zinc-800 data-[state=active]:text-white"
              >
                <MessageSquare className="w-4 h-4 mr-2" />
                Chat
              </TabsTrigger>
              <TabsTrigger 
                value="tasks" 
                data-testid="tasks-tab"
                className="data-[state=active]:bg-zinc-800 data-[state=active]:text-white"
              >
                <ListTodo className="w-4 h-4 mr-2" />
                Tasks
              </TabsTrigger>
              <TabsTrigger 
                value="files" 
                data-testid="files-tab"
                className="data-[state=active]:bg-zinc-800 data-[state=active]:text-white"
              >
                <FileCode className="w-4 h-4 mr-2" />
                Files
              </TabsTrigger>
            </TabsList>

            {/* Chat Tab */}
            <TabsContent value="chat" className="flex-1 flex flex-col m-0 p-0">
              <ScrollArea className="flex-1 p-4">
                <div className="space-y-4">
                  {messages.length === 0 ? (
                    <div className="text-center py-20">
                      <Bot className="w-12 h-12 mx-auto mb-4 text-zinc-600" />
                      <h3 className="font-rajdhani text-lg text-white mb-2">
                        Start a Conversation
                      </h3>
                      <p className="text-sm text-zinc-500 max-w-md mx-auto">
                        Tell your AI team what you want to build. NEXUS (Project Manager) 
                        will coordinate with the team to bring your vision to life.
                      </p>
                    </div>
                  ) : (
                    messages.map((msg) => {
                      const isUser = msg.agent_role === "user";
                      const AgentIcon = getAgentIcon(msg.agent_role);
                      const agent = agents.find(a => a.id === msg.agent_id);
                      
                      return (
                        <motion.div
                          key={msg.id}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          data-testid={`message-${msg.id}`}
                          className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}
                        >
                          {!isUser && (
                            <Avatar className="w-8 h-8 border border-zinc-700 flex-shrink-0">
                              <AvatarImage src={agent?.avatar} alt={msg.agent_name} />
                              <AvatarFallback className="bg-zinc-800">
                                <AgentIcon className="w-4 h-4 text-blue-400" />
                              </AvatarFallback>
                            </Avatar>
                          )}
                          <div className={`message-bubble ${isUser ? 'user' : 'agent'} px-4 py-3`}>
                            {!isUser && (
                              <div className="flex items-center gap-2 mb-1">
                                <span className="font-rajdhani font-bold text-sm text-blue-400">
                                  {msg.agent_name}
                                </span>
                                <Badge variant="outline" className="text-[10px] px-1.5 py-0 border-zinc-700 text-zinc-500">
                                  {msg.agent_role.replace('_', ' ')}
                                </Badge>
                              </div>
                            )}
                            <p className="text-sm text-zinc-200 whitespace-pre-wrap">
                              {msg.content}
                            </p>
                          </div>
                        </motion.div>
                      );
                    })
                  )}
                  {sending && (
                    <div className="flex gap-3">
                      <Avatar className="w-8 h-8 border border-zinc-700">
                        <AvatarFallback className="bg-zinc-800">
                          <Bot className="w-4 h-4 text-blue-400" />
                        </AvatarFallback>
                      </Avatar>
                      <div className="message-bubble agent px-4 py-3">
                        <div className="typing-indicator">
                          <span></span>
                          <span></span>
                          <span></span>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>
              </ScrollArea>

              {/* Chat Input */}
              <div className="p-4 border-t border-zinc-800">
                {selectedAgent && (
                  <div className="mb-2 flex items-center gap-2">
                    <span className="text-xs text-zinc-500">Speaking to:</span>
                    <Badge className="bg-blue-500/20 text-blue-400 border-0">
                      {agents.find(a => a.id === selectedAgent)?.name}
                    </Badge>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      className="h-6 px-2 text-xs text-zinc-500"
                      onClick={() => setSelectedAgent(null)}
                    >
                      Clear
                    </Button>
                  </div>
                )}
                <div className="flex gap-2">
                  <Textarea
                    data-testid="chat-input"
                    placeholder={selectedAgent 
                      ? `Ask ${agents.find(a => a.id === selectedAgent)?.name}...`
                      : "Describe what you want to build..."
                    }
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        sendMessage();
                      }
                    }}
                    className="bg-zinc-900 border-zinc-700 min-h-[60px] resize-none"
                  />
                  <Button 
                    data-testid="send-message-btn"
                    onClick={sendMessage}
                    disabled={sending || !chatInput.trim()}
                    className="bg-blue-500 hover:bg-blue-600 px-4"
                  >
                    {sending ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              </div>
            </TabsContent>

            {/* Tasks Tab (Kanban) */}
            <TabsContent value="tasks" className="flex-1 m-0 p-0 overflow-hidden">
              <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
                <h3 className="font-rajdhani font-bold text-white">Task Board</h3>
                <Dialog open={taskDialogOpen} onOpenChange={setTaskDialogOpen}>
                  <DialogTrigger asChild>
                    <Button 
                      data-testid="add-task-btn"
                      size="sm" 
                      className="bg-blue-500 hover:bg-blue-600"
                    >
                      <Plus className="w-4 h-4 mr-1" /> Add Task
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="bg-[#18181b] border-zinc-700" aria-describedby="new-task-desc">
                    <DialogHeader>
                      <DialogTitle className="font-rajdhani text-white">New Task</DialogTitle>
                      <p id="new-task-desc" className="sr-only">Create a new task with title, description and priority</p>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                      <Input
                        data-testid="task-title-input"
                        placeholder="Task title"
                        value={newTask.title}
                        onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                        className="bg-zinc-900 border-zinc-700"
                      />
                      <Textarea
                        data-testid="task-description-input"
                        placeholder="Description"
                        value={newTask.description}
                        onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                        className="bg-zinc-900 border-zinc-700"
                      />
                      <Select 
                        value={newTask.priority} 
                        onValueChange={(v) => setNewTask({ ...newTask, priority: v })}
                      >
                        <SelectTrigger data-testid="task-priority-select" className="bg-zinc-900 border-zinc-700">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-zinc-900 border-zinc-700">
                          <SelectItem value="low">Low</SelectItem>
                          <SelectItem value="medium">Medium</SelectItem>
                          <SelectItem value="high">High</SelectItem>
                          <SelectItem value="critical">Critical</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <DialogFooter>
                      <Button 
                        data-testid="create-task-btn"
                        onClick={createTask}
                        className="bg-blue-500 hover:bg-blue-600"
                      >
                        Create Task
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
              
              <ScrollArea className="flex-1">
                <div className="p-4 flex gap-4 min-w-max">
                  {Object.entries(tasksByStatus).map(([status, statusTasks]) => (
                    <div 
                      key={status}
                      data-testid={`kanban-column-${status}`}
                      className="kanban-column w-64 flex-shrink-0"
                    >
                      <div className="p-3 border-b border-zinc-700">
                        <h4 className="font-rajdhani font-bold text-sm text-white uppercase">
                          {status.replace('_', ' ')}
                        </h4>
                        <span className="text-xs text-zinc-500">{statusTasks.length} tasks</span>
                      </div>
                      <div className="p-2 space-y-2">
                        {statusTasks.map((task) => (
                          <motion.div
                            key={task.id}
                            layout
                            data-testid={`task-card-${task.id}`}
                            className={`p-3 rounded bg-zinc-900 border-l-2 ${getPriorityColor(task.priority)} hover:bg-zinc-800/50 transition-colors`}
                          >
                            <div className="flex items-start justify-between gap-2 mb-2">
                              <h5 className="text-sm text-white font-medium line-clamp-2">
                                {task.title}
                              </h5>
                              <Select 
                                value={task.status}
                                onValueChange={(v) => updateTaskStatus(task.id, v)}
                              >
                                <SelectTrigger className="w-8 h-6 p-0 border-0 bg-transparent">
                                  <MoreVertical className="w-4 h-4 text-zinc-500" />
                                </SelectTrigger>
                                <SelectContent className="bg-zinc-900 border-zinc-700">
                                  <SelectItem value="backlog">Backlog</SelectItem>
                                  <SelectItem value="todo">To Do</SelectItem>
                                  <SelectItem value="in_progress">In Progress</SelectItem>
                                  <SelectItem value="review">Review</SelectItem>
                                  <SelectItem value="done">Done</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>
                            {task.description && (
                              <p className="text-xs text-zinc-500 line-clamp-2 mb-2">
                                {task.description}
                              </p>
                            )}
                            <div className="flex items-center justify-between">
                              <Badge 
                                variant="outline" 
                                className={`text-[10px] border-0 ${
                                  task.priority === 'critical' ? 'bg-red-500/20 text-red-400' :
                                  task.priority === 'high' ? 'bg-amber-500/20 text-amber-400' :
                                  task.priority === 'medium' ? 'bg-blue-500/20 text-blue-400' :
                                  'bg-zinc-500/20 text-zinc-400'
                                }`}
                              >
                                {task.priority}
                              </Badge>
                              <Button 
                                variant="ghost" 
                                size="icon"
                                className="h-6 w-6 text-zinc-500 hover:text-red-400"
                                onClick={() => deleteTask(task.id)}
                              >
                                <Trash2 className="w-3 h-3" />
                              </Button>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </TabsContent>

            {/* Files Tab */}
            <TabsContent value="files" className="flex-1 m-0 p-4">
              {files.length === 0 ? (
                <div className="text-center py-20">
                  <FileCode className="w-12 h-12 mx-auto mb-4 text-zinc-600" />
                  <h3 className="font-rajdhani text-lg text-white mb-2">No Files Yet</h3>
                  <p className="text-sm text-zinc-500">
                    Files generated by agents will appear here
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {files.map((file) => (
                    <div
                      key={file.id}
                      data-testid={`file-card-${file.id}`}
                      className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 hover:border-blue-500/30 transition-colors"
                    >
                      <div className="flex items-center gap-3 mb-2">
                        <FileCode className="w-5 h-5 text-blue-400" />
                        <span className="font-mono text-sm text-white">{file.filename}</span>
                      </div>
                      <p className="text-xs text-zinc-500 mb-2">{file.filepath}</p>
                      <Badge variant="outline" className="text-xs border-zinc-700">
                        {file.language}
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>

        {/* Right Sidebar - Agent Details (Desktop) */}
        <div className="hidden lg:block w-80 bg-[#0d0d0f] border-l border-zinc-800 p-4">
          <h3 className="font-rajdhani font-bold text-white mb-4">AGENT ROSTER</h3>
          <div className="space-y-3">
            {agents.map((agent) => {
              const AgentIcon = getAgentIcon(agent.role);
              const isSelected = selectedAgent === agent.id;
              return (
                <motion.div
                  key={agent.id}
                  data-testid={`sidebar-agent-${agent.name.toLowerCase()}`}
                  className={`p-3 rounded-lg border transition-all cursor-pointer ${
                    isSelected 
                      ? 'bg-blue-500/10 border-blue-500/50' 
                      : 'bg-zinc-900 border-zinc-800 hover:border-zinc-700'
                  }`}
                  onClick={() => setSelectedAgent(isSelected ? null : agent.id)}
                >
                  <div className="flex items-center gap-3">
                    <Avatar className="w-10 h-10 border border-zinc-700">
                      <AvatarImage src={agent.avatar} alt={agent.name} />
                      <AvatarFallback className="bg-zinc-800">
                        <AgentIcon className="w-5 h-5 text-blue-400" />
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-rajdhani font-bold text-white text-sm">
                          {agent.name}
                        </span>
                        <div className={`w-2 h-2 rounded-full ${getStatusColor(agent.status)}`} />
                      </div>
                      <p className="text-xs text-zinc-500 capitalize">
                        {agent.role.replace('_', ' ')}
                      </p>
                    </div>
                  </div>
                  {isSelected && (
                    <motion.p 
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      className="text-xs text-zinc-400 mt-3 pt-3 border-t border-zinc-800"
                    >
                      Click "Send" to speak directly with {agent.name}
                    </motion.p>
                  )}
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectWorkspace;
