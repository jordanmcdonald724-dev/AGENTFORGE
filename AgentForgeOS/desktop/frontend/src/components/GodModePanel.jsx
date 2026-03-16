import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Zap, Play, Pause, RotateCcw, Settings, Download,
  Brain, Code, Shield, Rocket, Users, Activity, CheckCircle,
  XCircle, Clock, TrendingUp, Cpu, GitBranch, Layers, Eye,
  ChevronRight, Loader2, Terminal, BarChart3, AlertTriangle,
  Database, Timer, FileCode, Sparkles, RefreshCw
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import { API } from '@/App';
import axios from 'axios';

// Agent Icons & Colors for God Mode V2
const AGENT_CONFIG = {
  DIRECTOR: { icon: Users, color: '#FFD700', bg: 'bg-yellow-500/20' },
  ATLAS: { icon: Layers, color: '#3B82F6', bg: 'bg-blue-500/20' },
  PIXEL: { icon: Eye, color: '#10B981', bg: 'bg-green-500/20' },
  NEXUS: { icon: GitBranch, color: '#8B5CF6', bg: 'bg-purple-500/20' },
  TITAN: { icon: Cpu, color: '#F97316', bg: 'bg-orange-500/20' },
  SYNAPSE: { icon: Brain, color: '#EC4899', bg: 'bg-pink-500/20' },
  DEPLOY: { icon: Rocket, color: '#14B8A6', bg: 'bg-teal-500/20' },
  SENTINEL: { icon: Shield, color: '#EF4444', bg: 'bg-red-500/20' },
  PHOENIX: { icon: TrendingUp, color: '#F59E0B', bg: 'bg-amber-500/20' },
  PROBE: { icon: Activity, color: '#6366F1', bg: 'bg-indigo-500/20' }
};

const ITERATION_NAMES = [
  'Functional Build',
  'Improved UX',
  'Optimized Performance',
  'Production Polish'
];

