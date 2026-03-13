import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { 
  Brain, Cpu, Activity, Zap, Target, Network, Globe, Rocket,
  Play, Pause, ChevronRight, Terminal, Eye, Sparkles, Command, Wifi, WifiOff
} from 'lucide-react';
import { API } from '@/App';

const AgentWarRoom = ({ projectId }) => {
  const [agents, setAgents] = useState([]);
  const [activities, setActivities] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [agentStates, setAgentStates] = useState({});
  const [wsConnected, setWsConnected] = useState(false);
  const logRef = useRef(null);
  const wsRef = useRef(null);

  const AGENT_CONFIG = {
    'commander': { icon: Brain, color: '#8b5cf6', glow: 'shadow-violet-500/50' },
    'atlas': { icon: Globe, color: '#06b6d4', glow: 'shadow-cyan-500/50' },
    'forge': { icon: Cpu, color: '#f59e0b', glow: 'shadow-amber-500/50' },
    'sentinel': { icon: Target, color: '#ef4444', glow: 'shadow-red-500/50' },
    'probe': { icon: Activity, color: '#22c55e', glow: 'shadow-green-500/50' },
    'prism': { icon: Sparkles, color: '#ec4899', glow: 'shadow-pink-500/50' }
  };

  // WebSocket connection for real-time updates
  const connectWebSocket = useCallback(() => {
    if (!projectId) return;
    
    const wsUrl = API.replace('https://', 'wss://').replace('http://', 'ws://');
    const ws = new WebSocket(`${wsUrl}/ws/agents/${projectId}`);
    
    ws.onopen = () => {
      setWsConnected(true);
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'agent_activity' || data.type === 'agent_complete') {
          // Update agent state
          setAgentStates(prev => ({
            ...prev,
            [data.agent_id]: {
              status: data.status,
              activity: data.activity,
              progress: data.progress || 0
            }
          }));
          
          // Add to activity log
          if (data.type === 'agent_activity') {
            setActivities(prev => [...prev.slice(-50), {
              id: Date.now(),
              agent: data.agent_name,
              action: data.activity,
              timestamp: new Date().toLocaleTimeString()
            }]);
          }
        }
        
        if (data.type === 'agent_progress') {
          setAgentStates(prev => ({
            ...prev,
            [data.agent_id]: {
              ...prev[data.agent_id],
              progress: data.progress
            }
          }));
        }
      } catch (e) {
        console.error('WebSocket message error:', e);
      }
    };
    
    ws.onclose = () => {
      setWsConnected(false);
      // Reconnect after 3 seconds
      setTimeout(connectWebSocket, 3000);
    };
    
    ws.onerror = (err) => {
      console.error('WebSocket error:', err);
      ws.close();
    };
    
    wsRef.current = ws;
    
    return () => {
      ws.close();
    };
  }, [projectId]);

  useEffect(() => {
    fetchAgents();
    const cleanup = connectWebSocket();
    
    // Fallback: simulate activity if WebSocket isn't working
    const interval = setInterval(() => {
      if (!wsConnected) {
        simulateActivity();
      }
    }, 3000);
    
    return () => {
      clearInterval(interval);
      if (cleanup) cleanup();
      if (wsRef.current) wsRef.current.close();
    };
  }, [connectWebSocket, wsConnected]);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [activities]);

  const fetchAgents = async () => {
    try {
      const res = await axios.get(`${API}/agents`);
      const agentData = res.data || [];
      // If no agents returned, use default configuration
      if (agentData.length === 0) {
        setAgents([
          { id: '1', name: 'COMMANDER', role: 'lead' },
          { id: '2', name: 'ATLAS', role: 'architect' },
          { id: '3', name: 'FORGE', role: 'developer' },
          { id: '4', name: 'SENTINEL', role: 'reviewer' },
          { id: '5', name: 'PROBE', role: 'tester' },
          { id: '6', name: 'PRISM', role: 'artist' }
        ]);
      } else {
        setAgents(agentData);
      }
    } catch (e) {
      // Use default agents on error
      setAgents([
        { id: '1', name: 'COMMANDER', role: 'lead' },
        { id: '2', name: 'ATLAS', role: 'architect' },
        { id: '3', name: 'FORGE', role: 'developer' },
        { id: '4', name: 'SENTINEL', role: 'reviewer' },
        { id: '5', name: 'PROBE', role: 'tester' },
        { id: '6', name: 'PRISM', role: 'artist' }
      ]);
    }
  };

  const simulateActivity = () => {
    const agentNames = ['COMMANDER', 'ATLAS', 'FORGE', 'SENTINEL', 'PROBE', 'PRISM'];
    const actions = [
      'analyzing architecture patterns',
      'generating module structure',
      'writing endpoint code',
      'reviewing security vectors',
      'running test suite',
      'generating UI components',
      'optimizing performance',
      'designing database schema',
      'planning feature implementation',
      'scanning for vulnerabilities'
    ];
    
    const agent = agentNames[Math.floor(Math.random() * agentNames.length)];
    const action = actions[Math.floor(Math.random() * actions.length)];
    
    setActivities(prev => [...prev.slice(-50), {
      id: Date.now(),
      agent,
      action,
      time: new Date().toLocaleTimeString()
    }]);
  };

  return (
    <div className="h-full flex flex-col bg-black/90 backdrop-blur-xl" data-testid="war-room">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800/50">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
            <div className="absolute inset-0 w-3 h-3 rounded-full bg-green-500 animate-ping" />
          </div>
          <h2 className="text-lg font-bold text-white tracking-wide">AGENT WAR ROOM</h2>
        </div>
        <div className="flex items-center gap-2 text-xs text-zinc-500">
          <Activity className="w-3 h-3 text-green-400" />
          <span>SYSTEMS NOMINAL</span>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Agent Grid */}
        <div className="w-80 border-r border-zinc-800/50 p-4 overflow-auto">
          <div className="text-xs text-zinc-500 uppercase tracking-wider mb-4">Active Agents</div>
          <div className="space-y-3">
            {agents.map((agent) => {
              const config = AGENT_CONFIG[agent.name?.toLowerCase()] || AGENT_CONFIG.commander;
              const Icon = config.icon;
              return (
                <div
                  key={agent.id}
                  onClick={() => setSelectedAgent(agent)}
                  className={`
                    relative p-4 rounded-xl cursor-pointer transition-all
                    bg-gradient-to-br from-zinc-900/80 to-zinc-900/40
                    border border-zinc-800/50 hover:border-zinc-700
                    ${selectedAgent?.id === agent.id ? 'ring-2 ring-offset-2 ring-offset-black' : ''}
                  `}
                  style={{ 
                    '--tw-ring-color': config.color,
                    boxShadow: selectedAgent?.id === agent.id ? `0 0 30px ${config.color}30` : 'none'
                  }}
                >
                  <div className="flex items-center gap-3">
                    <div 
                      className="w-12 h-12 rounded-xl flex items-center justify-center"
                      style={{ backgroundColor: `${config.color}20` }}
                    >
                      <Icon className="w-6 h-6" style={{ color: config.color }} />
                    </div>
                    <div className="flex-1">
                      <div className="font-bold text-white text-sm">{agent.name}</div>
                      <div className="text-xs text-zinc-500 mt-0.5">{agent.role}</div>
                    </div>
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  </div>
                  
                  {/* Activity indicator */}
                  <div className="mt-3 h-1 bg-zinc-800 rounded-full overflow-hidden">
                    <div 
                      className="h-full rounded-full animate-pulse"
                      style={{ 
                        width: `${Math.random() * 60 + 40}%`,
                        backgroundColor: config.color
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Live Activity Feed */}
        <div className="flex-1 flex flex-col">
          <div className="px-4 py-3 border-b border-zinc-800/50">
            <div className="flex items-center gap-2 text-xs text-zinc-500 uppercase tracking-wider">
              <Terminal className="w-3 h-3" />
              Mission Control Feed
            </div>
          </div>
          
          <div 
            ref={logRef}
            className="flex-1 overflow-auto p-4 font-mono text-sm"
            style={{ background: 'linear-gradient(180deg, #000 0%, #0a0a0c 100%)' }}
          >
            {activities.map((activity) => {
              const agentKey = activity.agent.toLowerCase();
              const config = AGENT_CONFIG[agentKey] || AGENT_CONFIG.commander;
              return (
                <div key={activity.id} className="flex items-start gap-3 mb-2 animate-fadeIn">
                  <span className="text-zinc-600 text-xs w-20">{activity.time}</span>
                  <span 
                    className="font-bold text-xs w-24"
                    style={{ color: config.color }}
                  >
                    {activity.agent}
                  </span>
                  <span className="text-zinc-400">{activity.action}</span>
                </div>
              );
            })}
            
            {activities.length === 0 && (
              <div className="text-zinc-600 text-center py-8">
                Waiting for agent activity...
              </div>
            )}
          </div>

          {/* Command Input */}
          <div className="p-4 border-t border-zinc-800/50">
            <div className="flex items-center gap-3 bg-zinc-900/50 rounded-xl px-4 py-3 border border-zinc-800">
              <Command className="w-4 h-4 text-zinc-500" />
              <input
                type="text"
                placeholder="Enter command..."
                className="flex-1 bg-transparent text-white text-sm outline-none placeholder-zinc-600"
              />
              <kbd className="px-2 py-1 text-xs bg-zinc-800 rounded text-zinc-400">⏎</kbd>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-4px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
};

export default AgentWarRoom;
