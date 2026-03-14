import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { toast } from 'sonner';
import {
  Zap, ArrowLeft, Play, Pause, RotateCcw, Settings,
  Brain, Code, Shield, Rocket, Users, Activity, CheckCircle,
  XCircle, Clock, Cpu, Layers, Eye, ChevronRight, Loader2,
  Terminal, FileCode, Sparkles, Download, RefreshCw, Timer,
  Database, TrendingUp, GitBranch
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { API } from '@/App';

// Agent Configuration
const AGENTS = {
  DIRECTOR: { icon: Users, color: '#fbbf24', label: 'Director' },
  ATLAS: { icon: Layers, color: '#3b82f6', label: 'Architect' },
  PIXEL: { icon: Eye, color: '#10b981', label: 'Frontend' },
  NEXUS: { icon: GitBranch, color: '#8b5cf6', label: 'Backend' },
  TITAN: { icon: Cpu, color: '#f97316', label: 'Engine' },
  SYNAPSE: { icon: Brain, color: '#ec4899', label: 'AI/ML' },
  DEPLOY: { icon: Rocket, color: '#14b8a6', label: 'DevOps' },
  SENTINEL: { icon: Shield, color: '#ef4444', label: 'Reviewer' },
  PHOENIX: { icon: TrendingUp, color: '#f59e0b', label: 'Refactor' },
  PROBE: { icon: Activity, color: '#6366f1', label: 'QA' }
};

const PIPELINE_STEPS = [
  { id: 'director', label: 'Director', agent: 'DIRECTOR' },
  { id: 'architect', label: 'Architect', agent: 'ATLAS' },
  { id: 'build', label: 'Build', agent: 'TITAN' },
  { id: 'review', label: 'Review', agent: 'SENTINEL' },
  { id: 'complete', label: 'Complete', agent: null }
];

const GodModePage = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  
  const [project, setProject] = useState(null);
  const [isBuilding, setIsBuilding] = useState(false);
  const [buildPhase, setBuildPhase] = useState('idle');
  const [currentAgent, setCurrentAgent] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [iteration, setIteration] = useState({ current: 0, total: 4 });
  
  const [logs, setLogs] = useState([]);
  const [files, setFiles] = useState([]);
  const [stats, setStats] = useState({
    buildTime: 0,
    filesGenerated: 0,
    qualityScore: 0,
    memoryRecorded: false
  });
  
  const logsEndRef = useRef(null);
  const buildStartTime = useRef(null);
  const timerRef = useRef(null);

  useEffect(() => {
    fetchProject();
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [projectId]);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const fetchProject = async () => {
    try {
      const [projectRes, filesRes] = await Promise.all([
        axios.get(`${API}/projects/${projectId}`),
        axios.get(`${API}/files?project_id=${projectId}`)
      ]);
      setProject(projectRes.data);
      if (filesRes.data.length > 0) {
        setFiles(filesRes.data.map(f => f.filepath));
        setBuildPhase('complete');
        setProgress(100);
        setCurrentStep(4);
      }
    } catch (error) {
      toast.error('Failed to load project');
      navigate('/studio');
    }
  };

  const addLog = (agent, message, type = 'info') => {
    const time = new Date().toLocaleTimeString('en-US', { hour12: false });
    setLogs(prev => [...prev.slice(-200), { time, agent, message, type }]);
  };

  const startBuild = async () => {
    setIsBuilding(true);
    setBuildPhase('building');
    setProgress(0);
    setCurrentStep(0);
    setLogs([]);
    setFiles([]);
    setStats({ buildTime: 0, filesGenerated: 0, qualityScore: 0, memoryRecorded: false });
    buildStartTime.current = Date.now();
    
    // Start timer
    timerRef.current = setInterval(() => {
      setStats(prev => ({
        ...prev,
        buildTime: Math.floor((Date.now() - buildStartTime.current) / 1000)
      }));
    }, 1000);
    
    addLog('SYSTEM', 'Initializing God Mode...', 'system');
    addLog('SYSTEM', `Starting build with ${iteration.total} iterations`, 'system');

    try {
      const response = await fetch(`${API}/god-mode-v2/build/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          iterations: iteration.total,
          auto_review: true,
          quality_target: 85,
          enable_memory: true
        })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              processEvent(data);
            } catch (e) {}
          }
        }
      }

      setBuildPhase('complete');
      setCurrentStep(4);
      setProgress(100);
      addLog('SYSTEM', 'Build complete!', 'success');
      toast.success('Build completed successfully!');
    } catch (error) {
      setBuildPhase('error');
      addLog('SYSTEM', `Build failed: ${error.message}`, 'error');
      toast.error('Build failed');
    } finally {
      setIsBuilding(false);
      if (timerRef.current) clearInterval(timerRef.current);
    }
  };

  const processEvent = (data) => {
    switch (data.type) {
      case 'pipeline_start':
        addLog('SYSTEM', `Pipeline started for ${data.project}`, 'system');
        break;
        
      case 'phase_start':
        setCurrentAgent(data.agent);
        if (data.agent === 'DIRECTOR') setCurrentStep(0);
        else if (data.agent === 'ATLAS') setCurrentStep(1);
        else if (data.agent === 'TITAN') setCurrentStep(2);
        else if (data.agent === 'SENTINEL') setCurrentStep(3);
        addLog(data.agent, `${data.phase} - ${data.description || 'Working...'}`, 'info');
        break;

      case 'iteration_start':
        setIteration({ current: data.iteration, total: data.total });
        addLog('SYSTEM', `Iteration ${data.iteration}/${data.total}`, 'system');
        break;
        
      case 'file_saved':
        setFiles(prev => [...prev, data.filepath]);
        setStats(prev => ({ ...prev, filesGenerated: prev.filesGenerated + 1 }));
        addLog(currentAgent || 'TITAN', `Created: ${data.filepath.split('/').pop()}`, 'success');
        break;
        
      case 'phase_complete':
        addLog(data.agent || currentAgent, `Completed`, 'success');
        break;
        
      case 'progress':
        setProgress(data.percent || 0);
        break;

      case 'pipeline_complete':
        setStats(prev => ({
          ...prev,
          qualityScore: data.quality_score || 0,
          memoryRecorded: data.memory_recorded || false
        }));
        break;
        
      case 'heartbeat':
        break;
        
      default:
        if (data.message) addLog('SYSTEM', data.message, 'info');
    }
  };

  const cancelBuild = async () => {
    try {
      await axios.post(`${API}/god-mode-v2/cancel/${projectId}`);
    } catch (e) {}
    setIsBuilding(false);
    setBuildPhase('cancelled');
    if (timerRef.current) clearInterval(timerRef.current);
    addLog('SYSTEM', 'Build cancelled', 'warning');
    toast.info('Build cancelled');
  };

  const AgentIcon = ({ agent, size = 'md' }) => {
    const config = AGENTS[agent] || { icon: Code, color: '#fff' };
    const Icon = config.icon;
    const sizeClass = size === 'sm' ? 'w-4 h-4' : 'w-5 h-5';
    return <Icon className={sizeClass} style={{ color: config.color }} />;
  };

  const getLogColor = (type) => {
    switch (type) {
      case 'error': return 'text-red-400';
      case 'success': return 'text-emerald-400';
      case 'warning': return 'text-amber-400';
      case 'system': return 'text-cyan-400';
      default: return 'text-zinc-400';
    }
  };

  if (!project) {
    return (
      <div className="min-h-screen bg-[#09090b] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#09090b] flex flex-col">
      {/* Background */}
      <div className="fixed inset-0 gradient-mesh opacity-20" />
      
      {/* Header */}
      <header className="relative z-10 border-b border-white/5 bg-[#09090b]/80 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button 
                onClick={() => navigate(`/project/${projectId}`)}
                className="p-2 rounded-lg hover:bg-white/5 transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-zinc-400" />
              </button>
              <div>
                <div className="flex items-center gap-3">
                  <Zap className="w-5 h-5 text-amber-400" />
                  <h1 className="text-lg font-semibold text-white">God Mode</h1>
                  <Badge variant="outline" className="border-amber-500/30 text-amber-400 text-xs">
                    V2
                  </Badge>
                </div>
                <p className="text-sm text-zinc-500">{project.name}</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 flex-1 max-w-6xl mx-auto w-full px-6 py-8">
        {/* Build Control */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h2 className="text-2xl font-bold text-white mb-2">AI Software Factory</h2>
          <p className="text-zinc-500 mb-8">Recursive multi-agent build system</p>
          
          {!isBuilding ? (
            <Button
              onClick={startBuild}
              size="lg"
              className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-black font-semibold px-12 py-6 text-base rounded-xl shadow-lg shadow-amber-500/20 transition-all hover:shadow-amber-500/40 hover:scale-[1.02]"
            >
              <Play className="w-5 h-5 mr-2" />
              {files.length > 0 ? 'REBUILD PROJECT' : 'START BUILD'}
            </Button>
          ) : (
            <Button
              onClick={cancelBuild}
              size="lg"
              variant="outline"
              className="border-red-500/50 text-red-400 hover:bg-red-500/10 px-12 py-6 text-base rounded-xl"
            >
              <Pause className="w-5 h-5 mr-2" />
              CANCEL BUILD
            </Button>
          )}
        </motion.div>

        {/* Pipeline Progress */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <div className="flex items-center justify-center gap-2">
            {PIPELINE_STEPS.map((step, idx) => (
              <React.Fragment key={step.id}>
                <div 
                  className={`pipeline-step ${
                    idx < currentStep ? 'complete' : 
                    idx === currentStep && isBuilding ? 'active' : 
                    'pending'
                  }`}
                >
                  {step.agent && <AgentIcon agent={step.agent} size="sm" />}
                  {!step.agent && <CheckCircle className="w-4 h-4" />}
                  <span>{step.label}</span>
                </div>
                {idx < PIPELINE_STEPS.length - 1 && (
                  <ChevronRight className="w-4 h-4 text-zinc-600" />
                )}
              </React.Fragment>
            ))}
          </div>
        </motion.div>

        {/* Progress Bar */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-zinc-500">Progress</span>
            <span className="text-white font-medium">{progress}%</span>
          </div>
          <div className="h-2 bg-white/5 rounded-full overflow-hidden">
            <motion.div 
              className="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </motion.div>

        {/* Stats Grid */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="grid grid-cols-4 gap-4 mb-8"
        >
          <div className="p-4 rounded-xl bg-white/[0.02] border border-white/5">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-blue-500/10">
                <Timer className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <p className="text-xs text-zinc-500">Build Time</p>
                <p className="text-xl font-semibold text-white">{stats.buildTime}s</p>
              </div>
            </div>
          </div>
          
          <div className="p-4 rounded-xl bg-white/[0.02] border border-white/5">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-emerald-500/10">
                <FileCode className="w-5 h-5 text-emerald-400" />
              </div>
              <div>
                <p className="text-xs text-zinc-500">Files</p>
                <p className="text-xl font-semibold text-white">{files.length}</p>
              </div>
            </div>
          </div>
          
          <div className="p-4 rounded-xl bg-white/[0.02] border border-white/5">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-purple-500/10">
                <TrendingUp className="w-5 h-5 text-purple-400" />
              </div>
              <div>
                <p className="text-xs text-zinc-500">Quality</p>
                <p className="text-xl font-semibold text-white">{stats.qualityScore}/100</p>
              </div>
            </div>
          </div>
          
          <div className="p-4 rounded-xl bg-white/[0.02] border border-white/5">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-cyan-500/10">
                <Database className="w-5 h-5 text-cyan-400" />
              </div>
              <div>
                <p className="text-xs text-zinc-500">Memory</p>
                <p className="text-xl font-semibold text-white">
                  {stats.memoryRecorded ? (
                    <CheckCircle className="w-5 h-5 text-emerald-400" />
                  ) : '-'}
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Iteration Progress */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mb-8"
        >
          <p className="text-sm text-zinc-500 mb-3">Iteration {iteration.current}/{iteration.total}</p>
          <div className="grid grid-cols-4 gap-3">
            {['Functional', 'Improved UX', 'Optimized', 'Production'].map((name, idx) => (
              <div
                key={idx}
                className={`p-3 rounded-lg text-center text-sm font-medium transition-all ${
                  idx + 1 < iteration.current
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : idx + 1 === iteration.current && isBuilding
                    ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse'
                    : 'bg-white/[0.02] text-zinc-600 border border-white/5'
                }`}
              >
                {name}
              </div>
            ))}
          </div>
        </motion.div>

        {/* Current Agent */}
        <AnimatePresence>
          {isBuilding && currentAgent && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mb-8 p-4 rounded-xl bg-white/[0.02] border border-white/10"
            >
              <div className="flex items-center gap-4">
                <div 
                  className="p-3 rounded-xl"
                  style={{ backgroundColor: `${AGENTS[currentAgent]?.color}15` }}
                >
                  <AgentIcon agent={currentAgent} />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-white">{currentAgent}</p>
                  <p className="text-sm text-zinc-500">{AGENTS[currentAgent]?.label} - Working...</p>
                </div>
                <Loader2 className="w-5 h-5 animate-spin text-amber-400" />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Build Logs */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="flex-1"
        >
          <div className="flex items-center gap-2 mb-3">
            <Terminal className="w-4 h-4 text-zinc-500" />
            <span className="text-sm text-zinc-500">Build Logs ({logs.length})</span>
          </div>
          <div className="terminal h-[300px] overflow-hidden">
            <ScrollArea className="h-full">
              <div className="p-4 space-y-1">
                {logs.length === 0 ? (
                  <p className="text-zinc-600 text-center py-12">
                    Click START BUILD to begin
                  </p>
                ) : (
                  logs.map((log, idx) => (
                    <div key={idx} className="terminal-line flex gap-3">
                      <span className="terminal-time">[{log.time}]</span>
                      <span 
                        className="terminal-agent"
                        style={{ color: AGENTS[log.agent]?.color || '#71717a' }}
                      >
                        {log.agent}:
                      </span>
                      <span className={getLogColor(log.type)}>{log.message}</span>
                    </div>
                  ))
                )}
                <div ref={logsEndRef} />
              </div>
            </ScrollArea>
          </div>
        </motion.div>

        {/* Files Generated */}
        <AnimatePresence>
          {files.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-6"
            >
              <p className="text-sm text-zinc-500 mb-3">Files Generated ({files.length})</p>
              <div className="flex flex-wrap gap-2 max-h-24 overflow-auto">
                {files.slice(0, 30).map((file, idx) => (
                  <Badge 
                    key={idx} 
                    variant="outline" 
                    className="text-xs border-white/10 text-zinc-400 bg-white/[0.02]"
                  >
                    {file.split('/').pop()}
                  </Badge>
                ))}
                {files.length > 30 && (
                  <Badge variant="outline" className="text-xs border-white/10 text-zinc-500">
                    +{files.length - 30} more
                  </Badge>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
};

export default GodModePage;
