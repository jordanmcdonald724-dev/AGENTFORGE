import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Cloud, Rocket, Globe, Server, CheckCircle, XCircle, 
  RefreshCw, ExternalLink, Play, Trash2, Settings,
  Terminal, Clock, AlertTriangle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { API } from '@/App';

const AutoDeployPanel = () => {
  const [activeTab, setActiveTab] = useState('deploy');
  const [deployments, setDeployments] = useState([]);
  const [godModeSessions, setGodModeSessions] = useState([]);
  const [platforms, setPlatforms] = useState({});
  const [loading, setLoading] = useState(true);
  const [deploying, setDeploying] = useState(false);
  
  // Form state
  const [selectedSession, setSelectedSession] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState('vercel');
  const [projectName, setProjectName] = useState('');
  
  // Config state
  const [vercelKey, setVercelKey] = useState('');
  const [railwayKey, setRailwayKey] = useState('');
  const [netlifyKey, setNetlifyKey] = useState('');

  useEffect(() => {
    fetchData();
    // Poll for deployment updates
    const interval = setInterval(fetchDeployments, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [deploymentsRes, platformsRes, sessionsRes] = await Promise.all([
        axios.get(`${API}/auto-deploy/deployments`),
        axios.get(`${API}/auto-deploy/platforms`),
        axios.get(`${API}/god-mode/sessions`).catch(() => ({ data: [] }))
      ]);
      setDeployments(deploymentsRes.data || []);
      setPlatforms(platformsRes.data || {});
      setGodModeSessions(sessionsRes.data?.filter(s => s.status === 'completed') || []);
    } catch (e) {
      console.error('Failed to fetch data:', e);
    }
    setLoading(false);
  };

  const fetchDeployments = async () => {
    try {
      const res = await axios.get(`${API}/auto-deploy/deployments`);
      setDeployments(res.data || []);
    } catch (e) {}
  };

  const startDeploy = async () => {
    if (!selectedSession) return;
    
    setDeploying(true);
    try {
      await axios.post(`${API}/auto-deploy/deploy`, {
        god_mode_session_id: selectedSession,
        platform: selectedPlatform,
        project_name: projectName || undefined
      });
      setSelectedSession('');
      setProjectName('');
      fetchDeployments();
      setActiveTab('history');
    } catch (e) {
      console.error('Failed to start deployment:', e);
    }
    setDeploying(false);
  };

  const redeployProject = async (deploymentId) => {
    try {
      await axios.post(`${API}/auto-deploy/redeploy/${deploymentId}`);
      fetchDeployments();
    } catch (e) {
      console.error('Failed to redeploy:', e);
    }
  };

  const deleteDeployment = async (deploymentId) => {
    try {
      await axios.delete(`${API}/auto-deploy/deployments/${deploymentId}`);
      fetchDeployments();
    } catch (e) {
      console.error('Failed to delete:', e);
    }
  };

  const saveConfig = async (platform) => {
    const keys = { vercel: vercelKey, railway: railwayKey, netlify: netlifyKey };
    try {
      await axios.post(`${API}/auto-deploy/config`, {
        platform,
        api_key: keys[platform],
        auto_deploy_enabled: true
      });
    } catch (e) {
      console.error('Failed to save config:', e);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-500/20 text-green-400';
      case 'initializing':
      case 'running': return 'bg-blue-500/20 text-blue-400';
      case 'failed': return 'bg-red-500/20 text-red-400';
      case 'deleted': return 'bg-zinc-500/20 text-zinc-400';
      default: return 'bg-yellow-500/20 text-yellow-400';
    }
  };

  const getPlatformIcon = (platform) => {
    switch (platform) {
      case 'vercel': return <div className="w-5 h-5 rounded bg-black flex items-center justify-center text-[10px] font-bold text-white">▲</div>;
      case 'railway': return <div className="w-5 h-5 rounded bg-purple-600 flex items-center justify-center text-[10px] font-bold text-white">R</div>;
      case 'netlify': return <div className="w-5 h-5 rounded bg-teal-500 flex items-center justify-center text-[10px] font-bold text-white">N</div>;
      default: return <Cloud className="w-5 h-5" />;
    }
  };

  const getProgressForDeployment = (deployment) => {
    const stages = deployment.stages || [];
    const completed = stages.filter(s => s.status === 'completed').length;
    return (completed / stages.length) * 100;
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-emerald-950/20 to-black" data-testid="auto-deploy-panel">
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 border-b border-zinc-800/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
              <Rocket className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">AUTO DEPLOY</h2>
              <p className="text-xs text-zinc-500">One-click deployment to cloud</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {Object.keys(platforms).map(p => (
              <Badge key={p} className="bg-zinc-800 text-zinc-400 text-xs capitalize">
                {p}
              </Badge>
            ))}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col overflow-hidden">
        <TabsList className="flex-shrink-0 mx-6 mt-4 bg-zinc-900/50 p-1">
          <TabsTrigger value="deploy" className="flex-1 data-[state=active]:bg-emerald-600">
            <Rocket className="w-4 h-4 mr-2" />
            Deploy
          </TabsTrigger>
          <TabsTrigger value="history" className="flex-1 data-[state=active]:bg-emerald-600">
            <Clock className="w-4 h-4 mr-2" />
            History
          </TabsTrigger>
          <TabsTrigger value="config" className="flex-1 data-[state=active]:bg-emerald-600">
            <Settings className="w-4 h-4 mr-2" />
            Config
          </TabsTrigger>
        </TabsList>

        <div className="flex-1 overflow-auto p-6">
          {/* Deploy Tab */}
          <TabsContent value="deploy" className="m-0 space-y-6">
            <div className="bg-zinc-900/50 rounded-xl p-6 border border-zinc-800">
              <h3 className="text-sm font-medium text-white mb-4">Deploy God Mode Project</h3>
              
              <div className="space-y-4">
                {/* Session Selection */}
                <div>
                  <label className="text-xs text-zinc-400 mb-2 block">God Mode Session</label>
                  <Select value={selectedSession} onValueChange={setSelectedSession}>
                    <SelectTrigger className="bg-zinc-800/50 border-zinc-700">
                      <SelectValue placeholder="Select a completed session" />
                    </SelectTrigger>
                    <SelectContent>
                      {godModeSessions.length === 0 ? (
                        <SelectItem value="none" disabled>No completed sessions</SelectItem>
                      ) : (
                        godModeSessions.map(session => (
                          <SelectItem key={session.id} value={session.id}>
                            {session.project_name || session.prompt?.slice(0, 50)}
                          </SelectItem>
                        ))
                      )}
                    </SelectContent>
                  </Select>
                </div>

                {/* Platform Selection */}
                <div>
                  <label className="text-xs text-zinc-400 mb-2 block">Deployment Platform</label>
                  <div className="grid grid-cols-3 gap-3">
                    {Object.entries(platforms).map(([key, platform]) => (
                      <button
                        key={key}
                        onClick={() => setSelectedPlatform(key)}
                        className={`p-4 rounded-xl border transition-all ${
                          selectedPlatform === key
                            ? 'border-emerald-500 bg-emerald-500/10'
                            : 'border-zinc-800 hover:border-zinc-700'
                        }`}
                      >
                        <div className="flex flex-col items-center gap-2">
                          {getPlatformIcon(key)}
                          <span className="text-sm font-medium text-white">{platform.name}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Project Name */}
                <div>
                  <label className="text-xs text-zinc-400 mb-2 block">Project Name (optional)</label>
                  <Input
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                    placeholder="my-awesome-app"
                    className="bg-zinc-800/50 border-zinc-700"
                  />
                </div>

                {/* Platform Features */}
                {selectedPlatform && platforms[selectedPlatform] && (
                  <div className="p-3 bg-zinc-800/30 rounded-lg">
                    <p className="text-xs text-zinc-500 mb-2">Platform Features:</p>
                    <div className="flex flex-wrap gap-2">
                      {platforms[selectedPlatform].features?.map((feature, i) => (
                        <Badge key={i} variant="outline" className="text-xs">
                          {feature}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                <Button
                  onClick={startDeploy}
                  disabled={deploying || !selectedSession}
                  className="w-full bg-emerald-600 hover:bg-emerald-700"
                >
                  {deploying ? (
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Rocket className="w-4 h-4 mr-2" />
                  )}
                  Deploy to {platforms[selectedPlatform]?.name || 'Cloud'}
                </Button>
              </div>
            </div>
          </TabsContent>

          {/* History Tab */}
          <TabsContent value="history" className="m-0 space-y-4">
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <RefreshCw className="w-8 h-8 text-emerald-500 animate-spin" />
              </div>
            ) : deployments.length === 0 ? (
              <div className="text-center py-12">
                <Cloud className="w-12 h-12 text-zinc-600 mx-auto mb-4" />
                <p className="text-zinc-500">No deployments yet</p>
                <Button 
                  onClick={() => setActiveTab('deploy')} 
                  className="mt-4 bg-emerald-600 hover:bg-emerald-700"
                >
                  Create First Deployment
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {deployments.map(deployment => (
                  <div
                    key={deployment.id}
                    className="p-4 bg-zinc-900/50 rounded-xl border border-zinc-800"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        {getPlatformIcon(deployment.platform)}
                        <div>
                          <p className="text-sm font-medium text-white">{deployment.project_name}</p>
                          <p className="text-xs text-zinc-500">{deployment.platform}</p>
                        </div>
                      </div>
                      <Badge className={getStatusColor(deployment.status)}>
                        {deployment.status}
                      </Badge>
                    </div>

                    {/* Progress */}
                    {deployment.status !== 'completed' && deployment.status !== 'failed' && deployment.status !== 'deleted' && (
                      <div className="mb-3">
                        <Progress value={getProgressForDeployment(deployment)} className="h-1.5" />
                        <p className="text-xs text-zinc-500 mt-1">
                          {deployment.stages?.find(s => s.status === 'running')?.name || 'Processing...'}
                        </p>
                      </div>
                    )}

                    {/* Logs */}
                    {deployment.logs && deployment.logs.length > 0 && (
                      <div className="mb-3 p-2 bg-black/50 rounded-lg max-h-24 overflow-auto">
                        {deployment.logs.slice(-3).map((log, i) => (
                          <p key={i} className="text-[10px] font-mono text-zinc-400">{log}</p>
                        ))}
                      </div>
                    )}

                    {/* Actions */}
                    <div className="flex items-center justify-between pt-3 border-t border-zinc-800">
                      <span className="text-xs text-zinc-500">
                        <Clock className="w-3 h-3 inline mr-1" />
                        {new Date(deployment.created_at).toLocaleString()}
                      </span>
                      <div className="flex gap-2">
                        {deployment.deployment_url && (
                          <Button
                            size="sm"
                            variant="outline"
                            className="border-emerald-500/50 text-emerald-400"
                            onClick={() => window.open(deployment.deployment_url, '_blank')}
                          >
                            <ExternalLink className="w-3 h-3 mr-1" />
                            Visit
                          </Button>
                        )}
                        {deployment.status === 'completed' && (
                          <Button
                            size="sm"
                            variant="outline"
                            className="border-zinc-700"
                            onClick={() => redeployProject(deployment.id)}
                          >
                            <RefreshCw className="w-3 h-3 mr-1" />
                            Redeploy
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="ghost"
                          className="text-red-400 hover:text-red-300"
                          onClick={() => deleteDeployment(deployment.id)}
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Config Tab */}
          <TabsContent value="config" className="m-0 space-y-6">
            <div className="bg-zinc-900/50 rounded-xl p-6 border border-zinc-800">
              <h3 className="text-sm font-medium text-white mb-4">Platform API Keys</h3>
              
              <div className="space-y-6">
                {/* Vercel */}
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    {getPlatformIcon('vercel')}
                    <label className="text-sm text-white">Vercel API Token</label>
                  </div>
                  <div className="flex gap-2">
                    <Input
                      type="password"
                      value={vercelKey}
                      onChange={(e) => setVercelKey(e.target.value)}
                      placeholder="Enter Vercel API token"
                      className="bg-zinc-800/50 border-zinc-700"
                    />
                    <Button onClick={() => saveConfig('vercel')} variant="outline">Save</Button>
                  </div>
                  <p className="text-xs text-zinc-500 mt-1">
                    Get from: vercel.com/account/tokens
                  </p>
                </div>

                {/* Railway */}
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    {getPlatformIcon('railway')}
                    <label className="text-sm text-white">Railway API Token</label>
                  </div>
                  <div className="flex gap-2">
                    <Input
                      type="password"
                      value={railwayKey}
                      onChange={(e) => setRailwayKey(e.target.value)}
                      placeholder="Enter Railway API token"
                      className="bg-zinc-800/50 border-zinc-700"
                    />
                    <Button onClick={() => saveConfig('railway')} variant="outline">Save</Button>
                  </div>
                  <p className="text-xs text-zinc-500 mt-1">
                    Get from: railway.app/account/tokens
                  </p>
                </div>

                {/* Netlify */}
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    {getPlatformIcon('netlify')}
                    <label className="text-sm text-white">Netlify Personal Access Token</label>
                  </div>
                  <div className="flex gap-2">
                    <Input
                      type="password"
                      value={netlifyKey}
                      onChange={(e) => setNetlifyKey(e.target.value)}
                      placeholder="Enter Netlify token"
                      className="bg-zinc-800/50 border-zinc-700"
                    />
                    <Button onClick={() => saveConfig('netlify')} variant="outline">Save</Button>
                  </div>
                  <p className="text-xs text-zinc-500 mt-1">
                    Get from: app.netlify.com/user/applications
                  </p>
                </div>
              </div>
            </div>
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
};

export default AutoDeployPanel;
