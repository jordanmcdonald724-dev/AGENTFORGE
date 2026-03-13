import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { 
  Brain, Rocket, Network, Factory, Globe, Database, 
  Terminal, Activity, Zap, ChevronRight, Command, Mic,
  Play, Settings, ArrowLeft, Sparkles, Eye, Moon, History, Dna
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { API } from '@/App';

// Mission Control Components
import AgentWarRoom from '@/components/mission-control/AgentWarRoom';
import GodModePanel from '@/components/mission-control/GodModePanel';
import VisualProjectBrain from '@/components/mission-control/VisualProjectBrain';
import BuildTimeline from '@/components/mission-control/BuildTimeline';
import KnowledgeGraphPanel from '@/components/mission-control/KnowledgeGraphPanel';
import NightShiftPanel from '@/components/mission-control/NightShiftPanel';
import TimeTravelPanel from '@/components/mission-control/TimeTravelPanel';
import EvolutionPanel from '@/components/mission-control/EvolutionPanel';

const MissionControl = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [files, setFiles] = useState([]);
  const [activePanel, setActivePanel] = useState('war-room');
  const [commandInput, setCommandInput] = useState('');
  const [systemStatus, setSystemStatus] = useState({ status: 'online' });

  useEffect(() => {
    if (projectId) {
      fetchProject();
      fetchFiles();
    }
    checkSystemStatus();
  }, [projectId]);

  const fetchProject = async () => {
    try {
      const res = await axios.get(`${API}/projects/${projectId}`);
      setProject(res.data);
    } catch (e) {}
  };

  const fetchFiles = async () => {
    try {
      const res = await axios.get(`${API}/files?project_id=${projectId}`);
      setFiles(res.data || []);
    } catch (e) {}
  };

  const checkSystemStatus = async () => {
    try {
      const res = await axios.get(`${API}/health`);
      setSystemStatus({ status: res.data.status === 'healthy' ? 'online' : 'offline' });
    } catch (e) {
      setSystemStatus({ status: 'offline' });
    }
  };

  const executeCommand = async () => {
    if (!commandInput.trim()) return;
    
    toast.info(`Executing: ${commandInput}`);
    
    // Parse command
    const cmd = commandInput.toLowerCase();
    if (cmd.startsWith('build ') || cmd === 'build') {
      toast.success('Starting build...');
    } else if (cmd.startsWith('deploy')) {
      toast.success('Initiating deployment...');
    } else if (cmd.includes('god mode')) {
      setActivePanel('god-mode');
    }
    
    setCommandInput('');
  };

  const PANELS = [
    { id: 'war-room', label: 'Agent War Room', icon: Brain, color: '#8b5cf6' },
    { id: 'project-brain', label: 'Project Brain', icon: Network, color: '#06b6d4' },
    { id: 'god-mode', label: 'God Mode', icon: Rocket, color: '#f59e0b' },
    { id: 'timeline', label: 'Build Timeline', icon: Activity, color: '#22c55e' },
    { id: 'knowledge', label: 'Knowledge Graph', icon: Database, color: '#ec4899' },
    { id: 'evolution', label: 'Evolution', icon: Dna, color: '#10b981' },
    { id: 'night-shift', label: 'Night Shift', icon: Moon, color: '#6366f1' },
    { id: 'time-travel', label: 'Time Travel', icon: History, color: '#f97316' }
  ];

  return (
    <div className="h-screen flex flex-col bg-[#030305] text-white overflow-hidden" data-testid="mission-control">
      {/* Top Bar */}
      <div className="flex-shrink-0 h-14 bg-black/50 backdrop-blur-xl border-b border-zinc-800/50 flex items-center px-4">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/studio')}
            className="text-zinc-400 hover:text-white"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          
          <div className="h-6 w-px bg-zinc-800" />
          
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-cyan-600 flex items-center justify-center">
              <Zap className="w-4 h-4" />
            </div>
            <div>
              <div className="text-sm font-bold tracking-wide">AGENTFORGE OS</div>
              <div className="text-[10px] text-zinc-500 uppercase tracking-wider">Mission Control</div>
            </div>
          </div>
        </div>

        {/* Command Bar */}
        <div className="flex-1 max-w-2xl mx-8">
          <div className="relative">
            <Command className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
            <Input
              value={commandInput}
              onChange={(e) => setCommandInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && executeCommand()}
              placeholder="Enter command... (try 'god mode' or 'build')"
              className="w-full h-10 pl-12 pr-4 bg-zinc-900/50 border-zinc-800 focus:border-violet-500 text-sm"
            />
            <kbd className="absolute right-4 top-1/2 -translate-y-1/2 px-2 py-0.5 text-xs bg-zinc-800 rounded text-zinc-400">
              ⏎
            </kbd>
          </div>
        </div>

        {/* Status Indicators */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${systemStatus.status === 'online' ? 'bg-green-500' : 'bg-red-500'} animate-pulse`} />
            <span className="text-xs text-zinc-500 uppercase">
              {systemStatus.status === 'online' ? 'Systems Online' : 'Offline'}
            </span>
          </div>
          
          <Button variant="ghost" size="sm">
            <Mic className="w-4 h-4" />
          </Button>
          
          <Button variant="ghost" size="sm">
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Main Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Side Navigation */}
        <div className="w-64 flex-shrink-0 bg-black/30 border-r border-zinc-800/50 flex flex-col">
          {/* Project Info */}
          {project && (
            <div className="p-4 border-b border-zinc-800/50">
              <div className="text-sm font-bold text-white truncate">{project.name}</div>
              <div className="text-xs text-zinc-500 mt-1">{files.length} files</div>
            </div>
          )}

          {/* Panel Navigation */}
          <div className="flex-1 p-4 space-y-2">
            {PANELS.map(panel => (
              <button
                key={panel.id}
                onClick={() => setActivePanel(panel.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                  activePanel === panel.id
                    ? 'bg-zinc-800/50 border border-zinc-700'
                    : 'hover:bg-zinc-900/50 border border-transparent'
                }`}
              >
                <div 
                  className="w-8 h-8 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: `${panel.color}20` }}
                >
                  <panel.icon className="w-4 h-4" style={{ color: panel.color }} />
                </div>
                <span className="text-sm font-medium text-zinc-300">{panel.label}</span>
              </button>
            ))}
          </div>

          {/* Quick Actions */}
          <div className="p-4 border-t border-zinc-800/50 space-y-2">
            <Button 
              className="w-full bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-700 hover:to-cyan-700"
              onClick={() => setActivePanel('god-mode')}
            >
              <Rocket className="w-4 h-4 mr-2" />
              God Mode
            </Button>
            <Button variant="outline" className="w-full border-zinc-700">
              <Play className="w-4 h-4 mr-2" />
              Run Build
            </Button>
          </div>
        </div>

        {/* Main Panel */}
        <div className="flex-1 overflow-hidden">
          {activePanel === 'war-room' && <AgentWarRoom projectId={projectId} />}
          {activePanel === 'god-mode' && <GodModePanel />}
          {activePanel === 'project-brain' && <VisualProjectBrain projectId={projectId} files={files} />}
          {activePanel === 'timeline' && <BuildTimeline projectId={projectId} />}
          {activePanel === 'knowledge' && <KnowledgeGraphPanel />}
          {activePanel === 'evolution' && <EvolutionPanel projectId={projectId} />}
          {activePanel === 'night-shift' && <NightShiftPanel projectId={projectId} />}
          {activePanel === 'time-travel' && <TimeTravelPanel projectId={projectId} />}
        </div>
      </div>
    </div>
  );
};

export default MissionControl;
