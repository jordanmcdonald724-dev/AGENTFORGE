import { useState, useEffect, useRef, useMemo, useCallback, Component } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { 
  OrbitControls, Html, Environment,
  Float, Sparkles
} from "@react-three/drei";
import * as THREE from "three";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Box, RefreshCw, Eye, EyeOff, Folder, AlertCircle
} from "lucide-react";
import { API } from "@/App";

// Error Boundary for Canvas
class CanvasErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("3D Canvas error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="absolute inset-0 flex items-center justify-center bg-[#050507]">
          <div className="text-center p-4">
            <AlertCircle className="w-12 h-12 text-amber-500 mx-auto mb-2" />
            <p className="text-zinc-400 mb-2">3D Visualization unavailable</p>
            <p className="text-zinc-500 text-xs">WebGL context error - try refreshing</p>
            <Button 
              size="sm" 
              variant="outline" 
              className="mt-3"
              onClick={() => this.setState({ hasError: false, error: null })}
            >
              Retry
            </Button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

// File type colors
const FILE_COLORS = {
  jsx: "#61dafb",
  js: "#f7df1e", 
  ts: "#3178c6",
  tsx: "#61dafb",
  py: "#3776ab",
  css: "#264de4",
  html: "#e34c26",
  json: "#292929",
  md: "#083fa1",
  default: "#6b7280"
};

// 3D Node component for each file
function FileNode({ node, position, isSelected, onClick, showLabels }) {
  const meshRef = useRef();
  const [hovered, setHovered] = useState(false);
  
  const color = FILE_COLORS[node.type] || FILE_COLORS.default;
  const scale = Math.max(0.3, Math.min(1.2, 0.3 + (node.lines / 500)));
  
  useFrame((state) => {
    if (meshRef.current) {
      // Gentle floating animation
      meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime + position[0]) * 0.1;
      
      // Pulse when selected
      if (isSelected) {
        meshRef.current.scale.setScalar(scale * (1 + Math.sin(state.clock.elapsedTime * 3) * 0.1));
      }
    }
  });

  return (
    <group position={position}>
      <Float speed={2} rotationIntensity={0.2} floatIntensity={0.3}>
        <mesh
          ref={meshRef}
          onClick={(e) => { e.stopPropagation(); onClick(node); }}
          onPointerOver={() => setHovered(true)}
          onPointerOut={() => setHovered(false)}
        >
          <dodecahedronGeometry args={[scale * 0.5, 0]} />
          <meshStandardMaterial
            color={color}
            emissive={color}
            emissiveIntensity={isSelected ? 0.8 : hovered ? 0.5 : 0.2}
            metalness={0.3}
            roughness={0.4}
          />
        </mesh>
      </Float>
      
      {/* File name label */}
      {(showLabels || hovered || isSelected) && (
        <Html
          position={[0, scale * 0.7, 0]}
          center
          distanceFactor={8}
          style={{ pointerEvents: 'none' }}
        >
          <div className={`px-2 py-1 rounded text-xs whitespace-nowrap transition-opacity ${
            hovered || isSelected ? 'opacity-100' : 'opacity-70'
          }`} style={{
            backgroundColor: 'rgba(0,0,0,0.8)',
            border: `1px solid ${color}`,
            color: 'white'
          }}>
            {node.name}
            <span className="text-zinc-400 ml-1 text-[10px]">{node.lines}L</span>
          </div>
        </Html>
      )}
      
      {/* Selection ring */}
      {isSelected && (
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <ringGeometry args={[scale * 0.6, scale * 0.7, 32]} />
          <meshBasicMaterial color={color} transparent opacity={0.5} side={THREE.DoubleSide} />
        </mesh>
      )}
    </group>
  );
}

// Connection line between dependent files using native Three.js
function DependencyLine({ start, end, color = "#374151" }) {
  const lineRef = useRef();
  
  useEffect(() => {
    if (lineRef.current) {
      const points = [
        new THREE.Vector3(...start),
        new THREE.Vector3(...end)
      ];
      lineRef.current.geometry.setFromPoints(points);
    }
  }, [start, end]);

  return (
    <line ref={lineRef}>
      <bufferGeometry />
      <lineBasicMaterial color={color} transparent opacity={0.4} />
    </line>
  );
}

// Camera controller
function CameraController({ target }) {
  const { camera } = useThree();
  
  useEffect(() => {
    if (target) {
      camera.position.lerp(new THREE.Vector3(target[0] + 5, target[1] + 3, target[2] + 5), 0.1);
    }
  }, [target, camera]);
  
  return null;
}

// Main 3D Scene
function Scene({ nodes, edges, selectedNode, onSelectNode, showLabels }) {
  // Calculate positions using force-directed layout
  const nodePositions = useMemo(() => {
    const positions = {};
    const angleStep = (2 * Math.PI) / Math.max(nodes.length, 1);
    
    nodes.forEach((node, i) => {
      // Arrange in a spiral pattern
      const radius = 3 + (i / nodes.length) * 5;
      const angle = i * angleStep * 1.5;
      const height = (i % 5) - 2;
      
      positions[node.id] = [
        Math.cos(angle) * radius,
        height,
        Math.sin(angle) * radius
      ];
    });
    
    return positions;
  }, [nodes]);

  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={0.4} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} color="#4f46e5" />
      
      {/* Environment */}
      <Environment preset="night" />
      <Sparkles count={100} scale={20} size={2} speed={0.4} opacity={0.3} />
      
      {/* Grid helper */}
      <gridHelper args={[20, 20, '#1a1a1f', '#1a1a1f']} position={[0, -3, 0]} />
      
      {/* Dependency lines */}
      {edges.map((edge, i) => {
        const startPos = nodePositions[edge.from];
        const endPos = nodePositions[edge.to];
        if (!startPos || !endPos) return null;
        
        return (
          <DependencyLine
            key={i}
            start={startPos}
            end={endPos}
            color={selectedNode?.id === edge.from || selectedNode?.id === edge.to ? "#60a5fa" : "#374151"}
          />
        );
      })}
      
      {/* File nodes */}
      {nodes.map((node) => (
        <FileNode
          key={node.id}
          node={node}
          position={nodePositions[node.id] || [0, 0, 0]}
          isSelected={selectedNode?.id === node.id}
          onClick={onSelectNode}
          showLabels={showLabels}
        />
      ))}
      
      {/* Camera controls */}
      <OrbitControls
        makeDefault
        enableDamping
        dampingFactor={0.05}
        minDistance={3}
        maxDistance={30}
        maxPolarAngle={Math.PI / 1.5}
      />
      
      {selectedNode && (
        <CameraController target={nodePositions[selectedNode.id]} />
      )}
    </>
  );
}

