import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { 
  Zap, Plus, Rocket, Loader2, Globe, Gamepad2, Smartphone, Server, Code, CheckCircle
} from "lucide-react";
import { API } from "@/App";

const SaaSBuilderPanel = ({ onProjectCreated }) => {
  const [blueprints, setBlueprints] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [building, setBuilding] = useState(null);
  
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [form, setForm] = useState({ name: "", description: "" });

  useEffect(() => {
    fetchBlueprints();
  }, []);

  const fetchBlueprints = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/saas/blueprints`);
      setBlueprints(res.data || []);
    } catch (e) {}
    finally { setLoading(false); }
  };

  const generateBlueprint = async () => {
    if (!form.name || !form.description) {
      toast.error("Name and description required");
      return;
    }
    setGenerating(true);
    try {
      const res = await axios.post(`${API}/saas/generate`, null, {
        params: { name: form.name, description: form.description }
      });
      toast.success("SaaS blueprint generated!");
      setCreateDialogOpen(false);
      setForm({ name: "", description: "" });
      fetchBlueprints();
    } catch (e) {
      toast.error("Generation failed");
    } finally {
      setGenerating(false);
    }
  };

  const buildFromBlueprint = async (blueprintId) => {
    setBuilding(blueprintId);
    try {
      const res = await axios.post(`${API}/saas/blueprint/${blueprintId}/build`);
      toast.success(`Project created: ${res.data.project_id}`);
      if (onProjectCreated) onProjectCreated(res.data.project_id);
    } catch (e) {
      toast.error("Build failed");
    } finally {
      setBuilding(null);
    }
  };

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]" data-testid="saas-builder-panel">
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-emerald-400" />
            <span className="font-rajdhani font-bold text-white">One-Click SaaS Builder</span>
          </div>
          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button className="bg-emerald-500 hover:bg-emerald-600" data-testid="new-saas-btn">
                <Plus className="w-4 h-4 mr-1" />New SaaS
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-[#18181b] border-zinc-700 max-w-lg">
              <DialogHeader>
                <DialogTitle className="font-rajdhani text-white flex items-center gap-2">
                  <Zap className="w-5 h-5 text-emerald-400" />Generate SaaS Blueprint
                </DialogTitle>
              </DialogHeader>
              <div className="py-4 space-y-4">
                <Input
                  placeholder="SaaS Name (e.g., 'TaskMaster Pro')"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="bg-zinc-900 border-zinc-700"
                />
                <Input
                  placeholder="Description (e.g., 'AI-powered task management for teams')"
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  className="bg-zinc-900 border-zinc-700"
                />
                <div className="p-3 rounded-lg bg-zinc-800/50 text-xs text-zinc-400">
                  <p className="font-medium text-white mb-2">This will generate:</p>
                  <ul className="space-y-1">
                    <li>✓ Backend API (FastAPI)</li>
                    <li>✓ Database Schema (MongoDB)</li>
                    <li>✓ Auth System (JWT + OAuth)</li>
                    <li>✓ Frontend UI (React + Tailwind)</li>
                    <li>✓ Deployment Config (Vercel + Railway)</li>
                    <li>✓ Payment Integration (Stripe)</li>
                  </ul>
                </div>
              </div>
              <DialogFooter>
                <Button onClick={generateBlueprint} disabled={generating} className="bg-emerald-500 hover:bg-emerald-600">
                  {generating ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Zap className="w-4 h-4 mr-1" />}
                  Generate Blueprint
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <ScrollArea className="flex-1 p-4">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-zinc-500" />
          </div>
        ) : blueprints.length === 0 ? (
          <div className="text-center py-12">
            <Zap className="w-12 h-12 mx-auto mb-4 text-zinc-700" />
            <h3 className="font-rajdhani text-lg text-white mb-2">One-Click SaaS</h3>
            <p className="text-sm text-zinc-500 mb-4">
              Generate complete SaaS blueprints in seconds
            </p>
            <p className="text-xs text-zinc-600">
              Backend + Database + Auth + UI + Payments + Deployment
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {blueprints.map((bp) => (
              <div key={bp.id} className="p-4 rounded-lg bg-zinc-900 border border-zinc-800 hover:border-zinc-700">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium text-white">{bp.name}</h4>
                      <Badge className={bp.status === "ready" ? "bg-emerald-500" : "bg-amber-500"}>
                        {bp.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-zinc-500 mt-1">{bp.description}</p>
                  </div>
                  <Button
                    onClick={() => buildFromBlueprint(bp.id)}
                    disabled={building === bp.id}
                    size="sm"
                    className="bg-emerald-500 hover:bg-emerald-600"
                  >
                    {building === bp.id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        <Rocket className="w-3 h-3 mr-1" />Build
                      </>
                    )}
                  </Button>
                </div>
                
                {/* Tech Stack */}
                <div className="flex flex-wrap gap-2 mb-3">
                  {Object.entries(bp.tech_stack || {}).map(([key, value]) => (
                    <Badge key={key} variant="outline" className="text-xs border-zinc-700">
                      {value}
                    </Badge>
                  ))}
                </div>
                
                {/* Blueprint Details */}
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div className="p-2 rounded bg-zinc-800/50">
                    <span className="text-zinc-500">Endpoints</span>
                    <p className="text-white font-medium">{bp.backend_api?.endpoints?.length || 0}</p>
                  </div>
                  <div className="p-2 rounded bg-zinc-800/50">
                    <span className="text-zinc-500">Pages</span>
                    <p className="text-white font-medium">{bp.frontend_ui?.pages?.length || 0}</p>
                  </div>
                  <div className="p-2 rounded bg-zinc-800/50">
                    <span className="text-zinc-500">Collections</span>
                    <p className="text-white font-medium">{bp.database_schema?.collections?.length || 0}</p>
                  </div>
                </div>
                
                {/* Pricing Plans */}
                {bp.payment_integration?.plans && (
                  <div className="mt-3 pt-3 border-t border-zinc-800">
                    <p className="text-xs text-zinc-500 mb-2">Pricing Plans</p>
                    <div className="flex gap-2">
                      {bp.payment_integration.plans.map((plan, i) => (
                        <Badge key={i} variant="outline" className="text-xs border-emerald-500/30 text-emerald-400">
                          {plan.name}: ${plan.price}/mo
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  );
};

export default SaaSBuilderPanel;
