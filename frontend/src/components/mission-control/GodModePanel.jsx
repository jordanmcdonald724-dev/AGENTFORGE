import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { 
  Rocket, Zap, CheckCircle2, XCircle, Clock, Loader2,
  FileCode, Database, Shield, CreditCard, Layout, Globe,
  ArrowRight, Sparkles
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { API } from '@/App';

const GodModePanel = () => {
  const [prompt, setPrompt] = useState('');
  const [building, setBuilding] = useState(false);
  const [currentBuild, setCurrentBuild] = useState(null);
  const [builds, setBuilds] = useState([]);
  const logRef = useRef(null);

  const PHASES = [
    { id: 'planning', icon: Zap, label: 'Planning' },
    { id: 'backend', icon: FileCode, label: 'Backend' },
    { id: 'database', icon: Database, label: 'Database' },
    { id: 'auth', icon: Shield, label: 'Auth' },
    { id: 'payments', icon: CreditCard, label: 'Payments' },
    { id: 'frontend', icon: Layout, label: 'Frontend' },
    { id: 'landing', icon: Sparkles, label: 'Landing' },
    { id: 'deployment', icon: Globe, label: 'Deploy' }
  ];

  useEffect(() => {
    fetchBuilds();
  }, []);

  useEffect(() => {
    let interval;
    if (currentBuild && currentBuild.status !== 'complete' && currentBuild.status !== 'error') {
      interval = setInterval(() => pollBuild(currentBuild.id), 1000);
    }
    return () => clearInterval(interval);
  }, [currentBuild]);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [currentBuild?.logs]);

  const fetchBuilds = async () => {
    try {
      const res = await axios.get(`${API}/god-mode/builds`);
      setBuilds(res.data || []);
    } catch (e) {}
  };

  const pollBuild = async (buildId) => {
    try {
      const res = await axios.get(`${API}/god-mode/builds/${buildId}`);
      setCurrentBuild(res.data);
      if (res.data.status === 'complete') {
        toast.success('🎉 GOD MODE COMPLETE! Your company is live.');
        fetchBuilds();
      }
    } catch (e) {}
  };

  const startGodMode = async () => {
    if (!prompt.trim()) return toast.error('Enter your company idea');
    
    setBuilding(true);
    try {
      const res = await axios.post(`${API}/god-mode/create?prompt=${encodeURIComponent(prompt)}&template=saas`);
      setCurrentBuild(res.data);
      toast.success('🚀 GOD MODE ACTIVATED!');
    } catch (e) {
      toast.error('Failed to start God Mode');
    }
    setBuilding(false);
  };

  const getPhaseStatus = (phaseId) => {
    if (!currentBuild?.phases) return 'pending';
    return currentBuild.phases[phaseId]?.status || 'pending';
  };

  const StatusIcon = ({ status }) => {
    switch (status) {
      case 'complete': return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case 'running': return <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />;
      case 'error': return <XCircle className="w-4 h-4 text-red-500" />;
      default: return <Clock className="w-4 h-4 text-zinc-600" />;
    }
  };

  return (
    <div className="h-full flex flex-col bg-black/90 backdrop-blur-xl" data-testid="god-mode-panel">
      {/* Header */}
      <div className="px-6 py-4 border-b border-zinc-800/50 bg-gradient-to-r from-amber-900/20 to-transparent">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
            <Rocket className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">GOD MODE</h2>
            <p className="text-xs text-zinc-500">One prompt → Complete deployed company</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-6">
        {!currentBuild ? (
          <div className="max-w-2xl mx-auto">
            {/* Input Section */}
            <div className="text-center mb-8">
              <h3 className="text-2xl font-bold text-white mb-2">What will you build?</h3>
              <p className="text-zinc-500">Describe your company idea. I'll handle everything else.</p>
            </div>

            <div className="relative mb-8">
              <Input
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Build an AI fishing analytics SaaS..."
                className="h-14 text-lg bg-zinc-900/50 border-zinc-700 focus:border-amber-500 pr-32"
                onKeyDown={(e) => e.key === 'Enter' && startGodMode()}
              />
              <Button
                onClick={startGodMode}
                disabled={building}
                className="absolute right-2 top-2 h-10 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700"
              >
                {building ? <Loader2 className="w-4 h-4 animate-spin" /> : <Rocket className="w-4 h-4 mr-2" />}
                {building ? 'Creating...' : 'Create Company'}
              </Button>
            </div>

            {/* What you'll get */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {PHASES.map(phase => (
                <div key={phase.id} className="p-4 bg-zinc-900/50 rounded-xl border border-zinc-800">
                  <phase.icon className="w-5 h-5 text-amber-500 mb-2" />
                  <div className="text-sm font-medium text-white">{phase.label}</div>
                </div>
              ))}
            </div>

            {/* Recent Builds */}
            {builds.length > 0 && (
              <div className="mt-8">
                <h4 className="text-sm font-medium text-zinc-400 mb-3">Recent Builds</h4>
                <div className="space-y-2">
                  {builds.slice(0, 3).map(build => (
                    <div 
                      key={build.id}
                      onClick={() => setCurrentBuild(build)}
                      className="p-4 bg-zinc-900/50 rounded-xl border border-zinc-800 cursor-pointer hover:border-zinc-700"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-white">{build.company_name}</div>
                          <div className="text-xs text-zinc-500">{build.prompt?.slice(0, 50)}...</div>
                        </div>
                        <Badge className={build.status === 'complete' ? 'bg-green-500/20 text-green-400' : 'bg-amber-500/20 text-amber-400'}>
                          {build.status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="max-w-4xl mx-auto">
            {/* Build Progress */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-xl font-bold text-white">{currentBuild.company_name}</h3>
                  <p className="text-sm text-zinc-500">{currentBuild.tagline}</p>
                </div>
                <Badge className={
                  currentBuild.status === 'complete' ? 'bg-green-500/20 text-green-400' :
                  currentBuild.status === 'error' ? 'bg-red-500/20 text-red-400' :
                  'bg-cyan-500/20 text-cyan-400'
                }>
                  {currentBuild.status === 'complete' ? '✓ Complete' : `${currentBuild.progress}%`}
                </Badge>
              </div>

              {/* Progress Bar */}
              <div className="h-2 bg-zinc-800 rounded-full overflow-hidden mb-6">
                <div 
                  className="h-full bg-gradient-to-r from-amber-500 to-orange-600 transition-all duration-500"
                  style={{ width: `${currentBuild.progress}%` }}
                />
              </div>

              {/* Phase Grid */}
              <div className="grid grid-cols-4 md:grid-cols-8 gap-2 mb-6">
                {PHASES.map((phase, i) => {
                  const status = getPhaseStatus(phase.id);
                  return (
                    <div 
                      key={phase.id}
                      className={`p-3 rounded-xl border text-center transition-all ${
                        status === 'complete' ? 'bg-green-900/20 border-green-800' :
                        status === 'running' ? 'bg-cyan-900/20 border-cyan-800' :
                        'bg-zinc-900/50 border-zinc-800'
                      }`}
                    >
                      <phase.icon className={`w-5 h-5 mx-auto mb-1 ${
                        status === 'complete' ? 'text-green-400' :
                        status === 'running' ? 'text-cyan-400' :
                        'text-zinc-600'
                      }`} />
                      <div className="text-xs text-zinc-400">{phase.label}</div>
                      <StatusIcon status={status} />
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Live Logs */}
            <div className="bg-black/50 rounded-xl border border-zinc-800">
              <div className="px-4 py-2 border-b border-zinc-800 flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-xs text-zinc-500 uppercase tracking-wider">Build Logs</span>
              </div>
              <div 
                ref={logRef}
                className="h-64 overflow-auto p-4 font-mono text-sm"
              >
                {currentBuild.logs?.map((log, i) => (
                  <div key={i} className="text-zinc-400 mb-1">{log}</div>
                ))}
              </div>
            </div>

            {/* Deployment URL */}
            {currentBuild.deployment_url && currentBuild.status === 'complete' && (
              <div className="mt-6 p-4 bg-gradient-to-r from-green-900/20 to-emerald-900/20 rounded-xl border border-green-800">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm text-green-400 font-medium">🎉 Your company is live!</div>
                    <a 
                      href={currentBuild.deployment_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-white hover:text-green-400 transition-colors"
                    >
                      {currentBuild.deployment_url}
                    </a>
                  </div>
                  <Button size="sm" className="bg-green-600 hover:bg-green-700">
                    <Globe className="w-4 h-4 mr-2" />
                    Visit Site
                  </Button>
                </div>
              </div>
            )}

            {/* Back Button */}
            <Button
              variant="outline"
              onClick={() => setCurrentBuild(null)}
              className="mt-6"
            >
              ← Build Another
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default GodModePanel;
