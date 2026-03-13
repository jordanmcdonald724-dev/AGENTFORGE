import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Gamepad2, Play, Settings, Download, RefreshCw, 
  CheckCircle, Code, Layers, Box, Monitor
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { API } from '@/App';

const UnrealEnginePanel = () => {
  const [templates, setTemplates] = useState({});
  const [projects, setProjects] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  
  // Form state
  const [projectName, setProjectName] = useState('');
  const [projectDesc, setProjectDesc] = useState('');
  const [genre, setGenre] = useState('platformer');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [templatesRes, projectsRes] = await Promise.all([
        axios.get(`${API}/unreal/templates`),
        axios.get(`${API}/unreal/projects`)
      ]);
      setTemplates(templatesRes.data || {});
      setProjects(projectsRes.data || []);
    } catch (e) {
      console.error('Failed to fetch Unreal data');
    }
    setLoading(false);
  };

  const createProject = async () => {
    if (!projectName) return;
    
    setCreating(true);
    try {
      await axios.post(`${API}/unreal/projects/create`, {
        name: projectName,
        description: projectDesc,
        genre: genre,
        art_style: 'stylized',
        platforms: ['windows']
      });
      setProjectName('');
      setProjectDesc('');
      fetchData();
    } catch (e) {
      console.error('Failed to create project');
    }
    setCreating(false);
  };

  const buildProject = async (projectId) => {
    try {
      await axios.post(`${API}/unreal/projects/${projectId}/build`);
      fetchData();
    } catch (e) {
      console.error('Failed to start build');
    }
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-violet-950/20 to-black" data-testid="unreal-panel">
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 border-b border-zinc-800/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
              <Gamepad2 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">UNREAL ENGINE</h2>
              <p className="text-xs text-zinc-500">Generate complete game builds</p>
            </div>
          </div>
          <Badge className="bg-violet-500/20 text-violet-400 text-xs">
            UE 5.4
          </Badge>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-6">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <RefreshCw className="w-8 h-8 text-violet-500 animate-spin" />
          </div>
        ) : (
          <div className="space-y-6">
            {/* Create New Project */}
            <div className="bg-zinc-900/50 rounded-xl p-4 border border-zinc-800">
              <h3 className="text-sm font-medium text-white mb-4">Create New Game</h3>
              
              <div className="space-y-4">
                <Input
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  placeholder="Project Name"
                  className="bg-zinc-800/50 border-zinc-700"
                />
                
                <Input
                  value={projectDesc}
                  onChange={(e) => setProjectDesc(e.target.value)}
                  placeholder="Description"
                  className="bg-zinc-800/50 border-zinc-700"
                />
                
                <Select value={genre} onValueChange={setGenre}>
                  <SelectTrigger className="bg-zinc-800/50 border-zinc-700">
                    <SelectValue placeholder="Select Genre" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="action">Action/Shooter</SelectItem>
                    <SelectItem value="platformer">3D Platformer</SelectItem>
                    <SelectItem value="rpg">RPG Adventure</SelectItem>
                    <SelectItem value="racing">Racing</SelectItem>
                    <SelectItem value="puzzle">Puzzle</SelectItem>
                  </SelectContent>
                </Select>
                
                <Button
                  onClick={createProject}
                  disabled={creating || !projectName}
                  className="w-full bg-violet-600 hover:bg-violet-700"
                >
                  {creating ? (
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Play className="w-4 h-4 mr-2" />
                  )}
                  Create Game Project
                </Button>
              </div>
            </div>

            {/* Templates */}
            <div>
              <h3 className="text-sm font-medium text-white mb-3">Game Templates</h3>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(templates).map(([key, template]) => (
                  <div
                    key={key}
                    className="p-4 bg-zinc-900/50 rounded-xl border border-zinc-800 hover:border-violet-500/50 transition-all cursor-pointer"
                    onClick={() => setSelectedTemplate(key)}
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <Layers className="w-5 h-5 text-violet-400" />
                      <span className="text-sm font-medium text-white">{template.name}</span>
                    </div>
                    <p className="text-xs text-zinc-500 mb-3">{template.description}</p>
                    <div className="flex flex-wrap gap-1">
                      {template.features?.slice(0, 3).map((feature, i) => (
                        <Badge key={i} variant="outline" className="text-[10px]">
                          {feature}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Projects */}
            {projects.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-white mb-3">Your Projects</h3>
                <div className="space-y-3">
                  {projects.map(project => (
                    <div
                      key={project.id}
                      className="p-4 bg-zinc-900/50 rounded-xl border border-zinc-800"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <Box className="w-5 h-5 text-violet-400" />
                          <div>
                            <p className="text-sm font-medium text-white">{project.name}</p>
                            <p className="text-xs text-zinc-500">{project.genre}</p>
                          </div>
                        </div>
                        <Badge className={
                          project.status === 'ready' 
                            ? 'bg-green-500/20 text-green-400' 
                            : 'bg-yellow-500/20 text-yellow-400'
                        }>
                          {project.status}
                        </Badge>
                      </div>
                      
                      {project.blueprints?.length > 0 && (
                        <div className="flex flex-wrap gap-1 mb-3">
                          {project.blueprints.slice(0, 4).map((bp, i) => (
                            <span key={i} className="text-[10px] px-2 py-0.5 bg-zinc-800 rounded text-zinc-400">
                              {bp.name}
                            </span>
                          ))}
                          {project.blueprints.length > 4 && (
                            <span className="text-[10px] text-zinc-600">
                              +{project.blueprints.length - 4} more
                            </span>
                          )}
                        </div>
                      )}
                      
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => buildProject(project.id)}
                          className="border-violet-500/50 text-violet-400"
                        >
                          <Monitor className="w-3 h-3 mr-1" />
                          Build
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="text-zinc-400"
                        >
                          <Code className="w-3 h-3 mr-1" />
                          Blueprints
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default UnrealEnginePanel;
