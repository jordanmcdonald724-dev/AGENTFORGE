import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Zap, ArrowLeft, Play, Pause, RotateCcw, Settings, Download,
  Brain, Code, Shield, Rocket, Users, Activity, CheckCircle,
  XCircle, Clock, TrendingUp, Cpu, GitBranch, Layers, Eye,
  ChevronRight, Loader2, Terminal, BarChart3, AlertTriangle,
  Database, Timer, FileCode, Sparkles
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import { API } from '@/App';
import axios from 'axios';

// Agent Icons & Colors
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

const CommandCenter = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  
  const [project, setProject] = useState(null);
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
    memoryRecorded: false,
    hasLearnings: false
  });
  const [metrics, setMetrics] = useState({
    architecture_score: 0,
    code_quality: 0,
    security_score: 0,
    performance_score: 0
  });
  
  const logsEndRef = useRef(null);
  const buildStartTime = useRef(null);

  useEffect(() => {
    fetchProject();
  }, [projectId]);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const fetchProject = async () => {
    try {
      const res = await axios.get(`${API}/projects/${projectId}`);
      setProject(res.data);
      
      // Load existing files
      const filesRes = await axios.get(`${API}/files?project_id=${projectId}`);
      if (filesRes.data.length > 0) {
        setFiles(filesRes.data.map(f => f.filepath));
        setBuildPhase('complete');
        setProgress(100);
      }
    } catch (error) {
      toast.error('Failed to load project');
    }
  };

  const addLog = (agent, message, type = 'info') => {
    const time = new Date().toLocaleTimeString();
    setLogs(prev => [...prev.slice(-100), { time, agent, message, type }]);
  };

  const startRecursiveBuild = async () => {
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
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = decoder.decode(value);
        const lines = text.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              handleStreamEvent(data);
            } catch (e) {}
          }
        }
      }
    } catch (error) {
      addLog('SYSTEM', `Build error: ${error.message}`, 'error');
      setErrors(prev => [...prev, { phase: 'Connection', error: error.message }]);
      toast.error('Build failed - connection error');
    }
    
    setIsBuilding(false);
  };

  const handleStreamEvent = (data) => {
    switch (data.type) {
      case 'pipeline_start':
        setBuildPhase('planning');
        setBuildStats(prev => ({ ...prev, hasLearnings: data.has_learnings }));
        addLog('DIRECTOR', `Starting build for: ${data.project}`, 'info');
        if (data.has_learnings) {
          addLog('SYSTEM', 'Using learnings from past successful builds', 'success');
        }
        break;
        
      case 'phase_start':
        setCurrentAgent(data.agent);
        addLog(data.agent, `Starting: ${data.phase}${data.iteration ? ` (Iteration ${data.iteration})` : ''}`, 'phase');
        setPhases(prev => [...prev, { name: data.phase, agent: data.agent, status: 'active', iteration: data.iteration }]);
        break;
        
      case 'phase_complete':
        addLog(data.agent || currentAgent, `Completed: ${data.phase}${data.quality ? ` (Quality: ${data.quality})` : ''}`, 'success');
        setPhases(prev => prev.map(p => 
          p.name === data.phase ? { ...p, status: 'complete', quality: data.quality } : p
        ));
        if (data.quality) {
          setMetrics(prev => ({ ...prev, code_quality: Math.max(prev.code_quality, data.quality) }));
        }
        break;
        
      case 'phase_error':
        addLog(data.agent || 'SYSTEM', `Error: ${data.error}${data.recoverable ? ' (Continuing...)' : ''}`, 'error');
        setErrors(prev => [...prev, { phase: data.phase, error: data.error, iteration: data.iteration }]);
        setPhases(prev => prev.map(p => 
          p.name === data.phase ? { ...p, status: data.recoverable ? 'warning' : 'error' } : p
        ));
        break;
        
      case 'iteration_start':
        setCurrentIteration(data.iteration);
        setBuildPhase(
          data.iteration === 1 ? 'building' :
          data.iteration === 2 ? 'improving_ux' :
          data.iteration === 3 ? 'optimizing' :
          'polishing'
        );
        addLog('SYSTEM', `━━━ ITERATION ${data.iteration}/${data.total} ━━━`, 'iteration');
        break;
        
      case 'iteration_complete':
        addLog('SYSTEM', `Iteration ${data.iteration} complete${data.avg_quality ? ` (Avg Quality: ${data.avg_quality})` : ''}`, 'success');
        if (data.avg_quality) {
          setBuildStats(prev => ({ ...prev, qualityScore: data.avg_quality }));
        }
        break;
        
      case 'director_plan':
        addLog('DIRECTOR', 'Build plan created with AI learnings', 'success');
        break;
        
      case 'architecture':
        addLog('ATLAS', 'Architecture designed', 'success');
        setMetrics(prev => ({ ...prev, architecture_score: 85 }));
        break;
        
      case 'file_saved':
        setFiles(prev => [...prev, data.filepath]);
        addLog('TITAN', `File: ${data.filepath.split('/').pop()} (Iter ${data.iteration})`, 'file');
        setBuildStats(prev => ({ ...prev, filesGenerated: prev.filesGenerated + 1 }));
        break;
        
      case 'heartbeat':
        // Keep connection alive, update progress
        setProgress(prev => Math.min(prev + 1, 95));
        break;
        
      case 'review':
        addLog('SENTINEL', `Code review complete (Score: ${data.score || 'N/A'})`, 'review');
        if (data.score) {
          setMetrics(prev => ({ ...prev, code_quality: data.score }));
        }
        break;
        
      case 'pipeline_complete':
        setBuildPhase('complete');
        setProgress(100);
        const buildTime = buildStartTime.current ? Math.round((Date.now() - buildStartTime.current) / 1000) : data.build_time;
        setBuildStats({
          buildTime: buildTime,
          filesGenerated: data.total_files,
          qualityScore: data.quality_score || 0,
          memoryRecorded: data.memory_recorded,
          hasLearnings: buildStats.hasLearnings
        });
        addLog('SYSTEM', `BUILD COMPLETE - ${data.total_files} files, Quality: ${data.quality_score || 'N/A'}, Time: ${buildTime}s`, 'success');
        if (data.memory_recorded) {
          addLog('SYSTEM', 'Build recorded to memory system for future learning', 'success');
        }
        toast.success(`Recursive build complete! ${data.total_files} files generated`);
        break;
        
      case 'pipeline_error':
        addLog('SYSTEM', `Pipeline error: ${data.error}`, 'error');
        setBuildPhase('error');
        toast.error('Build pipeline failed');
        break;
        
      case 'build_cancelled':
        addLog('SYSTEM', `Build cancelled at iteration ${data.iteration}`, 'warning');
        setBuildPhase('cancelled');
        break;
    }
  };

  const getPhaseLabel = () => {
    switch (buildPhase) {
      case 'planning': return 'PLANNING';
      case 'building': return 'ITERATION 1: BUILDING';
      case 'improving_ux': return 'ITERATION 2: IMPROVING UX';
      case 'optimizing': return 'ITERATION 3: OPTIMIZING';
      case 'polishing': return 'ITERATION 4: PRODUCTION POLISH';
      case 'complete': return 'BUILD COMPLETE';
      default: return 'READY';
    }
  };

  const AgentIcon = ({ agent }) => {
    const config = AGENT_CONFIG[agent] || { icon: Cpu, color: '#888', bg: 'bg-zinc-500/20' };
    const Icon = config.icon;
    return (
      <div className={`w-6 h-6 rounded flex items-center justify-center ${config.bg}`}>
        <Icon className="w-4 h-4" style={{ color: config.color }} />
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-[#030712] text-white">
      {/* Header */}
      <header className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-yellow-500 to-orange-500 flex items-center justify-center">
                <Zap className="w-6 h-6 text-black" />
              </div>
              <div>
                <h1 className="font-bold text-lg">AI COMMAND CENTER</h1>
                <p className="text-xs text-zinc-500">{project?.name || 'Loading...'}</p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <Badge className={
              buildPhase === 'complete' ? 'bg-green-500/20 text-green-400' :
              isBuilding ? 'bg-yellow-500/20 text-yellow-400 animate-pulse' :
              'bg-zinc-800 text-zinc-400'
            }>
              {getPhaseLabel()}
            </Badge>
            
            {!isBuilding && buildPhase !== 'complete' && (
              <Button 
                onClick={startRecursiveBuild}
                className="bg-gradient-to-r from-yellow-500 to-orange-500 text-black font-bold"
              >
                <Play className="w-4 h-4 mr-2" />
                START FACTORY
              </Button>
            )}
            
            {isBuilding && (
              <Button variant="outline" className="border-red-500 text-red-400">
                <Pause className="w-4 h-4 mr-2" />
                BUILDING...
              </Button>
            )}
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-12 gap-6">
          
          {/* Left Column - Agent Activity */}
          <div className="col-span-3 space-y-4">
            <Card className="bg-zinc-900/50 border-zinc-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-zinc-400">AI AGENTS</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {Object.entries(AGENT_CONFIG).map(([name, config]) => {
                  const Icon = config.icon;
                  const isActive = currentAgent === name;
                  return (
                    <div 
                      key={name}
                      className={`flex items-center gap-3 p-2 rounded-lg transition-all ${
                        isActive ? 'bg-zinc-800 ring-1 ring-zinc-700' : 'opacity-50'
                      }`}
                    >
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${config.bg}`}>
                        <Icon className="w-4 h-4" style={{ color: config.color }} />
                      </div>
                      <div className="flex-1">
                        <div className="text-sm font-medium">{name}</div>
                      </div>
                      {isActive && (
                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                      )}
                    </div>
                  );
                })}
              </CardContent>
            </Card>

            {/* Iteration Progress */}
            <Card className="bg-zinc-900/50 border-zinc-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-zinc-400">RECURSIVE LOOP</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {[1, 2, 3, 4].map(i => (
                  <div key={i} className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                      i < currentIteration ? 'bg-green-500 text-black' :
                      i === currentIteration ? 'bg-yellow-500 text-black animate-pulse' :
                      'bg-zinc-800 text-zinc-500'
                    }`}>
                      {i < currentIteration ? <CheckCircle className="w-4 h-4" /> : i}
                    </div>
                    <div className="flex-1">
                      <div className={`text-sm ${i <= currentIteration ? 'text-white' : 'text-zinc-500'}`}>
                        {i === 1 ? 'Functional Build' :
                         i === 2 ? 'Improved UX' :
                         i === 3 ? 'Optimized Performance' :
                         'Production Polish'}
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Center Column - Main Build View */}
          <div className="col-span-6 space-y-4">
            {/* Progress */}
            <Card className="bg-zinc-900/50 border-zinc-800">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Build Progress</span>
                  <span className="text-sm text-zinc-400">{progress}%</span>
                </div>
                <Progress value={progress} className="h-2" />
              </CardContent>
            </Card>

            {/* Live Logs */}
            <Card className="bg-zinc-900/50 border-zinc-800 h-[500px]">
              <CardHeader className="pb-2 flex flex-row items-center justify-between">
                <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
                  <Terminal className="w-4 h-4" />
                  SYSTEM LOGS
                </CardTitle>
                <Badge variant="outline" className="text-xs">
                  {logs.length} entries
                </Badge>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[420px] pr-4">
                  <div className="space-y-1 font-mono text-xs">
                    {logs.map((log, i) => (
                      <div 
                        key={i} 
                        className={`flex gap-2 py-1 ${
                          log.type === 'error' ? 'text-red-400' :
                          log.type === 'success' ? 'text-green-400' :
                          log.type === 'phase' ? 'text-yellow-400' :
                          log.type === 'iteration' ? 'text-purple-400 font-bold' :
                          log.type === 'file' ? 'text-blue-400' :
                          log.type === 'system' ? 'text-cyan-400' :
                          'text-zinc-400'
                        }`}
                      >
                        <span className="text-zinc-600 w-20">{log.time}</span>
                        <span className="w-20 flex items-center gap-1">
                          {log.agent && <AgentIcon agent={log.agent} />}
                          <span className="truncate">{log.agent}</span>
                        </span>
                        <span className="flex-1">{log.message}</span>
                      </div>
                    ))}
                    <div ref={logsEndRef} />
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Metrics & Files */}
          <div className="col-span-3 space-y-4">
            {/* Quality Metrics */}
            <Card className="bg-zinc-900/50 border-zinc-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
                  <BarChart3 className="w-4 h-4" />
                  QUALITY SCORES
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {[
                  { label: 'Architecture', value: metrics.architecture_score, color: 'bg-blue-500' },
                  { label: 'Code Quality', value: metrics.code_quality, color: 'bg-green-500' },
                  { label: 'Security', value: metrics.security_score, color: 'bg-red-500' },
                  { label: 'Performance', value: metrics.performance_score, color: 'bg-yellow-500' }
                ].map(metric => (
                  <div key={metric.label}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-zinc-400">{metric.label}</span>
                      <span>{metric.value}/100</span>
                    </div>
                    <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${metric.color} transition-all duration-500`}
                        style={{ width: `${metric.value}%` }}
                      />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Files Generated */}
            <Card className="bg-zinc-900/50 border-zinc-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
                  <Code className="w-4 h-4" />
                  FILES ({files.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[300px]">
                  <div className="space-y-1">
                    {files.map((file, i) => (
                      <div 
                        key={i}
                        className="text-xs text-zinc-400 py-1 px-2 bg-zinc-800/50 rounded truncate"
                      >
                        {file.split('/').pop()}
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Actions */}
            {buildPhase === 'complete' && (
              <div className="space-y-2">
                <Button 
                  className="w-full bg-green-600 hover:bg-green-500"
                  onClick={() => navigate(`/god-mode/${projectId}`)}
                  data-testid="download-deploy-btn"
                >
                  <Download className="w-4 h-4 mr-2" />
                  DOWNLOAD & DEPLOY
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full"
                  onClick={() => {
                    setCurrentIteration(0);
                    setBuildPhase('idle');
                    setProgress(0);
                    setErrors([]);
                    setBuildStats({ buildTime: 0, filesGenerated: 0, qualityScore: 0, memoryRecorded: false, hasLearnings: false });
                  }}
                  data-testid="build-again-btn"
                >
                  <RotateCcw className="w-4 h-4 mr-2" />
                  BUILD AGAIN
                </Button>
              </div>
            )}

            {/* Build Stats Summary */}
            {buildPhase === 'complete' && (
              <Card className="bg-zinc-900/50 border-zinc-800" data-testid="build-stats-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
                    <Sparkles className="w-4 h-4" />
                    BUILD SUMMARY
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Build Time</span>
                    <span className="text-white flex items-center gap-1">
                      <Timer className="w-3 h-3" />
                      {buildStats.buildTime}s
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Files Generated</span>
                    <span className="text-white flex items-center gap-1">
                      <FileCode className="w-3 h-3" />
                      {buildStats.filesGenerated}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Quality Score</span>
                    <span className={`flex items-center gap-1 ${buildStats.qualityScore >= 80 ? 'text-green-400' : buildStats.qualityScore >= 60 ? 'text-yellow-400' : 'text-red-400'}`}>
                      <TrendingUp className="w-3 h-3" />
                      {buildStats.qualityScore}/100
                    </span>
                  </div>
                  {buildStats.memoryRecorded && (
                    <div className="flex justify-between">
                      <span className="text-zinc-500">Memory</span>
                      <span className="text-green-400 flex items-center gap-1">
                        <Database className="w-3 h-3" />
                        Recorded
                      </span>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Errors Panel */}
            {errors.length > 0 && (
              <Card className="bg-red-950/30 border-red-900/50" data-testid="errors-panel">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-red-400 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" />
                    ERRORS ({errors.length})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[100px]">
                    <div className="space-y-1">
                      {errors.map((err, i) => (
                        <div key={i} className="text-xs text-red-300 py-1">
                          <span className="text-red-500">{err.phase}:</span> {err.error.slice(0, 50)}...
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CommandCenter;
