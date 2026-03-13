import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  Play, Square, RotateCcw, Terminal, Server, Globe, 
  Gamepad2, Box, Code, ChevronRight, Loader2, Cpu, HardDrive
} from "lucide-react";
import { API } from "@/App";

const ENV_ICONS = {
  web: Globe,
  node: Server,
  python: Code,
  unity: Gamepad2,
  unreal: Box
};

const SandboxPanel = ({ projectId }) => {
  const [environments, setEnvironments] = useState([]);
  const [session, setSession] = useState(null);
  const [selectedEnv, setSelectedEnv] = useState("web");
  const [consoleInput, setConsoleInput] = useState("");
  const [loading, setLoading] = useState(false);
  const consoleEndRef = useRef(null);

  useEffect(() => {
    fetchEnvironments();
    fetchSession();
  }, [projectId]);

  useEffect(() => {
    consoleEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [session?.console_output]);

  const fetchEnvironments = async () => {
    try {
      const res = await axios.get(`${API}/sandbox/environments`);
      setEnvironments(res.data);
    } catch (e) {}
  };

  const fetchSession = async () => {
    try {
      const res = await axios.get(`${API}/sandbox/${projectId}`);
      if (res.data) {
        setSession(res.data);
        setSelectedEnv(res.data.environment);
      }
    } catch (e) {}
  };

  const createSession = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/sandbox/${projectId}/create`, null, {
        params: { environment: selectedEnv }
      });
      setSession(res.data);
      toast.success("Sandbox created!");
    } catch (e) {
      toast.error("Failed to create sandbox");
    } finally {
      setLoading(false);
    }
  };

  const runSandbox = async () => {
    if (!session) {
      await createSession();
    }
    setLoading(true);
    try {
      const res = await axios.post(`${API}/sandbox/${projectId}/run`);
      setSession(prev => ({ ...prev, ...res.data }));
      toast.success("Sandbox running!");
    } catch (e) {
      toast.error("Execution failed");
    } finally {
      setLoading(false);
    }
  };

  const stopSandbox = async () => {
    try {
      await axios.post(`${API}/sandbox/${projectId}/stop`);
      setSession(prev => ({ ...prev, status: "stopped" }));
    } catch (e) {}
  };

  const resetSandbox = async () => {
    try {
      await axios.post(`${API}/sandbox/${projectId}/reset`);
      setSession(prev => ({ ...prev, status: "idle", console_output: [], variables: {} }));
      toast.info("Sandbox reset");
    } catch (e) {}
  };

  const sendConsoleCommand = async () => {
    if (!consoleInput.trim() || !session) return;
    try {
      await axios.post(`${API}/sandbox/${projectId}/console`, null, {
        params: { command: consoleInput }
      });
      setConsoleInput("");
      fetchSession();
    } catch (e) {}
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "running": return "bg-emerald-500";
      case "paused": return "bg-amber-500";
      case "stopped": return "bg-red-500";
      case "error": return "bg-red-500";
      default: return "bg-zinc-500";
    }
  };

  const getLogColor = (type) => {
    switch (type) {
      case "error": return "text-red-400";
      case "warn": return "text-amber-400";
      default: return "text-emerald-400";
    }
  };

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]" data-testid="sandbox-panel">
      {/* Header */}
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-emerald-400" />
            <span className="font-rajdhani font-bold text-white">Build Sandbox</span>
            {session && (
              <Badge className={`${getStatusColor(session.status)} text-white text-xs`}>
                {session.status}
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-2">
            {session?.execution_time_ms > 0 && (
              <span className="text-xs text-zinc-500">{session.execution_time_ms.toFixed(0)}ms</span>
            )}
            {session?.memory_usage_mb > 0 && (
              <span className="text-xs text-zinc-500 flex items-center gap-1">
                <HardDrive className="w-3 h-3" />{session.memory_usage_mb}MB
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800 space-y-3">
        <div className="flex items-center gap-2">
          <Select value={selectedEnv} onValueChange={setSelectedEnv}>
            <SelectTrigger className="w-48 bg-zinc-900 border-zinc-700" data-testid="env-select">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-zinc-900 border-zinc-700">
              {environments.map(env => {
                const Icon = ENV_ICONS[env.id] || Terminal;
                return (
                  <SelectItem key={env.id} value={env.id}>
                    <div className="flex items-center gap-2">
                      <Icon className="w-4 h-4" />
                      {env.name}
                    </div>
                  </SelectItem>
                );
              })}
            </SelectContent>
          </Select>

          <Button
            onClick={runSandbox}
            disabled={loading || session?.status === "running"}
            className="bg-emerald-500 hover:bg-emerald-600"
            data-testid="run-sandbox-btn"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin mr-1" />
            ) : (
              <Play className="w-4 h-4 mr-1" />
            )}
            Run
          </Button>

          <Button
            onClick={stopSandbox}
            disabled={session?.status !== "running"}
            variant="outline"
            className="border-zinc-700"
            data-testid="stop-sandbox-btn"
          >
            <Square className="w-4 h-4 mr-1" />
            Stop
          </Button>

          <Button
            onClick={resetSandbox}
            variant="outline"
            className="border-zinc-700"
            data-testid="reset-sandbox-btn"
          >
            <RotateCcw className="w-4 h-4 mr-1" />
            Reset
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden flex">
        {/* Console Output */}
        <div className="flex-1 flex flex-col border-r border-zinc-800">
          <div className="flex-shrink-0 px-3 py-2 border-b border-zinc-800 bg-zinc-900/50">
            <span className="text-xs text-zinc-400 font-mono">Console Output</span>
          </div>
          <ScrollArea className="flex-1 p-3">
            <div className="font-mono text-xs space-y-1">
              {(!session?.console_output || session.console_output.length === 0) ? (
                <div className="text-zinc-600">
                  No output yet. Click "Run" to execute your code.
                </div>
              ) : (
                session.console_output.map((log, i) => (
                  <div key={i} className={`flex items-start gap-2 ${getLogColor(log.type)}`}>
                    <ChevronRight className="w-3 h-3 mt-0.5 flex-shrink-0" />
                    <span className="break-all">{log.message}</span>
                  </div>
                ))
              )}
              <div ref={consoleEndRef} />
            </div>
          </ScrollArea>
          
          {/* Console Input */}
          <div className="flex-shrink-0 p-2 border-t border-zinc-800 bg-zinc-900/50">
            <div className="flex gap-2">
              <div className="flex items-center text-zinc-500 text-xs font-mono">
                <ChevronRight className="w-3 h-3" />
              </div>
              <Input
                value={consoleInput}
                onChange={(e) => setConsoleInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendConsoleCommand()}
                placeholder="Enter command..."
                className="flex-1 h-7 bg-transparent border-none text-xs font-mono focus-visible:ring-0"
                data-testid="console-input"
              />
            </div>
          </div>
        </div>

        {/* Variables Inspector */}
        <div className="w-64 flex flex-col">
          <div className="flex-shrink-0 px-3 py-2 border-b border-zinc-800 bg-zinc-900/50">
            <span className="text-xs text-zinc-400 font-mono flex items-center gap-1">
              <Cpu className="w-3 h-3" /> Variables
            </span>
          </div>
          <ScrollArea className="flex-1 p-3">
            {(!session?.variables || Object.keys(session.variables).length === 0) ? (
              <div className="text-xs text-zinc-600">
                No variables in scope
              </div>
            ) : (
              <div className="space-y-2">
                {Object.entries(session.variables).map(([key, value]) => (
                  <div key={key} className="p-2 rounded bg-zinc-900 border border-zinc-800">
                    <div className="text-xs text-cyan-400 font-mono">{key}</div>
                    <div className="text-xs text-zinc-400 font-mono mt-1 break-all">
                      {typeof value === "object" ? JSON.stringify(value) : String(value)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </div>
      </div>
    </div>
  );
};

export default SandboxPanel;
