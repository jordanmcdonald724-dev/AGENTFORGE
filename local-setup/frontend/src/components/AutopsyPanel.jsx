import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { 
  Scan, FileSearch, AlertTriangle, CheckCircle, ArrowUpCircle, Code, 
  Loader2, ChevronRight, Layers, GitBranch
} from "lucide-react";
import { API } from "@/App";

const AutopsyPanel = ({ projectId }) => {
  const [autopsy, setAutopsy] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    fetchAutopsy();
  }, [projectId]);

  const fetchAutopsy = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/autopsy/${projectId}`);
      setAutopsy(res.data);
    } catch (e) {}
    finally { setLoading(false); }
  };

  const runAutopsy = async () => {
    setAnalyzing(true);
    try {
      const res = await axios.post(`${API}/autopsy/analyze`, null, {
        params: { project_id: projectId, source_type: "existing" }
      });
      setAutopsy(res.data);
      toast.success("Project analysis complete!");
    } catch (e) {
      toast.error("Analysis failed");
    } finally {
      setAnalyzing(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case "high": return "text-red-400 bg-red-500/10";
      case "medium": return "text-amber-400 bg-amber-500/10";
      default: return "text-blue-400 bg-blue-500/10";
    }
  };

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]" data-testid="autopsy-panel">
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Scan className="w-4 h-4 text-cyan-400" />
            <span className="font-rajdhani font-bold text-white">Project Autopsy</span>
            {autopsy?.status && (
              <Badge className={autopsy.status === "complete" ? "bg-emerald-500" : "bg-amber-500"}>
                {autopsy.status}
              </Badge>
            )}
          </div>
          <Button
            onClick={runAutopsy}
            disabled={analyzing}
            className="bg-cyan-500 hover:bg-cyan-600"
            data-testid="run-autopsy-btn"
          >
            {analyzing ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <FileSearch className="w-4 h-4 mr-1" />}
            Analyze Project
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1 p-4">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-zinc-500" />
          </div>
        ) : !autopsy ? (
          <div className="text-center py-12">
            <Scan className="w-12 h-12 mx-auto mb-4 text-zinc-700" />
            <h3 className="font-rajdhani text-lg text-white mb-2">No Analysis Yet</h3>
            <p className="text-sm text-zinc-500 mb-4">Run autopsy to reverse-engineer this project</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Stats Overview */}
            <div className="grid grid-cols-3 gap-3">
              <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800 text-center">
                <p className="text-2xl font-bold text-white">{autopsy.stats?.total_files || 0}</p>
                <p className="text-xs text-zinc-500">Files</p>
              </div>
              <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800 text-center">
                <p className="text-2xl font-bold text-white">{autopsy.stats?.total_lines || 0}</p>
                <p className="text-xs text-zinc-500">Lines</p>
              </div>
              <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800 text-center">
                <p className="text-2xl font-bold text-white">{autopsy.tech_stack?.length || 0}</p>
                <p className="text-xs text-zinc-500">Technologies</p>
              </div>
            </div>

            {/* Tech Stack */}
            {autopsy.tech_stack?.length > 0 && (
              <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
                <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                  <Layers className="w-4 h-4 text-cyan-400" /> Tech Stack Detected
                </h4>
                <div className="flex flex-wrap gap-2">
                  {autopsy.tech_stack.map((tech, i) => (
                    <Badge key={i} variant="outline" className="border-cyan-500/30 text-cyan-400">
                      {tech.name}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Design Patterns */}
            {autopsy.design_patterns?.length > 0 && (
              <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
                <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                  <Code className="w-4 h-4 text-purple-400" /> Design Patterns
                </h4>
                <div className="space-y-2">
                  {autopsy.design_patterns.map((pattern, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-emerald-400" />
                      <span className="text-sm text-white">{pattern.name}</span>
                      <span className="text-xs text-zinc-500">- {pattern.description}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Weak Points */}
            {autopsy.weak_points?.length > 0 && (
              <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
                <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400" /> Issues Found ({autopsy.weak_points.length})
                </h4>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {autopsy.weak_points.slice(0, 10).map((issue, i) => (
                    <div key={i} className={`p-2 rounded ${getSeverityColor(issue.severity)}`}>
                      <p className="text-sm">{issue.issue}</p>
                      <p className="text-xs opacity-70 mt-1">{issue.recommendation}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Upgrade Plan */}
            {autopsy.upgrade_plan?.length > 0 && (
              <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
                <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                  <ArrowUpCircle className="w-4 h-4 text-emerald-400" /> Upgrade Plan
                </h4>
                <div className="space-y-2">
                  {autopsy.upgrade_plan.map((action, i) => (
                    <div key={i} className="flex items-center gap-3 p-2 rounded bg-zinc-800/50">
                      <Badge className={action.priority === "high" ? "bg-red-500" : "bg-amber-500"}>
                        {action.priority}
                      </Badge>
                      <div>
                        <p className="text-sm text-white">{action.action}</p>
                        <p className="text-xs text-zinc-500">{action.impact}</p>
                      </div>
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

export default AutopsyPanel;
