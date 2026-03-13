import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Scan, Bug, History, Lightbulb, Zap, Server, Users, Map
} from "lucide-react";
import AutopsyPanel from "./AutopsyPanel";
import DebugLoopPanel from "./DebugLoopPanel";
import TimeMachinePanel from "./TimeMachinePanel";
import IdeaEnginePanel from "./IdeaEnginePanel";
import SaaSBuilderPanel from "./SaaSBuilderPanel";
import BuildFarmPanel from "./BuildFarmPanel";
import DynamicAgentsPanel from "./DynamicAgentsPanel";

const CommandCenter = ({ projectId, projectName, onNavigate }) => {
  const [activeTab, setActiveTab] = useState("autopsy");

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]" data-testid="command-center">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <TabsList className="flex-shrink-0 bg-transparent border-b border-zinc-800 rounded-none px-2 h-10 justify-start overflow-x-auto">
          <TabsTrigger value="autopsy" className="text-xs data-[state=active]:bg-zinc-800" data-testid="cmd-autopsy-tab">
            <Scan className="w-3 h-3 mr-1" />Autopsy
          </TabsTrigger>
          <TabsTrigger value="debug" className="text-xs data-[state=active]:bg-zinc-800" data-testid="cmd-debug-tab">
            <Bug className="w-3 h-3 mr-1" />Debug Loop
          </TabsTrigger>
          <TabsTrigger value="timemachine" className="text-xs data-[state=active]:bg-zinc-800" data-testid="cmd-time-tab">
            <History className="w-3 h-3 mr-1" />Time Machine
          </TabsTrigger>
          <TabsTrigger value="ideas" className="text-xs data-[state=active]:bg-zinc-800" data-testid="cmd-ideas-tab">
            <Lightbulb className="w-3 h-3 mr-1" />Ideas
          </TabsTrigger>
          <TabsTrigger value="saas" className="text-xs data-[state=active]:bg-zinc-800" data-testid="cmd-saas-tab">
            <Zap className="w-3 h-3 mr-1" />SaaS Builder
          </TabsTrigger>
          <TabsTrigger value="farm" className="text-xs data-[state=active]:bg-zinc-800" data-testid="cmd-farm-tab">
            <Server className="w-3 h-3 mr-1" />Build Farm
          </TabsTrigger>
          <TabsTrigger value="agents" className="text-xs data-[state=active]:bg-zinc-800" data-testid="cmd-agents-tab">
            <Users className="w-3 h-3 mr-1" />Agents+
          </TabsTrigger>
        </TabsList>

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
      </Tabs>
    </div>
  );
};

export default CommandCenter;
