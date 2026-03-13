import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Sparkles, Rocket, CheckCircle, Loader2, ArrowRight, Globe, Code, 
  Database, Shield, CreditCard, Upload, ExternalLink
} from "lucide-react";
import { API } from "@/App";

const PHASE_ICONS = {
  "Intake": Sparkles,
  "Clarification": Code,
  "Architecture": Database,
  "Asset Generation": Sparkles,
  "Code Generation": Code,
  "Code Review": Shield,
  "Testing": CheckCircle,
  "Deployment": Rocket,
  "Verification": CheckCircle
};

const RealityPipelinePanel = ({ onProjectCreated }) => {
  const [idea, setIdea] = useState("");
  const [pipelines, setPipelines] = useState([]);
  const [activePipeline, setActivePipeline] = useState(null);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    fetchPipelines();
  }, []);

  const fetchPipelines = async () => {
    try {
      const res = await axios.get(`${API}/reality-pipeline`);
      setPipelines(res.data || []);
      // Get most recent active
      const active = res.data?.find(p => p.status !== "live" && p.status !== "failed");
      if (active) setActivePipeline(active);
    } catch (e) {}
  };

  const startPipeline = async () => {
    if (!idea.trim()) {
      toast.error("Enter your idea");
      return;
    }
    setStarting(true);
    try {
      const res = await axios.post(`${API}/reality-pipeline/start`, null, {
        params: { idea }
      });
      setActivePipeline(res.data);
      toast.success("Idea → Reality pipeline complete!");
      fetchPipelines();
      if (res.data.project_id && onProjectCreated) {
        onProjectCreated(res.data.project_id);
      }
    } catch (e) {
      toast.error("Pipeline failed");
    } finally {
      setStarting(false);
    }
  };

  const selectedPipeline = activePipeline || pipelines[0];

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]" data-testid="reality-pipeline-panel">
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Rocket className="w-4 h-4 text-gradient-to-r from-purple-400 to-pink-400" />
          <span className="font-rajdhani font-bold text-white">Idea → Reality Pipeline</span>
          <Badge className="bg-gradient-to-r from-purple-500 to-pink-500 text-white">MAGIC</Badge>
        </div>
      </div>

      {/* Input */}
      <div className="flex-shrink-0 px-4 py-4 border-b border-zinc-800">
        <div className="flex gap-2">
          <Input
            placeholder="Describe your idea... (e.g., 'AI-powered marketing assistant for small businesses')"
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            className="flex-1 bg-zinc-900 border-zinc-700"
            data-testid="idea-input"
          />
          <Button
            onClick={startPipeline}
            disabled={starting}
            className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
            data-testid="start-pipeline-btn"
          >
            {starting ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Sparkles className="w-4 h-4 mr-1" />}
            Make It Real
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1 p-4">
        {!selectedPipeline ? (
          <div className="text-center py-12">
            <Rocket className="w-12 h-12 mx-auto mb-4 text-zinc-700" />
            <h3 className="font-rajdhani text-lg text-white mb-2">One-Click Reality</h3>
            <p className="text-sm text-zinc-500 mb-4">
              From idea to deployed product in one continuous pipeline
            </p>
            <div className="flex justify-center gap-2 flex-wrap text-xs text-zinc-600">
              {["Clarify", "Architect", "Generate", "Code", "Review", "Test", "Deploy"].map((step, i) => (
                <span key={i} className="flex items-center gap-1">
                  {step}
                  {i < 6 && <ArrowRight className="w-3 h-3" />}
                </span>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Pipeline Status */}
            <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-white">{selectedPipeline.idea}</h4>
                <Badge className={selectedPipeline.status === "live" ? "bg-emerald-500" : "bg-amber-500"}>
                  {selectedPipeline.status}
                </Badge>
              </div>
              {selectedPipeline.deploy_url && (
                <a 
                  href={selectedPipeline.deploy_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-sm text-purple-400 hover:text-purple-300"
                >
                  <ExternalLink className="w-4 h-4" />
                  {selectedPipeline.deploy_url}
                </a>
              )}
            </div>

            {/* Phases */}
            <div className="space-y-2">
              {selectedPipeline.phases?.map((phase, i) => {
                const Icon = PHASE_ICONS[phase.name] || Sparkles;
                const isComplete = phase.status === "complete";
                const isCurrent = i === selectedPipeline.current_phase;
                
                return (
                  <div 
                    key={i} 
                    className={`p-3 rounded-lg border ${
                      isComplete 
                        ? 'bg-emerald-500/10 border-emerald-500/30' 
                        : isCurrent 
                          ? 'bg-amber-500/10 border-amber-500/30'
                          : 'bg-zinc-900 border-zinc-800'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`p-1.5 rounded ${
                        isComplete ? 'bg-emerald-500/20' : 'bg-zinc-800'
                      }`}>
                        {isComplete ? (
                          <CheckCircle className="w-4 h-4 text-emerald-400" />
                        ) : isCurrent ? (
                          <Loader2 className="w-4 h-4 text-amber-400 animate-spin" />
                        ) : (
                          <Icon className="w-4 h-4 text-zinc-500" />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className={`text-sm font-medium ${isComplete ? 'text-emerald-400' : 'text-white'}`}>
                            {phase.name}
                          </span>
                          <Badge variant="outline" className="text-xs border-zinc-700">
                            {phase.agent}
                          </Badge>
                        </div>
                        {phase.output && (
                          <p className="text-xs text-zinc-500 mt-1">{phase.output}</p>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Outputs */}
            {selectedPipeline.status === "live" && (
              <div className="p-4 rounded-lg bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/30">
                <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-purple-400" />
                  Pipeline Complete!
                </h4>
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <span className="text-zinc-500">Files Created</span>
                    <p className="text-white">{selectedPipeline.files_created?.length || 0}</p>
                  </div>
                  <div>
                    <span className="text-zinc-500">Assets Generated</span>
                    <p className="text-white">{selectedPipeline.assets_generated?.length || 0}</p>
                  </div>
                  <div>
                    <span className="text-zinc-500">Tests</span>
                    <p className="text-emerald-400">
                      {selectedPipeline.test_results?.passed || 0} passed
                    </p>
                  </div>
                  <div>
                    <span className="text-zinc-500">Status</span>
                    <p className="text-emerald-400">LIVE</p>
                  </div>
                </div>
              </div>
            )}

            {/* Previous Pipelines */}
            {pipelines.length > 1 && (
              <div className="pt-4 border-t border-zinc-800">
                <h4 className="text-sm text-zinc-400 mb-3">Previous Pipelines</h4>
                <div className="space-y-2">
                  {pipelines.slice(1, 5).map((p) => (
                    <div 
                      key={p.id} 
                      className="flex items-center justify-between p-2 rounded bg-zinc-900 border border-zinc-800 cursor-pointer hover:border-zinc-700"
                      onClick={() => setActivePipeline(p)}
                    >
                      <span className="text-xs text-zinc-400 truncate max-w-xs">{p.idea}</span>
                      <Badge className={p.status === "live" ? "bg-emerald-500" : "bg-zinc-500"}>
                        {p.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </ScrollArea>
    </div>
  );
};

export default RealityPipelinePanel;
