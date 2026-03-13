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
import { Progress } from "@/components/ui/progress";
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
  Zap,
  Palette,
  Sparkles,
  Activity,
  FileCode,
  GitBranch,
  Settings,
  ChevronRight
} from "lucide-react";
import { API } from "@/App";

const PROJECT_TYPES = [
  { value: "unreal", label: "Unreal Engine 5", icon: Gamepad2, description: "AAA game development" },
  { value: "unity", label: "Unity", icon: Gamepad2, description: "Cross-platform games" },
  { value: "godot", label: "Godot", icon: Gamepad2, description: "Open source game engine" },
  { value: "web_game", label: "Web Game", icon: Globe, description: "Browser-based games" },
  { value: "web_app", label: "Web Application", icon: Globe, description: "Full-stack web apps" },
  { value: "mobile_app", label: "Mobile App", icon: Smartphone, description: "iOS & Android apps" }
];

const ENGINE_VERSIONS = {
  unreal: ["5.4", "5.3", "5.2", "5.1"],
  unity: ["2023.3 LTS", "2022.3 LTS", "6000.0"],
  godot: ["4.3", "4.2", "4.1"]
};

const Dashboard = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newProject, setNewProject] = useState({
    name: "",
    description: "",
    type: "unreal",
    engine_version: "5.4"
  });

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
      setDialogOpen(false);
      toast.success("Project created");
      navigate(`/project/${res.data.id}`);
    } catch (error) {
      toast.error("Failed to create project");
    }
  };

  const deleteProject = async (projectId, e) => {
    e.stopPropagation();
    try {
      await axios.delete(`${API}/projects/${projectId}`);
      setProjects(projects.filter(p => p.id !== projectId));
      toast.success("Project deleted");
    } catch (error) {
      toast.error("Failed to delete");
    }
  };

  const getTypeConfig = (type) => {
    return PROJECT_TYPES.find(t => t.value === type) || PROJECT_TYPES[0];
  };

  const getAgentIcon = (role) => {
    const icons = { lead: Users, architect: Layers, developer: Code2, reviewer: Shield, tester: Zap, artist: Palette };
    return icons[role] || Bot;
  };

  const getStatusColor = (status) => {
    const colors = { idle: "bg-zinc-500", thinking: "bg-amber-500 animate-pulse", working: "bg-blue-500 animate-pulse", completed: "bg-emerald-500" };
    return colors[status] || "bg-zinc-500";
  };

  const getPhaseProgress = (phase) => {
    const phases = { clarification: 25, planning: 50, development: 75, review: 90, complete: 100 };
    return phases[phase] || 0;
  };

  return (
    <div className="min-h-screen bg-[#09090b]">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-[#0d0d0f]/95 backdrop-blur-lg border-b border-zinc-800">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate("/")} data-testid="back-btn">
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <h1 className="font-rajdhani text-xl font-bold text-white">DEVELOPMENT STUDIO</h1>
                <p className="text-xs text-zinc-500">Your AI-powered game & app factory</p>
              </div>
            </div>
          </div>
          
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button className="bg-blue-500 hover:bg-blue-600" data-testid="new-project-btn">
                <Plus className="w-4 h-4 mr-2" /> New Project
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-[#18181b] border-zinc-700 max-w-lg" aria-describedby="new-project-desc">
              <DialogHeader>
                <DialogTitle className="font-rajdhani text-xl text-white">CREATE PROJECT</DialogTitle>
                <p id="new-project-desc" className="sr-only">Create a new development project</p>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div>
                  <label className="text-sm text-zinc-400 mb-2 block">Project Name</label>
                  <Input
                    data-testid="project-name-input"
                    placeholder="Project Titan"
                    value={newProject.name}
                    onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                    className="bg-zinc-900 border-zinc-700"
                  />
                </div>
                <div>
                  <label className="text-sm text-zinc-400 mb-2 block">Description</label>
                  <Textarea
                    data-testid="project-desc-input"
                    placeholder="Describe your project vision..."
                    value={newProject.description}
                    onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                    className="bg-zinc-900 border-zinc-700 min-h-[80px]"
                  />
                </div>
                <div>
                  <label className="text-sm text-zinc-400 mb-2 block">Project Type</label>
                  <div className="grid grid-cols-2 gap-2">
                    {PROJECT_TYPES.map((type) => {
                      const Icon = type.icon;
                      return (
                        <button
                          key={type.value}
                          data-testid={`type-${type.value}`}
                          onClick={() => setNewProject({ 
                            ...newProject, 
                            type: type.value,
                            engine_version: ENGINE_VERSIONS[type.value]?.[0] || null
                          })}
                          className={`p-3 rounded-lg border text-left transition-all ${
                            newProject.type === type.value
                              ? 'bg-blue-500/20 border-blue-500/50 text-white'
                              : 'bg-zinc-900 border-zinc-700 text-zinc-400 hover:border-zinc-600'
                          }`}
                        >
                          <div className="flex items-center gap-2 mb-1">
                            <Icon className="w-4 h-4" />
                            <span className="text-sm font-medium">{type.label}</span>
                          </div>
                          <p className="text-xs text-zinc-500">{type.description}</p>
                        </button>
                      );
                    })}
                  </div>
                </div>
                {ENGINE_VERSIONS[newProject.type] && (
                  <div>
                    <label className="text-sm text-zinc-400 mb-2 block">Engine Version</label>
                    <Select 
                      value={newProject.engine_version || ENGINE_VERSIONS[newProject.type][0]} 
                      onValueChange={(v) => setNewProject({ ...newProject, engine_version: v })}
                    >
                      <SelectTrigger className="bg-zinc-900 border-zinc-700" data-testid="engine-version-select">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-zinc-900 border-zinc-700">
                        {ENGINE_VERSIONS[newProject.type].map((v) => (
                          <SelectItem key={v} value={v}>{v}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </div>
              <DialogFooter>
                <DialogClose asChild>
                  <Button variant="ghost" className="text-zinc-400">Cancel</Button>
                </DialogClose>
                <Button onClick={createProject} className="bg-blue-500 hover:bg-blue-600" data-testid="create-btn">
                  Create Project
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Agent Team */}
        <section className="mb-10">
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-rajdhani text-2xl font-bold text-white flex items-center gap-2">
              <Activity className="w-6 h-6 text-blue-400" />
              AGENT TEAM
            </h2>
            <Badge variant="outline" className="border-emerald-500/50 text-emerald-400">
              {agents.filter(a => a.status === "idle").length}/{agents.length} Available
            </Badge>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {agents.map((agent) => {
              const AgentIcon = getAgentIcon(agent.role);
              return (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  data-testid={`agent-${agent.name.toLowerCase()}`}
                  className="bg-[#18181b] border border-zinc-800 rounded-lg p-4 hover:border-blue-500/30 transition-colors"
                >
                  <div className="flex items-center gap-3 mb-2">
                    <Avatar className="w-10 h-10 border border-zinc-700">
                      <AvatarImage src={agent.avatar} alt={agent.name} />
                      <AvatarFallback className="bg-zinc-800">
                        <AgentIcon className="w-5 h-5 text-blue-400" />
                      </AvatarFallback>
                    </Avatar>
                    <div className={`w-2.5 h-2.5 rounded-full ${getStatusColor(agent.status)}`} />
                  </div>
                  <h3 className="font-rajdhani font-bold text-white text-sm">{agent.name}</h3>
                  <p className="text-xs text-zinc-500 capitalize">{agent.role.replace('_', ' ')}</p>
                </motion.div>
              );
            })}
          </div>
        </section>

        {/* Projects */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-rajdhani text-2xl font-bold text-white flex items-center gap-2">
              <FolderOpen className="w-6 h-6 text-cyan-400" />
              PROJECTS
            </h2>
            <span className="text-sm text-zinc-500">{projects.length} total</span>
          </div>
          
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-[#18181b] border border-zinc-800 rounded-lg h-56 animate-pulse" />
              ))}
            </div>
          ) : projects.length === 0 ? (
            <div className="text-center py-20 bg-[#18181b] border border-zinc-800 rounded-lg">
              <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-zinc-800 flex items-center justify-center">
                <Gamepad2 className="w-10 h-10 text-zinc-600" />
              </div>
              <h3 className="font-rajdhani text-2xl text-white mb-2">No Projects Yet</h3>
              <p className="text-zinc-500 mb-6 max-w-md mx-auto">
                Start your first AAA project. Your AI team is ready to build games, apps, 
                and everything in between.
              </p>
              <Button onClick={() => setDialogOpen(true)} className="bg-blue-500 hover:bg-blue-600" data-testid="empty-new-btn">
                <Plus className="w-4 h-4 mr-2" /> Create First Project
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projects.map((project) => {
                const typeConfig = getTypeConfig(project.type);
                const TypeIcon = typeConfig.icon;
                return (
                  <motion.div
                    key={project.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    data-testid={`project-${project.id}`}
                    className="bg-[#18181b] border border-zinc-800 rounded-lg overflow-hidden hover:border-blue-500/30 transition-all cursor-pointer group"
                    onClick={() => navigate(`/project/${project.id}`)}
                  >
                    <div className="relative h-32 overflow-hidden">
                      <img 
                        src={project.thumbnail} 
                        alt={project.name}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-[#18181b] via-transparent to-transparent" />
                      <Badge className="absolute top-3 left-3 bg-zinc-900/90 border-zinc-700">
                        <TypeIcon className="w-3 h-3 mr-1" />
                        {typeConfig.label}
                      </Badge>
                      {project.engine_version && (
                        <Badge variant="outline" className="absolute top-3 right-3 border-zinc-700 bg-zinc-900/90 text-xs">
                          {project.engine_version}
                        </Badge>
                      )}
                    </div>
                    <div className="p-4">
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="font-rajdhani font-bold text-white text-lg line-clamp-1">
                          {project.name}
                        </h3>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                            <Button variant="ghost" size="icon" className="h-8 w-8 -mr-2">
                              <MoreVertical className="w-4 h-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent className="bg-zinc-900 border-zinc-700">
                            <DropdownMenuItem 
                              className="text-red-400"
                              onClick={(e) => deleteProject(project.id, e)}
                            >
                              <Trash2 className="w-4 h-4 mr-2" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                      <p className="text-sm text-zinc-500 line-clamp-2 mb-3 min-h-[40px]">
                        {project.description || "No description"}
                      </p>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-zinc-500 capitalize">{project.phase || "clarification"}</span>
                          <span className="text-zinc-600">{getPhaseProgress(project.phase)}%</span>
                        </div>
                        <Progress value={getPhaseProgress(project.phase)} className="h-1" />
                      </div>
                      <div className="flex items-center gap-2 mt-3 pt-3 border-t border-zinc-800">
                        <Clock className="w-3 h-3 text-zinc-600" />
                        <span className="text-xs text-zinc-600">
                          {new Date(project.created_at).toLocaleDateString()}
                        </span>
                        <ChevronRight className="w-4 h-4 text-zinc-600 ml-auto group-hover:text-blue-400 transition-colors" />
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
