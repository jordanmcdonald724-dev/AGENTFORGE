import React, { useState, useEffect } from 'react';
import { 
  Brain, Dna, Wand2, Sparkles, Store, FlaskConical, 
  ChevronRight, Play, Pause, Eye, Download, Star,
  Zap, TrendingUp, GitBranch, Layers, Atom, Rocket,
  Search, Filter, RefreshCw, ArrowRight, Check, X
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const LabsPanel = ({ projectId }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [worldModelData, setWorldModelData] = useState(null);
  const [dnaLibrary, setDnaLibrary] = useState(null);
  const [experiments, setExperiments] = useState([]);
  const [marketplace, setMarketplace] = useState([]);
  const [godModePrompt, setGodModePrompt] = useState('');
  const [godModeSession, setGodModeSession] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchLabsData();
  }, [activeTab]);

  const fetchLabsData = async () => {
    try {
      if (activeTab === 'world-model' || activeTab === 'overview') {
        const res = await fetch(`${API_URL}/api/world-model/insights`);
        const data = await res.json();
        setWorldModelData(data);
      }
      
      if (activeTab === 'dna' || activeTab === 'overview') {
        const res = await fetch(`${API_URL}/api/dna/library`);
        const data = await res.json();
        setDnaLibrary(data);
      }
      
      if (activeTab === 'discovery' || activeTab === 'overview') {
        const res = await fetch(`${API_URL}/api/discovery/experiments`);
        const data = await res.json();
        setExperiments(data);
      }
      
      if (activeTab === 'marketplace' || activeTab === 'overview') {
        const res = await fetch(`${API_URL}/api/marketplace/modules?limit=20`);
        const data = await res.json();
        setMarketplace(data);
      }
    } catch (error) {
      console.error('Error fetching labs data:', error);
    }
  };

  const executeGodMode = async () => {
    if (!godModePrompt.trim()) return;
    
    setIsLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/god-mode/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: godModePrompt })
      });
      const data = await res.json();
      setGodModeSession(data);
      
      // Auto-build if plan succeeded
      if (data.session_id && data.status === 'planned') {
        const buildRes = await fetch(`${API_URL}/api/god-mode/${data.session_id}/build`, {
          method: 'POST'
        });
        const buildData = await buildRes.json();
        setGodModeSession(prev => ({ ...prev, ...buildData }));
      }
    } catch (error) {
      console.error('God Mode error:', error);
    }
    setIsLoading(false);
  };

  const startExperiment = async (type, hypothesis) => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/discovery/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ experiment_type: type, hypothesis })
      });
      const data = await res.json();
      setExperiments(prev => [data, ...prev]);
    } catch (error) {
      console.error('Experiment error:', error);
    }
    setIsLoading(false);
  };

  const learnFromProject = async () => {
    if (!projectId) return;
    
    setIsLoading(true);
    try {
      await fetch(`${API_URL}/api/world-model/learn?project_id=${projectId}`, {
        method: 'POST'
      });
      fetchLabsData();
    } catch (error) {
      console.error('Learn error:', error);
    }
    setIsLoading(false);
  };

  const TABS = [
    { id: 'overview', label: 'Overview', icon: FlaskConical },
    { id: 'world-model', label: 'World Model', icon: Brain },
    { id: 'dna', label: 'Software DNA', icon: Dna },
    { id: 'god-mode', label: 'God Mode', icon: Wand2 },
    { id: 'discovery', label: 'Discovery', icon: Sparkles },
    { id: 'marketplace', label: 'Marketplace', icon: Store }
  ];

  return (
    <div className="labs-panel h-full bg-zinc-950 text-white" data-testid="labs-panel">
      {/* Header */}
      <div className="border-b border-zinc-800 p-4">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-gradient-to-br from-violet-600 to-fuchsia-600 rounded-lg">
            <FlaskConical className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold">AgentForge Labs</h2>
            <p className="text-xs text-zinc-500">Experimental Features</p>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <span className="px-2 py-1 bg-violet-500/20 text-violet-400 text-xs rounded-full">
              EXPERIMENTAL
            </span>
          </div>
        </div>
        
        {/* Tabs */}
        <div className="flex gap-1 overflow-x-auto pb-2">
          {TABS.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm whitespace-nowrap transition-all ${
                activeTab === tab.id
                  ? 'bg-violet-600 text-white'
                  : 'text-zinc-400 hover:bg-zinc-800 hover:text-white'
              }`}
              data-testid={`labs-tab-${tab.id}`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="p-4 overflow-y-auto" style={{ height: 'calc(100% - 140px)' }}>
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6" data-testid="labs-overview">
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard
                icon={Brain}
                label="World Model"
                value={worldModelData?.total_projects_analyzed || 0}
                subtitle="Projects Learned"
                color="violet"
              />
              <StatCard
                icon={Dna}
                label="Genes"
                value={dnaLibrary?.total_genes || 0}
                subtitle="Reusable Modules"
                color="fuchsia"
              />
              <StatCard
                icon={Sparkles}
                label="Experiments"
                value={experiments.length}
                subtitle="Discoveries"
                color="amber"
              />
              <StatCard
                icon={Store}
                label="Marketplace"
                value={marketplace.length}
                subtitle="Published Modules"
                color="emerald"
              />
            </div>

            {/* Quick Actions */}
            <div className="space-y-3">
              <h3 className="text-sm font-medium text-zinc-400">Quick Actions</h3>
              <div className="grid grid-cols-2 gap-3">
                <QuickActionCard
                  icon={Wand2}
                  title="God Mode"
                  description="Create full SaaS from one prompt"
                  onClick={() => setActiveTab('god-mode')}
                  gradient="from-violet-600 to-fuchsia-600"
                />
                <QuickActionCard
                  icon={Brain}
                  title="Learn from Project"
                  description="Feed project to World Model"
                  onClick={learnFromProject}
                  gradient="from-blue-600 to-cyan-600"
                  disabled={!projectId}
                />
                <QuickActionCard
                  icon={Sparkles}
                  title="Start Discovery"
                  description="Run autonomous experiments"
                  onClick={() => setActiveTab('discovery')}
                  gradient="from-amber-600 to-orange-600"
                />
                <QuickActionCard
                  icon={Dna}
                  title="Extract Genes"
                  description="Extract reusable patterns"
                  onClick={() => setActiveTab('dna')}
                  gradient="from-emerald-600 to-teal-600"
                />
              </div>
            </div>

            {/* Recent Activity */}
            {experiments.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-sm font-medium text-zinc-400">Recent Experiments</h3>
                <div className="space-y-2">
                  {experiments.slice(0, 3).map(exp => (
                    <div key={exp.id} className="p-3 bg-zinc-900 rounded-lg border border-zinc-800">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">{exp.hypothesis}</span>
                        <span className={`text-xs px-2 py-1 rounded ${
                          exp.status === 'running' ? 'bg-blue-500/20 text-blue-400' :
                          exp.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                          'bg-zinc-500/20 text-zinc-400'
                        }`}>
                          {exp.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* World Model Tab */}
        {activeTab === 'world-model' && (
          <div className="space-y-6" data-testid="labs-world-model">
            <div className="p-4 bg-gradient-to-br from-violet-900/30 to-fuchsia-900/30 rounded-xl border border-violet-500/30">
              <div className="flex items-center gap-3 mb-4">
                <Brain className="w-6 h-6 text-violet-400" />
                <div>
                  <h3 className="font-bold">World Model</h3>
                  <p className="text-xs text-zinc-400">Global knowledge graph from all projects</p>
                </div>
              </div>
              
              {worldModelData && (
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-zinc-900/50 rounded-lg">
                    <p className="text-xs text-zinc-500">Projects Analyzed</p>
                    <p className="text-2xl font-bold">{worldModelData.total_projects_analyzed}</p>
                  </div>
                  <div className="p-3 bg-zinc-900/50 rounded-lg">
                    <p className="text-xs text-zinc-500">Top Technologies</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {worldModelData.top_technologies?.slice(0, 5).map(([tech, count]) => (
                        <span key={tech} className="px-2 py-0.5 bg-violet-500/20 text-violet-300 text-xs rounded">
                          {tech} ({count})
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
              
              {projectId && (
                <button
                  onClick={learnFromProject}
                  disabled={isLoading}
                  className="mt-4 w-full py-2 bg-violet-600 hover:bg-violet-500 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                >
                  {isLoading ? 'Learning...' : 'Learn from Current Project'}
                </button>
              )}
            </div>

            {/* Recommendations */}
            {worldModelData?.recommendations?.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-sm font-medium text-zinc-400">AI Recommendations</h3>
                {worldModelData.recommendations.map((rec, i) => (
                  <div key={i} className="p-3 bg-zinc-900 rounded-lg border border-zinc-800 flex items-start gap-3">
                    <Zap className="w-4 h-4 text-amber-400 mt-0.5" />
                    <p className="text-sm text-zinc-300">{rec}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Software DNA Tab */}
        {activeTab === 'dna' && (
          <div className="space-y-6" data-testid="labs-dna">
            <div className="p-4 bg-gradient-to-br from-fuchsia-900/30 to-pink-900/30 rounded-xl border border-fuchsia-500/30">
              <div className="flex items-center gap-3 mb-4">
                <Dna className="w-6 h-6 text-fuchsia-400" />
                <div>
                  <h3 className="font-bold">Software DNA</h3>
                  <p className="text-xs text-zinc-400">Reusable genes extracted from projects</p>
                </div>
              </div>
              
              <div className="grid grid-cols-3 gap-3">
                {Object.entries(dnaLibrary?.categories || {}).map(([key, cat]) => (
                  <div key={key} className="p-3 bg-zinc-900/50 rounded-lg text-center">
                    <p className="text-xs text-zinc-500">{cat.name}</p>
                    <p className="text-lg font-bold">{dnaLibrary?.genes?.[key]?.length || 0}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Gene Library */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium text-zinc-400">Gene Library</h3>
                <button
                  onClick={async () => {
                    if (projectId) {
                      await fetch(`${API_URL}/api/dna/extract?project_id=${projectId}`, { method: 'POST' });
                      fetchLabsData();
                    }
                  }}
                  disabled={!projectId}
                  className="text-xs px-3 py-1 bg-fuchsia-600 hover:bg-fuchsia-500 rounded disabled:opacity-50"
                >
                  Extract from Project
                </button>
              </div>
              
              {Object.entries(dnaLibrary?.genes || {}).map(([category, genes]) => (
                genes.length > 0 && (
                  <div key={category} className="space-y-2">
                    <p className="text-xs text-zinc-500 uppercase">{category}</p>
                    {genes.slice(0, 3).map(gene => (
                      <div key={gene.id} className="p-3 bg-zinc-900 rounded-lg border border-zinc-800">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium">{gene.name}</span>
                          <span className="text-xs text-zinc-500">Used {gene.usage_count}x</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )
              ))}
            </div>
          </div>
        )}

        {/* God Mode Tab */}
        {activeTab === 'god-mode' && (
          <div className="space-y-6" data-testid="labs-god-mode">
            <div className="p-6 bg-gradient-to-br from-violet-900/50 to-fuchsia-900/50 rounded-xl border border-violet-500/50">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-gradient-to-br from-violet-600 to-fuchsia-600 rounded-xl">
                  <Wand2 className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-xl font-bold">GOD MODE</h3>
                  <p className="text-sm text-zinc-400">Create a full SaaS from one prompt</p>
                </div>
              </div>

              <div className="space-y-4">
                <textarea
                  value={godModePrompt}
                  onChange={(e) => setGodModePrompt(e.target.value)}
                  placeholder="Create a full SaaS business around AI fishing analytics..."
                  className="w-full h-32 p-4 bg-zinc-900 border border-zinc-700 rounded-xl text-white placeholder-zinc-500 resize-none focus:outline-none focus:border-violet-500"
                  data-testid="god-mode-prompt"
                />
                
                <button
                  onClick={executeGodMode}
                  disabled={isLoading || !godModePrompt.trim()}
                  className="w-full py-4 bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 rounded-xl text-lg font-bold transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                  data-testid="god-mode-execute"
                >
                  {isLoading ? (
                    <>
                      <RefreshCw className="w-5 h-5 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    <>
                      <Rocket className="w-5 h-5" />
                      ACTIVATE GOD MODE
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* God Mode Result */}
            {godModeSession && (
              <div className="p-4 bg-zinc-900 rounded-xl border border-zinc-800">
                <div className="flex items-center gap-2 mb-3">
                  <Check className="w-5 h-5 text-green-400" />
                  <span className="font-medium">SaaS Created!</span>
                </div>
                
                {godModeSession.plan && (
                  <div className="space-y-2 text-sm">
                    <p><span className="text-zinc-500">Name:</span> {godModeSession.plan.business_name}</p>
                    <p><span className="text-zinc-500">Tagline:</span> {godModeSession.plan.tagline}</p>
                    {godModeSession.files_generated && (
                      <div>
                        <p className="text-zinc-500 mb-1">Files Generated:</p>
                        <div className="flex flex-wrap gap-1">
                          {godModeSession.files_generated.map((f, i) => (
                            <span key={i} className="px-2 py-1 bg-zinc-800 rounded text-xs">{f}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Templates */}
            <div className="space-y-3">
              <h3 className="text-sm font-medium text-zinc-400">Quick Templates</h3>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { label: 'Analytics Dashboard', prompt: 'Create a full SaaS analytics dashboard with real-time data visualization' },
                  { label: 'AI Tool Platform', prompt: 'Create a full SaaS platform for AI-powered content generation' },
                  { label: 'Marketplace', prompt: 'Create a full SaaS marketplace with listings, search, and payments' },
                  { label: 'Community Platform', prompt: 'Create a full SaaS community platform with profiles, posts, and messaging' }
                ].map(template => (
                  <button
                    key={template.label}
                    onClick={() => setGodModePrompt(template.prompt)}
                    className="p-3 bg-zinc-900 hover:bg-zinc-800 rounded-lg text-left text-sm transition-colors"
                  >
                    {template.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Discovery Tab */}
        {activeTab === 'discovery' && (
          <div className="space-y-6" data-testid="labs-discovery">
            <div className="p-4 bg-gradient-to-br from-amber-900/30 to-orange-900/30 rounded-xl border border-amber-500/30">
              <div className="flex items-center gap-3 mb-4">
                <Sparkles className="w-6 h-6 text-amber-400" />
                <div>
                  <h3 className="font-bold">Autonomous Discovery</h3>
                  <p className="text-xs text-zinc-400">AI runs experiments in the background</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => startExperiment('architecture', 'Explore new microservices patterns')}
                  disabled={isLoading}
                  className="p-3 bg-zinc-900/50 hover:bg-zinc-800 rounded-lg text-left transition-colors"
                >
                  <Layers className="w-4 h-4 text-amber-400 mb-2" />
                  <p className="text-sm font-medium">Architecture</p>
                  <p className="text-xs text-zinc-500">Test new patterns</p>
                </button>
                <button
                  onClick={() => startExperiment('ui_component', 'Generate innovative UI components')}
                  disabled={isLoading}
                  className="p-3 bg-zinc-900/50 hover:bg-zinc-800 rounded-lg text-left transition-colors"
                >
                  <GitBranch className="w-4 h-4 text-amber-400 mb-2" />
                  <p className="text-sm font-medium">UI Discovery</p>
                  <p className="text-xs text-zinc-500">New components</p>
                </button>
                <button
                  onClick={() => startExperiment('game_system', 'Discover new game mechanics')}
                  disabled={isLoading}
                  className="p-3 bg-zinc-900/50 hover:bg-zinc-800 rounded-lg text-left transition-colors"
                >
                  <Atom className="w-4 h-4 text-amber-400 mb-2" />
                  <p className="text-sm font-medium">Game Systems</p>
                  <p className="text-xs text-zinc-500">New mechanics</p>
                </button>
                <button
                  onClick={() => startExperiment('algorithm', 'Optimize common algorithms')}
                  disabled={isLoading}
                  className="p-3 bg-zinc-900/50 hover:bg-zinc-800 rounded-lg text-left transition-colors"
                >
                  <TrendingUp className="w-4 h-4 text-amber-400 mb-2" />
                  <p className="text-sm font-medium">Algorithms</p>
                  <p className="text-xs text-zinc-500">Optimization</p>
                </button>
              </div>
            </div>

            {/* Experiments List */}
            <div className="space-y-3">
              <h3 className="text-sm font-medium text-zinc-400">Running Experiments</h3>
              {experiments.length === 0 ? (
                <p className="text-sm text-zinc-500 text-center py-8">No experiments yet. Start one above!</p>
              ) : (
                experiments.map(exp => (
                  <div key={exp.id} className="p-4 bg-zinc-900 rounded-lg border border-zinc-800">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{exp.type_name || exp.type}</span>
                      <span className={`text-xs px-2 py-1 rounded ${
                        exp.status === 'running' ? 'bg-blue-500/20 text-blue-400' :
                        exp.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                        exp.status === 'promoted' ? 'bg-violet-500/20 text-violet-400' :
                        'bg-zinc-500/20 text-zinc-400'
                      }`}>
                        {exp.status}
                      </span>
                    </div>
                    <p className="text-sm text-zinc-400 mb-2">{exp.hypothesis}</p>
                    <div className="flex items-center gap-2 text-xs text-zinc-500">
                      <span>Iterations: {exp.current_iteration || 0}/{exp.max_iterations || 5}</span>
                      {exp.best_score > 0 && (
                        <span>• Best Score: {(exp.best_score * 100).toFixed(0)}%</span>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Marketplace Tab */}
        {activeTab === 'marketplace' && (
          <div className="space-y-6" data-testid="labs-marketplace">
            <div className="p-4 bg-gradient-to-br from-emerald-900/30 to-teal-900/30 rounded-xl border border-emerald-500/30">
              <div className="flex items-center gap-3 mb-4">
                <Store className="w-6 h-6 text-emerald-400" />
                <div>
                  <h3 className="font-bold">Module Marketplace</h3>
                  <p className="text-xs text-zinc-400">Agents publish and share reusable modules</p>
                </div>
              </div>
              
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                  <input
                    type="text"
                    placeholder="Search modules..."
                    className="w-full pl-10 pr-4 py-2 bg-zinc-900/50 border border-zinc-700 rounded-lg text-sm focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <button className="px-3 py-2 bg-zinc-900/50 border border-zinc-700 rounded-lg">
                  <Filter className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Modules List */}
            <div className="space-y-3">
              {marketplace.length === 0 ? (
                <div className="text-center py-8">
                  <Store className="w-12 h-12 text-zinc-600 mx-auto mb-3" />
                  <p className="text-sm text-zinc-500">No modules published yet</p>
                  <button
                    onClick={async () => {
                      await fetch(`${API_URL}/api/marketplace/auto-publish`, { method: 'POST' });
                      fetchLabsData();
                    }}
                    className="mt-3 text-xs px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg"
                  >
                    Auto-Publish from Genes
                  </button>
                </div>
              ) : (
                marketplace.map(module => (
                  <div key={module.id} className="p-4 bg-zinc-900 rounded-lg border border-zinc-800 hover:border-emerald-500/50 transition-colors">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h4 className="font-medium">{module.name}</h4>
                        <p className="text-xs text-zinc-500">{module.category} / {module.subcategory}</p>
                      </div>
                      <div className="flex items-center gap-1 text-amber-400">
                        <Star className="w-3 h-3 fill-current" />
                        <span className="text-xs">{module.rating?.toFixed(1) || '0.0'}</span>
                      </div>
                    </div>
                    <p className="text-sm text-zinc-400 mb-3">{module.description}</p>
                    <div className="flex items-center justify-between">
                      <div className="flex gap-1">
                        {module.tags?.slice(0, 3).map(tag => (
                          <span key={tag} className="px-2 py-0.5 bg-zinc-800 text-zinc-400 text-xs rounded">
                            {tag}
                          </span>
                        ))}
                      </div>
                      <button className="flex items-center gap-1 px-3 py-1 bg-emerald-600 hover:bg-emerald-500 rounded text-xs">
                        <Download className="w-3 h-3" />
                        {module.downloads || 0}
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Helper Components
const StatCard = ({ icon: Icon, label, value, subtitle, color }) => (
  <div className={`p-4 bg-zinc-900 rounded-xl border border-zinc-800`}>
    <div className="flex items-center gap-2 mb-2">
      <Icon className={`w-4 h-4 text-${color}-400`} />
      <span className="text-xs text-zinc-500">{label}</span>
    </div>
    <p className="text-2xl font-bold">{value}</p>
    <p className="text-xs text-zinc-500">{subtitle}</p>
  </div>
);

const QuickActionCard = ({ icon: Icon, title, description, onClick, gradient, disabled }) => (
  <button
    onClick={onClick}
    disabled={disabled}
    className={`p-4 bg-gradient-to-br ${gradient} rounded-xl text-left transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:hover:scale-100`}
  >
    <Icon className="w-5 h-5 mb-2" />
    <h4 className="font-medium text-sm">{title}</h4>
    <p className="text-xs text-white/70">{description}</p>
  </button>
);

export default LabsPanel;
