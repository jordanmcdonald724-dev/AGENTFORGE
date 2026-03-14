import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
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
  Plus, 
  ArrowLeft,
  MoreHorizontal,
  Trash2,
  Sparkles,
  Gamepad2,
  Globe,
  Smartphone,
  Code2,
  Zap,
  FolderOpen,
  Clock,
  ChevronRight,
  Search,
  Settings,
  Layers,
  Users,
  Shield,
  Palette
} from "lucide-react";
import { API } from "@/App";

const PROJECT_TYPES = [
  { value: "unreal", label: "Unreal Engine 5", icon: Gamepad2 },
  { value: "unity", label: "Unity", icon: Gamepad2 },
  { value: "godot", label: "Godot", icon: Gamepad2 },
  { value: "web_app", label: "Web Application", icon: Globe },
  { value: "mobile_app", label: "Mobile App", icon: Smartphone },
];

const ENGINE_VERSIONS = {
  unreal: ["5.4", "5.3", "5.2"],
  unity: ["2023.3 LTS", "2022.3 LTS"],
  godot: ["4.3", "4.2"],
};

const Dashboard = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
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
      setNewProject({ name: "", description: "", type: "unreal", engine_version: "5.4" });
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

  const getTypeIcon = (type) => {
    const found = PROJECT_TYPES.find(t => t.value === type);
    return found?.icon || Code2;
  };

  const getPhaseProgress = (phase) => {
    const phases = { clarification: 25, planning: 50, development: 75, review: 90, complete: 100 };
    return phases[phase] || 0;
  };

  const filteredProjects = projects.filter(p => 
    p.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const agentList = [
    { name: "COMMANDER", icon: Users, color: "#3b82f6" },
    { name: "ATLAS", icon: Layers, color: "#06b6d4" },
    { name: "FORGE", icon: Code2, color: "#10b981" },
    { name: "SENTINEL", icon: Shield, color: "#f97316" },
    { name: "PROBE", icon: Zap, color: "#8b5cf6" },
    { name: "PRISM", icon: Palette, color: "#ec4899" },
  ];

  return (
    <div className="min-h-screen bg-[#09090b]">
      {/* Background */}
      <div className="fixed inset-0 gradient-mesh opacity-30" />
      
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-[#09090b]/80 border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button 
                onClick={() => navigate("/")}
                className="p-2 rounded-lg hover:bg-white/5 transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-zinc-400" />
              </button>
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-white">Studio</h1>
                  <p className="text-xs text-zinc-500">Your projects</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <button 
                onClick={() => navigate("/settings")}
                className="p-2 rounded-lg hover:bg-white/5 transition-colors"
              >
                <Settings className="w-5 h-5 text-zinc-400" />
              </button>
              
              <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <DialogTrigger asChild>
                  <Button 
                    className="bg-blue-500 hover:bg-blue-600 text-white gap-2"
                    data-testid="new-project-btn"
                  >
                    <Plus className="w-4 h-4" />
                    New Project
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-[#141417] border-white/10 max-w-md">
                  <DialogHeader>
                    <DialogTitle className="text-xl text-white">Create Project</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-5 py-4">
                    <div>
                      <label className="text-sm text-zinc-400 mb-2 block">Name</label>
                      <Input
                        data-testid="project-name-input"
                        placeholder="My Awesome Project"
                        value={newProject.name}
                        onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                        className="bg-white/5 border-white/10 focus:border-blue-500"
                      />
                    </div>
                    <div>
                      <label className="text-sm text-zinc-400 mb-2 block">Description</label>
                      <Textarea
                        data-testid="project-desc-input"
                        placeholder="Describe your project..."
                        value={newProject.description}
                        onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                        className="bg-white/5 border-white/10 focus:border-blue-500 min-h-[100px]"
                      />
                    </div>
                    <div>
                      <label className="text-sm text-zinc-400 mb-2 block">Type</label>
                      <Select
                        value={newProject.type}
                        onValueChange={(v) => setNewProject({ ...newProject, type: v, engine_version: ENGINE_VERSIONS[v]?.[0] || "" })}
                      >
                        <SelectTrigger className="bg-white/5 border-white/10">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-[#1a1a1f] border-white/10">
                          {PROJECT_TYPES.map(type => (
                            <SelectItem key={type.value} value={type.value}>
                              <div className="flex items-center gap-2">
                                <type.icon className="w-4 h-4" />
                                {type.label}
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    {ENGINE_VERSIONS[newProject.type] && (
                      <div>
                        <label className="text-sm text-zinc-400 mb-2 block">Version</label>
                        <Select
                          value={newProject.engine_version}
                          onValueChange={(v) => setNewProject({ ...newProject, engine_version: v })}
                        >
                          <SelectTrigger className="bg-white/5 border-white/10">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent className="bg-[#1a1a1f] border-white/10">
                            {ENGINE_VERSIONS[newProject.type].map(v => (
                              <SelectItem key={v} value={v}>{v}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    )}
                    <Button 
                      onClick={createProject} 
                      className="w-full bg-blue-500 hover:bg-blue-600"
                    >
                      Create Project
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>
      </header>

      <main className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        {/* Agent Status Bar */}
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 p-4 rounded-xl bg-white/[0.02] border border-white/5"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              {agentList.map(agent => (
                <div key={agent.name} className="flex items-center gap-2">
                  <div 
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: agent.color }}
                  />
                  <span className="text-xs text-zinc-500">{agent.name}</span>
                </div>
              ))}
            </div>
            <Badge variant="outline" className="border-emerald-500/30 text-emerald-400 text-xs">
              6/6 Available
            </Badge>
          </div>
        </motion.div>

        {/* Search */}
        <div className="mb-8">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
            <Input
              placeholder="Search projects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 bg-white/5 border-white/10 focus:border-blue-500"
            />
          </div>
        </div>

        {/* Projects Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-white">Projects</h2>
          <span className="text-sm text-zinc-500">{filteredProjects.length} total</span>
        </div>

        {/* Projects Grid */}
        {loading ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-48 rounded-xl bg-white/5 animate-pulse" />
            ))}
          </div>
        ) : filteredProjects.length === 0 ? (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-20"
          >
            <FolderOpen className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-zinc-400 mb-2">
              {searchQuery ? "No matching projects" : "No projects yet"}
            </h3>
            <p className="text-sm text-zinc-600 mb-6">
              {searchQuery ? "Try a different search" : "Create your first project to get started"}
            </p>
            {!searchQuery && (
              <Button 
                onClick={() => setDialogOpen(true)}
                className="bg-blue-500 hover:bg-blue-600"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Project
              </Button>
            )}
          </motion.div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            <AnimatePresence>
              {filteredProjects.map((project, idx) => {
                const TypeIcon = getTypeIcon(project.type);
                const progress = getPhaseProgress(project.phase);
                
                return (
                  <motion.div
                    key={project.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    transition={{ delay: idx * 0.05 }}
                    onClick={() => navigate(`/project/${project.id}`)}
                    className="group relative p-5 rounded-xl bg-white/[0.02] border border-white/5 hover:border-white/10 hover:bg-white/[0.04] transition-all cursor-pointer"
                  >
                    {/* Type Icon */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="p-2.5 rounded-lg bg-white/5">
                        <TypeIcon className="w-5 h-5 text-zinc-400" />
                      </div>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                          <button className="p-1.5 rounded-lg hover:bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity">
                            <MoreHorizontal className="w-4 h-4 text-zinc-400" />
                          </button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent className="bg-[#1a1a1f] border-white/10">
                          <DropdownMenuItem 
                            onClick={(e) => deleteProject(project.id, e)}
                            className="text-red-400 focus:text-red-400"
                          >
                            <Trash2 className="w-4 h-4 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>

                    {/* Project Info */}
                    <h3 className="text-base font-semibold text-white mb-1 truncate">
                      {project.name}
                    </h3>
                    <p className="text-sm text-zinc-500 mb-4 line-clamp-2 min-h-[40px]">
                      {project.description || "No description"}
                    </p>

                    {/* Meta Info */}
                    <div className="flex items-center gap-4 text-xs text-zinc-500 mb-4">
                      <span className="capitalize">{project.type?.replace('_', ' ')}</span>
                      {project.engine_version && (
                        <>
                          <span>•</span>
                          <span>{project.engine_version}</span>
                        </>
                      )}
                    </div>

                    {/* Progress */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-zinc-500 capitalize">{project.phase || 'New'}</span>
                        <span className="text-zinc-400">{progress}%</span>
                      </div>
                      <Progress value={progress} className="h-1 bg-white/5" />
                    </div>

                    {/* Quick Actions */}
                    <div className="flex items-center gap-2 mt-4 pt-4 border-t border-white/5">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/project/${project.id}`);
                        }}
                        className="flex-1 text-xs h-8 hover:bg-white/5"
                      >
                        Open
                      </Button>
                      <Button
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/project/${project.id}/god-mode`);
                        }}
                        className="flex-1 text-xs h-8 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-black font-medium"
                      >
                        <Zap className="w-3 h-3 mr-1" />
                        God Mode
                      </Button>
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
