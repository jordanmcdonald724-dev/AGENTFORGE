import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Smartphone, Play, Settings, Download, RefreshCw, 
  Code, Layers, Apple, Cpu, Layout, Plus, Trash2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { API } from '@/App';

const MobileBuilderPanel = () => {
  const [activeTab, setActiveTab] = useState('apps');
  const [apps, setApps] = useState([]);
  const [frameworks, setFrameworks] = useState({});
  const [templates, setTemplates] = useState({});
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  
  // Form state
  const [appName, setAppName] = useState('');
  const [appDesc, setAppDesc] = useState('');
  const [framework, setFramework] = useState('react_native');
  const [selectedApp, setSelectedApp] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [appsRes, frameworksRes, templatesRes] = await Promise.all([
        axios.get(`${API}/mobile-builder/apps`),
        axios.get(`${API}/mobile-builder/frameworks`),
        axios.get(`${API}/mobile-builder/templates`)
      ]);
      setApps(appsRes.data || []);
      setFrameworks(frameworksRes.data || {});
      setTemplates(templatesRes.data || {});
    } catch (e) {
      console.error('Failed to fetch data:', e);
    }
    setLoading(false);
  };

  const createApp = async () => {
    if (!appName) return;
    
    setCreating(true);
    try {
      await axios.post(`${API}/mobile-builder/apps`, {
        name: appName,
        description: appDesc,
        framework: framework,
        platforms: ['ios', 'android'],
        features: ['Authentication']
      });
      setAppName('');
      setAppDesc('');
      fetchData();
      setActiveTab('apps');
    } catch (e) {
      console.error('Failed to create app:', e);
    }
    setCreating(false);
  };

  const buildApp = async (appId, platform) => {
    try {
      await axios.post(`${API}/mobile-builder/apps/${appId}/build`, null, {
        params: { platform }
      });
      fetchData();
    } catch (e) {
      console.error('Failed to start build:', e);
    }
  };

  const deleteApp = async (appId) => {
    try {
      await axios.delete(`${API}/mobile-builder/apps/${appId}`);
      fetchData();
    } catch (e) {
      console.error('Failed to delete app:', e);
    }
  };

  const getFrameworkIcon = (fw) => {
    switch (fw) {
      case 'react_native': return <div className="w-6 h-6 rounded bg-cyan-500 flex items-center justify-center text-xs font-bold text-white">RN</div>;
      case 'flutter': return <div className="w-6 h-6 rounded bg-blue-500 flex items-center justify-center text-xs font-bold text-white">F</div>;
      case 'native_ios': return <Apple className="w-6 h-6 text-zinc-400" />;
      case 'native_android': return <Cpu className="w-6 h-6 text-green-500" />;
      default: return <Smartphone className="w-6 h-6 text-zinc-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ready': return 'bg-green-500/20 text-green-400';
      case 'generating': return 'bg-blue-500/20 text-blue-400';
      case 'building': return 'bg-yellow-500/20 text-yellow-400';
      default: return 'bg-zinc-500/20 text-zinc-400';
    }
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-cyan-950/20 to-black" data-testid="mobile-builder-panel">
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 border-b border-zinc-800/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
              <Smartphone className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">MOBILE BUILDER</h2>
              <p className="text-xs text-zinc-500">Autonomous mobile app generation</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge className="bg-cyan-500/20 text-cyan-400 text-xs">iOS</Badge>
            <Badge className="bg-green-500/20 text-green-400 text-xs">Android</Badge>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col overflow-hidden">
        <TabsList className="flex-shrink-0 mx-6 mt-4 bg-zinc-900/50 p-1">
          <TabsTrigger value="apps" className="flex-1 data-[state=active]:bg-cyan-600">
            <Layout className="w-4 h-4 mr-2" />
            Apps
          </TabsTrigger>
          <TabsTrigger value="create" className="flex-1 data-[state=active]:bg-cyan-600">
            <Plus className="w-4 h-4 mr-2" />
            Create
          </TabsTrigger>
          <TabsTrigger value="templates" className="flex-1 data-[state=active]:bg-cyan-600">
            <Layers className="w-4 h-4 mr-2" />
            Templates
          </TabsTrigger>
        </TabsList>

        <div className="flex-1 overflow-auto p-6">
          {/* Apps Tab */}
          <TabsContent value="apps" className="m-0 space-y-4">
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <RefreshCw className="w-8 h-8 text-cyan-500 animate-spin" />
              </div>
            ) : apps.length === 0 ? (
              <div className="text-center py-12">
                <Smartphone className="w-12 h-12 text-zinc-600 mx-auto mb-4" />
                <p className="text-zinc-500">No mobile apps yet</p>
                <Button 
                  onClick={() => setActiveTab('create')} 
                  className="mt-4 bg-cyan-600 hover:bg-cyan-700"
                >
                  Create First App
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {apps.map(app => (
                  <div
                    key={app.id}
                    className={`p-4 bg-zinc-900/50 rounded-xl border transition-all cursor-pointer ${
                      selectedApp?.id === app.id 
                        ? 'border-cyan-500' 
                        : 'border-zinc-800 hover:border-zinc-700'
                    }`}
                    onClick={() => setSelectedApp(app)}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        {getFrameworkIcon(app.framework)}
                        <div>
                          <p className="text-sm font-medium text-white">{app.name}</p>
                          <p className="text-xs text-zinc-500">{app.framework_info?.name || app.framework}</p>
                        </div>
                      </div>
                      <Badge className={getStatusColor(app.status)}>
                        {app.status}
                      </Badge>
                    </div>
                    
                    {app.description && (
                      <p className="text-xs text-zinc-400 mb-3">{app.description}</p>
                    )}

                    {/* Screens */}
                    {app.screens?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-3">
                        {app.screens.slice(0, 5).map((screen, i) => (
                          <Badge key={i} variant="outline" className="text-xs">
                            {screen.name}
                          </Badge>
                        ))}
                        {app.screens.length > 5 && (
                          <Badge variant="outline" className="text-xs text-zinc-500">
                            +{app.screens.length - 5}
                          </Badge>
                        )}
                      </div>
                    )}

                    {/* Actions */}
                    {selectedApp?.id === app.id && (
                      <div className="flex items-center gap-2 pt-3 border-t border-zinc-800">
                        <Button
                          size="sm"
                          onClick={(e) => { e.stopPropagation(); buildApp(app.id, 'ios'); }}
                          className="bg-zinc-800 hover:bg-zinc-700"
                        >
                          <Apple className="w-3 h-3 mr-1" />
                          iOS Build
                        </Button>
                        <Button
                          size="sm"
                          onClick={(e) => { e.stopPropagation(); buildApp(app.id, 'android'); }}
                          className="bg-zinc-800 hover:bg-zinc-700"
                        >
                          <Cpu className="w-3 h-3 mr-1" />
                          Android
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={(e) => { e.stopPropagation(); deleteApp(app.id); }}
                          className="text-red-400 hover:text-red-300 ml-auto"
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Create Tab */}
          <TabsContent value="create" className="m-0 space-y-6">
            <div className="bg-zinc-900/50 rounded-xl p-6 border border-zinc-800">
              <h3 className="text-sm font-medium text-white mb-4">Create Mobile App</h3>
              
              <div className="space-y-4">
                {/* Framework Selection */}
                <div>
                  <label className="text-xs text-zinc-400 mb-2 block">Framework</label>
                  <div className="grid grid-cols-2 gap-3">
                    {Object.entries(frameworks).map(([key, fw]) => (
                      <button
                        key={key}
                        onClick={() => setFramework(key)}
                        className={`p-4 rounded-xl border transition-all text-left ${
                          framework === key
                            ? 'border-cyan-500 bg-cyan-500/10'
                            : 'border-zinc-800 hover:border-zinc-700'
                        }`}
                      >
                        <div className="flex items-center gap-3 mb-2">
                          {getFrameworkIcon(key)}
                          <span className="text-sm font-medium text-white">{fw.name}</span>
                        </div>
                        <p className="text-xs text-zinc-500">{fw.language}</p>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {fw.platforms?.map((p, i) => (
                            <Badge key={i} variant="outline" className="text-[10px]">
                              {p}
                            </Badge>
                          ))}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                <Input
                  value={appName}
                  onChange={(e) => setAppName(e.target.value)}
                  placeholder="App Name"
                  className="bg-zinc-800/50 border-zinc-700"
                />
                
                <Input
                  value={appDesc}
                  onChange={(e) => setAppDesc(e.target.value)}
                  placeholder="Description (optional)"
                  className="bg-zinc-800/50 border-zinc-700"
                />

                <Button
                  onClick={createApp}
                  disabled={creating || !appName}
                  className="w-full bg-cyan-600 hover:bg-cyan-700"
                >
                  {creating ? (
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Smartphone className="w-4 h-4 mr-2" />
                  )}
                  Create Mobile App
                </Button>
              </div>
            </div>
          </TabsContent>

          {/* Templates Tab */}
          <TabsContent value="templates" className="m-0 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              {Object.entries(templates).map(([key, template]) => (
                <div
                  key={key}
                  className="p-4 bg-zinc-900/50 rounded-xl border border-zinc-800 hover:border-cyan-500/50 transition-all cursor-pointer"
                >
                  <h4 className="text-sm font-medium text-white mb-2">{template.name}</h4>
                  <p className="text-xs text-zinc-500 mb-3">{template.description}</p>
                  <div className="flex flex-wrap gap-1">
                    {template.features?.slice(0, 3).map((feature, i) => (
                      <Badge key={i} variant="outline" className="text-[10px]">
                        {feature}
                      </Badge>
                    ))}
                  </div>
                  <div className="mt-3 pt-3 border-t border-zinc-800">
                    <p className="text-xs text-zinc-500">
                      {template.screens?.length || 0} screens included
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
};

export default MobileBuilderPanel;
