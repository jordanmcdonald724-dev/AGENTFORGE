import { useState, useRef, useCallback, useEffect } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { 
  Play, Zap, GitBranch, Variable, Calculator, CircleDot, 
  Plus, Trash2, Save, Code2, RefreshCw, Search, Loader2,
  ArrowRight, Circle
} from "lucide-react";

const NODE_COLORS = {
  event: "from-red-500/20 to-red-600/10 border-red-500/50",
  function: "from-blue-500/20 to-blue-600/10 border-blue-500/50",
  variable: "from-purple-500/20 to-purple-600/10 border-purple-500/50",
  flow: "from-zinc-500/20 to-zinc-600/10 border-zinc-500/50",
  math: "from-emerald-500/20 to-emerald-600/10 border-emerald-500/50",
  logic: "from-amber-500/20 to-amber-600/10 border-amber-500/50",
  custom: "from-cyan-500/20 to-cyan-600/10 border-cyan-500/50"
};

const PIN_COLORS = {
  exec: "bg-white",
  bool: "bg-red-400",
  int: "bg-cyan-400",
  float: "bg-emerald-400",
  string: "bg-pink-400",
  vector: "bg-amber-400",
  actor: "bg-blue-400",
  any: "bg-purple-400"
};

const BlueprintEditor = ({ blueprint, onUpdate, onGenerateCode, onSyncFromCode, templates = {} }) => {
  const canvasRef = useRef(null);
  const [nodes, setNodes] = useState(blueprint?.nodes || []);
  const [connections, setConnections] = useState(blueprint?.connections || []);
  const [selectedNode, setSelectedNode] = useState(null);
  const [draggingNode, setDraggingNode] = useState(null);
  const [connectingFrom, setConnectingFrom] = useState(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [scale, setScale] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [showNodePalette, setShowNodePalette] = useState(false);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    if (blueprint) {
      setNodes(blueprint.nodes || []);
      setConnections(blueprint.connections || []);
    }
  }, [blueprint]);

  const handleMouseMove = useCallback((e) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (rect) {
      setMousePos({
        x: (e.clientX - rect.left - offset.x) / scale,
        y: (e.clientY - rect.top - offset.y) / scale
      });
    }

    if (draggingNode) {
      setNodes(prev => prev.map(n => 
        n.id === draggingNode.id 
          ? { ...n, position: { x: mousePos.x - draggingNode.offsetX, y: mousePos.y - draggingNode.offsetY } }
          : n
      ));
    }
  }, [draggingNode, offset, scale, mousePos]);

  const handleMouseUp = useCallback(() => {
    if (draggingNode) {
      setDraggingNode(null);
      onUpdate?.({ nodes, connections });
    }
    setConnectingFrom(null);
  }, [draggingNode, nodes, connections, onUpdate]);

  const addNode = (template, position) => {
    const newNode = {
      id: `node_${Date.now()}`,
      ...template,
      position: position || { x: 200 + Math.random() * 100, y: 200 + Math.random() * 100 }
    };
    const updated = [...nodes, newNode];
    setNodes(updated);
    onUpdate?.({ nodes: updated, connections });
    setShowNodePalette(false);
  };

  const deleteNode = (nodeId) => {
    const updated = nodes.filter(n => n.id !== nodeId);
    const updatedConns = connections.filter(c => c.from_node !== nodeId && c.to_node !== nodeId);
    setNodes(updated);
    setConnections(updatedConns);
    onUpdate?.({ nodes: updated, connections: updatedConns });
    setSelectedNode(null);
  };

  const startConnection = (nodeId, outputName, outputType) => {
    setConnectingFrom({ nodeId, outputName, outputType });
  };

  const completeConnection = (nodeId, inputName, inputType) => {
    if (!connectingFrom) return;
    if (connectingFrom.nodeId === nodeId) return;
    
    // Type checking (exec can only connect to exec)
    if (connectingFrom.outputType === 'exec' && inputType !== 'exec') return;
    if (connectingFrom.outputType !== 'exec' && inputType === 'exec') return;

    const newConn = {
      from_node: connectingFrom.nodeId,
      from_output: connectingFrom.outputName,
      to_node: nodeId,
      to_input: inputName
    };

    // Remove existing connection to this input
    const updated = connections.filter(c => !(c.to_node === nodeId && c.to_input === inputName));
    updated.push(newConn);
    
    setConnections(updated);
    setConnectingFrom(null);
    onUpdate?.({ nodes, connections: updated });
  };

  const handleGenerateCode = async () => {
    setGenerating(true);
    try {
      await onGenerateCode?.();
    } finally {
      setGenerating(false);
    }
  };

  const getNodePosition = (nodeId) => {
    const node = nodes.find(n => n.id === nodeId);
    return node?.position || { x: 0, y: 0 };
  };

  const filteredTemplates = Object.entries(templates).filter(([key, template]) =>
    template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    template.type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const renderConnection = (conn, index) => {
    const fromPos = getNodePosition(conn.from_node);
    const toPos = getNodePosition(conn.to_node);
    const fromNode = nodes.find(n => n.id === conn.from_node);
    const toNode = nodes.find(n => n.id === conn.to_node);
    
    if (!fromNode || !toNode) return null;

    const fromOutput = fromNode.outputs?.find(o => o.name === conn.from_output);
    const outputIndex = fromNode.outputs?.findIndex(o => o.name === conn.from_output) || 0;
    const inputIndex = toNode.inputs?.findIndex(i => i.name === conn.to_input) || 0;

    const x1 = fromPos.x + 200;
    const y1 = fromPos.y + 40 + outputIndex * 24;
    const x2 = toPos.x;
    const y2 = toPos.y + 40 + inputIndex * 24;

    const midX = (x1 + x2) / 2;
    const color = fromOutput?.type === 'exec' ? '#fff' : PIN_COLORS[fromOutput?.type] || '#888';

    return (
      <path
        key={index}
        d={`M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`}
        stroke={color}
        strokeWidth={fromOutput?.type === 'exec' ? 3 : 2}
        fill="none"
        className="pointer-events-none"
      />
    );
  };

  const renderNode = (node) => {
    const colorClass = NODE_COLORS[node.type] || NODE_COLORS.custom;
    const isSelected = selectedNode === node.id;

    return (
      <motion.div
        key={node.id}
        className={`absolute rounded-lg border-2 bg-gradient-to-b ${colorClass} backdrop-blur-sm min-w-[180px] ${isSelected ? 'ring-2 ring-blue-400' : ''}`}
        style={{ left: node.position?.x || 0, top: node.position?.y || 0 }}
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        onMouseDown={(e) => {
          e.stopPropagation();
          setSelectedNode(node.id);
          setDraggingNode({
            id: node.id,
            offsetX: e.nativeEvent.offsetX,
            offsetY: e.nativeEvent.offsetY
          });
        }}
      >
        {/* Header */}
        <div className="px-3 py-2 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            {node.type === 'event' && <Zap className="w-3 h-3 text-red-400" />}
            {node.type === 'function' && <Play className="w-3 h-3 text-blue-400" />}
            {node.type === 'variable' && <Variable className="w-3 h-3 text-purple-400" />}
            {node.type === 'flow' && <GitBranch className="w-3 h-3 text-zinc-400" />}
            {node.type === 'math' && <Calculator className="w-3 h-3 text-emerald-400" />}
            <span className="text-xs font-medium text-white truncate max-w-[120px]">{node.name}</span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-5 w-5 opacity-0 group-hover:opacity-100 hover:bg-red-500/20"
            onClick={(e) => { e.stopPropagation(); deleteNode(node.id); }}
          >
            <Trash2 className="w-3 h-3 text-red-400" />
          </Button>
        </div>

        {/* Pins */}
        <div className="p-2 flex justify-between gap-4">
          {/* Inputs */}
          <div className="flex flex-col gap-1">
            {node.inputs?.map((input, i) => (
              <div
                key={i}
                className="flex items-center gap-2 cursor-pointer hover:bg-white/5 rounded px-1"
                onClick={() => completeConnection(node.id, input.name, input.type)}
              >
                <div className={`w-3 h-3 rounded-full border-2 border-zinc-600 ${connectingFrom && connectingFrom.outputType === input.type ? PIN_COLORS[input.type] : 'bg-zinc-800'}`}>
                  {input.type === 'exec' && <ArrowRight className="w-2 h-2 text-white" />}
                </div>
                <span className="text-[10px] text-zinc-400">{input.name}</span>
              </div>
            ))}
          </div>

          {/* Outputs */}
          <div className="flex flex-col gap-1 items-end">
            {node.outputs?.map((output, i) => (
              <div
                key={i}
                className="flex items-center gap-2 cursor-pointer hover:bg-white/5 rounded px-1"
                onClick={() => startConnection(node.id, output.name, output.type)}
              >
                <span className="text-[10px] text-zinc-400">{output.name}</span>
                <div className={`w-3 h-3 rounded-full ${PIN_COLORS[output.type] || 'bg-zinc-500'} ${connectingFrom?.nodeId === node.id && connectingFrom?.outputName === output.name ? 'ring-2 ring-white' : ''}`}>
                  {output.type === 'exec' && <ArrowRight className="w-2 h-2 text-zinc-800" />}
                </div>
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    );
  };

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]">
      {/* Toolbar */}
      <div className="flex-shrink-0 px-4 py-2 border-b border-zinc-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="border-blue-500 text-blue-400">
            <Code2 className="w-3 h-3 mr-1" />
            {blueprint?.name || 'Blueprint'}
          </Badge>
          <Badge variant="outline" className="border-zinc-700 text-zinc-400">
            {nodes.length} nodes
          </Badge>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            className="border-zinc-700"
            onClick={() => setShowNodePalette(!showNodePalette)}
          >
            <Plus className="w-4 h-4 mr-1" />Add Node
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="border-zinc-700"
            onClick={onSyncFromCode}
          >
            <RefreshCw className="w-4 h-4 mr-1" />Sync from Code
          </Button>
          <Button
            size="sm"
            className="bg-emerald-500 hover:bg-emerald-600"
            onClick={handleGenerateCode}
            disabled={generating}
          >
            {generating ? <Loader2 className="w-4 h-4 mr-1 animate-spin" /> : <Code2 className="w-4 h-4 mr-1" />}
            Generate Code
          </Button>
        </div>
      </div>

      <div className="flex-1 flex">
        {/* Node Palette */}
        {showNodePalette && (
          <div className="w-64 border-r border-zinc-800 bg-zinc-900/50">
            <div className="p-2 border-b border-zinc-800">
              <div className="relative">
                <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                <Input
                  placeholder="Search nodes..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-8 bg-zinc-800 border-zinc-700 h-8 text-sm"
                />
              </div>
            </div>
            <ScrollArea className="h-[calc(100%-52px)]">
              <div className="p-2 space-y-1">
                {filteredTemplates.map(([key, template]) => (
                  <button
                    key={key}
                    className={`w-full p-2 rounded text-left hover:bg-zinc-800 transition-colors`}
                    onClick={() => addNode(template, { x: 300, y: 200 })}
                  >
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${template.type === 'event' ? 'bg-red-400' : template.type === 'function' ? 'bg-blue-400' : template.type === 'math' ? 'bg-emerald-400' : 'bg-zinc-400'}`} />
                      <span className="text-xs text-white">{template.name}</span>
                    </div>
                    <span className="text-[10px] text-zinc-500 ml-4">{template.type}</span>
                  </button>
                ))}
              </div>
            </ScrollArea>
          </div>
        )}

        {/* Canvas */}
        <div
          ref={canvasRef}
          className="flex-1 relative overflow-hidden cursor-crosshair"
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          style={{ backgroundImage: 'radial-gradient(circle, #333 1px, transparent 1px)', backgroundSize: '20px 20px' }}
        >
          {/* Connections SVG */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ transform: `translate(${offset.x}px, ${offset.y}px) scale(${scale})` }}>
            {connections.map((conn, i) => renderConnection(conn, i))}
            {/* Drawing connection line */}
            {connectingFrom && (
              <line
                x1={getNodePosition(connectingFrom.nodeId).x + 200}
                y1={getNodePosition(connectingFrom.nodeId).y + 50}
                x2={mousePos.x}
                y2={mousePos.y}
                stroke="#888"
                strokeWidth={2}
                strokeDasharray="5,5"
              />
            )}
          </svg>

          {/* Nodes */}
          <div className="absolute inset-0" style={{ transform: `translate(${offset.x}px, ${offset.y}px) scale(${scale})` }}>
            {nodes.map(node => renderNode(node))}
          </div>

          {/* Empty state */}
          {nodes.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <CircleDot className="w-16 h-16 mx-auto mb-4 text-zinc-700" />
                <h3 className="text-lg font-rajdhani text-zinc-500 mb-2">Empty Blueprint</h3>
                <p className="text-sm text-zinc-600 mb-4">Add nodes from the palette to start</p>
                <Button variant="outline" className="border-zinc-700" onClick={() => setShowNodePalette(true)}>
                  <Plus className="w-4 h-4 mr-2" />Add First Node
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BlueprintEditor;
