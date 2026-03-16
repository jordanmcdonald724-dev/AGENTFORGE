import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { 
  Users, Plus, Bot, Loader2, Zap, Trash2, RefreshCw, Brain, Code, 
  Shield, TestTube, Server, Palette
} from "lucide-react";
import { API } from "@/App";

const SPECIALTY_ICONS = {
  api: Server,
  database: Code,
  ui: Palette,
  security: Shield,
  testing: TestTube,
  devops: Server,
  default: Bot
};

const DynamicAgentsPanel = ({ projectId }) => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [spawning, setSpawning] = useState(false);
  const [autoSpawning, setAutoSpawning] = useState(false);
  
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [form, setForm] = useState({ name: "", specialty: "", description: "" });

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/dynamic-agents`);
      setAgents(res.data || []);
    } catch (e) {}
    finally { setLoading(false); }
  };

  const spawnAgent = async () => {
    if (!form.name || !form.specialty) {
      toast.error("Name and specialty required");
      return;
    }
    setSpawning(true);
    try {
      await axios.post(`${API}/dynamic-agents/spawn`, null, {
        params: { 
          name: form.name, 
          specialty: form.specialty, 
          description: form.description || `Specialized agent for ${form.specialty}`,
          created_by: "COMMANDER"
        }
      });
      toast.success(`Agent ${form.name} spawned!`);
      setCreateDialogOpen(false);
      setForm({ name: "", specialty: "", description: "" });
      fetchAgents();
    } catch (e) {
      toast.error("Failed to spawn agent");
    } finally {
      setSpawning(false);
    }
  };

  const autoSpawnAgents = async () => {
    if (!projectId) {
      toast.error("No project selected");
      return;
    }
    setAutoSpawning(true);
    try {
      const res = await axios.post(`${API}/dynamic-agents/auto-spawn`, null, {
        params: { project_id: projectId }
      });
      toast.success(`Auto-spawned ${res.data.agents_spawned?.length || 0} agents!`);
      fetchAgents();
    } catch (e) {
      toast.error("Auto-spawn failed");
    } finally {
      setAutoSpawning(false);
    }
  };

  const deactivateAgent = async (agentId) => {
    try {
      await axios.delete(`${API}/dynamic-agents/${agentId}`);
      toast.success("Agent deactivated");
      fetchAgents();
    } catch (e) {
      toast.error("Failed to deactivate");
    }
  };

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]" data-testid="dynamic-agents-panel">
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-violet-400" />
            <span className="font-rajdhani font-bold text-white">Self-Expanding Agents</span>
            <Badge variant="outline" className="text-xs border-zinc-700">
              {agents.filter(a => a.active).length} active
            </Badge>
          </div>
          <div className="flex gap-2">
            <Button
              onClick={autoSpawnAgents}
              disabled={autoSpawning || !projectId}
              variant="outline"
              size="sm"
              className="border-violet-500/30 text-violet-400"
              data-testid="auto-spawn-btn"
            >
              {autoSpawning ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Brain className="w-4 h-4 mr-1" />}
              Auto-Detect
            </Button>
            <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-violet-500 hover:bg-violet-600" data-testid="spawn-agent-btn">
                  <Plus className="w-4 h-4 mr-1" />Spawn Agent
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-[#18181b] border-zinc-700">
                <DialogHeader>
                  <DialogTitle className="font-rajdhani text-white flex items-center gap-2">
                    <Bot className="w-5 h-5 text-violet-400" />Spawn New Agent
                  </DialogTitle>
                </DialogHeader>
                <div className="py-4 space-y-4">
                  <Input
                    placeholder="Agent name (e.g., 'API_MASTER')"
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value.toUpperCase().replace(/\s/g, '_') })}
                    className="bg-zinc-900 border-zinc-700"
                  />
                  <Input
                    placeholder="Specialty (e.g., 'api', 'database', 'ui', 'security', 'testing', 'devops')"
                    value={form.specialty}
                    onChange={(e) => setForm({ ...form, specialty: e.target.value.toLowerCase() })}
                    className="bg-zinc-900 border-zinc-700"
                  />
                  <Input
                    placeholder="Description (optional)"
                    value={form.description}
                    onChange={(e) => setForm({ ...form, description: e.target.value })}
                    className="bg-zinc-900 border-zinc-700"
                  />
                </div>
                <DialogFooter>
                  <Button onClick={spawnAgent} disabled={spawning} className="bg-violet-500 hover:bg-violet-600">
                    {spawning ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Zap className="w-4 h-4 mr-1" />}
                    Spawn Agent
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </div>

      <ScrollArea className="flex-1 p-4">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-zinc-500" />
          </div>
        ) : agents.length === 0 ? (
          <div className="text-center py-12">
            <Users className="w-12 h-12 mx-auto mb-4 text-zinc-700" />
            <h3 className="font-rajdhani text-lg text-white mb-2">Self-Expanding System</h3>
            <p className="text-sm text-zinc-500 mb-4">
              Agents can create new specialized agents
            </p>
            <p className="text-xs text-zinc-600">
              Click "Auto-Detect" to spawn agents based on project needs
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-3">
            {agents.map((agent) => {
              const Icon = SPECIALTY_ICONS[agent.specialty] || SPECIALTY_ICONS.default;
              return (
                <div key={agent.id} className={`p-4 rounded-lg bg-zinc-900 border ${agent.active ? 'border-violet-500/30' : 'border-zinc-800 opacity-50'}`}>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <div className="p-2 rounded-lg bg-violet-500/10">
                        <Icon className="w-5 h-5 text-violet-400" />
                      </div>
                      <div>
                        <h4 className="font-medium text-white">{agent.name}</h4>
                        <Badge variant="outline" className="text-xs border-zinc-700 mt-1">
                          {agent.specialty}
                        </Badge>
                      </div>
                    </div>
                    <Button
                      onClick={() => deactivateAgent(agent.id)}
                      variant="ghost"
                      size="sm"
                      className="text-red-400 hover:bg-red-500/10"
                    >
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                  
                  <p className="text-xs text-zinc-500 mt-3">{agent.description}</p>
                  
                  <div className="flex flex-wrap gap-1 mt-3">
                    {agent.capabilities?.slice(0, 4).map((cap, i) => (
                      <span key={i} className="text-xs px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400">
                        {cap}
                      </span>
                    ))}
                  </div>
                  
                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-zinc-800">
                    <span className="text-xs text-zinc-600">Created by {agent.created_by}</span>
                    <span className="text-xs text-zinc-600">{agent.tasks_handled} tasks</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </ScrollArea>
    </div>
  );
};

export default DynamicAgentsPanel;
