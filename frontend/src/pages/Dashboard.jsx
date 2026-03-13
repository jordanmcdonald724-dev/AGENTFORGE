import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { 
  Bot, 
  Plus, 
  FolderOpen, 
  Clock, 
  MoreVertical,
  Trash2,
  ArrowLeft,
  Gamepad2,
  Globe,
  Smartphone,
  Code2,
  Layers,
  Users,
  Shield,
  Zap
} from "lucide-react";
import { API } from "@/App";

const Dashboard = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newProject, setNewProject] = useState({
    name: "",
    description: "",
    type: "web_app"
  });
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [projectsRes, agentsRes] = await Promise.all([
        axios.get(`${API}/projects`),
        axios.get(`${API}/agents`)
      ]);
      setProjects(projectsRes.data);
      setAgents(agentsRes.data);
    } catch (error) {
      toast.error("Failed to fetch data");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const createProject = async () => {
    if (!newProject.name.trim()) {
      toast.error("Project name is required");
      return;
    }
    try {
      const res = await axios.post(`${API}/projects`, newProject);
      setProjects([res.data, ...projects]);
      setNewProject({ name: "", description: "", type: "web_app" });
      setDialogOpen(false);
      toast.success("Project created successfully");
      navigate(`/project/${res.data.id}`);
    } catch (error) {
      toast.error("Failed to create project");
    }
  };

  const deleteProject = async (projectId) => {
    try {
      await axios.delete(`${API}/projects/${projectId}`);
      setProjects(projects.filter(p => p.id !== projectId));
      toast.success("Project deleted");
    } catch (error) {
      toast.error("Failed to delete project");
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case "game": return <Gamepad2 className="w-4 h-4" />;
      case "unreal_project": return <Gamepad2 className="w-4 h-4" />;
      case "web_app": return <Globe className="w-4 h-4" />;
      case "mobile_app": return <Smartphone className="w-4 h-4" />;
      default: return <Code2 className="w-4 h-4" />;
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

  return (
    <div className="min-h-screen bg-[#09090b]">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-[#0d0d0f]/80 backdrop-blur-lg border-b border-zinc-800">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              size="icon"
              onClick={() => navigate("/")}
              data-testid="back-to-home-btn"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div className="flex items-center gap-2">
              <Bot className="w-6 h-6 text-blue-400" />
              <span className="font-rajdhani text-xl font-bold text-white">
                COMMAND CENTER
              </span>
            </div>
          </div>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button 
                data-testid="new-project-btn"
                className="bg-blue-500 hover:bg-blue-600"
              >
                <Plus className="w-4 h-4 mr-2" /> New Project
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-[#18181b] border-zinc-700">
              <DialogHeader>
                <DialogTitle className="font-rajdhani text-xl text-white">
                  CREATE NEW PROJECT
                </DialogTitle>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div>
                  <label className="text-sm text-zinc-400 mb-2 block">Project Name</label>
                  <Input
                    data-testid="project-name-input"
                    placeholder="My Awesome Project"
                    value={newProject.name}
                    onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                    className="bg-zinc-900 border-zinc-700"
                  />
                </div>
                <div>
                  <label className="text-sm text-zinc-400 mb-2 block">Description</label>
                  <Textarea
                    data-testid="project-description-input"
                    placeholder="Describe what you want to build..."
                    value={newProject.description}
                    onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                    className="bg-zinc-900 border-zinc-700 min-h-[100px]"
                  />
                </div>
                <div>
                  <label className="text-sm text-zinc-400 mb-2 block">Project Type</label>
                  <Select 
                    value={newProject.type} 
                    onValueChange={(value) => setNewProject({ ...newProject, type: value })}
                  >
                    <SelectTrigger data-testid="project-type-select" className="bg-zinc-900 border-zinc-700">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-zinc-900 border-zinc-700">
                      <SelectItem value="web_app">Web Application</SelectItem>
                      <SelectItem value="game">Game</SelectItem>
                      <SelectItem value="unreal_project">Unreal Engine Project</SelectItem>
                      <SelectItem value="mobile_app">Mobile App</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <DialogFooter>
                <DialogClose asChild>
                  <Button variant="ghost" className="text-zinc-400">Cancel</Button>
                </DialogClose>
                <Button 
                  data-testid="create-project-btn"
                  onClick={createProject}
                  className="bg-blue-500 hover:bg-blue-600"
                >
                  Create Project
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Agent Team Status */}
        <section className="mb-10">
          <h2 className="font-rajdhani text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <Users className="w-6 h-6 text-blue-400" />
            AGENT TEAM STATUS
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {agents.map((agent) => {
              const AgentIcon = getAgentIcon(agent.role);
              return (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  data-testid={`dashboard-agent-${agent.name.toLowerCase()}`}
                  className="bg-[#18181b] border border-zinc-800 rounded-lg p-4 hover:border-blue-500/30 transition-colors"
                >
                  <div className="flex items-center gap-3 mb-3">
                    <Avatar className="w-10 h-10 border border-zinc-700">
                      <AvatarImage src={agent.avatar} alt={agent.name} />
                      <AvatarFallback className="bg-zinc-800">
                        <AgentIcon className="w-5 h-5 text-blue-400" />
                      </AvatarFallback>
                    </Avatar>
                    <div className={`w-2 h-2 rounded-full ${getStatusColor(agent.status)}`} />
                  </div>
                  <h3 className="font-rajdhani font-bold text-white text-sm">{agent.name}</h3>
                  <p className="text-xs text-zinc-500 capitalize">{agent.role.replace('_', ' ')}</p>
                </motion.div>
              );
            })}
          </div>
        </section>

        {/* Projects Grid */}
        <section>
          <h2 className="font-rajdhani text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <FolderOpen className="w-6 h-6 text-cyan-400" />
            PROJECTS
          </h2>
          
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-[#18181b] border border-zinc-800 rounded-lg h-48 animate-pulse" />
              ))}
            </div>
          ) : projects.length === 0 ? (
            <div className="text-center py-20">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-zinc-800 flex items-center justify-center">
                <FolderOpen className="w-8 h-8 text-zinc-600" />
              </div>
              <h3 className="font-rajdhani text-xl text-white mb-2">No Projects Yet</h3>
              <p className="text-zinc-500 mb-6">Create your first project to get started</p>
              <Button 
                data-testid="empty-state-new-project-btn"
                onClick={() => setDialogOpen(true)}
                className="bg-blue-500 hover:bg-blue-600"
              >
                <Plus className="w-4 h-4 mr-2" /> Create Project
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projects.map((project) => (
                <motion.div
                  key={project.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  data-testid={`project-card-${project.id}`}
                  className="bg-[#18181b] border border-zinc-800 rounded-lg overflow-hidden hover:border-blue-500/30 transition-all cursor-pointer group"
                  onClick={() => navigate(`/project/${project.id}`)}
                >
                  <div className="relative h-32 overflow-hidden">
                    <img 
                      src={project.thumbnail} 
                      alt={project.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-[#18181b] to-transparent" />
                    <Badge 
                      className="absolute top-3 left-3 bg-zinc-900/80 text-zinc-300 border-zinc-700"
                    >
                      {getTypeIcon(project.type)}
                      <span className="ml-1 capitalize">{project.type.replace('_', ' ')}</span>
                    </Badge>
                  </div>
                  <div className="p-4">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-rajdhani font-bold text-white text-lg line-clamp-1">
                        {project.name}
                      </h3>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <MoreVertical className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent className="bg-zinc-900 border-zinc-700">
                          <DropdownMenuItem 
                            data-testid={`delete-project-${project.id}`}
                            className="text-red-400 focus:text-red-400"
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteProject(project.id);
                            }}
                          >
                            <Trash2 className="w-4 h-4 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                    <p className="text-sm text-zinc-500 line-clamp-2 mb-3">
                      {project.description || "No description"}
                    </p>
                    <div className="flex items-center gap-2 text-xs text-zinc-600">
                      <Clock className="w-3 h-3" />
                      <span>{new Date(project.created_at).toLocaleDateString()}</span>
                      <Badge variant="outline" className="ml-auto text-xs capitalize border-zinc-700">
                        {project.status}
                      </Badge>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
