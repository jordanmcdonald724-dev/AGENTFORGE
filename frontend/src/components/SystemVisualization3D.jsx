import { useState, useEffect, useRef, useMemo, useCallback, Suspense } from "react";
import * as THREE from "three";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Box, RefreshCw, Eye, EyeOff, Folder, Layers, GitBranch,
  Network, BarChart3, CircleDot
} from "lucide-react";
import { API } from "@/App";

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

// Pure Three.js Visualization Component (no R3F to avoid reconciler issues)
const ThreeJSCanvas = ({ nodes, edges, selectedNode, onSelectNode, showLabels, viewMode }) => {
  const containerRef = useRef(null);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const rendererRef = useRef(null);
  const controlsRef = useRef(null);
  const nodesRef = useRef({});
  const linesRef = useRef([]);
  const animationRef = useRef(null);
  const raycasterRef = useRef(new THREE.Raycaster());
  const mouseRef = useRef(new THREE.Vector2());

  // Initialize Three.js scene
  useEffect(() => {
    if (!containerRef.current) return;

    // Scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x050507);
    scene.fog = new THREE.Fog(0x050507, 20, 50);
    sceneRef.current = scene;

    // Camera
    const camera = new THREE.PerspectiveCamera(
      60,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.set(15, 10, 15);
    cameraRef.current = camera;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ 
      antialias: true,
      alpha: true,
      powerPreference: "high-performance"
    });
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);

    const pointLight1 = new THREE.PointLight(0x60a5fa, 1, 50);
    pointLight1.position.set(10, 10, 10);
    scene.add(pointLight1);

    const pointLight2 = new THREE.PointLight(0xa855f7, 0.5, 50);
    pointLight2.position.set(-10, -5, -10);
    scene.add(pointLight2);

    // Grid
    const grid = new THREE.GridHelper(30, 30, 0x1a1a1f, 0x1a1a1f);
    grid.position.y = -3;
    scene.add(grid);

    // Orbit controls (manual implementation)
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };
    let spherical = new THREE.Spherical(20, Math.PI / 3, Math.PI / 4);

    const updateCamera = () => {
      camera.position.setFromSpherical(spherical);
      camera.lookAt(0, 0, 0);
    };
    updateCamera();

    const onMouseDown = (e) => {
      isDragging = true;
      previousMousePosition = { x: e.clientX, y: e.clientY };
    };

    const onMouseMove = (e) => {
      if (!isDragging) return;
      
      const deltaX = e.clientX - previousMousePosition.x;
      const deltaY = e.clientY - previousMousePosition.y;
      
      spherical.theta -= deltaX * 0.01;
      spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, spherical.phi + deltaY * 0.01));
      
      updateCamera();
      previousMousePosition = { x: e.clientX, y: e.clientY };
    };

    const onMouseUp = () => {
      isDragging = false;
    };

    const onWheel = (e) => {
      spherical.radius = Math.max(5, Math.min(40, spherical.radius + e.deltaY * 0.01));
      updateCamera();
    };

    // Click handler
    const onClick = (e) => {
      const rect = renderer.domElement.getBoundingClientRect();
      mouseRef.current.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouseRef.current.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      raycasterRef.current.setFromCamera(mouseRef.current, camera);
      const intersects = raycasterRef.current.intersectObjects(Object.values(nodesRef.current));
      
      if (intersects.length > 0) {
        const nodeId = intersects[0].object.userData.nodeId;
        const node = nodes.find(n => n.id === nodeId);
        if (node) onSelectNode(node);
      }
    };

    renderer.domElement.addEventListener('mousedown', onMouseDown);
    renderer.domElement.addEventListener('mousemove', onMouseMove);
    renderer.domElement.addEventListener('mouseup', onMouseUp);
    renderer.domElement.addEventListener('mouseleave', onMouseUp);
    renderer.domElement.addEventListener('wheel', onWheel);
    renderer.domElement.addEventListener('click', onClick);

    // Animation loop
    const animate = () => {
      animationRef.current = requestAnimationFrame(animate);
      
      // Animate nodes
      const time = Date.now() * 0.001;
      Object.values(nodesRef.current).forEach((mesh, i) => {
        if (mesh) {
          mesh.position.y = mesh.userData.baseY + Math.sin(time + i) * 0.2;
          mesh.rotation.y = time * 0.5;
        }
      });

      renderer.render(scene, camera);
    };
    animate();

    // Resize handler
    const handleResize = () => {
      if (!containerRef.current) return;
      camera.aspect = containerRef.current.clientWidth / containerRef.current.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    };
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      cancelAnimationFrame(animationRef.current);
      renderer.domElement.removeEventListener('mousedown', onMouseDown);
      renderer.domElement.removeEventListener('mousemove', onMouseMove);
      renderer.domElement.removeEventListener('mouseup', onMouseUp);
      renderer.domElement.removeEventListener('mouseleave', onMouseUp);
      renderer.domElement.removeEventListener('wheel', onWheel);
      renderer.domElement.removeEventListener('click', onClick);
      window.removeEventListener('resize', handleResize);
      
      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  // Update nodes when data changes
  useEffect(() => {
    if (!sceneRef.current) return;

    // Clear existing nodes
    Object.values(nodesRef.current).forEach(mesh => {
      if (mesh) sceneRef.current.remove(mesh);
    });
    nodesRef.current = {};

    // Clear existing lines
    linesRef.current.forEach(line => {
      if (line) sceneRef.current.remove(line);
    });
    linesRef.current = [];

    // Calculate positions based on view mode
    const positions = {};
    
    // For force-directed, we need to simulate forces
    const simulateForces = () => {
      // Initialize positions randomly
      const pos = {};
      nodes.forEach((node, i) => {
        pos[node.id] = {
          x: (Math.random() - 0.5) * 10,
          y: (Math.random() - 0.5) * 6,
          z: (Math.random() - 0.5) * 10,
          vx: 0, vy: 0, vz: 0
        };
      });
      
      // Run force simulation iterations
      for (let iter = 0; iter < 50; iter++) {
        // Repulsion between nodes
        nodes.forEach((n1, i) => {
          nodes.forEach((n2, j) => {
            if (i >= j) return;
            const dx = pos[n1.id].x - pos[n2.id].x;
            const dy = pos[n1.id].y - pos[n2.id].y;
            const dz = pos[n1.id].z - pos[n2.id].z;
            const dist = Math.sqrt(dx*dx + dy*dy + dz*dz) + 0.01;
            const force = 2 / (dist * dist);
            const fx = (dx / dist) * force;
            const fy = (dy / dist) * force;
            const fz = (dz / dist) * force;
            pos[n1.id].vx += fx; pos[n1.id].vy += fy; pos[n1.id].vz += fz;
            pos[n2.id].vx -= fx; pos[n2.id].vy -= fy; pos[n2.id].vz -= fz;
          });
        });
        
        // Attraction along edges
        edges.forEach(edge => {
          const p1 = pos[edge.from];
          const p2 = pos[edge.to];
          if (!p1 || !p2) return;
          const dx = p2.x - p1.x;
          const dy = p2.y - p1.y;
          const dz = p2.z - p1.z;
          const dist = Math.sqrt(dx*dx + dy*dy + dz*dz) + 0.01;
          const force = dist * 0.1;
          p1.vx += (dx / dist) * force;
          p1.vy += (dy / dist) * force;
          p1.vz += (dz / dist) * force;
          p2.vx -= (dx / dist) * force;
          p2.vy -= (dy / dist) * force;
          p2.vz -= (dz / dist) * force;
        });
        
        // Apply velocities with damping
        nodes.forEach(node => {
          const p = pos[node.id];
          p.x += p.vx * 0.1;
          p.y += p.vy * 0.1;
          p.z += p.vz * 0.1;
          p.vx *= 0.8; p.vy *= 0.8; p.vz *= 0.8;
        });
      }
      
      return pos;
    };
    
    // For treemap, calculate 2D layout based on file sizes
    const calculateTreemap = () => {
      const pos = {};
      const totalSize = nodes.reduce((sum, n) => sum + Math.max(n.size, 100), 0);
      const gridSize = 12;
      let currentX = -gridSize / 2;
      let currentZ = -gridSize / 2;
      let rowHeight = 0;
      
      // Sort by size descending
      const sortedNodes = [...nodes].sort((a, b) => b.size - a.size);
      
      sortedNodes.forEach((node, i) => {
        const proportion = Math.max(node.size, 100) / totalSize;
        const width = Math.max(0.5, Math.min(4, Math.sqrt(proportion * gridSize * gridSize)));
        const depth = width;
        
        if (currentX + width > gridSize / 2) {
          currentX = -gridSize / 2;
          currentZ += rowHeight + 0.3;
          rowHeight = 0;
        }
        
        pos[node.id] = {
          x: currentX + width / 2,
          y: 0,
          z: currentZ + depth / 2
        };
        
        currentX += width + 0.2;
        rowHeight = Math.max(rowHeight, depth);
      });
      
      return pos;
    };
    
    // Calculate positions based on selected view mode
    if (viewMode === 'force') {
      const forcePos = simulateForces();
      nodes.forEach(node => {
        positions[node.id] = { x: forcePos[node.id].x, y: forcePos[node.id].y, z: forcePos[node.id].z };
      });
    } else if (viewMode === 'treemap') {
      const treemapPos = calculateTreemap();
      nodes.forEach(node => {
        positions[node.id] = treemapPos[node.id] || { x: 0, y: 0, z: 0 };
      });
    } else {
      nodes.forEach((node, i) => {
        let x, y, z;
        
        switch (viewMode) {
          case 'spiral':
            const angle = i * 0.5;
            const radius = 2 + i * 0.3;
            x = Math.cos(angle) * radius;
            z = Math.sin(angle) * radius;
            y = (i / nodes.length) * 4 - 2;
            break;
          case 'cluster':
            // Group by file type
            const typeIndex = Object.keys(FILE_COLORS).indexOf(node.type);
            const groupAngle = (typeIndex / Object.keys(FILE_COLORS).length) * Math.PI * 2;
            const groupRadius = 5;
            const innerAngle = (i * 0.7) % (Math.PI * 2);
            x = Math.cos(groupAngle) * groupRadius + Math.cos(innerAngle) * 2;
            z = Math.sin(groupAngle) * groupRadius + Math.sin(innerAngle) * 2;
            y = ((i % 5) - 2) * 0.5;
            break;
          case 'tree':
            // Tree layout
            const depth = Math.floor(Math.log2(i + 1));
            const posInLevel = i - Math.pow(2, depth) + 1;
            const levelWidth = Math.pow(2, depth);
            x = (posInLevel / levelWidth - 0.5) * (10 / (depth + 1));
            y = depth * -2;
            z = 0;
            break;
          default: // radial
            const radAngle = (i / nodes.length) * Math.PI * 2;
            const radRadius = 4 + (i % 3) * 2;
            x = Math.cos(radAngle) * radRadius;
            z = Math.sin(radAngle) * radRadius;
            y = ((i % 5) - 2) * 0.5;
        }
        
        positions[node.id] = { x, y, z };
      });
    }

    // Create node meshes
    nodes.forEach((node) => {
      const color = FILE_COLORS[node.type] || FILE_COLORS.default;
      const scale = Math.max(0.3, Math.min(1, 0.3 + (node.lines / 500)));
      const pos = positions[node.id];

      // Create geometry based on file type
      let geometry;
      switch (node.type) {
        case 'jsx':
        case 'tsx':
          geometry = new THREE.OctahedronGeometry(scale * 0.5, 0);
          break;
        case 'py':
          geometry = new THREE.CylinderGeometry(scale * 0.4, scale * 0.4, scale * 0.6, 6);
          break;
        case 'json':
          geometry = new THREE.BoxGeometry(scale * 0.6, scale * 0.6, scale * 0.6);
          break;
        default:
          geometry = new THREE.DodecahedronGeometry(scale * 0.4, 0);
      }

      const material = new THREE.MeshStandardMaterial({
        color: new THREE.Color(color),
        emissive: new THREE.Color(color),
        emissiveIntensity: selectedNode?.id === node.id ? 0.8 : 0.3,
        metalness: 0.3,
        roughness: 0.4
      });

      const mesh = new THREE.Mesh(geometry, material);
      mesh.position.set(pos.x, pos.y, pos.z);
      mesh.userData = { nodeId: node.id, baseY: pos.y };
      mesh.castShadow = true;

      sceneRef.current.add(mesh);
      nodesRef.current[node.id] = mesh;
    });

    // Create edge lines
    edges.forEach((edge) => {
      const fromPos = positions[edge.from];
      const toPos = positions[edge.to];
      if (!fromPos || !toPos) return;

      const points = [
        new THREE.Vector3(fromPos.x, fromPos.y, fromPos.z),
        new THREE.Vector3(toPos.x, toPos.y, toPos.z)
      ];

      const geometry = new THREE.BufferGeometry().setFromPoints(points);
      const material = new THREE.LineBasicMaterial({
        color: selectedNode?.id === edge.from || selectedNode?.id === edge.to ? 0x60a5fa : 0x374151,
        transparent: true,
        opacity: 0.5
      });

      const line = new THREE.Line(geometry, material);
      sceneRef.current.add(line);
      linesRef.current.push(line);
    });

  }, [nodes, edges, selectedNode, viewMode]);

  return <div ref={containerRef} className="w-full h-full" />;
};

