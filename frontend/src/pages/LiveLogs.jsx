import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Trash2, Download, Pause, Play } from 'lucide-react';
import { Button } from '@/components/ui/button';

const LiveLogs = () => {
  const [logs, setLogs] = useState([]);
  const [isPaused, setIsPaused] = useState(false);
  const [filter, setFilter] = useState('all');
  const logsEndRef = useRef(null);
  const channelRef = useRef(null);

  useEffect(() => {
    // Create broadcast channel to receive logs from other tabs
    channelRef.current = new BroadcastChannel('agentforge-logs');
    
    channelRef.current.onmessage = (event) => {
      if (!isPaused) {
        const log = {
          ...event.data,
          id: Date.now() + Math.random(),
          timestamp: new Date().toLocaleTimeString()
        };
        setLogs(prev => [...prev.slice(-500), log]); // Keep last 500 logs
      }
    };

    // Also listen for bridge events on this page
    const handleBridgeStatus = (e) => {
      addLog('bridge', e.detail.connected ? 'CONNECTED' : 'DISCONNECTED', e.detail.connected ? 'success' : 'error');
    };
    
    const handleFileSaved = (e) => {
      addLog('file', `Saved: ${e.detail.filepath}`, 'success');
    };
    
    const handleBuildStatus = (e) => {
      const { status, data } = e.detail;
      addLog('build', `${status}: ${JSON.stringify(data)}`, status === 'error' ? 'error' : 'info');
    };

    window.addEventListener('agentforge-bridge-status', handleBridgeStatus);
    window.addEventListener('agentforge-file-saved', handleFileSaved);
    window.addEventListener('agentforge-build-status', handleBuildStatus);

    // Add initial log
    addLog('system', 'Live Logs started - watching for events...', 'info');

    return () => {
      channelRef.current?.close();
      window.removeEventListener('agentforge-bridge-status', handleBridgeStatus);
      window.removeEventListener('agentforge-file-saved', handleFileSaved);
      window.removeEventListener('agentforge-build-status', handleBuildStatus);
    };
  }, [isPaused]);

  useEffect(() => {
    if (!isPaused) {
      logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, isPaused]);

  const addLog = (type, message, level = 'info') => {
    const log = {
      id: Date.now() + Math.random(),
      timestamp: new Date().toLocaleTimeString(),
      type,
      message,
      level
    };
    setLogs(prev => [...prev.slice(-500), log]);
    
    // Broadcast to other tabs
    channelRef.current?.postMessage(log);
  };

  const clearLogs = () => setLogs([]);

  const downloadLogs = () => {
    const content = logs.map(l => `[${l.timestamp}] [${l.type}] ${l.message}`).join('\n');
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `agentforge-logs-${new Date().toISOString().slice(0,10)}.txt`;
    a.click();
  };

  const getLogColor = (level) => {
    switch (level) {
      case 'success': return 'text-green-400';
      case 'error': return 'text-red-400';
      case 'warning': return 'text-yellow-400';
      default: return 'text-zinc-300';
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'bridge': return 'text-purple-400';
      case 'file': return 'text-blue-400';
      case 'build': return 'text-orange-400';
      case 'push': return 'text-cyan-400';
      case 'phase': return 'text-yellow-400';
      default: return 'text-zinc-500';
    }
  };

  const filteredLogs = filter === 'all' 
    ? logs 
    : logs.filter(l => l.type === filter);

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white font-mono">
      {/* Header */}
      <header className="border-b border-zinc-800 bg-zinc-900/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Terminal className="w-6 h-6 text-green-400" />
            <h1 className="font-bold text-lg">AgentForge Live Logs</h1>
            <span className="text-xs text-zinc-500">({logs.length} entries)</span>
          </div>
          
          <div className="flex items-center gap-2">
            {/* Filter */}
            <select 
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="bg-zinc-800 border border-zinc-700 rounded px-2 py-1 text-sm"
            >
              <option value="all">All</option>
              <option value="bridge">Bridge</option>
              <option value="file">Files</option>
              <option value="build">Build</option>
              <option value="push">Push</option>
              <option value="phase">Phase</option>
            </select>

            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => setIsPaused(!isPaused)}
              className={isPaused ? 'border-yellow-500 text-yellow-400' : 'border-zinc-700'}
            >
              {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
            </Button>
            
            <Button variant="outline" size="sm" onClick={downloadLogs} className="border-zinc-700">
              <Download className="w-4 h-4" />
            </Button>
            
            <Button variant="outline" size="sm" onClick={clearLogs} className="border-zinc-700">
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </header>

      {/* Logs */}
      <div className="p-4 space-y-1">
        {filteredLogs.length === 0 ? (
          <div className="text-center text-zinc-600 py-20">
            <Terminal className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Waiting for events...</p>
            <p className="text-sm mt-2">Open God Mode in another tab and start a build</p>
          </div>
        ) : (
          filteredLogs.map((log) => (
            <div key={log.id} className="flex gap-3 text-sm hover:bg-zinc-900/50 px-2 py-0.5 rounded">
              <span className="text-zinc-600 w-24 flex-shrink-0">{log.timestamp}</span>
              <span className={`w-16 flex-shrink-0 ${getTypeColor(log.type)}`}>[{log.type}]</span>
              <span className={getLogColor(log.level)}>{log.message}</span>
            </div>
          ))
        )}
        <div ref={logsEndRef} />
      </div>

      {/* Status bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-zinc-900 border-t border-zinc-800 px-4 py-2 text-xs text-zinc-500 flex justify-between">
        <span>Press F5 in God Mode tab to see events here</span>
        <span>{isPaused ? '⏸ PAUSED' : '● LIVE'}</span>
      </div>
    </div>
  );
};

export default LiveLogs;
