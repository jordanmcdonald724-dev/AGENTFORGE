import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Scan, Bug, History, Lightbulb, Zap, Server, Users, Target, Brain, Radio, Rocket, Box
} from "lucide-react";
import AutopsyPanel from "./AutopsyPanel";
import DebugLoopPanel from "./DebugLoopPanel";
import TimeMachinePanel from "./TimeMachinePanel";
import IdeaEnginePanel from "./IdeaEnginePanel";
import SaaSBuilderPanel from "./SaaSBuilderPanel";
import BuildFarmPanel from "./BuildFarmPanel";
import DynamicAgentsPanel from "./DynamicAgentsPanel";
import GoalLoopPanel from "./GoalLoopPanel";
import KnowledgeGraphPanel from "./KnowledgeGraphPanel";
import MissionControlPanel from "./MissionControlPanel";
import RealityPipelinePanel from "./RealityPipelinePanel";
import SystemVisualization3D from "./SystemVisualization3D";

const CommandCenter = ({ projectId, projectName, onNavigate }) => {
  const [activeTab, setActiveTab] = useState("mission");

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]" data-testid="command-center">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <TabsList className="flex-shrink-0 bg-transparent border-b border-zinc-800 rounded-none px-2 h-10 justify-start overflow-x-auto">
          <TabsTrigger value="mission" className="text-xs data-[state=active]:bg-zinc-800" data-testid="cmd-mission-tab">
            <Radio className="w-3 h-3 mr-1" />Mission
          </TabsTrigger>
          <TabsTrigger value="goal" className="text-xs data-[state=active]:bg-zinc-800" data-testid="cmd-goal-tab">
            <Target className="w-3 h-3 mr-1" />Goal Loop
          </TabsTrigger>
          <TabsTrigger value="reality" className="text-xs data-[state=active]:bg-zinc-800" data-testid="cmd-reality-tab">
            <Rocket className="w-3 h-3 mr-1" />Idea→Reality
          </TabsTrigger>
          <TabsTrigger value="knowledge" className="text-xs data-[state=active]:bg-zinc-800" data-testid="cmd-knowledge-tab">
            <Brain className="w-3 h-3 mr-1" />Knowledge
          </TabsTrigger>
          <TabsTrigger value="autopsy" className="text-xs data-[state=active]:bg-zinc-800" data-testid="cmd-autopsy-tab">
            <Scan className="w-3 h-3 mr-1" />Autopsy
          </TabsTrigger>
          <TabsTrigger value="debug" className="text-xs data-[state=active]:bg-zinc-800" data-testid="cmd-debug-tab">
            <Bug className="w-3 h-3 mr-1" />Debug
          </TabsTrigger>
          <TabsTrigger value="timemachine" className="text-xs data-[state=active]:bg-zinc-800" data-testid="cmd-time-tab">
            <History className="w-3 h-3 mr-1" />Time
          </TabsTrigger>
          <TabsTrigger value="ideas" className="text-xs data-[state=active]:bg-zinc-800" data-testid="cmd-ideas-tab">
            <Lightbulb className="w-3 h-3 mr-1" />Ideas
          </TabsTrigger>
          <TabsTrigger value="saas" className="text-xs data-[state=active]:bg-zinc-800" data-testid="cmd-saas-tab">
            <Zap className="w-3 h-3 mr-1" />SaaS
          </TabsTrigger>
          <TabsTrigger value="farm" className="text-xs data-[state=active]:bg-zinc-800" data-testid="cmd-farm-tab">
            <Server className="w-3 h-3 mr-1" />Farm
          </TabsTrigger>
          <TabsTrigger value="agents" className="text-xs data-[state=active]:bg-zinc-800" data-testid="cmd-agents-tab">
            <Users className="w-3 h-3 mr-1" />Agents+
          </TabsTrigger>
          <TabsTrigger value="visualize" className="text-xs data-[state=active]:bg-zinc-800" data-testid="cmd-viz-tab">
            <Box className="w-3 h-3 mr-1" />3D Map
          </TabsTrigger>
        </TabsList>

        <TabsContent value="mission" className="flex-1 m-0 overflow-hidden">
          <MissionControlPanel projectId={projectId} />
        </TabsContent>

        <TabsContent value="goal" className="flex-1 m-0 overflow-hidden">
          <GoalLoopPanel projectId={projectId} />
        </TabsContent>

        <TabsContent value="reality" className="flex-1 m-0 overflow-hidden">
          <RealityPipelinePanel onProjectCreated={(id) => onNavigate && onNavigate(`/project/${id}`)} />
        </TabsContent>

        <TabsContent value="knowledge" className="flex-1 m-0 overflow-hidden">
          <KnowledgeGraphPanel projectId={projectId} />
        </TabsContent>

        <TabsContent value="autopsy" className="flex-1 m-0 overflow-hidden">
          <AutopsyPanel projectId={projectId} />
        </TabsContent>

        <TabsContent value="debug" className="flex-1 m-0 overflow-hidden">
          <DebugLoopPanel projectId={projectId} />
        </TabsContent>

        <TabsContent value="timemachine" className="flex-1 m-0 overflow-hidden">
          <TimeMachinePanel projectId={projectId} />
        </TabsContent>

        <TabsContent value="ideas" className="flex-1 m-0 overflow-hidden">
          <IdeaEnginePanel onBuildIdea={(id) => onNavigate && onNavigate(`/project/${id}`)} />
        </TabsContent>

        <TabsContent value="saas" className="flex-1 m-0 overflow-hidden">
          <SaaSBuilderPanel onProjectCreated={(id) => onNavigate && onNavigate(`/project/${id}`)} />
        </TabsContent>

        <TabsContent value="farm" className="flex-1 m-0 overflow-hidden">
          <BuildFarmPanel projectId={projectId} projectName={projectName} />
        </TabsContent>

        <TabsContent value="agents" className="flex-1 m-0 overflow-hidden">
          <DynamicAgentsPanel projectId={projectId} />
        </TabsContent>

        <TabsContent value="visualize" className="flex-1 m-0 overflow-hidden">
          <SystemVisualization3D projectId={projectId} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CommandCenter;