const GodModePanel = ({ projectId, projectName, onFilesGenerated }) => {
  const [isBuilding, setIsBuilding] = useState(false);
  const [buildPhase, setBuildPhase] = useState('idle');
  const [currentAgent, setCurrentAgent] = useState(null);
  const [currentIteration, setCurrentIteration] = useState(0);
  const [totalIterations, setTotalIterations] = useState(4);
  const [progress, setProgress] = useState(0);
  
  const [phases, setPhases] = useState([]);
  const [logs, setLogs] = useState([]);
  const [files, setFiles] = useState([]);
  const [errors, setErrors] = useState([]);
  const [buildStats, setBuildStats] = useState({
    buildTime: 0,
    filesGenerated: 0,
    qualityScore: 0,
    memoryRecorded: false
  });
  const [metrics, setMetrics] = useState({
    architecture_score: 0,
    code_quality: 0,
    security_score: 0,
    performance_score: 0
  });
  
  const logsEndRef = useRef(null);
  const buildStartTime = useRef(null);
  const eventSourceRef = useRef(null);

  useEffect(() => {
    loadExistingFiles();
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [projectId]);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const loadExistingFiles = async () => {
    try {
      const filesRes = await axios.get(`${API}/files?project_id=${projectId}`);
      if (filesRes.data.length > 0) {
        setFiles(filesRes.data.map(f => f.filepath));
        setBuildPhase('complete');
        setProgress(100);
      }
    } catch (error) {
      console.error('Failed to load files');
    }
  };

  const addLog = (agent, message, type = 'info') => {
    const time = new Date().toLocaleTimeString();
    setLogs(prev => [...prev.slice(-100), { time, agent, message, type }]);
  };

  const startBuild = async () => {
    setIsBuilding(true);
    setBuildPhase('starting');
    setProgress(0);
    setLogs([]);
    setFiles([]);
    setPhases([]);
    setErrors([]);
    buildStartTime.current = Date.now();
    
    addLog('SYSTEM', 'Initializing AI Software Factory...', 'system');
    addLog('SYSTEM', `Starting recursive build with ${totalIterations} iterations`, 'system');

    try {
      const response = await fetch(`${API}/god-mode-v2/build/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          iterations: totalIterations,
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
              processStreamEvent(data);
            } catch (e) {
              // Skip malformed JSON
            }
          }
        }
      }

      setBuildPhase('complete');
      setBuildStats(prev => ({
        ...prev,
        buildTime: Math.floor((Date.now() - buildStartTime.current) / 1000)
      }));
      addLog('SYSTEM', 'Build complete!', 'success');
      toast.success('Build completed successfully!');
      
      if (onFilesGenerated) {
        onFilesGenerated();
      }
    } catch (error) {
      setBuildPhase('error');
      addLog('SYSTEM', `Build failed: ${error.message}`, 'error');
      toast.error('Build failed');
    } finally {
      setIsBuilding(false);
    }
  };

  const processStreamEvent = (data) => {
    switch (data.type) {
      case 'pipeline_started':
        setBuildPhase('building');
        addLog('SYSTEM', `Pipeline started for ${data.project_name}`, 'system');
        break;
        
      case 'plan_created':
        setPhases(data.phases || []);
        addLog('DIRECTOR', `Build plan created with ${data.phases?.length || 0} phases`, 'info');
        break;
        
      case 'iteration_start':
        setCurrentIteration(data.iteration);
        setTotalIterations(data.total);
        addLog('SYSTEM', `Starting iteration ${data.iteration}/${data.total}: ${data.focus}`, 'info');
        break;
        
      case 'phase_start':
        setCurrentAgent(data.agent);
        addLog(data.agent, `Starting: ${data.phase}`, 'info');
        break;
        
      case 'agent_working':
        setCurrentAgent(data.agent);
        addLog(data.agent, data.task, 'info');
        break;
        
      case 'file_created':
        setFiles(prev => [...prev, data.filepath]);
        setBuildStats(prev => ({ ...prev, filesGenerated: prev.filesGenerated + 1 }));
        addLog(data.agent || 'FORGE', `Created: ${data.filepath}`, 'success');
        break;
        
      case 'phase_complete':
        addLog(data.agent, `Completed: ${data.phase}`, 'success');
        break;
        
      case 'progress':
        setProgress(data.percent);
        if (data.message) {
          addLog('SYSTEM', data.message, 'info');
        }
        break;
        
      case 'quality_update':
        setMetrics(prev => ({ ...prev, ...data.scores }));
        setBuildStats(prev => ({ ...prev, qualityScore: data.overall || 0 }));
        break;
        
      case 'memory_recorded':
        setBuildStats(prev => ({ ...prev, memoryRecorded: true }));
        addLog('SYSTEM', 'Build learnings recorded to memory', 'success');
        break;
        
      case 'error':
        setErrors(prev => [...prev, data.message]);
        addLog('ERROR', data.message, 'error');
        break;
        
      case 'complete':
        setProgress(100);
        setBuildPhase('complete');
        break;
        
      case 'heartbeat':
        // Keep connection alive
        break;
    }
  };

  const cancelBuild = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    setIsBuilding(false);
    setBuildPhase('cancelled');
    addLog('SYSTEM', 'Build cancelled by user', 'warning');
    toast.info('Build cancelled');
  };

  const AgentIcon = ({ agent }) => {
    const config = AGENT_CONFIG[agent] || { icon: Code, color: '#fff' };
    const Icon = config.icon;
    return <Icon className="w-4 h-4" style={{ color: config.color }} />;
  };

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c] p-4 overflow-auto" data-testid="god-mode-panel">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Zap className="w-5 h-5 text-yellow-400" />
            God Mode
            <Badge className="bg-purple-500/20 text-purple-400">V2</Badge>
          </h2>
          <p className="text-xs text-zinc-500">AI Software Factory - Recursive Build System</p>
        </div>
        
        <div className="flex gap-2">
          {!isBuilding ? (
            <Button
              onClick={startBuild}
              className="bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-black font-bold"
              data-testid="start-build-btn"
            >
              <Play className="w-4 h-4 mr-2" />
              {files.length > 0 ? 'REBUILD' : 'START BUILD'}
            </Button>
          ) : (
            <Button
              onClick={cancelBuild}
              variant="destructive"
              data-testid="cancel-build-btn"
            >
              <Pause className="w-4 h-4 mr-2" />
              CANCEL
            </Button>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex justify-between text-xs text-zinc-400 mb-1">
          <span>Build Progress</span>
          <span>{progress}%</span>
        </div>
        <Progress value={progress} className="h-2" />
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-4 gap-3 mb-4">
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardContent className="p-3">
            <div className="flex items-center gap-2">
              <Timer className="w-4 h-4 text-blue-400" />
              <div>
                <p className="text-xs text-zinc-500">Build Time</p>
                <p className="text-lg font-bold text-white">{buildStats.buildTime}s</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardContent className="p-3">
            <div className="flex items-center gap-2">
              <FileCode className="w-4 h-4 text-green-400" />
              <div>
                <p className="text-xs text-zinc-500">Files</p>
                <p className="text-lg font-bold text-white">{files.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardContent className="p-3">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-purple-400" />
              <div>
                <p className="text-xs text-zinc-500">Quality</p>
                <p className="text-lg font-bold text-white">{buildStats.qualityScore}/100</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardContent className="p-3">
            <div className="flex items-center gap-2">
              <Database className="w-4 h-4 text-cyan-400" />
              <div>
                <p className="text-xs text-zinc-500">Memory</p>
                <p className="text-lg font-bold text-white">
                  {buildStats.memoryRecorded ? <CheckCircle className="w-4 h-4 text-green-400" /> : '-'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Agents Status */}
      {isBuilding && currentAgent && (
        <div className="mb-4 p-3 rounded-lg bg-zinc-900/50 border border-zinc-800">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${AGENT_CONFIG[currentAgent]?.bg || 'bg-zinc-800'}`}>
              <AgentIcon agent={currentAgent} />
            </div>
            <div>
              <p className="text-sm font-medium text-white">{currentAgent}</p>
              <p className="text-xs text-zinc-500">Currently working...</p>
            </div>
            <Loader2 className="w-4 h-4 animate-spin text-yellow-400 ml-auto" />
          </div>
        </div>
      )}

      {/* Iteration Progress */}
      <div className="mb-4">
        <p className="text-xs text-zinc-500 mb-2">Recursive Loop ({currentIteration}/{totalIterations})</p>
        <div className="grid grid-cols-4 gap-2">
          {ITERATION_NAMES.map((name, idx) => (
            <div
              key={idx}
              className={`p-2 rounded text-center text-xs ${
                idx + 1 < currentIteration
                  ? 'bg-green-500/20 text-green-400 border border-green-500/50'
                  : idx + 1 === currentIteration
                  ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/50 animate-pulse'
                  : 'bg-zinc-800 text-zinc-500 border border-zinc-700'
              }`}
            >
              {name}
            </div>
          ))}
        </div>
      </div>

      {/* Build Logs */}
      <div className="flex-1 min-h-0">
        <p className="text-xs text-zinc-500 mb-2 flex items-center gap-2">
          <Terminal className="w-3 h-3" />
          Build Logs ({logs.length})
        </p>
        <ScrollArea className="h-[calc(100%-24px)] rounded-lg bg-black/50 border border-zinc-800">
          <div className="p-3 font-mono text-xs space-y-1">
            {logs.length === 0 ? (
              <p className="text-zinc-600 text-center py-8">
                Click START BUILD to begin God Mode
              </p>
            ) : (
              logs.map((log, idx) => (
                <div
                  key={idx}
                  className={`flex gap-2 ${
                    log.type === 'error' ? 'text-red-400' :
                    log.type === 'success' ? 'text-green-400' :
                    log.type === 'warning' ? 'text-yellow-400' :
                    log.type === 'system' ? 'text-cyan-400' :
                    'text-zinc-400'
                  }`}
                >
                  <span className="text-zinc-600">[{log.time}]</span>
                  <span className="text-zinc-500">{log.agent}:</span>
                  <span>{log.message}</span>
                </div>
              ))
            )}
            <div ref={logsEndRef} />
          </div>
        </ScrollArea>
      </div>

      {/* Files Generated */}
      {files.length > 0 && (
        <div className="mt-4">
          <p className="text-xs text-zinc-500 mb-2">Files Generated ({files.length})</p>
          <div className="flex flex-wrap gap-1 max-h-20 overflow-auto">
            {files.slice(0, 20).map((file, idx) => (
              <Badge key={idx} variant="outline" className="text-xs border-zinc-700 text-zinc-400">
                {file.split('/').pop()}
              </Badge>
            ))}
            {files.length > 20 && (
              <Badge variant="outline" className="text-xs border-zinc-700 text-zinc-400">
                +{files.length - 20} more
              </Badge>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default GodModePanel;
