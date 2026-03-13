import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Dna, Zap, Shield, Code, Play, CheckCircle, XCircle, 
  RefreshCw, AlertTriangle, TrendingUp, Wrench
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { API } from '@/App';

const IMPACT_COLORS = {
  critical: { bg: 'bg-red-500/20', text: 'text-red-400', border: 'border-red-500/50' },
  high: { bg: 'bg-orange-500/20', text: 'text-orange-400', border: 'border-orange-500/50' },
  medium: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', border: 'border-yellow-500/50' },
  low: { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-green-500/50' }
};

const TYPE_ICONS = {
  performance: { icon: Zap, color: '#8b5cf6' },
  security: { icon: Shield, color: '#ef4444' },
  code_quality: { icon: Code, color: '#06b6d4' }
};

const EvolutionPanel = ({ projectId }) => {
  const [scans, setScans] = useState([]);
  const [currentScan, setCurrentScan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [selectedFindings, setSelectedFindings] = useState([]);
  const [applying, setApplying] = useState(false);

  useEffect(() => {
    fetchScans();
  }, [projectId]);

  const fetchScans = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/evolution/scans/${projectId}`);
      setScans(res.data || []);
      if (res.data?.length > 0) {
        setCurrentScan(res.data[0]);
      }
    } catch (e) {
      console.error('Failed to fetch evolution scans');
    }
    setLoading(false);
  };

  const startScan = async (scanType = 'full') => {
    setScanning(true);
    try {
      const res = await axios.post(`${API}/evolution/scan`, {
        project_id: projectId,
        scan_type: scanType
      });
      
      // Poll for completion
      const pollScan = async () => {
        const scanRes = await axios.get(`${API}/evolution/scan/${res.data.scan_id}`);
        if (scanRes.data.status === 'completed') {
          setCurrentScan(scanRes.data);
          fetchScans();
          setScanning(false);
        } else {
          setTimeout(pollScan, 1000);
        }
      };
      
      setTimeout(pollScan, 1000);
    } catch (e) {
      console.error('Failed to start scan');
      setScanning(false);
    }
  };

  const toggleFinding = (findingId) => {
    setSelectedFindings(prev => 
      prev.includes(findingId) 
        ? prev.filter(id => id !== findingId)
        : [...prev, findingId]
    );
  };

  const applyOptimizations = async () => {
    if (selectedFindings.length === 0) return;
    
    setApplying(true);
    try {
      await axios.post(`${API}/evolution/optimize`, {
        project_id: projectId,
        optimization_ids: selectedFindings
      });
      setSelectedFindings([]);
      fetchScans();
    } catch (e) {
      console.error('Failed to apply optimizations');
    }
    setApplying(false);
  };

  const findings = currentScan?.findings || [];
  const summary = currentScan?.summary || {};

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-emerald-950/20 to-black" data-testid="evolution-panel">
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 border-b border-zinc-800/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
              <Dna className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">SOFTWARE EVOLUTION</h2>
              <p className="text-xs text-zinc-500">Auto-optimize & evolve your project</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="ghost"
              onClick={fetchScans}
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
            <RefreshCw className="w-8 h-8 text-emerald-500 animate-spin" />
          </div>
        ) : (
          <div className="space-y-6">
            {/* Scan Actions */}
            <div className="grid grid-cols-3 gap-3">
              <Button
                onClick={() => startScan('full')}
                disabled={scanning}
                className="bg-emerald-600 hover:bg-emerald-700"
              >
                {scanning ? (
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Dna className="w-4 h-4 mr-2" />
                )}
                Full Scan
              </Button>
              <Button
                onClick={() => startScan('performance')}
                disabled={scanning}
                variant="outline"
                className="border-violet-500/50 text-violet-400 hover:bg-violet-500/10"
              >
                <Zap className="w-4 h-4 mr-2" />
                Performance
              </Button>
              <Button
                onClick={() => startScan('security')}
                disabled={scanning}
                variant="outline"
                className="border-red-500/50 text-red-400 hover:bg-red-500/10"
              >
                <Shield className="w-4 h-4 mr-2" />
                Security
              </Button>
            </div>

            {/* Summary */}
            {currentScan && (
              <div className="bg-zinc-900/50 rounded-xl p-4 border border-zinc-800">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-medium text-white">Latest Scan Results</h3>
                  <Badge className={currentScan.status === 'completed' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}>
                    {currentScan.status}
                  </Badge>
                </div>
                
                <div className="grid grid-cols-5 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-white">{summary.total_findings || 0}</p>
                    <p className="text-xs text-zinc-500">Total</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-red-400">{summary.critical || 0}</p>
                    <p className="text-xs text-zinc-500">Critical</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-orange-400">{summary.high || 0}</p>
                    <p className="text-xs text-zinc-500">High</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-yellow-400">{summary.medium || 0}</p>
                    <p className="text-xs text-zinc-500">Medium</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-green-400">{summary.auto_fixable || 0}</p>
                    <p className="text-xs text-zinc-500">Auto-fix</p>
                  </div>
                </div>
              </div>
            )}

            {/* Findings */}
            {findings.length > 0 && (
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-medium text-white">Findings</h3>
                  {selectedFindings.length > 0 && (
                    <Button
                      size="sm"
                      onClick={applyOptimizations}
                      disabled={applying}
                      className="bg-emerald-600 hover:bg-emerald-700"
                    >
                      {applying ? (
                        <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
                      ) : (
                        <Wrench className="w-3 h-3 mr-1" />
                      )}
                      Apply {selectedFindings.length} Fixes
                    </Button>
                  )}
                </div>
                
                <div className="space-y-3">
                  {findings.map(finding => {
                    const impactStyle = IMPACT_COLORS[finding.impact] || IMPACT_COLORS.low;
                    const typeConfig = TYPE_ICONS[finding.type] || TYPE_ICONS.code_quality;
                    const TypeIcon = typeConfig.icon;
                    const isSelected = selectedFindings.includes(finding.id);
                    
                    return (
                      <div 
                        key={finding.id}
                        onClick={() => finding.auto_fix && toggleFinding(finding.id)}
                        className={`p-4 rounded-xl border transition-all ${
                          finding.auto_fix ? 'cursor-pointer' : ''
                        } ${
                          isSelected 
                            ? 'bg-emerald-500/10 border-emerald-500/50' 
                            : 'bg-zinc-900/50 border-zinc-800 hover:border-zinc-700'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <div 
                            className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                            style={{ backgroundColor: `${typeConfig.color}20` }}
                          >
                            <TypeIcon className="w-4 h-4" style={{ color: typeConfig.color }} />
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-sm font-medium text-white">{finding.name}</span>
                              <Badge className={`text-[10px] ${impactStyle.bg} ${impactStyle.text}`}>
                                {finding.impact}
                              </Badge>
                              {finding.auto_fix && (
                                <Badge className="text-[10px] bg-emerald-500/20 text-emerald-400">
                                  Auto-fix
                                </Badge>
                              )}
                              {isSelected && (
                                <CheckCircle className="w-4 h-4 text-emerald-400" />
                              )}
                            </div>
                            
                            <p className="text-xs text-zinc-500 mb-2">{finding.description}</p>
                            
                            {finding.affected_files?.length > 0 && (
                              <div className="flex flex-wrap gap-1">
                                {finding.affected_files.slice(0, 3).map((file, i) => (
                                  <span key={i} className="text-[10px] px-2 py-0.5 bg-zinc-800 rounded text-zinc-400">
                                    {file.split('/').pop()}
                                  </span>
                                ))}
                                {finding.affected_files.length > 3 && (
                                  <span className="text-[10px] text-zinc-600">
                                    +{finding.affected_files.length - 3} more
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Empty State */}
            {!currentScan && (
              <div className="text-center py-12 bg-zinc-900/50 rounded-xl border border-zinc-800">
                <Dna className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-white">No Scans Yet</h3>
                <p className="text-sm text-zinc-500 mt-2">
                  Run your first evolution scan to discover optimization opportunities
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default EvolutionPanel;
