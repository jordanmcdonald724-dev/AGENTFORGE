import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Gamepad2, Play, Settings, Download, RefreshCw, 
  CheckCircle, Code, Layers, Box, Monitor, Cpu,
  Search, FolderOpen, Terminal, XCircle, Loader2,
  ChevronDown, ChevronRight, Clock, AlertTriangle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { API } from '@/App';

const GameBuilderPanel = () => {
  const [activeTab, setActiveTab] = useState('projects');
  const [engines, setEngines] = useState({ engines: [], unreal_installations: [], unity_installations: [] });
  const [projects, setProjects] = useState([]);
  const [builds, setBuilds] = useState([]);
  const [templates, setTemplates] = useState({});
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [detecting, setDetecting] = useState(false);
  
  // Form state
  const [selectedEngine, setSelectedEngine] = useState('unreal');
  const [projectName, setProjectName] = useState('');
  const [projectDesc, setProjectDesc] = useState('');
  const [template, setTemplate] = useState('blank');
  const [selectedProject, setSelectedProject] = useState(null);
  const [buildPlatform, setBuildPlatform] = useState('Win64');
  const [buildConfig, setBuildConfig] = useState('Development');
  
  // Engine path config
  const [unrealPath, setUnrealPath] = useState('');
  const [unityPath, setUnityPath] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (selectedEngine) {
      fetchTemplates(selectedEngine);
    }
  }, [selectedEngine]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [projectsRes, buildsRes] = await Promise.all([
        axios.get(`${API}/game-builder/projects`),
        axios.get(`${API}/game-builder/builds`)
      ]);
      setProjects(projectsRes.data || []);
      setBuilds(buildsRes.data || []);
    } catch (e) {
      console.error('Failed to fetch data:', e);
    }
    setLoading(false);
  };

  const detectEngines = async () => {
    setDetecting(true);
    try {
      const res = await axios.get(`${API}/game-builder/detect`);
      setEngines(res.data);
    } catch (e) {
      console.error('Failed to detect engines:', e);
    }
    setDetecting(false);
  };

  const fetchTemplates = async (engine) => {
    try {
      const res = await axios.get(`${API}/game-builder/templates/${engine}`);
      setTemplates(res.data || {});
    } catch (e) {
      console.error('Failed to fetch templates:', e);
    }
  };

  const saveEnginePaths = async () => {
    try {
      await axios.post(`${API}/game-builder/set-paths`, {
        unreal_path: unrealPath,
        unity_path: unityPath
      });
      detectEngines();
    } catch (e) {
      console.error('Failed to save paths:', e);
    }
  };

  const createProject = async () => {
    if (!projectName) return;
    
    setCreating(true);
    try {
      await axios.post(`${API}/game-builder/projects`, {
        name: projectName,
        description: projectDesc,
        engine: selectedEngine,
        template: template,
        platforms: ['Win64']
      });
      setProjectName('');
      setProjectDesc('');
      fetchData();
      setActiveTab('projects');
    } catch (e) {
      console.error('Failed to create project:', e);
    }
    setCreating(false);
  };

  const startBuild = async (projectId) => {
    try {
      await axios.post(`${API}/game-builder/build`, {
        project_id: projectId,
        platform: buildPlatform,
        configuration: buildConfig,
        clean_build: false
      });
      fetchData();
      setActiveTab('builds');
    } catch (e) {
      console.error('Failed to start build:', e);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-500/20 text-green-400';
      case 'building': return 'bg-blue-500/20 text-blue-400';
      case 'queued': return 'bg-yellow-500/20 text-yellow-400';
      case 'failed': return 'bg-red-500/20 text-red-400';
      case 'cancelled': return 'bg-zinc-500/20 text-zinc-400';
      default: return 'bg-zinc-500/20 text-zinc-400';
    }
  };

  const getEngineIcon = (engine) => {
    return engine === 'unity' ? (
      <div className="w-6 h-6 rounded bg-zinc-800 flex items-center justify-center text-xs font-bold text-white">U</div>
    ) : (
      <div className="w-6 h-6 rounded bg-zinc-800 flex items-center justify-center">
        <Gamepad2 className="w-4 h-4 text-violet-400" />
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-violet-950/20 to-black" data-testid="game-builder-panel">
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 border-b border-zinc-800/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center">
              <Gamepad2 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">GAME BUILDER</h2>
              <p className="text-xs text-zinc-500">Unreal Engine 5 & Unity</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge className="bg-violet-500/20 text-violet-400 text-xs">UE5</Badge>
            <Badge className="bg-fuchsia-500/20 text-fuchsia-400 text-xs">Unity</Badge>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col overflow-hidden">
        <TabsList className="flex-shrink-0 mx-6 mt-4 bg-zinc-900/50 p-1">
          <TabsTrigger value="projects" className="flex-1 data-[state=active]:bg-violet-600">
            <FolderOpen className="w-4 h-4 mr-2" />
            Projects
          </TabsTrigger>
          <TabsTrigger value="builds" className="flex-1 data-[state=active]:bg-violet-600">
            <Terminal className="w-4 h-4 mr-2" />
            Builds
          </TabsTrigger>
          <TabsTrigger value="create" className="flex-1 data-[state=active]:bg-violet-600">
            <Play className="w-4 h-4 mr-2" />
            Create
          </TabsTrigger>
          <TabsTrigger value="config" className="flex-1 data-[state=active]:bg-violet-600">
            <Settings className="w-4 h-4 mr-2" />
            Config
          </TabsTrigger>
        </TabsList>

        <div className="flex-1 overflow-auto p-6">
          {/* Projects Tab */}
          <TabsContent value="projects" className="m-0 space-y-4">
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <RefreshCw className="w-8 h-8 text-violet-500 animate-spin" />
              </div>
            ) : projects.length === 0 ? (
              <div className="text-center py-12">
                <Gamepad2 className="w-12 h-12 text-zinc-600 mx-auto mb-4" />
                <p className="text-zinc-500">No projects yet</p>
                <Button 
                  onClick={() => setActiveTab('create')} 
                  className="mt-4 bg-violet-600 hover:bg-violet-700"
                >
                  Create First Project
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {projects.map(project => (
                  <div
                    key={project.id}
                    className={`p-4 bg-zinc-900/50 rounded-xl border transition-all cursor-pointer ${
                      selectedProject?.id === project.id 
                        ? 'border-violet-500' 
                        : 'border-zinc-800 hover:border-zinc-700'
                    }`}
                    onClick={() => setSelectedProject(project)}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        {getEngineIcon(project.engine)}
                        <div>
                          <p className="text-sm font-medium text-white">{project.name}</p>
                          <p className="text-xs text-zinc-500">{project.engine_name} • {project.template}</p>
                        </div>
                      </div>
                      <Badge className={getStatusColor(project.status)}>
                        {project.status}
                      </Badge>
                    </div>
                    
                    {project.description && (
                      <p className="text-xs text-zinc-400 mb-3">{project.description}</p>
                    )}
                    
                    {selectedProject?.id === project.id && (
                      <div className="flex items-center gap-2 pt-3 border-t border-zinc-800">
                        <Select value={buildPlatform} onValueChange={setBuildPlatform}>
                          <SelectTrigger className="w-32 h-8 text-xs bg-zinc-800 border-zinc-700">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="Win64">Windows</SelectItem>
                            <SelectItem value="Mac">macOS</SelectItem>
                            <SelectItem value="Linux">Linux</SelectItem>
                            <SelectItem value="Android">Android</SelectItem>
                          </SelectContent>
                        </Select>
                        
                        <Select value={buildConfig} onValueChange={setBuildConfig}>
                          <SelectTrigger className="w-32 h-8 text-xs bg-zinc-800 border-zinc-700">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="Development">Development</SelectItem>
                            <SelectItem value="Shipping">Shipping</SelectItem>
                            <SelectItem value="Debug">Debug</SelectItem>
                          </SelectContent>
                        </Select>
                        
                        <Button
                          size="sm"
                          onClick={(e) => { e.stopPropagation(); startBuild(project.id); }}
                          className="bg-violet-600 hover:bg-violet-700"
                        >
                          <Play className="w-3 h-3 mr-1" />
                          Build
                        </Button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Builds Tab */}
          <TabsContent value="builds" className="m-0 space-y-4">
            {builds.length === 0 ? (
              <div className="text-center py-12">
                <Terminal className="w-12 h-12 text-zinc-600 mx-auto mb-4" />
                <p className="text-zinc-500">No builds yet</p>
              </div>
            ) : (
              <div className="space-y-3">
                {builds.map(build => (
                  <div
                    key={build.id}
                    className="p-4 bg-zinc-900/50 rounded-xl border border-zinc-800"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        {getEngineIcon(build.engine)}
                        <div>
                          <p className="text-sm font-medium text-white">{build.project_name}</p>
                          <p className="text-xs text-zinc-500">
                            {build.platform} • {build.configuration}
                          </p>
                        </div>
                      </div>
                      <Badge className={getStatusColor(build.status)}>
                        {build.status === 'building' && (
                          <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                        )}
                        {build.status}
                      </Badge>
                    </div>
                    
                    {build.status === 'building' && (
                      <div className="space-y-2 mb-3">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-zinc-400">
                            {build.stages?.[build.stages.length - 1]?.name || 'Starting...'}
                          </span>
                          <span className="text-violet-400">{build.progress}%</span>
                        </div>
                        <Progress value={build.progress} className="h-1.5" />
                      </div>
                    )}
                    
                    {build.logs && build.logs.length > 0 && (
                      <div className="mt-3 p-2 bg-black/50 rounded-lg max-h-32 overflow-auto">
                        {build.logs.slice(-5).map((log, i) => (
                          <p key={i} className="text-[10px] font-mono text-zinc-400">{log}</p>
                        ))}
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between mt-3 pt-3 border-t border-zinc-800">
                      <span className="text-xs text-zinc-500">
                        <Clock className="w-3 h-3 inline mr-1" />
                        {new Date(build.started_at).toLocaleString()}
                      </span>
                      {build.status === 'completed' && build.output_path && (
                        <Button size="sm" variant="outline" className="border-green-500/50 text-green-400">
                          <Download className="w-3 h-3 mr-1" />
                          Download
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Create Tab */}
          <TabsContent value="create" className="m-0 space-y-6">
            <div className="bg-zinc-900/50 rounded-xl p-4 border border-zinc-800">
              <h3 className="text-sm font-medium text-white mb-4">Create New Game Project</h3>
              
              <div className="space-y-4">
                {/* Engine Selection */}
                <div>
                  <label className="text-xs text-zinc-400 mb-2 block">Game Engine</label>
                  <div className="grid grid-cols-2 gap-3">
                    <button
                      onClick={() => setSelectedEngine('unreal')}
                      className={`p-4 rounded-xl border transition-all ${
                        selectedEngine === 'unreal'
                          ? 'border-violet-500 bg-violet-500/10'
                          : 'border-zinc-800 hover:border-zinc-700'
                      }`}
                    >
                      <Gamepad2 className="w-8 h-8 text-violet-400 mx-auto mb-2" />
                      <p className="text-sm font-medium text-white">Unreal Engine 5</p>
                      <p className="text-xs text-zinc-500">AAA quality games</p>
                    </button>
                    
                    <button
                      onClick={() => setSelectedEngine('unity')}
                      className={`p-4 rounded-xl border transition-all ${
                        selectedEngine === 'unity'
                          ? 'border-fuchsia-500 bg-fuchsia-500/10'
                          : 'border-zinc-800 hover:border-zinc-700'
                      }`}
                    >
                      <div className="w-8 h-8 rounded bg-zinc-700 flex items-center justify-center text-lg font-bold text-white mx-auto mb-2">U</div>
                      <p className="text-sm font-medium text-white">Unity</p>
                      <p className="text-xs text-zinc-500">2D/3D/Mobile/VR</p>
                    </button>
                  </div>
                </div>
                
                <Input
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  placeholder="Project Name"
                  className="bg-zinc-800/50 border-zinc-700"
                />
                
                <Input
                  value={projectDesc}
                  onChange={(e) => setProjectDesc(e.target.value)}
                  placeholder="Description (optional)"
                  className="bg-zinc-800/50 border-zinc-700"
                />
                
                <Select value={template} onValueChange={setTemplate}>
                  <SelectTrigger className="bg-zinc-800/50 border-zinc-700">
                    <SelectValue placeholder="Select Template" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(templates).map(([key, tmpl]) => (
                      <SelectItem key={key} value={key}>
                        {tmpl.name} - {tmpl.description}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                
                <Button
                  onClick={createProject}
                  disabled={creating || !projectName}
                  className={`w-full ${
                    selectedEngine === 'unity' 
                      ? 'bg-fuchsia-600 hover:bg-fuchsia-700' 
                      : 'bg-violet-600 hover:bg-violet-700'
                  }`}
                >
                  {creating ? (
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Play className="w-4 h-4 mr-2" />
                  )}
                  Create {selectedEngine === 'unity' ? 'Unity' : 'Unreal'} Project
                </Button>
              </div>
            </div>
          </TabsContent>

          {/* Config Tab */}
          <TabsContent value="config" className="m-0 space-y-6">
            {/* Engine Detection */}
            <div className="bg-zinc-900/50 rounded-xl p-4 border border-zinc-800">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-white">Detect Installed Engines</h3>
                <Button
                  size="sm"
                  onClick={detectEngines}
                  disabled={detecting}
                  variant="outline"
                  className="border-violet-500/50"
                >
                  {detecting ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Search className="w-4 h-4 mr-2" />
                  )}
                  Scan System
                </Button>
              </div>
              
              {engines.engines.length > 0 ? (
                <div className="space-y-3">
                  {engines.unreal_installations.map((inst, i) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-zinc-800/50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <Gamepad2 className="w-5 h-5 text-violet-400" />
                        <div>
                          <p className="text-sm font-medium text-white">Unreal Engine {inst.version}</p>
                          <p className="text-xs text-zinc-500">{inst.path}</p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        {inst.editor_available && (
                          <Badge className="bg-green-500/20 text-green-400 text-xs">Editor</Badge>
                        )}
                        {inst.build_tools_available && (
                          <Badge className="bg-blue-500/20 text-blue-400 text-xs">Build Tools</Badge>
                        )}
                      </div>
                    </div>
                  ))}
                  
                  {engines.unity_installations.map((inst, i) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-zinc-800/50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="w-5 h-5 rounded bg-zinc-700 flex items-center justify-center text-xs font-bold text-white">U</div>
                        <div>
                          <p className="text-sm font-medium text-white">Unity {inst.version}</p>
                          <p className="text-xs text-zinc-500">{inst.path}</p>
                        </div>
                      </div>
                      <Badge className="bg-green-500/20 text-green-400 text-xs">Ready</Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6">
                  <AlertTriangle className="w-8 h-8 text-yellow-500 mx-auto mb-2" />
                  <p className="text-sm text-zinc-400">Click "Scan System" to detect installed engines</p>
                </div>
              )}
            </div>
            
            {/* Manual Path Configuration */}
            <div className="bg-zinc-900/50 rounded-xl p-4 border border-zinc-800">
              <h3 className="text-sm font-medium text-white mb-4">Manual Engine Paths</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="text-xs text-zinc-400 mb-2 block">Unreal Engine Path</label>
                  <Input
                    value={unrealPath}
                    onChange={(e) => setUnrealPath(e.target.value)}
                    placeholder="C:/Program Files/Epic Games/UE_5.4"
                    className="bg-zinc-800/50 border-zinc-700 text-xs"
                  />
                </div>
                
                <div>
                  <label className="text-xs text-zinc-400 mb-2 block">Unity Path</label>
                  <Input
                    value={unityPath}
                    onChange={(e) => setUnityPath(e.target.value)}
                    placeholder="C:/Program Files/Unity/Hub/Editor/2023.2"
                    className="bg-zinc-800/50 border-zinc-700 text-xs"
                  />
                </div>
                
                <Button
                  onClick={saveEnginePaths}
                  className="w-full bg-zinc-700 hover:bg-zinc-600"
                >
                  Save Configuration
                </Button>
              </div>
            </div>
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
};

export default GameBuilderPanel;
