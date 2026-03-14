/**
 * WarRoomPanel Component
 * ======================
 * Immersive view of AI agents collaborating in real-time.
 * Shows agents as avatars in a "war room" actively discussing and building.
 * Supports resizable split-pane layout.
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Radio, Bot, Zap, Code, Shield, Palette, 
  Brain, Cpu, Music, Gamepad2, BookOpen, Layers,
  ArrowRight, MessageCircle, CheckCircle, AlertTriangle,
  Loader2, Play, Pause, Square, Volume2, VolumeX,
  Columns, Rows, Maximize2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { ResizablePanelGroup, ResizablePanel, ResizableHandle } from '@/components/ui/resizable';

// Agent configurations with personalities
const AGENT_CONFIG = {
  COMMANDER: { 
    icon: Zap, 
    color: 'from-amber-500 to-orange-600',
    bgColor: 'bg-amber-500/20',
    textColor: 'text-amber-400',
    role: 'Lead Director',
    personality: 'Decisive, strategic, commanding'
  },
  ATLAS: { 
    icon: Brain, 
    color: 'from-blue-500 to-cyan-600',
    bgColor: 'bg-blue-500/20',
    textColor: 'text-blue-400',
    role: 'Systems Architect',
    personality: 'Analytical, thorough, visionary'
  },
  FORGE: { 
    icon: Code, 
    color: 'from-emerald-500 to-green-600',
    bgColor: 'bg-emerald-500/20',
    textColor: 'text-emerald-400',
    role: 'Code Architect',
    personality: 'Fast, precise, perfectionist'
  },
  SENTINEL: { 
    icon: Shield, 
    color: 'from-red-500 to-rose-600',
    bgColor: 'bg-red-500/20',
    textColor: 'text-red-400',
    role: 'Code Reviewer',
    personality: 'Critical, thorough, protective'
  },
  PROBE: { 
    icon: CheckCircle, 
    color: 'from-pink-500 to-rose-600',
    bgColor: 'bg-pink-500/20',
    textColor: 'text-pink-400',
    role: 'QA Specialist',
    personality: 'Meticulous, persistent, quality-focused'
  },
  PRISM: { 
    icon: Palette, 
    color: 'from-violet-500 to-purple-600',
    bgColor: 'bg-violet-500/20',
    textColor: 'text-violet-400',
    role: 'UI/UX Designer',
    personality: 'Creative, aesthetic, user-focused'
  },
  TERRA: { 
    icon: Layers, 
    color: 'from-green-500 to-teal-600',
    bgColor: 'bg-green-500/20',
    textColor: 'text-green-400',
    role: 'Level Designer',
    personality: 'Spatial, immersive, detail-oriented'
  },
  KINETIC: { 
    icon: Gamepad2, 
    color: 'from-orange-500 to-yellow-600',
    bgColor: 'bg-orange-500/20',
    textColor: 'text-orange-400',
    role: 'Animation Lead',
    personality: 'Dynamic, fluid, expressive'
  },
  SONIC: { 
    icon: Music, 
    color: 'from-cyan-500 to-blue-600',
    bgColor: 'bg-cyan-500/20',
    textColor: 'text-cyan-400',
    role: 'Audio Engineer',
    personality: 'Atmospheric, immersive, rhythmic'
  },
  NEXUS: { 
    icon: Cpu, 
    color: 'from-purple-500 to-indigo-600',
    bgColor: 'bg-purple-500/20',
    textColor: 'text-purple-400',
    role: 'Game Designer',
    personality: 'Systematic, balanced, engaging'
  },
  CHRONICLE: { 
    icon: BookOpen, 
    color: 'from-yellow-500 to-amber-600',
    bgColor: 'bg-yellow-500/20',
    textColor: 'text-yellow-400',
    role: 'Narrative Designer',
    personality: 'Storyteller, emotional, deep'
  },
  VERTEX: { 
    icon: Layers, 
    color: 'from-teal-500 to-emerald-600',
    bgColor: 'bg-teal-500/20',
    textColor: 'text-teal-400',
    role: 'Technical Artist',
    personality: 'Technical, visual, optimizer'
  }
};

// Speaking animation component
const SpeakingIndicator = () => (
  <div className="flex items-center gap-0.5">
    {[0, 1, 2].map((i) => (
      <motion.div
        key={i}
        className="w-1 bg-cyan-400 rounded-full"
        animate={{ height: [4, 12, 4] }}
        transition={{ duration: 0.5, repeat: Infinity, delay: i * 0.1 }}
      />
    ))}
  </div>
);

// Agent Avatar in the room
const AgentAvatar = ({ agent, isActive, isSpeaking, status }) => {
  const config = AGENT_CONFIG[agent] || AGENT_CONFIG.COMMANDER;
  const Icon = config.icon;
  
  return (
    <motion.div
      className="relative flex flex-col items-center"
      animate={isSpeaking ? { scale: [1, 1.05, 1] } : {}}
      transition={{ duration: 0.5, repeat: isSpeaking ? Infinity : 0 }}
    >
      <div className={`relative w-12 h-12 rounded-full flex items-center justify-center ${config.bgColor} ${isActive ? 'ring-2 ring-cyan-400' : ''}`}>
        <Icon className={`w-6 h-6 ${config.textColor}`} />
        {isSpeaking && (
          <motion.div
            className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-cyan-500 flex items-center justify-center"
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 0.3, repeat: Infinity }}
          >
            <MessageCircle className="w-2.5 h-2.5 text-white" />
          </motion.div>
        )}
        {status === 'working' && !isSpeaking && (
          <motion.div
            className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-emerald-500 flex items-center justify-center"
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          >
            <Loader2 className="w-2.5 h-2.5 text-white" />
          </motion.div>
        )}
      </div>
      <span className="mt-1 text-[10px] font-medium text-zinc-400">{agent}</span>
      <span className="text-[8px] text-zinc-600">{config.role}</span>
    </motion.div>
  );
};

// Chat bubble component
const ChatBubble = ({ message, isLatest }) => {
  const config = AGENT_CONFIG[message.from_agent] || AGENT_CONFIG.COMMANDER;
  const Icon = config.icon;
  
  const getTypeStyle = (type) => {
    switch(type) {
      case 'handoff': return 'border-l-cyan-500 bg-cyan-500/5';
      case 'warning': return 'border-l-red-500 bg-red-500/5';
      case 'complete': return 'border-l-emerald-500 bg-emerald-500/5';
      case 'thinking': return 'border-l-purple-500 bg-purple-500/5';
      case 'code': return 'border-l-blue-500 bg-blue-500/5';
      default: return 'border-l-zinc-600 bg-zinc-800/50';
    }
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      className={`flex gap-3 p-3 rounded-lg border-l-4 ${getTypeStyle(message.message_type)} ${isLatest ? 'ring-1 ring-cyan-500/30' : ''}`}
    >
      <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${config.bgColor}`}>
        <Icon className={`w-5 h-5 ${config.textColor}`} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1 flex-wrap">
          <span className={`font-rajdhani font-bold text-sm ${config.textColor}`}>{message.from_agent}</span>
          {message.to_agent && (
            <>
              <ArrowRight className="w-3 h-3 text-zinc-600" />
              <span className="text-xs text-zinc-500">{message.to_agent}</span>
            </>
          )}
          <Badge variant="outline" className={`text-[10px] border-zinc-700 ${config.textColor}`}>
            {message.message_type}
          </Badge>
          {isLatest && (
            <Badge className="text-[10px] bg-cyan-500/20 text-cyan-400 animate-pulse">
              LIVE
            </Badge>
          )}
        </div>
        <p className="text-sm text-zinc-300 leading-relaxed">{message.content}</p>
        {message.files_mentioned && message.files_mentioned.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {message.files_mentioned.map((file, i) => (
              <Badge key={i} variant="outline" className="text-[10px] border-zinc-700 text-zinc-400">
                {file}
              </Badge>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
};

const WarRoomPanel = ({ 
  messages = [], 
  currentBuild,
  onSimulate,
  onPause,
  onResume,
  onCancel,
  activeAgents = []
}) => {
  const scrollRef = useRef(null);
  const [soundEnabled, setSoundEnabled] = useState(false);
  const [speakingAgent, setSpeakingAgent] = useState(null);
  const [layout, setLayout] = useState('stacked'); // 'stacked', 'horizontal', 'agents-only', 'messages-only'
  
  // Determine which agents are currently active based on messages
  const getActiveAgents = () => {
    if (!currentBuild || currentBuild.status !== 'running') return [];
    const recentMessages = messages.slice(-5);
    const agents = new Set();
    recentMessages.forEach(msg => {
      if (msg.from_agent) agents.add(msg.from_agent);
      if (msg.to_agent) agents.add(msg.to_agent);
    });
    return Array.from(agents);
  };
  
  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);
  
  // Update speaking agent based on latest message
  useEffect(() => {
    if (messages.length > 0) {
      const latest = messages[messages.length - 1];
      setSpeakingAgent(latest.from_agent);
      // Clear speaking after 3 seconds
      const timer = setTimeout(() => setSpeakingAgent(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [messages]);
  
  const currentActiveAgents = getActiveAgents();

  // Agents Grid Component
  const AgentsGrid = ({ compact = false }) => (
    <div className={`${compact ? 'p-2' : 'p-4'} border-b border-zinc-800 bg-zinc-900/50`}>
      <div className={`flex items-center justify-center gap-${compact ? '2' : '4'} flex-wrap`}>
        {Object.keys(AGENT_CONFIG).slice(0, 8).map((agent) => (
          <AgentAvatar
            key={agent}
            agent={agent}
            isActive={currentActiveAgents.includes(agent)}
            isSpeaking={speakingAgent === agent}
            status={currentActiveAgents.includes(agent) ? 'working' : 'idle'}
          />
        ))}
      </div>
      {!compact && (
        <div className="flex items-center justify-center gap-4 flex-wrap mt-3">
          {Object.keys(AGENT_CONFIG).slice(8).map((agent) => (
            <AgentAvatar
              key={agent}
              agent={agent}
              isActive={currentActiveAgents.includes(agent)}
              isSpeaking={speakingAgent === agent}
              status={currentActiveAgents.includes(agent) ? 'working' : 'idle'}
            />
          ))}
        </div>
      )}
    </div>
  );

  // Messages Feed Component
  const MessagesFeed = () => (
    <div className="flex-1 overflow-y-auto p-4" ref={scrollRef}>
      <div className="space-y-3">
        {messages.length === 0 ? (
          <div className="text-center py-16">
            <motion.div
              animate={{ scale: [1, 1.1, 1], rotate: [0, 5, -5, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <Radio className="w-16 h-16 mx-auto mb-4 text-cyan-400/30" />
            </motion.div>
            <h3 className="font-rajdhani text-xl text-white mb-2">War Room Standing By</h3>
            <p className="text-sm text-zinc-500 mb-6 max-w-md mx-auto">
              Start a build to watch your AI team collaborate in real-time. 
              Each agent will discuss, delegate, and create together.
            </p>
            <Button onClick={onSimulate} className="bg-cyan-500 hover:bg-cyan-600">
              <Radio className="w-4 h-4 mr-2" />
              Start Simulation
            </Button>
          </div>
        ) : (
          <>
            <AnimatePresence>
              {messages.map((msg, i) => (
                <ChatBubble 
                  key={msg.id || i} 
                  message={msg} 
                  isLatest={i === messages.length - 1 && currentBuild?.status === 'running'}
                />
              ))}
            </AnimatePresence>
            
            {currentBuild?.status === 'running' && speakingAgent && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-zinc-800/30"
              >
                <SpeakingIndicator />
                <span className="text-xs text-zinc-400">{speakingAgent} is thinking...</span>
              </motion.div>
            )}
          </>
        )}
      </div>
    </div>
  );

  // Build Stages Component
  const BuildStages = () => currentBuild && currentBuild.stages && currentBuild.stages.length > 0 ? (
    <div className="flex-shrink-0 p-3 border-b border-zinc-800 bg-zinc-900/30">
      <div className="flex gap-2 overflow-x-auto pb-1">
        {currentBuild.stages.map((stage, i) => (
          <div 
            key={i} 
            className={`flex-shrink-0 px-3 py-2 rounded-lg border text-xs transition-all ${
              stage.status === 'completed' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 
              stage.status === 'in_progress' ? 'bg-blue-500/10 border-blue-500/30 text-blue-400 animate-pulse' : 
              stage.status === 'failed' ? 'bg-red-500/10 border-red-500/30 text-red-400' : 
              'bg-zinc-800/50 border-zinc-700 text-zinc-500'
            }`}
          >
            <div className="font-medium flex items-center gap-1">
              {stage.status === 'completed' && <CheckCircle className="w-3 h-3" />}
              {stage.status === 'in_progress' && <Loader2 className="w-3 h-3 animate-spin" />}
              {stage.name}
            </div>
            {stage.files_created?.length > 0 && (
              <div className="text-[10px] mt-1 opacity-70">{stage.files_created.length} files</div>
            )}
          </div>
        ))}
      </div>
    </div>
  ) : null;
  
  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-gradient-to-b from-zinc-900 to-zinc-950">
      {/* Header with status */}
      <div className="flex-shrink-0 p-4 border-b border-zinc-800 bg-gradient-to-r from-cyan-500/10 via-transparent to-purple-500/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <Radio className="w-6 h-6 text-cyan-400" />
              {currentBuild?.status === 'running' && (
                <motion.div
                  className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"
                  animate={{ scale: [1, 1.2, 1], opacity: [1, 0.5, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                />
              )}
            </div>
            <div>
              <h3 className="font-rajdhani font-bold text-white text-lg flex items-center gap-2">
                Agent War Room
                {currentBuild?.status === 'running' && (
                  <Badge className="bg-red-500/20 text-red-400 text-[10px] animate-pulse">LIVE</Badge>
                )}
              </h3>
              <p className="text-xs text-zinc-500">Watch the team build in real-time</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {/* Layout toggle buttons */}
            <div className="flex items-center gap-1 bg-zinc-800/50 rounded-lg p-1">
              <Button 
                variant="ghost" 
                size="icon" 
                className={`h-7 w-7 ${layout === 'stacked' ? 'bg-zinc-700' : ''}`}
                onClick={() => setLayout('stacked')}
                title="Stacked view"
              >
                <Rows className="w-3.5 h-3.5 text-zinc-400" />
              </Button>
              <Button 
                variant="ghost" 
                size="icon" 
                className={`h-7 w-7 ${layout === 'horizontal' ? 'bg-zinc-700' : ''}`}
                onClick={() => setLayout('horizontal')}
                title="Side-by-side view"
              >
                <Columns className="w-3.5 h-3.5 text-zinc-400" />
              </Button>
              <Button 
                variant="ghost" 
                size="icon" 
                className={`h-7 w-7 ${layout === 'messages-only' ? 'bg-zinc-700' : ''}`}
                onClick={() => setLayout('messages-only')}
                title="Messages only"
              >
                <Maximize2 className="w-3.5 h-3.5 text-zinc-400" />
              </Button>
            </div>

            {/* Sound toggle */}
            <Button 
              variant="ghost" 
              size="icon" 
              className="h-8 w-8"
              onClick={() => setSoundEnabled(!soundEnabled)}
            >
              {soundEnabled ? <Volume2 className="w-4 h-4 text-cyan-400" /> : <VolumeX className="w-4 h-4 text-zinc-500" />}
            </Button>
            
            {currentBuild && (
              <div className="flex items-center gap-2">
                <Badge className={`text-xs ${
                  currentBuild.status === 'running' ? 'bg-blue-500/20 text-blue-400' : 
                  currentBuild.status === 'completed' ? 'bg-emerald-500/20 text-emerald-400' : 
                  currentBuild.status === 'paused' ? 'bg-yellow-500/20 text-yellow-400' : 
                  'bg-zinc-800 text-zinc-400'
                }`}>
                  {currentBuild.status?.toUpperCase()}
                </Badge>
                {currentBuild.status === "running" && (
                  <>
                    <Progress value={currentBuild.progress_percent || 0} className="w-24 h-2" />
                    <span className="text-xs text-zinc-400">{currentBuild.progress_percent || 0}%</span>
                    <Button variant="ghost" size="icon" className="h-7 w-7" onClick={onPause}>
                      <Pause className="w-3.5 h-3.5" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-7 w-7 text-red-400" onClick={onCancel}>
                      <Square className="w-3.5 h-3.5" />
                    </Button>
                  </>
                )}
                {currentBuild.status === "paused" && (
                  <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={onResume}>
                    <Play className="w-3 h-3 mr-1" />Resume
                  </Button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Main Content - Layout dependent */}
      {layout === 'stacked' && (
        <>
          <AgentsGrid />
          <BuildStages />
          <MessagesFeed />
        </>
      )}
      
      {layout === 'horizontal' && (
        <ResizablePanelGroup direction="horizontal" className="flex-1">
          <ResizablePanel defaultSize={35} minSize={20} maxSize={50}>
            <div className="h-full flex flex-col overflow-hidden">
              <AgentsGrid compact />
              <BuildStages />
            </div>
          </ResizablePanel>
          <ResizableHandle withHandle className="bg-zinc-800 hover:bg-cyan-500/50 transition-colors" />
          <ResizablePanel defaultSize={65} minSize={40}>
            <MessagesFeed />
          </ResizablePanel>
        </ResizablePanelGroup>
      )}
      
      {layout === 'messages-only' && (
        <>
          <BuildStages />
          <MessagesFeed />
        </>
      )}
    </div>
  );
};

export default WarRoomPanel;
