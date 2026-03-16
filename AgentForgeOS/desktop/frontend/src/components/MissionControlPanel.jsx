import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Activity, Radio, Bot, Zap, AlertTriangle, CheckCircle, Info, XCircle,
  Clock, Cpu, Target, Code, TestTube, Palette
} from "lucide-react";
import { API } from "@/App";

const AGENT_ICONS = {
  COMMANDER: Target,
  ATLAS: Code,
  FORGE: Zap,
  SENTINEL: AlertTriangle,
  PROBE: TestTube,
  PRISM: Palette
};

const AGENT_COLORS = {
  COMMANDER: "text-orange-400",
  ATLAS: "text-blue-400",
  FORGE: "text-emerald-400",
  SENTINEL: "text-amber-400",
  PROBE: "text-cyan-400",
  PRISM: "text-pink-400"
};

const SEVERITY_STYLES = {
  info: { icon: Info, color: "text-blue-400", bg: "bg-blue-500/10" },
  success: { icon: CheckCircle, color: "text-emerald-400", bg: "bg-emerald-500/10" },
  warning: { icon: AlertTriangle, color: "text-amber-400", bg: "bg-amber-500/10" },
  error: { icon: XCircle, color: "text-red-400", bg: "bg-red-500/10" }
};

const MissionControlPanel = ({ projectId }) => {
  const [events, setEvents] = useState([]);
  const [status, setStatus] = useState(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    fetchFeed();
    fetchStatus();
    
    // Poll for updates
    const interval = setInterval(() => {
      fetchFeed();
      fetchStatus();
    }, 5000);
    
    return () => clearInterval(interval);
  }, [projectId]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: 0, behavior: "smooth" });
  }, [events.length]);

  const fetchFeed = async () => {
    try {
      const res = await axios.get(`${API}/mission-control/${projectId}/feed`, {
        params: { limit: 50 }
      });
      setEvents(res.data || []);
    } catch (e) {}
  };

  const fetchStatus = async () => {
    try {
      const res = await axios.get(`${API}/mission-control/${projectId}/status`);
      setStatus(res.data);
    } catch (e) {}
  };

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]" data-testid="mission-control-panel">
      {/* Header */}
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800 bg-gradient-to-r from-zinc-900 to-zinc-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Radio className="w-4 h-4 text-red-500 animate-pulse" />
            <span className="font-rajdhani font-bold text-white">MISSION CONTROL</span>
            <Badge className="bg-red-500/20 text-red-400 border border-red-500/30">LIVE</Badge>
          </div>
          <div className="flex items-center gap-3 text-xs">
            {status?.active_goal_loop && (
              <Badge className="bg-orange-500/20 text-orange-400">GOAL LOOP ACTIVE</Badge>
            )}
            {status?.active_build && (
              <Badge className="bg-emerald-500/20 text-emerald-400">BUILD RUNNING</Badge>
            )}
          </div>
        </div>
      </div>

      {/* Agent Status Row */}
      <div className="flex-shrink-0 px-4 py-2 border-b border-zinc-800 bg-zinc-900/50">
        <div className="flex gap-2 overflow-x-auto">
          {status?.agents && Object.entries(status.agents).map(([name, data]) => {
            const Icon = AGENT_ICONS[name] || Bot;
            const color = AGENT_COLORS[name] || "text-zinc-400";
            const isActive = data.status === "active" || data.status === "working";
            
            return (
              <div 
                key={name} 
                className={`flex items-center gap-2 px-3 py-1.5 rounded-full border ${
                  isActive 
                    ? 'bg-zinc-800 border-zinc-600' 
                    : 'bg-zinc-900 border-zinc-800'
                }`}
              >
                <Icon className={`w-3 h-3 ${color} ${isActive ? 'animate-pulse' : ''}`} />
                <span className="text-xs text-zinc-400">{name}</span>
                <div className={`w-1.5 h-1.5 rounded-full ${isActive ? 'bg-emerald-500' : 'bg-zinc-600'}`} />
              </div>
            );
          })}
        </div>
      </div>

      {/* Event Feed */}
      <ScrollArea className="flex-1" ref={scrollRef}>
        <div className="p-4 space-y-2">
          {events.length === 0 ? (
            <div className="text-center py-12">
              <Activity className="w-12 h-12 mx-auto mb-4 text-zinc-700" />
              <h3 className="font-rajdhani text-lg text-white mb-2">Mission Control</h3>
              <p className="text-sm text-zinc-500">
                Real-time agent activity and system events
              </p>
            </div>
          ) : (
            events.map((event) => {
              const severity = SEVERITY_STYLES[event.severity] || SEVERITY_STYLES.info;
              const SeverityIcon = severity.icon;
              const AgentIcon = event.agent_name ? (AGENT_ICONS[event.agent_name] || Bot) : Activity;
              const agentColor = event.agent_name ? (AGENT_COLORS[event.agent_name] || "text-zinc-400") : "text-zinc-400";
              
              return (
                <div 
                  key={event.id} 
                  className={`p-3 rounded-lg border border-zinc-800 ${severity.bg}`}
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-0.5">
                      <SeverityIcon className={`w-4 h-4 ${severity.color}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium text-white">{event.title}</span>
                        {event.agent_name && (
                          <Badge variant="outline" className={`text-xs ${agentColor} border-current/30`}>
                            <AgentIcon className="w-3 h-3 mr-1" />
                            {event.agent_name}
                          </Badge>
                        )}
                      </div>
                      <p className="text-xs text-zinc-500">{event.description}</p>
                      <div className="flex items-center gap-2 mt-2 text-xs text-zinc-600">
                        <Clock className="w-3 h-3" />
                        {new Date(event.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </ScrollArea>

      {/* Footer Stats */}
      <div className="flex-shrink-0 px-4 py-2 border-t border-zinc-800 bg-zinc-900/50">
        <div className="flex items-center justify-between text-xs text-zinc-500">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <Activity className="w-3 h-3" /> {events.length} events
            </span>
            {status?.errors > 0 && (
              <span className="flex items-center gap-1 text-red-400">
                <XCircle className="w-3 h-3" /> {status.errors} errors
              </span>
            )}
            {status?.warnings > 0 && (
              <span className="flex items-center gap-1 text-amber-400">
                <AlertTriangle className="w-3 h-3" /> {status.warnings} warnings
              </span>
            )}
          </div>
          <span>Auto-refresh: 5s</span>
        </div>
      </div>
    </div>
  );
};

export default MissionControlPanel;
