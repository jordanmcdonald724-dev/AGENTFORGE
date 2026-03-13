import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Cpu, Wifi, Zap, Settings, Play, RefreshCw,
  Thermometer, Radio, Lightbulb, Code
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { API } from '@/App';

const HardwarePanel = () => {
  const [platforms, setPlatforms] = useState({});
  const [sensors, setSensors] = useState({});
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  
  // Form state
  const [projectName, setProjectName] = useState('');
  const [projectDesc, setProjectDesc] = useState('');
  const [platform, setPlatform] = useState('arduino_uno');
  const [projectType, setProjectType] = useState('sensor');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [platformsRes, sensorsRes, projectsRes] = await Promise.all([
        axios.get(`${API}/hardware/platforms`),
        axios.get(`${API}/hardware/sensors`),
        axios.get(`${API}/hardware/projects`)
      ]);
      setPlatforms(platformsRes.data || {});
      setSensors(sensorsRes.data || {});
      setProjects(projectsRes.data || []);
    } catch (e) {
      console.error('Failed to fetch hardware data');
    }
    setLoading(false);
  };

  const createProject = async () => {
    if (!projectName) return;
    
    setCreating(true);
    try {
      await axios.post(`${API}/hardware/projects/create`, {
        name: projectName,
        description: projectDesc,
        platform: platform,
        project_type: projectType,
        sensors: [],
        actuators: []
      });
      setProjectName('');
      setProjectDesc('');
      fetchData();
    } catch (e) {
      console.error('Failed to create project');
    }
    setCreating(false);
  };

  const compileProject = async (projectId) => {
    try {
      await axios.post(`${API}/hardware/projects/${projectId}/compile`);
      fetchData();
    } catch (e) {
      console.error('Failed to compile');
    }
  };

  const getPlatformIcon = (platformKey) => {
    if (platformKey.includes('esp')) return <Wifi className="w-5 h-5 text-cyan-400" />;
    if (platformKey.includes('raspberry')) return <Cpu className="w-5 h-5 text-pink-400" />;
    return <Zap className="w-5 h-5 text-amber-400" />;
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-amber-950/20 to-black" data-testid="hardware-panel">
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 border-b border-zinc-800/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
              <Cpu className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">HARDWARE</h2>
              <p className="text-xs text-zinc-500">Arduino & Raspberry Pi integration</p>
            </div>
          </div>
          <Button
            size="sm"
            variant="ghost"
            onClick={fetchData}
            className="text-zinc-400 hover:text-white"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-6">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <RefreshCw className="w-8 h-8 text-amber-500 animate-spin" />
          </div>
        ) : (
          <div className="space-y-6">
            {/* Create Project */}
            <div className="bg-zinc-900/50 rounded-xl p-4 border border-zinc-800">
              <h3 className="text-sm font-medium text-white mb-4">New Hardware Project</h3>
              
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
                
                <div className="grid grid-cols-2 gap-4">
                  <Select value={platform} onValueChange={setPlatform}>
                    <SelectTrigger className="bg-zinc-800/50 border-zinc-700">
                      <SelectValue placeholder="Platform" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="arduino_uno">Arduino Uno</SelectItem>
                      <SelectItem value="arduino_mega">Arduino Mega</SelectItem>
                      <SelectItem value="esp32">ESP32</SelectItem>
                      <SelectItem value="raspberry_pi_4">Raspberry Pi 4</SelectItem>
                      <SelectItem value="raspberry_pi_pico">Raspberry Pi Pico</SelectItem>
                    </SelectContent>
                  </Select>
                  
                  <Select value={projectType} onValueChange={setProjectType}>
                    <SelectTrigger className="bg-zinc-800/50 border-zinc-700">
                      <SelectValue placeholder="Type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="sensor">Sensor</SelectItem>
                      <SelectItem value="actuator">Actuator</SelectItem>
                      <SelectItem value="iot">IoT</SelectItem>
                      <SelectItem value="robotics">Robotics</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <Button
                  onClick={createProject}
                  disabled={creating || !projectName}
                  className="w-full bg-amber-600 hover:bg-amber-700"
                >
                  {creating ? (
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Play className="w-4 h-4 mr-2" />
                  )}
                  Create Project
                </Button>
              </div>
            </div>

            {/* Supported Platforms */}
            <div>
              <h3 className="text-sm font-medium text-white mb-3">Supported Platforms</h3>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(platforms).slice(0, 4).map(([key, plat]) => (
                  <div
                    key={key}
                    className="p-4 bg-zinc-900/50 rounded-xl border border-zinc-800"
                  >
                    <div className="flex items-center gap-3 mb-2">
                      {getPlatformIcon(key)}
                      <span className="text-sm font-medium text-white">{plat.name}</span>
                    </div>
                    <div className="text-xs text-zinc-500 space-y-1">
                      <p>Chip: {plat.chip}</p>
                      <p>Flash: {plat.flash}</p>
                      <p>Language: {plat.language}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Sensors */}
            <div>
              <h3 className="text-sm font-medium text-white mb-3">Supported Sensors</h3>
              <div className="flex flex-wrap gap-2">
                {Object.entries(sensors).slice(0, 8).map(([key, sensor]) => (
                  <div
                    key={key}
                    className="px-3 py-2 bg-zinc-900/50 rounded-lg border border-zinc-800 flex items-center gap-2"
                  >
                    <Thermometer className="w-3 h-3 text-cyan-400" />
                    <span className="text-xs text-zinc-400">{sensor.name}</span>
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
                          {getPlatformIcon(project.platform)}
                          <div>
                            <p className="text-sm font-medium text-white">{project.name}</p>
                            <p className="text-xs text-zinc-500">
                              {project.platform_info?.name}
                            </p>
                          </div>
                        </div>
                        <Badge variant="outline" className="text-[10px]">
                          {project.project_type}
                        </Badge>
                      </div>
                      
                      {project.code_files?.length > 0 && (
                        <div className="flex flex-wrap gap-1 mb-3">
                          {project.code_files.map((file, i) => (
                            <span key={i} className="text-[10px] px-2 py-0.5 bg-zinc-800 rounded text-zinc-400">
                              {file.name}
                            </span>
                          ))}
                        </div>
                      )}
                      
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          onClick={() => compileProject(project.id)}
                          className="bg-amber-600 hover:bg-amber-700"
                        >
                          <Zap className="w-3 h-3 mr-1" />
                          Compile
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="border-zinc-700"
                        >
                          <Code className="w-3 h-3 mr-1" />
                          Generate
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

export default HardwarePanel;