// Main component
const SystemVisualization3D = ({ projectId }) => {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);
  const [showLabels, setShowLabels] = useState(false);
  const [canvasReady, setCanvasReady] = useState(false);

  useEffect(() => {
    fetchVisualization();
    // Delay canvas mount to avoid race conditions
    const timer = setTimeout(() => setCanvasReady(true), 100);
    return () => {
      setCanvasReady(false);
      clearTimeout(timer);
    };
  }, [projectId]);

  const fetchVisualization = async () => {
    setLoading(true);
    try {
      const filesRes = await axios.get(`${API}/files?project_id=${projectId}`);
      const files = filesRes.data || [];
      
      // Create nodes
      const fileNodes = files.map((file) => {
        const ext = file.filepath?.split('.').pop() || 'default';
        return {
          id: file.id,
          name: file.filename || file.filepath?.split('/').pop() || 'Unknown',
          filepath: file.filepath,
          type: ext,
          lines: file.content?.split('\n').length || 0,
          size: file.content?.length || 0
        };
      });
      
      // Create edges based on imports
      const fileEdges = [];
      files.forEach((file) => {
        const content = file.content || '';
        files.forEach((otherFile) => {
          if (file.id !== otherFile.id) {
            const otherName = otherFile.filename?.replace(/\.[^/.]+$/, '') || '';
            if (otherName && content.includes(`import`) && content.includes(otherName)) {
              fileEdges.push({ from: file.id, to: otherFile.id });
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

  const handleSelectNode = useCallback((node) => {
    setSelectedNode(prev => prev?.id === node.id ? null : node);
  }, []);

  // Stats
  const stats = useMemo(() => ({
    totalFiles: nodes.length,
    totalLines: nodes.reduce((sum, n) => sum + n.lines, 0),
    totalDeps: edges.length,
    fileTypes: [...new Set(nodes.map(n => n.type))]
  }), [nodes, edges]);

  return (
    <div className="h-full flex flex-col bg-[#050507]" data-testid="system-visualization-3d">
      {/* Header */}
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800 bg-[#0a0a0c]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Box className="w-5 h-5 text-cyan-400" />
            <span className="font-rajdhani font-bold text-white">3D System Map</span>
            <Badge variant="outline" className="text-[10px] border-cyan-500/30 text-cyan-400">
              {stats.totalFiles} files
            </Badge>
            <Badge variant="outline" className="text-[10px] border-purple-500/30 text-purple-400">
              {stats.totalLines.toLocaleString()} lines
            </Badge>
            <Badge variant="outline" className="text-[10px] border-amber-500/30 text-amber-400">
              {stats.totalDeps} deps
            </Badge>
          </div>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="ghost"
              className="h-8 text-xs"
              onClick={() => setShowLabels(!showLabels)}
            >
              {showLabels ? <EyeOff className="w-3 h-3 mr-1" /> : <Eye className="w-3 h-3 mr-1" />}
              Labels
            </Button>
            <Button
              size="sm"
              variant="ghost"
              className="h-8 text-xs"
              onClick={fetchVisualization}
            >
              <RefreshCw className="w-3 h-3 mr-1" />
              Refresh
            </Button>
          </div>
        </div>
      </div>

      {/* 3D Canvas */}
      <div className="flex-1 relative">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-[#050507]">
            <div className="text-center">
              <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin mx-auto mb-2" />
              <p className="text-zinc-500 text-sm">Loading system map...</p>
            </div>
          </div>
        ) : nodes.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center bg-[#050507]">
            <div className="text-center">
              <Folder className="w-12 h-12 text-zinc-600 mx-auto mb-2" />
              <p className="text-zinc-500">No files in this project yet</p>
            </div>
          </div>
        ) : !canvasReady ? (
          <div className="absolute inset-0 flex items-center justify-center bg-[#050507]">
            <div className="text-center">
              <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin mx-auto mb-2" />
              <p className="text-zinc-500 text-sm">Initializing 3D view...</p>
            </div>
          </div>
        ) : (
          <CanvasErrorBoundary>
            <Canvas
              camera={{ position: [8, 5, 8], fov: 50 }}
              style={{ background: '#050507' }}
              onCreated={({ gl }) => {
                gl.setClearColor('#050507');
              }}
            >
              <Scene
                nodes={nodes}
                edges={edges}
                selectedNode={selectedNode}
                onSelectNode={handleSelectNode}
                showLabels={showLabels}
              />
            </Canvas>
          </CanvasErrorBoundary>
        )}

        {/* Selected node info panel */}
        {selectedNode && (
          <div className="absolute right-4 top-4 w-64 bg-zinc-900/95 border border-zinc-700 rounded-lg p-4 backdrop-blur-sm">
            <div className="flex items-center gap-2 mb-3">
              <div 
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: FILE_COLORS[selectedNode.type] || FILE_COLORS.default }}
              />
              <h4 className="font-medium text-white truncate">{selectedNode.name}</h4>
            </div>
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-zinc-500">Path:</span>
                <span className="text-zinc-300 text-xs truncate max-w-[140px]" title={selectedNode.filepath}>
                  {selectedNode.filepath}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Type:</span>
                <Badge 
                  className="text-[10px]"
                  style={{ 
                    backgroundColor: `${FILE_COLORS[selectedNode.type] || FILE_COLORS.default}20`,
                    color: FILE_COLORS[selectedNode.type] || FILE_COLORS.default
                  }}
                >
                  {selectedNode.type.toUpperCase()}
                </Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Lines:</span>
                <span className="text-zinc-300">{selectedNode.lines.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Size:</span>
                <span className="text-zinc-300">{(selectedNode.size / 1024).toFixed(1)} KB</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Imports:</span>
                <span className="text-zinc-300">
                  {edges.filter(e => e.from === selectedNode.id).length}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Imported by:</span>
                <span className="text-zinc-300">
                  {edges.filter(e => e.to === selectedNode.id).length}
                </span>
              </div>
            </div>
            
            <Button
              size="sm"
              variant="outline"
              className="w-full mt-3 text-xs border-zinc-700"
              onClick={() => setSelectedNode(null)}
            >
              Deselect
            </Button>
          </div>
        )}

        {/* Controls hint */}
        <div className="absolute left-4 bottom-4 text-[10px] text-zinc-600">
          <p>Drag to rotate • Scroll to zoom • Click node to select</p>
        </div>

        {/* Legend */}
        <div className="absolute left-4 top-4 bg-zinc-900/80 border border-zinc-800 rounded-lg p-3 backdrop-blur-sm">
          <p className="text-[10px] text-zinc-500 mb-2">File Types</p>
          <div className="flex flex-wrap gap-2">
            {stats.fileTypes.slice(0, 6).map(type => (
              <div key={type} className="flex items-center gap-1">
                <div 
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: FILE_COLORS[type] || FILE_COLORS.default }}
                />
                <span className="text-[10px] text-zinc-400">{type}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemVisualization3D;
