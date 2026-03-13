import React, { useState } from 'react';
import { Network, Database, Globe, Shield, CreditCard, FileCode } from 'lucide-react';

const VisualProjectBrain = ({ projectId, files = [] }) => {
  const [selectedNode, setSelectedNode] = useState(null);

  const nodes = [
    { id: 'frontend', label: 'Frontend', type: 'frontend', color: '#8b5cf6', icon: Globe },
    { id: 'api', label: 'API Layer', type: 'api', color: '#06b6d4', icon: Network },
    { id: 'backend', label: 'Backend', type: 'backend', color: '#f59e0b', icon: FileCode },
    { id: 'database', label: 'Database', type: 'database', color: '#22c55e', icon: Database },
    { id: 'auth', label: 'Auth', type: 'service', color: '#ef4444', icon: Shield },
    { id: 'payments', label: 'Payments', type: 'service', color: '#ec4899', icon: CreditCard },
  ];

  return (
    <div className="h-full w-full bg-black/95 p-6 overflow-auto" data-testid="project-brain">
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-white mb-2">Visual Project Brain</h2>
        <p className="text-sm text-zinc-500">System architecture visualization</p>
      </div>

      {/* Architecture Grid */}
      <div className="max-w-4xl mx-auto">
        {/* Top Layer - Frontend */}
        <div className="flex justify-center mb-4">
          <NodeCard 
            node={nodes[0]} 
            selected={selectedNode === 'frontend'}
            onClick={() => setSelectedNode('frontend')}
          />
        </div>
        
        {/* Connection line */}
        <div className="flex justify-center">
          <div className="w-0.5 h-8 bg-gradient-to-b from-violet-500 to-cyan-500" />
        </div>

        {/* Middle Layer - API */}
        <div className="flex justify-center mb-4">
          <NodeCard 
            node={nodes[1]} 
            selected={selectedNode === 'api'}
            onClick={() => setSelectedNode('api')}
          />
        </div>

        {/* Connection lines to services */}
        <div className="flex justify-center items-center gap-8 mb-4">
          <div className="flex flex-col items-center">
            <div className="w-0.5 h-8 bg-red-500/50 transform -rotate-45 origin-top" />
            <NodeCard 
              node={nodes[4]} 
              selected={selectedNode === 'auth'}
              onClick={() => setSelectedNode('auth')}
              small
            />
          </div>
          
          <div className="flex flex-col items-center">
            <div className="w-0.5 h-8 bg-cyan-500/50" />
            <NodeCard 
              node={nodes[2]} 
              selected={selectedNode === 'backend'}
              onClick={() => setSelectedNode('backend')}
            />
          </div>
          
          <div className="flex flex-col items-center">
            <div className="w-0.5 h-8 bg-pink-500/50 transform rotate-45 origin-top" />
            <NodeCard 
              node={nodes[5]} 
              selected={selectedNode === 'payments'}
              onClick={() => setSelectedNode('payments')}
              small
            />
          </div>
        </div>

        {/* Connection line */}
        <div className="flex justify-center">
          <div className="w-0.5 h-8 bg-gradient-to-b from-amber-500 to-green-500" />
        </div>

        {/* Bottom Layer - Database */}
        <div className="flex justify-center">
          <NodeCard 
            node={nodes[3]} 
            selected={selectedNode === 'database'}
            onClick={() => setSelectedNode('database')}
          />
        </div>
      </div>

      {/* File Stats */}
      <div className="mt-12 max-w-4xl mx-auto">
        <h3 className="text-sm font-medium text-zinc-400 mb-4">Project Files</h3>
        <div className="grid grid-cols-4 gap-3">
          {Object.entries(
            files.reduce((acc, f) => {
              const ext = f.name?.split('.').pop() || 'other';
              acc[ext] = (acc[ext] || 0) + 1;
              return acc;
            }, {})
          ).slice(0, 8).map(([ext, count]) => (
            <div key={ext} className="p-3 bg-zinc-900/50 rounded-lg border border-zinc-800">
              <div className="text-lg font-bold text-white">{count}</div>
              <div className="text-xs text-zinc-500">.{ext} files</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const NodeCard = ({ node, selected, onClick, small }) => {
  const Icon = node.icon;
  return (
    <div
      onClick={onClick}
      className={`
        ${small ? 'p-3' : 'p-4'} rounded-xl cursor-pointer transition-all
        bg-zinc-900/80 border
        ${selected ? 'border-white ring-2 ring-white/20' : 'border-zinc-800 hover:border-zinc-700'}
      `}
      style={{ 
        boxShadow: selected ? `0 0 30px ${node.color}40` : 'none'
      }}
    >
      <div className="flex items-center gap-3">
        <div 
          className={`${small ? 'w-8 h-8' : 'w-10 h-10'} rounded-lg flex items-center justify-center`}
          style={{ backgroundColor: `${node.color}20` }}
        >
          <Icon className={`${small ? 'w-4 h-4' : 'w-5 h-5'}`} style={{ color: node.color }} />
        </div>
        <div>
          <div className={`font-bold text-white ${small ? 'text-xs' : 'text-sm'}`}>{node.label}</div>
          <div className={`text-zinc-500 ${small ? 'text-[10px]' : 'text-xs'}`}>{node.type}</div>
        </div>
      </div>
    </div>
  );
};

export default VisualProjectBrain;

export default VisualProjectBrain;
