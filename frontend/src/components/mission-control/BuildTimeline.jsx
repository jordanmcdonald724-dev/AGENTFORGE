import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Clock, CheckCircle2, XCircle, Loader2, Play, Pause, 
  RotateCcw, ChevronRight, Zap, FileCode, TestTube, Rocket
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { API } from '@/App';

const BuildTimeline = ({ projectId }) => {
  const [builds, setBuilds] = useState([]);
  const [selectedBuild, setSelectedBuild] = useState(null);
  const [timelineView, setTimelineView] = useState('list'); // list | timeline

  useEffect(() => {
    fetchBuilds();
  }, [projectId]);

  const fetchBuilds = async () => {
    if (!projectId) return;
    try {
      const res = await axios.get(`${API}/builds/${projectId}`);
      setBuilds(res.data || []);
    } catch (e) {}
  };

  const BUILD_PHASES = [
    { id: 'architecture', icon: Zap, label: 'Architecture', color: '#8b5cf6' },
    { id: 'code_generation', icon: FileCode, label: 'Code Generation', color: '#06b6d4' },
    { id: 'asset_generation', icon: Rocket, label: 'Asset Generation', color: '#f59e0b' },
    { id: 'testing', icon: TestTube, label: 'Testing', color: '#22c55e' },
    { id: 'deployment', icon: Rocket, label: 'Deployment', color: '#ec4899' }
  ];

  const StatusIcon = ({ status }) => {
    switch (status) {
      case 'complete': return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case 'running': return <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />;
      case 'error': return <XCircle className="w-4 h-4 text-red-500" />;
      default: return <Clock className="w-4 h-4 text-zinc-600" />;
    }
  };

  return (
    <div className="h-full flex flex-col bg-black/90 backdrop-blur-xl" data-testid="build-timeline">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800/50">
        <div className="flex items-center gap-3">
          <Clock className="w-5 h-5 text-cyan-400" />
          <h2 className="text-lg font-bold text-white">Build Timeline</h2>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={timelineView === 'list' ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => setTimelineView('list')}
          >
            List
          </Button>
          <Button
            variant={timelineView === 'timeline' ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => setTimelineView('timeline')}
          >
            Timeline
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-6">
        {timelineView === 'timeline' ? (
          /* Timeline View */
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-zinc-800" />
            
            {BUILD_PHASES.map((phase, index) => (
              <div key={phase.id} className="relative flex items-start mb-8 ml-4">
                {/* Node */}
                <div 
                  className="absolute left-4 w-8 h-8 rounded-full flex items-center justify-center border-2 bg-black z-10"
                  style={{ borderColor: phase.color }}
                >
                  <phase.icon className="w-4 h-4" style={{ color: phase.color }} />
                </div>
                
                {/* Content */}
                <div className="ml-16 flex-1">
                  <div className="p-4 bg-zinc-900/50 rounded-xl border border-zinc-800">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-bold text-white">{phase.label}</h4>
                      <Badge className="bg-green-500/20 text-green-400">Complete</Badge>
                    </div>
                    <p className="text-sm text-zinc-500">
                      Phase completed successfully
                    </p>
                    <div className="flex items-center gap-2 mt-3 text-xs text-zinc-600">
                      <Clock className="w-3 h-3" />
                      <span>2.5s</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* List View */
          <div className="space-y-4">
            {builds.length > 0 ? builds.map((build) => (
              <div
                key={build.id}
                onClick={() => setSelectedBuild(build)}
                className={`p-4 bg-zinc-900/50 rounded-xl border cursor-pointer transition-all ${
                  selectedBuild?.id === build.id 
                    ? 'border-cyan-500 ring-2 ring-cyan-500/20' 
                    : 'border-zinc-800 hover:border-zinc-700'
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                      build.status === 'complete' ? 'bg-green-500/20' :
                      build.status === 'running' ? 'bg-cyan-500/20' :
                      'bg-zinc-800'
                    }`}>
                      {build.status === 'complete' ? (
                        <CheckCircle2 className="w-5 h-5 text-green-500" />
                      ) : build.status === 'running' ? (
                        <Loader2 className="w-5 h-5 text-cyan-400 animate-spin" />
                      ) : (
                        <Clock className="w-5 h-5 text-zinc-500" />
                      )}
                    </div>
                    <div>
                      <div className="font-bold text-white">Build #{build.id?.slice(-6)}</div>
                      <div className="text-xs text-zinc-500">
                        {build.created_at ? new Date(build.created_at).toLocaleString() : 'Unknown'}
                      </div>
                    </div>
                  </div>
                  <ChevronRight className="w-5 h-5 text-zinc-600" />
                </div>

                {/* Progress */}
                <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full transition-all ${
                      build.status === 'complete' ? 'bg-green-500' :
                      build.status === 'error' ? 'bg-red-500' :
                      'bg-cyan-500'
                    }`}
                    style={{ width: `${build.progress || 0}%` }}
                  />
                </div>

                {/* Phase indicators */}
                <div className="flex items-center gap-2 mt-3">
                  {BUILD_PHASES.map(phase => (
                    <div 
                      key={phase.id}
                      className="flex items-center gap-1 text-xs text-zinc-500"
                    >
                      <StatusIcon status="complete" />
                      <span>{phase.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            )) : (
              <div className="text-center py-12">
                <Clock className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-zinc-400">No builds yet</h3>
                <p className="text-sm text-zinc-600 mt-1">Start a build to see the timeline</p>
              </div>
            )}
          </div>
        )}

        {/* Rewind Feature */}
        {selectedBuild && (
          <div className="mt-6 p-4 bg-zinc-900/50 rounded-xl border border-zinc-800">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-bold text-white">Time Machine</div>
                <p className="text-sm text-zinc-500">Rewind to a previous build state</p>
              </div>
              <Button className="bg-violet-600 hover:bg-violet-700">
                <RotateCcw className="w-4 h-4 mr-2" />
                Restore Build
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BuildTimeline;
