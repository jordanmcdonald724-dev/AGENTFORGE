import React, { useState, useEffect, useRef, useCallback } from 'react';
import * as THREE from 'three';
import axios from 'axios';
import { 
  Network, Database, Globe, Shield, CreditCard, FileCode, 
  RefreshCw, Cpu, Cloud, Server, Zap, Eye, EyeOff
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { API } from '@/App';

// Architecture node colors
const NODE_COLORS = {
  frontend: '#8b5cf6',
  api: '#06b6d4',
  backend: '#f59e0b',
  database: '#22c55e',
  auth: '#ef4444',
  payments: '#ec4899',
  cache: '#f97316',
  cdn: '#3b82f6',
  default: '#6b7280'
};

// Pure Three.js 3D Visualization
const ThreeBrainCanvas = ({ nodes, connections, selectedNode, onSelectNode }) => {
  const containerRef = useRef(null);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const rendererRef = useRef(null);
  const nodesRef = useRef({});
  const linesRef = useRef([]);
  const animationRef = useRef(null);
  const particlesRef = useRef([]);

  useEffect(() => {
    if (!containerRef.current) return;
    
    // Prevent double initialization
    if (rendererRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x030305);
    scene.fog = new THREE.FogExp2(0x030305, 0.02);
    sceneRef.current = scene;

    // Camera
    const camera = new THREE.PerspectiveCamera(
      60,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.set(0, 12, 20);
    camera.lookAt(0, 0, 0);
    cameraRef.current = camera;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ 
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance'
    });
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.2);
    scene.add(ambientLight);

    // Point lights with colors
    const lights = [
      { color: 0x8b5cf6, pos: [10, 10, 10], intensity: 1 },
      { color: 0x06b6d4, pos: [-10, 5, -10], intensity: 0.8 },
      { color: 0xf59e0b, pos: [0, -10, 5], intensity: 0.5 },
    ];
    
    lights.forEach(({ color, pos, intensity }) => {
      const light = new THREE.PointLight(color, intensity, 50);
      light.position.set(...pos);
      scene.add(light);
    });

    // Create a glowing grid floor
    const gridSize = 30;
    const gridDivisions = 30;
    const gridHelper = new THREE.GridHelper(gridSize, gridDivisions, 0x1a1a2e, 0x0a0a12);
    gridHelper.position.y = -5;
    scene.add(gridHelper);

    // Add central holographic ring
    const ringGeometry = new THREE.RingGeometry(6, 6.2, 64);
    const ringMaterial = new THREE.MeshBasicMaterial({ 
      color: 0x06b6d4, 
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.3
    });
    const ring = new THREE.Mesh(ringGeometry, ringMaterial);
    ring.rotation.x = Math.PI / 2;
    ring.position.y = -4.9;
    scene.add(ring);

    // Particle system for atmosphere
    const particleCount = 200;
    const particleGeometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    
    for (let i = 0; i < particleCount * 3; i += 3) {
      positions[i] = (Math.random() - 0.5) * 40;
      positions[i + 1] = (Math.random() - 0.5) * 20;
      positions[i + 2] = (Math.random() - 0.5) * 40;
    }
    
    particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    const particleMaterial = new THREE.PointsMaterial({
      color: 0x06b6d4,
      size: 0.05,
      transparent: true,
      opacity: 0.6
    });
    
    const particles = new THREE.Points(particleGeometry, particleMaterial);
    scene.add(particles);
    particlesRef.current = particles;

    // Camera controls
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };
    let spherical = new THREE.Spherical(22, Math.PI / 2.5, Math.PI / 4);
    const target = new THREE.Vector3(0, 1, 0);

    const updateCamera = () => {
      camera.position.setFromSpherical(spherical);
      camera.position.add(target);
      camera.lookAt(target);
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
      spherical.phi = Math.max(0.2, Math.min(Math.PI - 0.2, spherical.phi + deltaY * 0.01));
      
      updateCamera();
      previousMousePosition = { x: e.clientX, y: e.clientY };
    };

    const onMouseUp = () => { isDragging = false; };

    const onWheel = (e) => {
      spherical.radius = Math.max(8, Math.min(30, spherical.radius + e.deltaY * 0.02));
      updateCamera();
    };

    // Click detection
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const onClick = (e) => {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(Object.values(nodesRef.current).filter(Boolean));
      
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
    renderer.domElement.addEventListener('wheel', onWheel, { passive: true });
    renderer.domElement.addEventListener('click', onClick);

    // Animation loop
    const animate = () => {
      animationRef.current = requestAnimationFrame(animate);
      
      const time = Date.now() * 0.001;
      
      // Animate nodes
      Object.values(nodesRef.current).forEach((mesh, i) => {
        if (mesh) {
          mesh.position.y = mesh.userData.baseY + Math.sin(time * 0.5 + i * 0.5) * 0.3;
          mesh.rotation.y = time * 0.3;
        }
      });

      // Animate ring
      ring.rotation.z = time * 0.2;

      // Animate particles
      if (particlesRef.current) {
        particlesRef.current.rotation.y = time * 0.05;
      }

      // Pulse effect on lines
      linesRef.current.forEach((line, i) => {
        if (line && line.material) {
          line.material.opacity = 0.3 + Math.sin(time * 2 + i) * 0.2;
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
      
      // Robust cleanup - check if element exists before removing
      if (containerRef.current && renderer.domElement && renderer.domElement.parentNode === containerRef.current) {
        containerRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
      sceneRef.current = null;
      cameraRef.current = null;
      rendererRef.current = null;
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

    // Create nodes in a circular layout
    nodes.forEach((node, i) => {
      const color = NODE_COLORS[node.type] || NODE_COLORS.default;
      
      // Position calculation - layered architecture (more compact)
      let x, y, z;
      const layerMap = { frontend: 2, api: 0.5, backend: 0, database: -2, auth: 0.5, payments: 0.5, cache: -1, cdn: 2 };
      const yPos = layerMap[node.type] ?? 0;
      
      const angle = (i / nodes.length) * Math.PI * 2;
      const radius = 5;
      
      x = Math.cos(angle) * radius;
      z = Math.sin(angle) * radius;
      y = yPos;

      // Create glowing node - larger size for visibility
      const geometry = new THREE.IcosahedronGeometry(0.8, 1);
      const material = new THREE.MeshStandardMaterial({
        color: new THREE.Color(color),
        emissive: new THREE.Color(color),
        emissiveIntensity: selectedNode?.id === node.id ? 1.5 : 1.0,
        metalness: 0.6,
        roughness: 0.3,
        transparent: true,
        opacity: 1.0
      });

      const mesh = new THREE.Mesh(geometry, material);
      mesh.position.set(x, y, z);
      mesh.userData = { nodeId: node.id, baseY: y };
      mesh.castShadow = true;

      // Add glow ring around selected node
      if (selectedNode?.id === node.id) {
        const glowRing = new THREE.RingGeometry(1.3, 1.6, 32);
        const glowMat = new THREE.MeshBasicMaterial({
          color: new THREE.Color(color),
          side: THREE.DoubleSide,
          transparent: true,
          opacity: 0.6
        });
        const glowMesh = new THREE.Mesh(glowRing, glowMat);
        glowMesh.position.copy(mesh.position);
        glowMesh.lookAt(cameraRef.current?.position || new THREE.Vector3(0, 10, 10));
        sceneRef.current.add(glowMesh);
        linesRef.current.push(glowMesh); // Add to cleanup array
      }

      sceneRef.current.add(mesh);
      nodesRef.current[node.id] = mesh;
    });

    // Create connection lines
    connections.forEach((conn) => {
      const fromMesh = nodesRef.current[conn.from];
      const toMesh = nodesRef.current[conn.to];
      if (!fromMesh || !toMesh) return;

      const fromNode = nodes.find(n => n.id === conn.from);
      const toNode = nodes.find(n => n.id === conn.to);
      
      const points = [];
      const fromPos = fromMesh.position.clone();
      const toPos = toMesh.position.clone();
      
      // Create curved line
      const mid = new THREE.Vector3().addVectors(fromPos, toPos).multiplyScalar(0.5);
      mid.y += 1;
      
      const curve = new THREE.QuadraticBezierCurve3(fromPos, mid, toPos);
      points.push(...curve.getPoints(20));

      const geometry = new THREE.BufferGeometry().setFromPoints(points);
      
      const isHighlighted = selectedNode && (conn.from === selectedNode.id || conn.to === selectedNode.id);
      const lineColor = isHighlighted ? 0x06b6d4 : 0x4a5568;
      
      const material = new THREE.LineBasicMaterial({
        color: lineColor,
        transparent: true,
        opacity: isHighlighted ? 0.9 : 0.5,
        linewidth: 2
      });

      const line = new THREE.Line(geometry, material);
      sceneRef.current.add(line);
      linesRef.current.push(line);
    });

  }, [nodes, connections, selectedNode]);

  return <div ref={containerRef} className="w-full h-full" />;
};

// Main Component
const VisualProjectBrain = ({ projectId, files = [] }) => {
  const [nodes, setNodes] = useState([]);
  const [connections, setConnections] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showStats, setShowStats] = useState(true);
  const [viewMode, setViewMode] = useState('architecture'); // architecture, files, dependencies

  // Analyze files and create dynamic nodes
  useEffect(() => {
    setLoading(true);
    
    if (viewMode === 'files' && files.length > 0) {
      // Create nodes from actual project files
      const fileNodes = [];
      const fileConnections = [];
      
      // Group files by directory
      const directories = {};
      files.forEach(file => {
        const path = file.filepath || file.filename || '';
        const dir = path.split('/').slice(0, -1).join('/') || '/';
        if (!directories[dir]) {
          directories[dir] = [];
        }
        directories[dir].push(file);
      });

      // Create directory nodes
      Object.keys(directories).forEach((dir, i) => {
        const dirFiles = directories[dir];
        const type = dir.includes('frontend') || dir.includes('src') ? 'frontend' :
                     dir.includes('backend') || dir.includes('routes') ? 'backend' :
                     dir.includes('models') ? 'database' :
                     dir.includes('auth') ? 'auth' : 'default';
        
        fileNodes.push({
          id: dir,
          label: dir.split('/').pop() || 'root',
          type,
          icon: type === 'frontend' ? Globe : type === 'backend' ? Server : FileCode,
          description: `${dirFiles.length} files`,
          fileCount: dirFiles.length
        });
      });

      // Create connections between related directories
      const dirList = Object.keys(directories);
      for (let i = 0; i < dirList.length; i++) {
        for (let j = i + 1; j < dirList.length; j++) {
          if (dirList[i].includes(dirList[j]) || dirList[j].includes(dirList[i])) {
            fileConnections.push({ from: dirList[i], to: dirList[j] });
          }
        }
      }

      setNodes(fileNodes.slice(0, 12)); // Limit to 12 nodes for performance
      setConnections(fileConnections.slice(0, 15));
    } else {
      // Default architecture view
      const architectureNodes = [
        { id: 'frontend', label: 'Frontend', type: 'frontend', icon: Globe, description: 'React UI Layer' },
        { id: 'api', label: 'API Gateway', type: 'api', icon: Network, description: 'REST/GraphQL Endpoints' },
        { id: 'backend', label: 'Backend Services', type: 'backend', icon: Server, description: 'Business Logic' },
        { id: 'database', label: 'Database', type: 'database', icon: Database, description: 'MongoDB Storage' },
        { id: 'auth', label: 'Authentication', type: 'auth', icon: Shield, description: 'JWT/OAuth' },
        { id: 'payments', label: 'Payments', type: 'payments', icon: CreditCard, description: 'Stripe Integration' },
        { id: 'cache', label: 'Cache Layer', type: 'cache', icon: Zap, description: 'Redis Cache' },
        { id: 'cdn', label: 'CDN', type: 'cdn', icon: Cloud, description: 'Static Assets' },
      ];

      const architectureConnections = [
        { from: 'cdn', to: 'frontend' },
        { from: 'frontend', to: 'api' },
        { from: 'api', to: 'backend' },
        { from: 'api', to: 'auth' },
        { from: 'api', to: 'payments' },
        { from: 'backend', to: 'database' },
        { from: 'backend', to: 'cache' },
        { from: 'auth', to: 'database' },
        { from: 'payments', to: 'backend' },
      ];

      setNodes(architectureNodes);
      setConnections(architectureConnections);
    }
    
    setLoading(false);
  }, [projectId, files, viewMode]);

  const handleSelectNode = useCallback((node) => {
    setSelectedNode(prev => prev?.id === node.id ? null : node);
  }, []);

  // Calculate file stats by type
  const fileStats = files.reduce((acc, file) => {
    const ext = file.name?.split('.').pop() || 'other';
    acc[ext] = (acc[ext] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="h-full flex flex-col bg-[#030305]" data-testid="project-brain">
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 border-b border-zinc-800/50 bg-black/50 backdrop-blur-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-3 h-3 rounded-full bg-cyan-500 animate-pulse" />
              <div className="absolute inset-0 w-3 h-3 rounded-full bg-cyan-500 animate-ping" />
            </div>
            <h2 className="text-lg font-bold text-white tracking-wide">VISUAL PROJECT BRAIN</h2>
            <Badge className="bg-cyan-500/20 text-cyan-400 text-[10px]">
              {nodes.length} NODES
            </Badge>
            <Badge className="bg-violet-500/20 text-violet-400 text-[10px]">
              {connections.length} CONNECTIONS
            </Badge>
          </div>
          <div className="flex items-center gap-2">
            {/* View Mode Toggle */}
            <div className="flex bg-zinc-900 rounded-lg p-1">
              <button
                onClick={() => setViewMode('architecture')}
                className={`px-3 py-1 text-xs rounded-md transition-all ${
                  viewMode === 'architecture' 
                    ? 'bg-cyan-500/20 text-cyan-400' 
                    : 'text-zinc-500 hover:text-white'
                }`}
              >
                Architecture
              </button>
              <button
                onClick={() => setViewMode('files')}
                className={`px-3 py-1 text-xs rounded-md transition-all ${
                  viewMode === 'files' 
                    ? 'bg-cyan-500/20 text-cyan-400' 
                    : 'text-zinc-500 hover:text-white'
                }`}
              >
                Files
              </button>
            </div>
            <Button
              size="sm"
              variant="ghost"
              className="h-8 text-xs text-zinc-400 hover:text-white"
              onClick={() => setShowStats(!showStats)}
            >
              {showStats ? <EyeOff className="w-3 h-3 mr-1" /> : <Eye className="w-3 h-3 mr-1" />}
              Stats
            </Button>
            <Button
              size="sm"
              variant="ghost"
              className="h-8 text-xs text-zinc-400 hover:text-white"
              onClick={() => setSelectedNode(null)}
            >
              <RefreshCw className="w-3 h-3 mr-1" />
              Reset
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 relative overflow-hidden">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin mx-auto mb-2" />
              <p className="text-zinc-500 text-sm">Initializing neural network...</p>
            </div>
          </div>
        ) : (
          <ThreeBrainCanvas
            nodes={nodes}
            connections={connections}
            selectedNode={selectedNode}
            onSelectNode={handleSelectNode}
          />
        )}

        {/* Selected Node Details */}
        {selectedNode && (
          <div className="absolute right-4 top-4 w-72 bg-zinc-900/95 border border-zinc-700/50 rounded-xl p-4 backdrop-blur-xl shadow-2xl">
            <div className="flex items-center gap-3 mb-4">
              <div 
                className="w-10 h-10 rounded-lg flex items-center justify-center"
                style={{ backgroundColor: `${NODE_COLORS[selectedNode.type]}20` }}
              >
                {selectedNode.icon && <selectedNode.icon className="w-5 h-5" style={{ color: NODE_COLORS[selectedNode.type] }} />}
              </div>
              <div>
                <h4 className="font-bold text-white">{selectedNode.label}</h4>
                <p className="text-xs text-zinc-500">{selectedNode.type.toUpperCase()}</p>
              </div>
            </div>
            
            <p className="text-sm text-zinc-400 mb-4">{selectedNode.description}</p>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-zinc-500">Connections In:</span>
                <span className="text-cyan-400 font-mono">
                  {connections.filter(c => c.to === selectedNode.id).length}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-zinc-500">Connections Out:</span>
                <span className="text-violet-400 font-mono">
                  {connections.filter(c => c.from === selectedNode.id).length}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-zinc-500">Status:</span>
                <Badge className="bg-green-500/20 text-green-400 text-[10px]">ACTIVE</Badge>
              </div>
            </div>

            <Button
              size="sm"
              variant="outline"
              className="w-full mt-4 text-xs border-zinc-700"
              onClick={() => setSelectedNode(null)}
            >
              Close
            </Button>
          </div>
        )}

        {/* File Stats Panel */}
        {showStats && Object.keys(fileStats).length > 0 && (
          <div className="absolute left-4 bottom-4 bg-zinc-900/90 border border-zinc-800/50 rounded-xl p-4 backdrop-blur-xl">
            <p className="text-xs text-zinc-500 uppercase tracking-wider mb-3">Project Files</p>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(fileStats).slice(0, 6).map(([ext, count]) => (
                <div key={ext} className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-cyan-500" />
                  <span className="text-xs text-zinc-400">.{ext}</span>
                  <span className="text-xs text-white font-mono ml-auto">{count}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Legend */}
        <div className="absolute left-4 top-4 bg-zinc-900/80 border border-zinc-800/50 rounded-xl p-3 backdrop-blur-xl">
          <p className="text-[10px] text-zinc-500 uppercase tracking-wider mb-2">Architecture Layers</p>
          <div className="space-y-1.5">
            {[
              { label: 'Presentation', color: NODE_COLORS.frontend },
              { label: 'Gateway', color: NODE_COLORS.api },
              { label: 'Services', color: NODE_COLORS.backend },
              { label: 'Data', color: NODE_COLORS.database },
            ].map(item => (
              <div key={item.label} className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-[10px] text-zinc-400">{item.label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Controls hint */}
        <div className="absolute right-4 bottom-4 text-[10px] text-zinc-600 text-right">
          <p>Drag to rotate</p>
          <p>Scroll to zoom</p>
          <p>Click node to inspect</p>
        </div>
      </div>
    </div>
  );
};

export default VisualProjectBrain;
