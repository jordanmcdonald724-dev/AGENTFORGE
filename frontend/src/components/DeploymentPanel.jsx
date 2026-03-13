import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { 
  Rocket, Triangle, Train, Gamepad2, ExternalLink, 
  Loader2, CheckCircle, XCircle, Clock, Trash2
} from "lucide-react";
import { API } from "@/App";

const PLATFORM_ICONS = {
  vercel: Triangle,
  railway: Train,
  itch: Gamepad2
};

const PLATFORM_COLORS = {
  vercel: "zinc",
  railway: "purple",
  itch: "red"
};

const DeploymentPanel = ({ projectId, projectName }) => {
  const [platforms, setPlatforms] = useState([]);
  const [deployments, setDeployments] = useState([]);
  const [deploying, setDeploying] = useState(null);
  const [deployDialogOpen, setDeployDialogOpen] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState(null);
  
  const [credentials, setCredentials] = useState({
    vercel_token: "",
    railway_token: "",
    itch_api_key: "",
    itch_username: ""
  });
  
  const [newProjectName, setNewProjectName] = useState(projectName?.toLowerCase().replace(/\s+/g, '-') || "");

  useEffect(() => {
    fetchPlatforms();
    fetchDeployments();
  }, [projectId]);

  const fetchPlatforms = async () => {
    try {
      const res = await axios.get(`${API}/deploy/platforms`);
      setPlatforms(res.data);
    } catch (e) {}
  };

  const fetchDeployments = async () => {
    try {
      const res = await axios.get(`${API}/deploy/${projectId}`);
      setDeployments(res.data);
    } catch (e) {}
  };

  const deploy = async () => {
    if (!selectedPlatform || !newProjectName) return;
    
    setDeploying(selectedPlatform);
    try {
      let res;
      switch (selectedPlatform) {
        case "vercel":
          res = await axios.post(`${API}/deploy/${projectId}/vercel`, null, {
            params: {
              project_name: newProjectName,
              vercel_token: credentials.vercel_token
            }
          });
          break;
        case "railway":
          res = await axios.post(`${API}/deploy/${projectId}/railway`, null, {
            params: {
              project_name: newProjectName,
              railway_token: credentials.railway_token
            }
          });
          break;
        case "itch":
          res = await axios.post(`${API}/deploy/${projectId}/itch`, null, {
            params: {
              project_name: newProjectName,
              itch_api_key: credentials.itch_api_key,
              itch_username: credentials.itch_username
            }
          });
          break;
      }
      
      if (res.data.status === "live") {
        toast.success("Deployed successfully!");
      } else {
        toast.info("Deployment initiated");
      }
      
      fetchDeployments();
      setDeployDialogOpen(false);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Deployment failed");
    } finally {
      setDeploying(null);
    }
  };

  const deleteDeployment = async (deploymentId) => {
    await axios.delete(`${API}/deploy/${deploymentId}`);
    setDeployments(deployments.filter(d => d.id !== deploymentId));
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "live": return <CheckCircle className="w-4 h-4 text-emerald-400" />;
      case "failed": return <XCircle className="w-4 h-4 text-red-400" />;
      case "deploying": return <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />;
      default: return <Clock className="w-4 h-4 text-zinc-400" />;
    }
  };

  const openDeployDialog = (platformId) => {
    setSelectedPlatform(platformId);
    setDeployDialogOpen(true);
  };

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]">
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Rocket className="w-4 h-4 text-emerald-400" />
          <span className="font-rajdhani font-bold text-white">One-Click Deploy</span>
        </div>
      </div>

      <ScrollArea className="flex-1 p-4">
        <div className="space-y-6">
          {/* Platform Cards */}
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-zinc-400">Deploy to:</h4>
            {platforms.map((platform) => {
              const Icon = PLATFORM_ICONS[platform.id] || Rocket;
              const color = PLATFORM_COLORS[platform.id] || "zinc";
              const existingDeploy = deployments.find(d => d.platform === platform.id && d.status === "live");
              
              return (
                <div
                  key={platform.id}
                  className={`p-4 rounded-lg border transition-all ${
                    existingDeploy 
                      ? `bg-${color}-500/10 border-${color}-500/30` 
                      : 'bg-zinc-900/50 border-zinc-800 hover:border-zinc-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg bg-${color}-500/20`}>
                        <Icon className={`w-6 h-6 text-${color}-400`} />
                      </div>
                      <div>
                        <h5 className="font-medium text-white">{platform.name}</h5>
                        <p className="text-xs text-zinc-500">{platform.description}</p>
                      </div>
                    </div>
                    
                    {existingDeploy ? (
                      <div className="flex items-center gap-2">
                        <Badge className="bg-emerald-500/20 text-emerald-400">Live</Badge>
                        <a
                          href={existingDeploy.deploy_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-2 hover:bg-zinc-800 rounded"
                        >
                          <ExternalLink className="w-4 h-4 text-zinc-400" />
                        </a>
                      </div>
                    ) : (
                      <Button
                        size="sm"
                        className={`bg-${color}-500 hover:bg-${color}-600`}
                        onClick={() => openDeployDialog(platform.id)}
                      >
                        <Rocket className="w-4 h-4 mr-1" />Deploy
                      </Button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Deployment History */}
          {deployments.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-zinc-400 mb-3">Deployment History</h4>
              <div className="space-y-2">
                {deployments.map((deploy) => {
                  const Icon = PLATFORM_ICONS[deploy.platform] || Rocket;
                  return (
                    <div key={deploy.id} className="p-3 rounded bg-zinc-900/50 border border-zinc-800 group">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          {getStatusIcon(deploy.status)}
                          <Icon className="w-4 h-4 text-zinc-500" />
                          <div>
                            <span className="text-sm text-white">{deploy.project_name}</span>
                            <span className="text-xs text-zinc-500 ml-2">
                              {new Date(deploy.created_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {deploy.deploy_url && (
                            <a
                              href={deploy.deploy_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-blue-400 hover:underline"
                            >
                              {deploy.deploy_url}
                            </a>
                          )}
                          <button
                            onClick={() => deleteDeployment(deploy.id)}
                            className="p-1 opacity-0 group-hover:opacity-100 hover:bg-red-500/20 rounded"
                          >
                            <Trash2 className="w-3 h-3 text-red-400" />
                          </button>
                        </div>
                      </div>
                      {deploy.logs?.length > 0 && (
                        <p className="text-[10px] text-zinc-600 mt-2 truncate">
                          {deploy.logs[deploy.logs.length - 1]}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Deploy Dialog */}
      <Dialog open={deployDialogOpen} onOpenChange={setDeployDialogOpen}>
        <DialogContent className="bg-[#18181b] border-zinc-700">
          <DialogHeader>
            <DialogTitle className="font-rajdhani text-white flex items-center gap-2">
              <Rocket className="w-5 h-5 text-emerald-400" />
              Deploy to {selectedPlatform?.charAt(0).toUpperCase() + selectedPlatform?.slice(1)}
            </DialogTitle>
          </DialogHeader>
          <div className="py-4 space-y-4">
            <div>
              <label className="text-sm text-zinc-400 mb-2 block">Project Name</label>
              <Input
                value={newProjectName}
                onChange={(e) => setNewProjectName(e.target.value.toLowerCase().replace(/\s+/g, '-'))}
                className="bg-zinc-900 border-zinc-700"
                placeholder="my-project"
              />
            </div>

            {selectedPlatform === "vercel" && (
              <div>
                <label className="text-sm text-zinc-400 mb-2 block">Vercel Token</label>
                <Input
                  type="password"
                  value={credentials.vercel_token}
                  onChange={(e) => setCredentials({ ...credentials, vercel_token: e.target.value })}
                  className="bg-zinc-900 border-zinc-700"
                  placeholder="Get from vercel.com/account/tokens"
                />
              </div>
            )}

            {selectedPlatform === "railway" && (
              <div>
                <label className="text-sm text-zinc-400 mb-2 block">Railway Token</label>
                <Input
                  type="password"
                  value={credentials.railway_token}
                  onChange={(e) => setCredentials({ ...credentials, railway_token: e.target.value })}
                  className="bg-zinc-900 border-zinc-700"
                  placeholder="Get from railway.app/account/tokens"
                />
              </div>
            )}

            {selectedPlatform === "itch" && (
              <>
                <div>
                  <label className="text-sm text-zinc-400 mb-2 block">Itch.io Username</label>
                  <Input
                    value={credentials.itch_username}
                    onChange={(e) => setCredentials({ ...credentials, itch_username: e.target.value })}
                    className="bg-zinc-900 border-zinc-700"
                    placeholder="Your itch.io username"
                  />
                </div>
                <div>
                  <label className="text-sm text-zinc-400 mb-2 block">Itch.io API Key</label>
                  <Input
                    type="password"
                    value={credentials.itch_api_key}
                    onChange={(e) => setCredentials({ ...credentials, itch_api_key: e.target.value })}
                    className="bg-zinc-900 border-zinc-700"
                    placeholder="Get from itch.io/user/settings/api-keys"
                  />
                </div>
              </>
            )}
          </div>
          <DialogFooter>
            <Button
              onClick={deploy}
              disabled={deploying || !newProjectName}
              className="bg-emerald-500 hover:bg-emerald-600"
            >
              {deploying ? (
                <><Loader2 className="w-4 h-4 animate-spin mr-2" />Deploying...</>
              ) : (
                <><Rocket className="w-4 h-4 mr-2" />Deploy Now</>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DeploymentPanel;
