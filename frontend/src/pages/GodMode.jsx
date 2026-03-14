import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Zap, ArrowLeft, Loader2, CheckCircle, Code, FileCode, Rocket, 
  Brain, Search, GitBranch, Box, Layers, Sparkles, Terminal,
  ChevronRight, Play, Pause, RotateCcw
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { API } from '@/App';
import { toast } from 'sonner';
import axios from 'axios';

// Throttle function to prevent too many re-renders
const throttle = (func, limit) => {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

const GodMode = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  
  const [project, setProject] = useState(null);
  const [isBuilding, setIsBuilding] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [buildPhase, setBuildPhase] = useState('idle');
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState([]);
  const [files, setFiles] = useState([]);
  const [streamContent, setStreamContent] = useState('');
  const logsEndRef = useRef(null);
  
  const phases = [
    { id: 'research', name: 'Research', icon: Search, description: 'Analyzing requirements & best practices' },
    { id: 'architecture', name: 'Architecture', icon: GitBranch, description: 'Designing system structure' },
    { id: 'core', name: 'Core Systems', icon: Box, description: 'Building foundational code' },
    { id: 'features', name: 'Features', icon: Layers, description: 'Implementing all features' },
    { id: 'polish', name: 'Polish', icon: Sparkles, description: 'Optimizing & finishing touches' },
    { id: 'complete', name: 'Complete', icon: CheckCircle, description: 'Project ready!' },
  ];

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
      navigate('/dashboard');
    }
  };

  const addLog = (message, type = 'info') => {
    setLogs(prev => [...prev, { 
      id: Date.now(), 
      message, 
      type, 
      timestamp: new Date().toLocaleTimeString() 
    }]);
  };

  const startGodMode = async () => {
    setIsBuilding(true);
    setProgress(0);
    setBuildPhase('research');
    setLogs([]);
    setFiles([]);
    setStreamContent('');
    
    addLog('🚀 GOD MODE ACTIVATED', 'success');
    addLog(`Building: ${project?.name}`, 'info');
    addLog('AI is taking full control...', 'info');
    
    try {
      // Phase 1: Research
      addLog('📚 Starting research phase...', 'phase');
      setProgress(5);
      
      const response = await fetch(`${API}/god-mode/build/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId })
      });
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullContent = "";
      let currentPhaseIndex = 0;
      let lastUpdateTime = 0;
      const UPDATE_INTERVAL = 200; // Only update UI every 200ms
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = decoder.decode(value);
        const lines = text.split('\n').filter(line => line.startsWith('data: '));
        
        for (const line of lines) {
          try {
            const data = JSON.parse(line.slice(6));
            
            if (data.type === 'god_mode_start') {
              addLog(`🎯 Target: ${data.project}`, 'info');
              addLog(`📦 Building ${data.total_phases} systems...`, 'info');
              setBuildPhase('architecture');
              setProgress(5);
            } else if (data.type === 'phase_start') {
              addLog(`\n🔨 Phase ${data.phase_num}/${data.total}: ${data.phase}`, 'phase');
              setBuildPhase(data.phase_num <= 2 ? 'core' : data.phase_num <= 4 ? 'features' : 'polish');
              setProgress(Math.floor((data.phase_num / data.total) * 80) + 10);
            } else if (data.type === 'phase_complete') {
              addLog(`✅ ${data.phase} complete (${data.files} files)`, 'success');
            } else if (data.type === 'phase_error') {
              addLog(`⚠️ ${data.phase} error: ${data.error}`, 'error');
            } else if (data.type === 'content') {
              fullContent += data.content;
              
              // Throttle UI updates
              const now = Date.now();
              if (now - lastUpdateTime > UPDATE_INTERVAL) {
                setStreamContent(fullContent.slice(-8000));
                lastUpdateTime = now;
              }
              
            } else if (data.type === 'file_saved') {
              // Real-time file save notification
              addLog(`📄 Saved: ${data.filepath}`, 'file');
              setFiles(prev => prev.includes(data.filepath) ? prev : [...prev, data.filepath]);
              // Update progress based on files saved
              setProgress(prev => Math.min(prev + 3, 95));
              
            } else if (data.type === 'god_mode_complete') {
              setBuildPhase('complete');
              setProgress(100);
              addLog(`✅ Created ${data.files_created} files!`, 'success');
              
              data.saved_files?.forEach(file => {
                addLog(`📄 ${file}`, 'file');
                setFiles(prev => [...prev, file]);
              });
              
              addLog('🎉 GOD MODE BUILD COMPLETE!', 'success');
              toast.success('God Mode Complete!');
              
              // Refresh project
              fetchProject();
            } else if (data.type === 'error') {
              addLog(`❌ Error: ${data.message}`, 'error');
              toast.error('Build failed');
            }
          } catch (e) {
            // Skip malformed JSON
          }
        }
      }
      
      // Stream ended - check what we got
      addLog('📊 Stream ended, checking results...', 'info');
      
    } catch (error) {
      addLog(`⚠️ Connection issue: ${error.message}`, 'error');
    }
    
    // Always refresh files at the end to show what was saved
    try {
      const filesRes = await axios.get(`${API}/files?project_id=${projectId}`);
      const savedFiles = filesRes.data.map(f => f.filepath);
      setFiles(savedFiles);
      
      if (savedFiles.length > 0) {
        addLog(`\n✅ Total files saved: ${savedFiles.length}`, 'success');
        setBuildPhase('complete');
        setProgress(100);
        toast.success(`Build saved ${savedFiles.length} files!`);
      } else {
        addLog('⚠️ No files were saved', 'error');
      }
    } catch (e) {
      addLog('Could not refresh files', 'error');
    }
    
    setIsBuilding(false);
    fetchProject();
  };

  const getPhaseStatus = (phaseId) => {
    const phaseOrder = phases.map(p => p.id);
    const currentIndex = phaseOrder.indexOf(buildPhase);
    const phaseIndex = phaseOrder.indexOf(phaseId);
    
    if (phaseIndex < currentIndex) return 'complete';
    if (phaseIndex === currentIndex) return 'active';
    return 'pending';
  };

  const getLogColor = (type) => {
    switch (type) {
      case 'success': return 'text-green-400';
      case 'error': return 'text-red-400';
      case 'phase': return 'text-yellow-400';
      case 'file': return 'text-blue-400';
      default: return 'text-zinc-400';
    }
  };

  return (
    <div className="min-h-screen bg-[#09090b] text-white">
      {/* Header */}
      <header className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate('/dashboard')}>
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-yellow-500 to-orange-500 flex items-center justify-center">
                <Zap className="w-6 h-6 text-black" />
              </div>
              <div>
                <h1 className="font-bold text-xl flex items-center gap-2">
                  GOD MODE
                  <Badge className="bg-yellow-500/20 text-yellow-400">AUTONOMOUS</Badge>
                </h1>
                <p className="text-sm text-zinc-500">{project?.name || 'Loading...'}</p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {!isBuilding && buildPhase !== 'complete' && (
              <Button 
                onClick={startGodMode}
                className="bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-400 hover:to-orange-400 text-black font-bold px-6"
                data-testid="start-god-mode"
              >
                <Play className="w-5 h-5 mr-2" />
                {files.length > 0 ? 'CONTINUE BUILD' : 'START BUILD'}
              </Button>
            )}
            {isBuilding && (
              <Button variant="outline" className="border-yellow-500/50 text-yellow-400" disabled>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                BUILDING...
              </Button>
            )}
            {buildPhase === 'complete' && (
              <>
                <Button 
                  onClick={startGodMode}
                  variant="outline"
                  className="border-yellow-500/50 text-yellow-400"
                >
                  <RotateCcw className="w-4 h-4 mr-2" />
                  REBUILD
                </Button>
                <Button 
                  onClick={() => navigate(`/project/${projectId}`)}
                  className="bg-green-500 hover:bg-green-600"
                >
                  <Rocket className="w-5 h-5 mr-2" />
                  VIEW PROJECT
                </Button>
              </>
            )}
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Progress Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-bold text-lg">Build Progress</h2>
            <span className="text-2xl font-bold text-yellow-400">{progress}%</span>
          </div>
          <Progress value={progress} className="h-3 bg-zinc-800" />
          
          {/* Phase Indicators */}
          <div className="mt-6 grid grid-cols-6 gap-2">
            {phases.map((phase, index) => {
              const status = getPhaseStatus(phase.id);
              const Icon = phase.icon;
              return (
                <div 
                  key={phase.id}
                  className={`p-3 rounded-lg border transition-all ${
                    status === 'complete' ? 'bg-green-500/10 border-green-500/50' :
                    status === 'active' ? 'bg-yellow-500/10 border-yellow-500/50 animate-pulse' :
                    'bg-zinc-900 border-zinc-800'
                  }`}
                >
                  <Icon className={`w-5 h-5 mb-2 ${
                    status === 'complete' ? 'text-green-400' :
                    status === 'active' ? 'text-yellow-400' :
                    'text-zinc-600'
                  }`} />
                  <p className={`text-xs font-medium ${
                    status === 'complete' ? 'text-green-400' :
                    status === 'active' ? 'text-yellow-400' :
                    'text-zinc-500'
                  }`}>{phase.name}</p>
                </div>
              );
            })}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-6">
          {/* Build Log */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
            <div className="px-4 py-3 border-b border-zinc-800 flex items-center gap-2">
              <Terminal className="w-4 h-4 text-yellow-400" />
              <span className="font-medium">Build Log</span>
              <Badge variant="outline" className="ml-auto">{logs.length} entries</Badge>
            </div>
            <ScrollArea className="h-[400px] p-4">
              <div className="space-y-1 font-mono text-sm">
                {logs.map((log) => (
                  <div key={log.id} className={`${getLogColor(log.type)}`}>
                    <span className="text-zinc-600 mr-2">[{log.timestamp}]</span>
                    {log.message}
                  </div>
                ))}
                {logs.length === 0 && (
                  <div className="text-zinc-600 text-center py-8">
                    Click START BUILD to begin God Mode
                  </div>
                )}
                <div ref={logsEndRef} />
              </div>
            </ScrollArea>
          </div>

          {/* Files Created */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
            <div className="px-4 py-3 border-b border-zinc-800 flex items-center gap-2">
              <FileCode className="w-4 h-4 text-blue-400" />
              <span className="font-medium">Files Created</span>
              <Badge variant="outline" className="ml-auto">{files.length} files</Badge>
            </div>
            <ScrollArea className="h-[400px] p-4">
              <div className="space-y-2">
                {files.map((file, index) => (
                  <motion.div
                    key={file}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center gap-2 p-2 bg-zinc-800/50 rounded-lg"
                  >
                    <FileCode className="w-4 h-4 text-blue-400" />
                    <span className="text-sm text-zinc-300">{file}</span>
                    <CheckCircle className="w-4 h-4 text-green-400 ml-auto" />
                  </motion.div>
                ))}
                {files.length === 0 && (
                  <div className="text-zinc-600 text-center py-8">
                    Files will appear here as they're created
                  </div>
                )}
              </div>
            </ScrollArea>
          </div>
        </div>

        {/* Live Output */}
        {streamContent && (
          <div className="mt-6 bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
            <div className="px-4 py-3 border-b border-zinc-800 flex items-center gap-2">
              <Code className="w-4 h-4 text-green-400" />
              <span className="font-medium">Live Output</span>
              {isBuilding && <Loader2 className="w-4 h-4 animate-spin text-yellow-400 ml-auto" />}
            </div>
            <ScrollArea className="h-[300px] p-4">
              <pre className="text-sm text-zinc-300 whitespace-pre-wrap font-mono">
                {streamContent.slice(-5000)}
              </pre>
            </ScrollArea>
          </div>
        )}

        {/* Instructions when idle */}
        {buildPhase === 'idle' && (
          <div className="mt-8 text-center">
            <div className="inline-flex items-center gap-4 p-6 bg-gradient-to-r from-yellow-500/10 to-orange-500/10 border border-yellow-500/30 rounded-2xl">
              <Brain className="w-12 h-12 text-yellow-400" />
              <div className="text-left">
                <h3 className="font-bold text-lg text-yellow-400">Ready to Build</h3>
                <p className="text-sm text-zinc-400 max-w-md">
                  God Mode will automatically research, design, and build your entire project.
                  No questions asked. Just the best possible implementation.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default GodMode;
