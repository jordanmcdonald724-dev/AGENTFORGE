import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  History, Clock, RotateCcw, Camera, ChevronRight, 
  CheckCircle, AlertCircle, RefreshCw, Trash2, Download, GitBranch
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { API } from '@/App';

const TimeTravelPanel = ({ projectId }) => {
  const [snapshots, setSnapshots] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [selectedSnapshot, setSelectedSnapshot] = useState(null);
  const [rollingBack, setRollingBack] = useState(false);

  useEffect(() => {
    fetchData();
  }, [projectId]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [snapshotsRes, timelineRes] = await Promise.all([
        axios.get(`${API}/time-travel/snapshots/${projectId}`),
        axios.get(`${API}/time-travel/history/${projectId}`)
      ]);
      setSnapshots(snapshotsRes.data || []);
      setTimeline(timelineRes.data?.timeline || []);
    } catch (e) {
      console.error('Failed to fetch time travel data');
    }
    setLoading(false);
  };

  const createSnapshot = async () => {
    setCreating(true);
    try {
      await axios.post(`${API}/time-travel/snapshot`, {
        project_id: projectId,
        name: `Snapshot ${new Date().toLocaleString()}`,
        description: 'Manual snapshot'
      });
      fetchData();
    } catch (e) {
      console.error('Failed to create snapshot');
    }
    setCreating(false);
  };

  const rollbackToSnapshot = async (snapshotId) => {
    if (!confirm('Are you sure? This will revert all files to this snapshot. A backup will be created first.')) {
      return;
    }
    
    setRollingBack(true);
    try {
      await axios.post(`${API}/time-travel/rollback`, {
        project_id: projectId,
        snapshot_id: snapshotId,
        confirm: true
      });
      fetchData();
    } catch (e) {
      console.error('Failed to rollback');
    }
    setRollingBack(false);
  };

  const deleteSnapshot = async (snapshotId) => {
    if (!confirm('Delete this snapshot?')) return;
    
    try {
      await axios.delete(`${API}/time-travel/snapshot/${snapshotId}`);
      fetchData();
    } catch (e) {
      console.error('Failed to delete snapshot');
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-amber-950/20 to-black" data-testid="time-travel-panel">
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 border-b border-zinc-800/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
              <History className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">TIME TRAVEL</h2>
              <p className="text-xs text-zinc-500">Project state history & rollback</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge className="bg-amber-500/20 text-amber-400 text-xs">
              {snapshots.length} Snapshots
            </Badge>
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
            <RefreshCw className="w-8 h-8 text-amber-500 animate-spin" />
          </div>
        ) : (
          <div className="space-y-6">
            {/* Create Snapshot */}
            <Button
              onClick={createSnapshot}
              disabled={creating}
              className="w-full bg-amber-600 hover:bg-amber-700"
            >
              {creating ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Camera className="w-4 h-4 mr-2" />
              )}
              Create Snapshot
            </Button>

            {/* Timeline */}
            {timeline.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-white mb-3">Timeline</h3>
                <div className="relative">
                  {/* Timeline line */}
                  <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-zinc-800" />
                  
                  <div className="space-y-4">
                    {timeline.slice(0, 10).map((item, i) => (
                      <div key={i} className="relative flex items-start gap-4 pl-10">
                        {/* Timeline dot */}
                        <div className={`absolute left-2.5 w-3 h-3 rounded-full ${
                          item.type === 'rollback' 
                            ? 'bg-red-500' 
                            : item.data?.auto 
                              ? 'bg-zinc-500' 
                              : 'bg-amber-500'
                        }`} />
                        
                        <div className="flex-1 bg-zinc-900/50 rounded-lg p-3 border border-zinc-800">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              {item.type === 'rollback' ? (
                                <RotateCcw className="w-4 h-4 text-red-400" />
                              ) : (
                                <Camera className="w-4 h-4 text-amber-400" />
                              )}
                              <span className="text-sm font-medium text-white">
                                {item.type === 'rollback' ? 'Rollback' : item.data?.name || 'Snapshot'}
                              </span>
                            </div>
                            <span className="text-xs text-zinc-500">
                              {formatDate(item.timestamp)}
                            </span>
                          </div>
                          
                          {item.data?.stats && (
                            <div className="flex gap-4 mt-2 text-xs text-zinc-500">
                              <span>{item.data.stats.file_count} files</span>
                              <span>{item.data.stats.task_count} tasks</span>
                              <span>{formatSize(item.data.stats.total_size_bytes)}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Snapshots List */}
            <div>
              <h3 className="text-sm font-medium text-white mb-3">All Snapshots</h3>
              
              {snapshots.length === 0 ? (
                <div className="text-center py-8 bg-zinc-900/50 rounded-xl border border-zinc-800">
                  <History className="w-12 h-12 text-zinc-700 mx-auto mb-3" />
                  <p className="text-zinc-500">No snapshots yet</p>
                  <p className="text-xs text-zinc-600 mt-1">Create your first snapshot to enable time travel</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {snapshots.map(snapshot => (
                    <div 
                      key={snapshot.id}
                      className={`p-4 rounded-xl border transition-all cursor-pointer ${
                        selectedSnapshot?.id === snapshot.id
                          ? 'bg-amber-500/10 border-amber-500/50'
                          : 'bg-zinc-900/50 border-zinc-800 hover:border-zinc-700'
                      }`}
                      onClick={() => setSelectedSnapshot(
                        selectedSnapshot?.id === snapshot.id ? null : snapshot
                      )}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                            snapshot.auto ? 'bg-zinc-800' : 'bg-amber-500/20'
                          }`}>
                            {snapshot.auto ? (
                              <Clock className="w-4 h-4 text-zinc-400" />
                            ) : (
                              <Camera className="w-4 h-4 text-amber-400" />
                            )}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-white">{snapshot.name}</p>
                            <p className="text-xs text-zinc-500">{formatDate(snapshot.created_at)}</p>
                          </div>
                        </div>
                        <ChevronRight className={`w-4 h-4 text-zinc-600 transition-transform ${
                          selectedSnapshot?.id === snapshot.id ? 'rotate-90' : ''
                        }`} />
                      </div>
                      
                      {snapshot.stats && (
                        <div className="flex gap-4 mt-3 text-xs text-zinc-500">
                          <span>{snapshot.stats.file_count} files</span>
                          <span>{snapshot.stats.task_count} tasks</span>
                          <span>{formatSize(snapshot.stats.total_size_bytes)}</span>
                        </div>
                      )}
                      
                      {selectedSnapshot?.id === snapshot.id && (
                        <div className="flex gap-2 mt-4 pt-4 border-t border-zinc-800">
                          <Button
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              rollbackToSnapshot(snapshot.id);
                            }}
                            disabled={rollingBack}
                            className="bg-amber-600 hover:bg-amber-700"
                          >
                            {rollingBack ? (
                              <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
                            ) : (
                              <RotateCcw className="w-3 h-3 mr-1" />
                            )}
                            Restore
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteSnapshot(snapshot.id);
                            }}
                            className="border-red-500/50 text-red-400 hover:bg-red-500/10"
                          >
                            <Trash2 className="w-3 h-3 mr-1" />
                            Delete
                          </Button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TimeTravelPanel;
