import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Progress } from "@/components/ui/progress";
import { 
  Play, Target, CheckCircle, XCircle, Loader2, Pause, RotateCcw,
  Gauge, TrendingUp, Activity
} from "lucide-react";
import { API } from "@/App";

const GoalLoopPanel = ({ projectId }) => {
  const [goal, setGoal] = useState("");
  const [activeLoop, setActiveLoop] = useState(null);
  const [loops, setLoops] = useState([]);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    fetchLoops();
    fetchActive();
  }, [projectId]);

  const fetchLoops = async () => {
    try {
      const res = await axios.get(`${API}/goal-loop/${projectId}`);
      setLoops(res.data || []);
    } catch (e) {}
  };

  const fetchActive = async () => {
    try {
      const res = await axios.get(`${API}/goal-loop/${projectId}/active`);
      setActiveLoop(res.data);
    } catch (e) {}
  };

  const startLoop = async () => {
    if (!goal.trim()) {
      toast.error("Enter a goal");
      return;
    }
    setRunning(true);
    try {
      const res = await axios.post(`${API}/goal-loop/${projectId}/start`, null, {
        params: { goal, max_cycles: 50 }
      });
      setActiveLoop(res.data);
      toast.success(res.data.status === "success" ? "Goal achieved!" : "Loop running...");
      fetchLoops();
    } catch (e) {
      toast.error("Failed to start loop");
    } finally {
      setRunning(false);
    }
  };

  const getMetricColor = (value, threshold) => {
    if (value >= threshold) return "text-emerald-400";
    if (value >= threshold * 0.7) return "text-amber-400";
    return "text-red-400";
  };

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]" data-testid="goal-loop-panel">
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Target className="w-4 h-4 text-orange-400" />
          <span className="font-rajdhani font-bold text-white">Run Until Done</span>
          {activeLoop?.status === "running" && (
            <Badge className="bg-orange-500 animate-pulse">RUNNING</Badge>
          )}
          {activeLoop?.status === "success" && (
            <Badge className="bg-emerald-500">SUCCESS</Badge>
          )}
        </div>
      </div>

      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800">
        <div className="flex gap-2">
          <Input
            placeholder="Enter goal... (e.g., 'Build multiplayer fishing simulator')"
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            className="flex-1 bg-zinc-900 border-zinc-700"
            data-testid="goal-input"
          />
          <Button
            onClick={startLoop}
            disabled={running}
            className="bg-orange-500 hover:bg-orange-600"
            data-testid="start-loop-btn"
          >
            {running ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Play className="w-4 h-4 mr-1" />}
            Run Until Done
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1 p-4">
        {!activeLoop && loops.length === 0 ? (
          <div className="text-center py-12">
            <Target className="w-12 h-12 mx-auto mb-4 text-zinc-700" />
            <h3 className="font-rajdhani text-lg text-white mb-2">Autonomous Goal Loop</h3>
            <p className="text-sm text-zinc-500 mb-4">
              Set a goal and let the system work until it's achieved
            </p>
            <div className="text-xs text-zinc-600 space-y-1">
              <p>• Runs until quality thresholds met</p>
              <p>• Tests pass rate ≥ 90%</p>
              <p>• Performance score ≥ 70%</p>
              <p>• Demo playable</p>
            </div>
          </div>
        ) : activeLoop && (
          <div className="space-y-6">
            {/* Goal */}
            <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
              <h4 className="text-sm text-zinc-400 mb-2">Current Goal</h4>
              <p className="text-white font-medium">{activeLoop.goal}</p>
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(activeLoop.current_metrics || {}).map(([key, value]) => {
                const threshold = activeLoop.thresholds?.[key];
                const met = activeLoop.thresholds_met?.[key];
                const displayValue = typeof value === "boolean" ? (value ? "Yes" : "No") : `${value}%`;
                
                return (
                  <div key={key} className="p-3 rounded-lg bg-zinc-900 border border-zinc-800">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-zinc-500">{key.replace(/_/g, " ")}</span>
                      {met ? (
                        <CheckCircle className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <XCircle className="w-4 h-4 text-red-400" />
                      )}
                    </div>
                    <p className={`text-xl font-bold ${met ? 'text-emerald-400' : 'text-amber-400'}`}>
                      {displayValue}
                    </p>
                    {typeof threshold === "number" && (
                      <Progress 
                        value={typeof value === "number" ? value : 0} 
                        className="mt-2 h-1"
                      />
                    )}
                  </div>
                );
              })}
            </div>

            {/* Cycles */}
            <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
              <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                <Activity className="w-4 h-4 text-cyan-400" />
                Cycles ({activeLoop.cycles?.length || 0} / {activeLoop.max_cycles})
              </h4>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {activeLoop.cycles?.slice(-10).map((cycle, i) => (
                  <div key={i} className="flex items-center gap-3 text-xs p-2 rounded bg-zinc-800/50">
                    <Badge variant="outline" className="border-zinc-700">{cycle.cycle}</Badge>
                    <span className="text-cyan-400 font-mono">{cycle.agent}</span>
                    <span className="text-zinc-400 flex-1 truncate">{cycle.action}</span>
                    <Badge className={cycle.result === "complete" ? "bg-emerald-500" : "bg-blue-500"}>
                      {cycle.result}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </ScrollArea>
    </div>
  );
};

export default GoalLoopPanel;
