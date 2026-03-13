import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Moon, Sun, Clock, Play, Pause, CheckCircle, XCircle, 
  RefreshCw, Settings, Zap, Shield, Code, FileText, Database
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { API } from '@/App';

const TASK_ICONS = {
  evolution_scan: { icon: Zap, color: '#8b5cf6' },
  test_suite: { icon: CheckCircle, color: '#22c55e' },
  dependency_update: { icon: Code, color: '#06b6d4' },
  backup: { icon: Database, color: '#f59e0b' },
  performance_audit: { icon: Zap, color: '#ec4899' },
  security_scan: { icon: Shield, color: '#ef4444' },
  code_cleanup: { icon: Code, color: '#6366f1' },
  documentation_gen: { icon: FileText, color: '#14b8a6' }
};

const NightShiftPanel = ({ projectId }) => {
  const [config, setConfig] = useState(null);
  const [availableTasks, setAvailableTasks] = useState({});
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTasks, setSelectedTasks] = useState([]);
  const [triggering, setTriggering] = useState(false);

  useEffect(() => {
    fetchData();
  }, [projectId]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [configRes, tasksRes, runsRes] = await Promise.all([
        axios.get(`${API}/night-shift/config/${projectId}`).catch(() => ({ data: null })),
        axios.get(`${API}/night-shift/tasks`),
        axios.get(`${API}/night-shift/runs/${projectId}`).catch(() => ({ data: [] }))
      ]);
      
      setConfig(configRes.data);
      setAvailableTasks(tasksRes.data);
      setRuns(runsRes.data || []);
      
      if (configRes.data?.tasks) {
        setSelectedTasks(configRes.data.tasks);
      }
    } catch (e) {
      console.error('Failed to fetch night shift data');
    }
    setLoading(false);
  };

  const saveConfig = async () => {
    try {
      await axios.post(`${API}/night-shift/configure`, {
        project_id: projectId,
        enabled: true,
        tasks: selectedTasks
      });
      fetchData();
    } catch (e) {
      console.error('Failed to save config');
    }
  };

  const triggerNightShift = async () => {
    setTriggering(true);
    try {
      await axios.post(`${API}/night-shift/trigger/${projectId}`);
      setTimeout(fetchData, 2000);
    } catch (e) {
      console.error('Failed to trigger night shift');
    }
    setTriggering(false);
  };

  const toggleTask = (taskName) => {
    setSelectedTasks(prev => 
      prev.includes(taskName) 
        ? prev.filter(t => t !== taskName)
        : [...prev, taskName]
    );
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-indigo-950/30 to-black" data-testid="night-shift-panel">
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 border-b border-zinc-800/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <Moon className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">NIGHT SHIFT</h2>
              <p className="text-xs text-zinc-500">Autonomous overnight processing</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {config?.enabled && (
              <Badge className="bg-indigo-500/20 text-indigo-400 text-xs">
                Active
              </Badge>
            )}
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
      </div>

      <div className="flex-1 overflow-auto p-6">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <RefreshCw className="w-8 h-8 text-indigo-500 animate-spin" />
          </div>
        ) : (
          <div className="space-y-6">
            {/* Schedule Info */}
            <div className="bg-zinc-900/50 rounded-xl p-4 border border-zinc-800">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-indigo-400" />
                  <span className="text-sm font-medium text-white">Schedule</span>
                </div>
                <Badge variant="outline" className="text-xs">
                  10 PM - 6 AM
                </Badge>
              </div>
              
              {config?.next_run && (
                <p className="text-xs text-zinc-500">
                  Next run: {new Date(config.next_run).toLocaleString()}
                </p>
              )}
              
              {config?.last_run && (
                <p className="text-xs text-zinc-500">
                  Last run: {new Date(config.last_run).toLocaleString()}
                </p>
              )}
            </div>

            {/* Task Selection */}
            <div>
              <h3 className="text-sm font-medium text-white mb-3">Scheduled Tasks</h3>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(availableTasks).map(([key, task]) => {
                  const TaskIcon = TASK_ICONS[key]?.icon || Zap;
                  const color = TASK_ICONS[key]?.color || '#6b7280';
                  const isSelected = selectedTasks.includes(key);
                  
                  return (
                    <button
                      key={key}
                      onClick={() => toggleTask(key)}
                      className={`p-4 rounded-xl border transition-all text-left ${
                        isSelected 
                          ? 'bg-indigo-500/10 border-indigo-500/50' 
                          : 'bg-zinc-900/50 border-zinc-800 hover:border-zinc-700'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div 
                          className="w-8 h-8 rounded-lg flex items-center justify-center"
                          style={{ backgroundColor: `${color}20` }}
                        >
                          <TaskIcon className="w-4 h-4" style={{ color }} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium text-white truncate">
                              {task.name}
                            </span>
                            {isSelected && (
                              <CheckCircle className="w-3 h-3 text-indigo-400 flex-shrink-0" />
                            )}
                          </div>
                          <p className="text-xs text-zinc-500 mt-1">{task.duration_estimate}</p>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <Button
                onClick={saveConfig}
                className="flex-1 bg-indigo-600 hover:bg-indigo-700"
              >
                <Settings className="w-4 h-4 mr-2" />
                Save Configuration
              </Button>
              <Button
                onClick={triggerNightShift}
                disabled={triggering || selectedTasks.length === 0}
                variant="outline"
                className="border-indigo-500/50 text-indigo-400 hover:bg-indigo-500/10"
              >
                {triggering ? (
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Play className="w-4 h-4 mr-2" />
                )}
                Run Now
              </Button>
            </div>

            {/* Recent Runs */}
            {runs.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-white mb-3">Recent Runs</h3>
                <div className="space-y-2">
                  {runs.slice(0, 5).map(run => (
                    <div 
                      key={run.id}
                      className="p-3 bg-zinc-900/50 rounded-lg border border-zinc-800"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {run.status === 'completed' ? (
                            <CheckCircle className="w-4 h-4 text-green-500" />
                          ) : run.status === 'running' ? (
                            <RefreshCw className="w-4 h-4 text-indigo-400 animate-spin" />
                          ) : (
                            <XCircle className="w-4 h-4 text-red-500" />
                          )}
                          <span className="text-sm text-white">
                            {run.triggered_by === 'manual' ? 'Manual Run' : 'Scheduled Run'}
                          </span>
                        </div>
                        <span className="text-xs text-zinc-500">
                          {new Date(run.started_at).toLocaleDateString()}
                        </span>
                      </div>
                      {run.summary && (
                        <p className="text-xs text-zinc-500 mt-2">
                          {run.summary.completed}/{run.summary.total} tasks completed
                        </p>
                      )}
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

export default NightShiftPanel;
