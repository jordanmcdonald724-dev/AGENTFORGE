import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  GitBranch, Cloud, Terminal, Palette, Factory, Gamepad2, 
  Brain, Activity, Cpu, Network, Globe, Rocket, Play, Loader2
} from "lucide-react";
import { API } from "@/App";

const OSFeaturesPanel = ({ projectId }) => {
  const [activeTab, setActiveTab] = useState("overview");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState({});
  
  // GitHub Universe
  const [repoUrl, setRepoUrl] = useState("");
  const [scanResult, setScanResult] = useState(null);
  
  // Cloud Deploy
  const [deployStatus, setDeployStatus] = useState(null);
  
  // Dev Environment
  const [envTemplates, setEnvTemplates] = useState({});
  const [selectedTemplate, setSelectedTemplate] = useState("node");
  
  // Asset Factory
  const [assetPipelines, setAssetPipelines] = useState({});
  const [assetPrompt, setAssetPrompt] = useState("");
  
  // Game Studio
  const [gameIdea, setGameIdea] = useState("");
  const [gameBuild, setGameBuild] = useState(null);
  
  // SaaS Factory
  const [saasIdea, setSaasIdea] = useState("");
  const [saasBuild, setSaasBuild] = useState(null);

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const [github, deploy, env, assets] = await Promise.all([
        axios.get(`${API}/github-universe/status`).catch(() => ({ data: {} })),
        axios.get(`${API}/cloud-deploy/status`).catch(() => ({ data: {} })),
        axios.get(`${API}/dev-env/templates`).catch(() => ({ data: {} })),
        axios.get(`${API}/asset-factory/pipelines`).catch(() => ({ data: {} }))
      ]);
      setStatus({
        github: github.data,
        deploy: deploy.data,
        env: env.data,
        assets: assets.data
      });
      setEnvTemplates(env.data);
      setAssetPipelines(assets.data);
    } catch (e) {
      console.error("Failed to fetch status", e);
    }
  };

  const scanRepository = async () => {
    if (!repoUrl) return toast.error("Enter a repository URL");
    setLoading(true);
    try {
      const res = await axios.post(`${API}/github-universe/scan?repo_url=${encodeURIComponent(repoUrl)}`);
      setScanResult(res.data);
      toast.success("Repository scanned!");
    } catch (e) {
      toast.error("Scan failed");
    }
    setLoading(false);
  };

  const instantDeploy = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/cloud-deploy/instant?project_id=${projectId}`);
      setDeployStatus(res.data);
      if (res.data.url) toast.success(`Deployed to ${res.data.url}`);
    } catch (e) {
      toast.error("Deployment failed");
    }
    setLoading(false);
  };

  const createDevEnv = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/dev-env/create?project_id=${projectId}&template=${selectedTemplate}`);
      toast.success(`Created ${res.data.template_name} environment!`);
    } catch (e) {
      toast.error("Failed to create environment");
    }
    setLoading(false);
  };

  const generateAsset = async (pipeline) => {
    if (!assetPrompt) return toast.error("Enter an asset description");
    setLoading(true);
    try {
      const res = await axios.post(`${API}/asset-factory/generate?project_id=${projectId}&pipeline=${pipeline}&prompt=${encodeURIComponent(assetPrompt)}`);
      toast.success(`Generated ${res.data.assets?.length || 0} assets!`);
    } catch (e) {
      toast.error("Asset generation failed");
    }
    setLoading(false);
  };

  const createGame = async () => {
    if (!gameIdea) return toast.error("Enter a game idea");
    setLoading(true);
    try {
      const res = await axios.post(`${API}/game-studio/create?idea=${encodeURIComponent(gameIdea)}&engine=unreal`);
      setGameBuild(res.data);
      toast.success(`Game "${res.data.title}" created!`);
    } catch (e) {
      toast.error("Game creation failed");
    }
    setLoading(false);
  };

  const createSaaS = async () => {
    if (!saasIdea) return toast.error("Enter a SaaS idea");
    setLoading(true);
    try {
      const res = await axios.post(`${API}/saas-factory/create?idea=${encodeURIComponent(saasIdea)}`);
      setSaasBuild(res.data);
      toast.success(`SaaS "${res.data.business_name}" created!`);
    } catch (e) {
      toast.error("SaaS creation failed");
    }
    setLoading(false);
  };

  const OS_FEATURES = [
    { id: "github", name: "GitHub Universe", icon: GitBranch, color: "text-purple-400", desc: "AI repository management" },
    { id: "deploy", name: "Cloud Deploy", icon: Cloud, color: "text-blue-400", desc: "Instant deployments" },
    { id: "devenv", name: "Dev Environment", icon: Terminal, color: "text-green-400", desc: "Containerized environments" },
    { id: "assets", name: "Asset Factory", icon: Palette, color: "text-pink-400", desc: "AI asset generation" },
    { id: "saas", name: "SaaS Factory", icon: Factory, color: "text-amber-400", desc: "One-prompt SaaS" },
    { id: "game", name: "Game Studio", icon: Gamepad2, color: "text-red-400", desc: "Autonomous game creation" }
  ];

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]" data-testid="os-features-panel">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800">
          <TabsList className="bg-zinc-900 p-1">
            <TabsTrigger value="overview" className="text-xs">Overview</TabsTrigger>
            <TabsTrigger value="github" className="text-xs">GitHub</TabsTrigger>
            <TabsTrigger value="deploy" className="text-xs">Deploy</TabsTrigger>
            <TabsTrigger value="devenv" className="text-xs">Dev Env</TabsTrigger>
            <TabsTrigger value="assets" className="text-xs">Assets</TabsTrigger>
            <TabsTrigger value="factory" className="text-xs">Factory</TabsTrigger>
          </TabsList>
        </div>

        <div className="flex-1 overflow-auto p-4">
          <TabsContent value="overview" className="m-0 space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Rocket className="w-5 h-5 text-cyan-400" />
              OS-Level Features
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {OS_FEATURES.map(f => (
                <div 
                  key={f.id}
                  onClick={() => setActiveTab(f.id === "saas" || f.id === "game" ? "factory" : f.id)}
                  className="p-4 bg-zinc-900 rounded-xl border border-zinc-800 hover:border-zinc-700 cursor-pointer transition-all"
                >
                  <f.icon className={`w-6 h-6 ${f.color} mb-2`} />
                  <h4 className="font-medium text-white text-sm">{f.name}</h4>
                  <p className="text-xs text-zinc-500 mt-1">{f.desc}</p>
                </div>
              ))}
            </div>
            
            <div className="p-4 bg-gradient-to-r from-cyan-900/30 to-purple-900/30 rounded-xl border border-cyan-800/30">
              <h4 className="font-medium text-white mb-2">System Status</h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${status.github?.connected ? 'bg-green-500' : 'bg-zinc-500'}`} />
                  <span className="text-zinc-400">GitHub: {status.github?.connected ? 'Connected' : 'Not connected'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${status.deploy?.vercel?.connected ? 'bg-green-500' : 'bg-zinc-500'}`} />
                  <span className="text-zinc-400">Vercel: {status.deploy?.vercel?.connected ? 'Connected' : 'Not connected'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  <span className="text-zinc-400">Dev Envs: {Object.keys(envTemplates).length} templates</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  <span className="text-zinc-400">Asset Pipelines: {Object.keys(assetPipelines).length}</span>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="github" className="m-0 space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <GitBranch className="w-5 h-5 text-purple-400" />
              GitHub Universe Control
            </h3>
            <p className="text-sm text-zinc-400">Scan repositories, learn patterns, auto-fix bugs, propose PRs.</p>
            
            <div className="space-y-3">
              <div className="flex gap-2">
                <Input 
                  placeholder="https://github.com/owner/repo"
                  value={repoUrl}
                  onChange={e => setRepoUrl(e.target.value)}
                  className="bg-zinc-900 border-zinc-700"
                />
                <Button onClick={scanRepository} disabled={loading}>
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Scan"}
                </Button>
              </div>
              
              {scanResult && (
                <div className="p-4 bg-zinc-900 rounded-lg space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-white">{scanResult.repo_info?.name || scanResult.repo}</span>
                    <Badge variant="outline" className="text-xs">{scanResult.status}</Badge>
                  </div>
                  <p className="text-sm text-zinc-400">{scanResult.repo_info?.description}</p>
                  <div className="flex gap-2 flex-wrap">
                    <Badge className="bg-blue-500/20 text-blue-400">{scanResult.file_count} files</Badge>
                    <Badge className="bg-amber-500/20 text-amber-400">{scanResult.repo_info?.stars} stars</Badge>
                    {scanResult.patterns_detected?.map((p, i) => (
                      <Badge key={i} className="bg-purple-500/20 text-purple-400">{p.pattern}</Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="deploy" className="m-0 space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Cloud className="w-5 h-5 text-blue-400" />
              Cloud Auto-Deployment
            </h3>
            <p className="text-sm text-zinc-400">Deploy this project instantly to Vercel or Cloudflare.</p>
            
            <div className="grid grid-cols-2 gap-3">
              <div className="p-4 bg-zinc-900 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <div className={`w-3 h-3 rounded-full ${status.deploy?.vercel?.connected ? 'bg-green-500' : 'bg-zinc-500'}`} />
                  <span className="font-medium text-white">Vercel</span>
                </div>
                <Button 
                  onClick={instantDeploy}
                  disabled={loading || !status.deploy?.vercel?.connected}
                  className="w-full"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Play className="w-4 h-4 mr-2" />}
                  Deploy Now
                </Button>
              </div>
              
              <div className="p-4 bg-zinc-900 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <div className={`w-3 h-3 rounded-full ${status.deploy?.cloudflare?.connected ? 'bg-green-500' : 'bg-zinc-500'}`} />
                  <span className="font-medium text-white">Cloudflare</span>
                </div>
                <Button variant="outline" disabled className="w-full">
                  Coming Soon
                </Button>
              </div>
            </div>
            
            {deployStatus && (
              <div className="p-4 bg-zinc-900 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-white">Deployment Status</span>
                  <Badge className={deployStatus.status === 'live' ? 'bg-green-500' : 'bg-amber-500'}>
                    {deployStatus.status}
                  </Badge>
                </div>
                {deployStatus.url && (
                  <a href={deployStatus.url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline text-sm">
                    {deployStatus.url}
                  </a>
                )}
              </div>
            )}
          </TabsContent>

          <TabsContent value="devenv" className="m-0 space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Terminal className="w-5 h-5 text-green-400" />
              Development Environments
            </h3>
            <p className="text-sm text-zinc-400">Create isolated Docker environments for your project.</p>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {Object.entries(envTemplates).map(([key, template]) => (
                <button
                  key={key}
                  onClick={() => setSelectedTemplate(key)}
                  className={`p-3 rounded-lg border transition-all ${
                    selectedTemplate === key 
                      ? 'bg-green-900/30 border-green-500' 
                      : 'bg-zinc-900 border-zinc-700 hover:border-zinc-600'
                  }`}
                >
                  <span className="font-medium text-white text-sm">{template.name}</span>
                  <p className="text-[10px] text-zinc-500 mt-1">{template.base_image}</p>
                </button>
              ))}
            </div>
            
            <Button onClick={createDevEnv} disabled={loading}>
              {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Terminal className="w-4 h-4 mr-2" />}
              Create {envTemplates[selectedTemplate]?.name} Environment
            </Button>
          </TabsContent>

          <TabsContent value="assets" className="m-0 space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Palette className="w-5 h-5 text-pink-400" />
              AI Asset Factory
            </h3>
            <p className="text-sm text-zinc-400">Generate UI kits, textures, icons, character art, and more.</p>
            
            <Input 
              placeholder="Describe the asset you want to generate..."
              value={assetPrompt}
              onChange={e => setAssetPrompt(e.target.value)}
              className="bg-zinc-900 border-zinc-700"
            />
            
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {Object.entries(assetPipelines).slice(0, 6).map(([key, pipeline]) => (
                <button
                  key={key}
                  onClick={() => generateAsset(key)}
                  disabled={loading}
                  className="p-3 bg-zinc-900 rounded-lg border border-zinc-700 hover:border-pink-500/50 transition-all text-left"
                >
                  <span className="font-medium text-white text-sm">{pipeline.name}</span>
                  <p className="text-[10px] text-zinc-500 mt-1">{pipeline.description}</p>
                </button>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="factory" className="m-0 space-y-6">
            <div className="space-y-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Factory className="w-5 h-5 text-amber-400" />
                Autonomous SaaS Factory
              </h3>
              <p className="text-sm text-zinc-400">One prompt → Complete SaaS with auth, payments, and deployment.</p>
              
              <div className="flex gap-2">
                <Input 
                  placeholder="Describe your SaaS idea..."
                  value={saasIdea}
                  onChange={e => setSaasIdea(e.target.value)}
                  className="bg-zinc-900 border-zinc-700"
                />
                <Button onClick={createSaaS} disabled={loading}>
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Create SaaS"}
                </Button>
              </div>
              
              {saasBuild && (
                <div className="p-4 bg-zinc-900 rounded-lg space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-white">{saasBuild.business_name}</span>
                    <Badge className="bg-amber-500/20 text-amber-400">{saasBuild.status}</Badge>
                  </div>
                  <p className="text-sm text-zinc-400">{saasBuild.plan?.tagline}</p>
                  <p className="text-xs text-zinc-500">{saasBuild.files?.length} files generated</p>
                </div>
              )}
            </div>

            <div className="border-t border-zinc-800 pt-6 space-y-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Gamepad2 className="w-5 h-5 text-red-400" />
                Autonomous Game Studio
              </h3>
              <p className="text-sm text-zinc-400">Game idea → Design doc → Code → Assets → Playable demo.</p>
              
              <div className="flex gap-2">
                <Input 
                  placeholder="Describe your game idea..."
                  value={gameIdea}
                  onChange={e => setGameIdea(e.target.value)}
                  className="bg-zinc-900 border-zinc-700"
                />
                <Button onClick={createGame} disabled={loading} className="bg-red-600 hover:bg-red-700">
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Create Game"}
                </Button>
              </div>
              
              {gameBuild && (
                <div className="p-4 bg-zinc-900 rounded-lg space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-white">{gameBuild.title}</span>
                    <Badge className="bg-red-500/20 text-red-400">{gameBuild.status}</Badge>
                  </div>
                  <p className="text-sm text-zinc-400">{gameBuild.design_doc?.tagline}</p>
                  <div className="flex gap-2 flex-wrap">
                    <Badge className="text-xs">{gameBuild.engine}</Badge>
                    <Badge className="text-xs">{gameBuild.systems?.length || 0} systems</Badge>
                    <Badge className="text-xs">{gameBuild.files?.length || 0} files</Badge>
                  </div>
                </div>
              )}
            </div>
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
};

export default OSFeaturesPanel;