// Main Component
const SystemVisualization3D = ({ projectId }) => {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);
  const [showLabels, setShowLabels] = useState(false);
  const [viewMode, setViewMode] = useState('radial');

  useEffect(() => {
    fetchVisualization();
  }, [projectId]);

  const fetchVisualization = async () => {
    setLoading(true);
    try {
      const filesRes = await axios.get(`${API}/files?project_id=${projectId}`);
      const files = filesRes.data || [];
      
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

  const stats = useMemo(() => ({
    totalFiles: nodes.length,
    totalLines: nodes.reduce((sum, n) => sum + n.lines, 0),
    totalDeps: edges.length,
    fileTypes: [...new Set(nodes.map(n => n.type))]
  }), [nodes, edges]);

  const VIEW_MODES = [
    { id: 'radial', name: 'Radial', icon: CircleDot },
    { id: 'spiral', name: 'Spiral', icon: GitBranch },
    { id: 'cluster', name: 'Cluster', icon: Network },
    { id: 'tree', name: 'Tree', icon: Layers },
    { id: 'force', name: 'Force Graph', icon: Network },
    { id: 'treemap', name: 'Treemap', icon: BarChart3 }
  ];

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
            {/* View Mode Selector */}
            <div className="flex items-center gap-1 bg-zinc-900 rounded-lg p-1">
              {VIEW_MODES.map(mode => {
                const Icon = mode.icon;
                return (
                  <button
                    key={mode.id}
                    onClick={() => setViewMode(mode.id)}
                    className={`p-1.5 rounded transition-colors ${
                      viewMode === mode.id 
                        ? 'bg-cyan-500/20 text-cyan-400' 
                        : 'text-zinc-500 hover:text-zinc-300'
                    }`}
                    title={mode.name}
                  >
                    <Icon className="w-3.5 h-3.5" />
                  </button>
                );
              })}
            </div>
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
              <p className="text-zinc-600 text-xs mt-1">Add files to see the 3D visualization</p>
            </div>
          </div>
        ) : (
          <ThreeJSCanvas
            nodes={nodes}
            edges={edges}
            selectedNode={selectedNode}
            onSelectNode={handleSelectNode}
            showLabels={showLabels}
            viewMode={viewMode}
          />
        )}

        {/* Selected Node Info */}
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
          <div className="grid grid-cols-2 gap-x-3 gap-y-1">
            {stats.fileTypes.slice(0, 8).map(type => (
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
