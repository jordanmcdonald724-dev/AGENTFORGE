import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Progress } from "@/components/ui/progress";
import { 
  Bug, Play, CheckCircle, XCircle, RefreshCw, Loader2, AlertTriangle,
  Wrench, TestTube, ChevronRight
} from "lucide-react";
import { API } from "@/App";

const DebugLoopPanel = ({ projectId }) => {
  const [debugLoop, setDebugLoop] = useState(null);
  const [loops, setLoops] = useState([]);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    fetchLoops();
    fetchLatest();
  }, [projectId]);

  const fetchLoops = async () => {
    try {
      const res = await axios.get(`${API}/debug-loop/${projectId}`);
      setLoops(res.data || []);
    } catch (e) {}
  };

  const fetchLatest = async () => {
    try {
      const res = await axios.get(`${API}/debug-loop/${projectId}/latest`);
      setDebugLoop(res.data);
    } catch (e) {}
  };

  const startDebugLoop = async () => {
    setRunning(true);
    try {
      const res = await axios.post(`${API}/debug-loop/${projectId}/start`, null, {
        params: { max_iterations: 10 }
      });
      setDebugLoop(res.data);
      toast.success("Debug loop complete!");
      fetchLoops();
    } catch (e) {
      toast.error("Debug loop failed");
    } finally {
      setRunning(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "fixed": return <CheckCircle className="w-4 h-4 text-emerald-400" />;
      case "partial": return <AlertTriangle className="w-4 h-4 text-amber-400" />;
      case "failed": return <XCircle className="w-4 h-4 text-red-400" />;
      default: return <RefreshCw className="w-4 h-4 text-zinc-400" />;
    }
  };

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]" data-testid="debug-loop-panel">
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bug className="w-4 h-4 text-red-400" />
            <span className="font-rajdhani font-bold text-white">Self-Debugging Loop</span>
            {debugLoop?.success && (
              <Badge className="bg-emerald-500">All Fixed</Badge>
            )}
          </div>
          <Button
            onClick={startDebugLoop}
            disabled={running}
            className="bg-red-500 hover:bg-red-600"
            data-testid="start-debug-btn"
          >
            {running ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Play className="w-4 h-4 mr-1" />}
            Start Debug Loop
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1 p-4">
        {!debugLoop ? (
          <div className="text-center py-12">
            <Bug className="w-12 h-12 mx-auto mb-4 text-zinc-700" />
            <h3 className="font-rajdhani text-lg text-white mb-2">AI Self-Debugging</h3>
            <p className="text-sm text-zinc-500 mb-4">
              Automatically detect, analyze, fix, and test errors
            </p>
            <div className="text-xs text-zinc-600 space-y-1">
              <p>1. PROBE detects errors</p>
              <p>2. SENTINEL analyzes root cause</p>
              <p>3. FORGE applies fixes</p>
              <p>4. PROBE tests again</p>
              <p>5. Loop until success</p>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Summary */}
            <div className="grid grid-cols-4 gap-3">
              <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800 text-center">
                <p className="text-2xl font-bold text-white">{debugLoop.errors_detected?.length || 0}</p>
                <p className="text-xs text-zinc-500">Errors Found</p>
              </div>
              <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800 text-center">
                <p className="text-2xl font-bold text-emerald-400">{debugLoop.fixes_applied?.length || 0}</p>
                <p className="text-xs text-zinc-500">Fixes Applied</p>
              </div>
              <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800 text-center">
                <p className="text-2xl font-bold text-white">{debugLoop.iterations?.length || 0}</p>
                <p className="text-xs text-zinc-500">Iterations</p>
              </div>
              <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800 text-center">
                <p className={`text-2xl font-bold ${debugLoop.success ? 'text-emerald-400' : 'text-amber-400'}`}>
                  {debugLoop.success ? '✓' : '~'}
                </p>
                <p className="text-xs text-zinc-500">{debugLoop.success ? 'Success' : 'Partial'}</p>
              </div>
            </div>

            {/* Iterations */}
            {debugLoop.iterations?.length > 0 && (
              <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
                <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                  <RefreshCw className="w-4 h-4 text-cyan-400" /> Debug Iterations
                </h4>
                <div className="space-y-3">
                  {debugLoop.iterations.map((iter, i) => (
                    <div key={i} className="p-3 rounded bg-zinc-800/50 border border-zinc-700">
                      <div className="flex items-center gap-2 mb-2">
                        {getStatusIcon(iter.status)}
                        <span className="text-sm font-medium text-white">Iteration {iter.iteration}</span>
                        <Badge variant="outline" className={iter.status === "fixed" ? "border-emerald-500 text-emerald-400" : "border-amber-500 text-amber-400"}>
                          {iter.status}
                        </Badge>
                      </div>
                      <div className="space-y-1 text-xs text-zinc-400">
                        <p className="flex items-center gap-1"><AlertTriangle className="w-3 h-3 text-red-400" /> {iter.error?.message}</p>
                        <p className="flex items-center gap-1"><TestTube className="w-3 h-3 text-cyan-400" /> {iter.analysis}</p>
                        <p className="flex items-center gap-1"><Wrench className="w-3 h-3 text-amber-400" /> {iter.fix}</p>
                        <p className="flex items-center gap-1"><CheckCircle className="w-3 h-3 text-emerald-400" /> {iter.test_result}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Previous Loops */}
            {loops.length > 1 && (
              <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
                <h4 className="font-medium text-white mb-3">Previous Debug Sessions</h4>
                <div className="space-y-2">
                  {loops.slice(1, 5).map((loop, i) => (
                    <div key={i} className="flex items-center justify-between p-2 rounded bg-zinc-800/50">
                      <span className="text-xs text-zinc-400">{new Date(loop.created_at).toLocaleString()}</span>
                      <Badge className={loop.success ? "bg-emerald-500" : "bg-amber-500"}>
                        {loop.success ? "Success" : "Partial"}
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

export default DebugLoopPanel;
