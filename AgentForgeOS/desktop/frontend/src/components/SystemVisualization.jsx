import { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Box, Cpu, Database, Globe, FileCode, Folder, RefreshCw,
  ZoomIn, ZoomOut, Maximize2, Move
} from "lucide-react";
import { API } from "@/App";

const NODE_COLORS = {
  jsx: "#61dafb",
  js: "#f7df1e",
  ts: "#3178c6",
  tsx: "#61dafb",
  py: "#3776ab",
  css: "#264de4",
  html: "#e34c26",
  json: "#000000",
  md: "#083fa1",
  default: "#6b7280"
};

const NODE_ICONS = {
  jsx: Globe,
  js: FileCode,
  ts: FileCode,
  tsx: Globe,
  py: Cpu,
  css: FileCode,
  html: Globe,
  json: Database,
  md: FileCode,
  default: Folder
};

const SystemVisualization = ({ projectId }) => {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const canvasRef = useRef(null);

  useEffect(() => {
    fetchVisualization();
  }, [projectId]);

  const fetchVisualization = async () => {
    setLoading(true);
    try {
      // Get files and build a visualization
      const filesRes = await axios.get(`${API}/files?project_id=${projectId}`);
      const files = filesRes.data || [];
      
      // Create nodes from files
      const fileNodes = files.map((file, index) => {
        const ext = file.filepath?.split('.').pop() || 'default';
        const angle = (index / files.length) * 2 * Math.PI;
        const radius = 150 + Math.random() * 100;
        
        return {
          id: file.id,
          name: file.filename || file.filepath?.split('/').pop() || 'Unknown',
          filepath: file.filepath,
          type: ext,
          x: 300 + Math.cos(angle) * radius,
          y: 250 + Math.sin(angle) * radius,
          size: Math.min(50, 20 + (file.content?.length || 0) / 500),
          lines: file.content?.split('\n').length || 0
        };
      });
      
      // Create edges based on imports (simplified)
      const fileEdges = [];
      files.forEach((file, i) => {
        const content = file.content || '';
        files.forEach((otherFile, j) => {
          if (i !== j) {
            const otherName = otherFile.filename?.replace(/\.[^/.]+$/, '') || '';
            if (content.includes(`import`) && content.includes(otherName)) {
              fileEdges.push({
                from: file.id,
                to: otherFile.id
              });
            }
          }
        });
      });
      
      setNodes(fileNodes);
      setEdges(fileEdges);
    } catch (error) {
      toast.error("Failed to load visualization");
    } finally {
      setLoading(false);
    }
  };

  const handleMouseDown = useCallback((e) => {
    if (e.target === canvasRef.current) {
      setIsDragging(true);
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  }, [pan]);

  const handleMouseMove = useCallback((e) => {
    if (isDragging) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  }, [isDragging, dragStart]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleZoom = (delta) => {
    setZoom(prev => Math.max(0.3, Math.min(2, prev + delta)));
  };

  const resetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
    setSelectedNode(null);
  };

  const getNodePosition = (node) => ({
    x: node.x * zoom + pan.x,
    y: node.y * zoom + pan.y
  });

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]" data-testid="system-visualization">
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Box className="w-4 h-4 text-cyan-400" />
            <span className="font-rajdhani font-bold text-white">System Visualization</span>
            <Badge variant="outline" className="text-[10px] border-cyan-500/30 text-cyan-400">
              {nodes.length} files
            </Badge>
          </div>
          <div className="flex items-center gap-1">
            <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => handleZoom(0.1)}>
              <ZoomIn className="w-3 h-3" />
            </Button>
            <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => handleZoom(-0.1)}>
              <ZoomOut className="w-3 h-3" />
            </Button>
            <Button size="icon" variant="ghost" className="h-7 w-7" onClick={resetView}>
              <Maximize2 className="w-3 h-3" />
            </Button>
            <Button size="icon" variant="ghost" className="h-7 w-7" onClick={fetchVisualization}>
              <RefreshCw className="w-3 h-3" />
            </Button>
          </div>
        </div>
      </div>

      <div className="flex-1 flex">
        {/* Canvas Area */}
        <div 
          ref={canvasRef}
          className="flex-1 relative overflow-hidden bg-[#050507] cursor-move"
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          {loading ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
            </div>
          ) : (
            <>
              {/* Grid Background */}
              <svg className="absolute inset-0 w-full h-full pointer-events-none">
                <defs>
                  <pattern id="grid" width={20 * zoom} height={20 * zoom} patternUnits="userSpaceOnUse">
                    <path d={`M ${20 * zoom} 0 L 0 0 0 ${20 * zoom}`} fill="none" stroke="#1a1a1f" strokeWidth="0.5"/>
                  </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#grid)" />
              </svg>

              {/* Edges */}
              <svg className="absolute inset-0 w-full h-full pointer-events-none">
                {edges.map((edge, i) => {
                  const fromNode = nodes.find(n => n.id === edge.from);
                  const toNode = nodes.find(n => n.id === edge.to);
                  if (!fromNode || !toNode) return null;
                  
                  const from = getNodePosition(fromNode);
                  const to = getNodePosition(toNode);
                  
                  return (
                    <line
                      key={i}
                      x1={from.x}
                      y1={from.y}
                      x2={to.x}
                      y2={to.y}
                      stroke="#374151"
                      strokeWidth={1}
                      strokeOpacity={0.5}
                    />
                  );
                })}
              </svg>

              {/* Nodes */}
              {nodes.map((node) => {
                const pos = getNodePosition(node);
                const Icon = NODE_ICONS[node.type] || NODE_ICONS.default;
                const color = NODE_COLORS[node.type] || NODE_COLORS.default;
                const isSelected = selectedNode?.id === node.id;
                
                return (
                  <div
                    key={node.id}
                    className={`absolute transition-transform duration-100 cursor-pointer group ${
                      isSelected ? 'z-20' : 'z-10'
                    }`}
                    style={{
                      left: pos.x - (node.size * zoom) / 2,
                      top: pos.y - (node.size * zoom) / 2,
                      width: node.size * zoom,
                      height: node.size * zoom,
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedNode(isSelected ? null : node);
                    }}
                  >
                    <div
                      className={`w-full h-full rounded-lg flex items-center justify-center transition-all ${
                        isSelected 
                          ? 'ring-2 ring-offset-2 ring-offset-[#050507]' 
                          : 'hover:scale-110'
                      }`}
                      style={{
                        backgroundColor: `${color}20`,
                        borderColor: color,
                        borderWidth: 2,
                        ringColor: color
                      }}
                    >
                      <Icon className="w-1/2 h-1/2" style={{ color }} />
                    </div>
                    
                    {/* Tooltip */}
                    <div className={`absolute left-full ml-2 top-1/2 -translate-y-1/2 
                      bg-zinc-900 border border-zinc-700 rounded px-2 py-1 whitespace-nowrap
                      opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-30`}
                    >
                      <span className="text-xs text-white">{node.name}</span>
                      <span className="text-[10px] text-zinc-500 ml-2">{node.lines} lines</span>
                    </div>
                  </div>
                );
              })}
            </>
          )}
        </div>

        {/* Info Panel */}
        {selectedNode && (
          <div className="w-64 border-l border-zinc-800 bg-zinc-900/50 p-4">
            <h4 className="font-medium text-white mb-3">{selectedNode.name}</h4>
            <div className="space-y-3 text-sm">
              <div>
                <span className="text-zinc-500">Path:</span>
                <p className="text-zinc-300 text-xs truncate">{selectedNode.filepath}</p>
              </div>
              <div>
                <span className="text-zinc-500">Type:</span>
                <Badge 
                  className="ml-2 text-[10px]"
                  style={{ 
                    backgroundColor: `${NODE_COLORS[selectedNode.type] || NODE_COLORS.default}20`,
                    color: NODE_COLORS[selectedNode.type] || NODE_COLORS.default
                  }}
                >
                  {selectedNode.type.toUpperCase()}
                </Badge>
              </div>
              <div>
                <span className="text-zinc-500">Lines:</span>
                <span className="text-zinc-300 ml-2">{selectedNode.lines}</span>
              </div>
              <div>
                <span className="text-zinc-500">Dependencies:</span>
                <span className="text-zinc-300 ml-2">
                  {edges.filter(e => e.from === selectedNode.id).length}
                </span>
              </div>
              <div>
                <span className="text-zinc-500">Dependents:</span>
                <span className="text-zinc-300 ml-2">
                  {edges.filter(e => e.to === selectedNode.id).length}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="flex-shrink-0 px-4 py-2 border-t border-zinc-800 bg-zinc-900/30">
        <div className="flex items-center gap-4 text-[10px]">
          <span className="text-zinc-500">File Types:</span>
          {Object.entries(NODE_COLORS).slice(0, 6).map(([type, color]) => (
            <div key={type} className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
              <span className="text-zinc-400">{type.toUpperCase()}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SystemVisualization;
