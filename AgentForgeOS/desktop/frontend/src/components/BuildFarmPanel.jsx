import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Server, Loader2, Plus, Play, Pause, CheckCircle, AlertTriangle, 
  Clock, Cpu, BarChart3, X, RefreshCw, Trash2, Zap
} from "lucide-react";
import { API } from "@/App";

const BuildFarmPanel = ({ projectId, projectName }) => {
  const [workers, setWorkers] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [adding, setAdding] = useState(false);
  const [selectedJobType, setSelectedJobType] = useState("prototype");
  const pollRef = useRef(null);

  useEffect(() => {
    fetchAll();
    // Poll for updates every 2 seconds
    pollRef.current = setInterval(fetchAll, 2000);
    return () => clearInterval(pollRef.current);
  }, []);

  const fetchAll = async () => {
    await Promise.all([fetchWorkers(), fetchJobs(), fetchStatus()]);
  };

  const fetchWorkers = async () => {
    try {
      const res = await axios.get(`${API}/build-farm/workers`);
      setWorkers(res.data || []);
    } catch (e) {}
  };

  const fetchJobs = async () => {
    try {
      const res = await axios.get(`${API}/build-farm/jobs`);
      setJobs(res.data || []);
    } catch (e) {}
  };

  const fetchStatus = async () => {
    try {
      const res = await axios.get(`${API}/build-farm/status`);
      setStatus(res.data);
    } catch (e) {}
  };

  const addJob = async (jobType = "prototype", priority = 5) => {
    if (!projectId || !projectName) {
      toast.error("No project selected");
      return;
    }
    setAdding(true);
    try {
      const res = await axios.post(`${API}/build-farm/jobs/add`, null, {
        params: { project_id: projectId, project_name: projectName, job_type: jobType, priority }
      });
      toast.success("Job added to build farm!");
      fetchAll();
    } catch (e) {
      toast.error("Failed to add job");
    } finally {
      setAdding(false);
    }
  };

  const startJob = async (jobId) => {
    try {
      await axios.post(`${API}/build-farm/jobs/${jobId}/start`);
      toast.success("Build started!");
      fetchAll();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Failed to start job");
    }
  };

  const cancelJob = async (jobId) => {
    try {
      await axios.post(`${API}/build-farm/jobs/${jobId}/cancel`);
      toast.info("Job cancelled");
      fetchAll();
    } catch (e) {
      toast.error("Failed to cancel job");
    }
  };

  const pauseWorker = async (workerId) => {
    await axios.post(`${API}/build-farm/workers/${workerId}/pause`);
    fetchWorkers();
  };

  const resumeWorker = async (workerId) => {
    await axios.post(`${API}/build-farm/workers/${workerId}/resume`);
    fetchWorkers();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "building": return "bg-amber-500";
      case "complete": return "bg-emerald-500";
      case "failed": return "bg-red-500";
      case "queued": return "bg-blue-500";
      case "cancelled": return "bg-zinc-500";
      default: return "bg-zinc-500";
    }
  };

  const getWorkerStatusColor = (status) => {
    switch (status) {
      case "building": return "text-amber-400 bg-amber-500/10 border-amber-500/30";
      case "idle": return "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
      case "paused": return "text-zinc-400 bg-zinc-500/10 border-zinc-500/30";
      case "error": return "text-red-400 bg-red-500/10 border-red-500/30";
      default: return "text-zinc-400 bg-zinc-500/10 border-zinc-500/30";
    }
  };

  const JOB_TYPES = [
    { id: "prototype", name: "Prototype", time: "~2min" },
    { id: "full_build", name: "Full Build", time: "~10min" },
    { id: "demo", name: "Demo", time: "~5min" },
    { id: "code_gen", name: "Code Gen", time: "~1min" },
    { id: "test_suite", name: "Test Suite", time: "~2min" }
  ];

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]" data-testid="build-farm-panel">
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Server className="w-4 h-4 text-blue-400" />
            <span className="font-rajdhani font-bold text-white">Distributed Build Farm</span>
            {status && (
              <Badge variant="outline" className="text-xs border-zinc-700">
                {status.active_workers}/{status.total_workers} active
              </Badge>
            )}
          </div>
          <Button
            size="sm"
            variant="ghost"
            onClick={fetchAll}
            className="h-8"
          >
            <RefreshCw className="w-3 h-3" />
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1 p-4">
        {/* Farm Status Overview */}
        {status && (
          <div className="grid grid-cols-5 gap-2 mb-4">
            <div className="p-2 rounded-lg bg-zinc-900 border border-zinc-800 text-center">
              <Server className="w-4 h-4 mx-auto mb-1 text-blue-400" />
              <p className="text-lg font-bold text-white">{status.total_workers}</p>
              <p className="text-[10px] text-zinc-500">Workers</p>
            </div>
            <div className="p-2 rounded-lg bg-zinc-900 border border-zinc-800 text-center">
              <Cpu className="w-4 h-4 mx-auto mb-1 text-amber-400" />
              <p className="text-lg font-bold text-white">{status.active_workers}</p>
              <p className="text-[10px] text-zinc-500">Building</p>
            </div>
            <div className="p-2 rounded-lg bg-zinc-900 border border-zinc-800 text-center">
              <Clock className="w-4 h-4 mx-auto mb-1 text-cyan-400" />
              <p className="text-lg font-bold text-white">{status.queued_jobs}</p>
              <p className="text-[10px] text-zinc-500">Queued</p>
            </div>
            <div className="p-2 rounded-lg bg-zinc-900 border border-zinc-800 text-center">
              <CheckCircle className="w-4 h-4 mx-auto mb-1 text-emerald-400" />
              <p className="text-lg font-bold text-white">{status.completed_jobs}</p>
              <p className="text-[10px] text-zinc-500">Complete</p>
            </div>
            <div className="p-2 rounded-lg bg-zinc-900 border border-zinc-800 text-center">
              <AlertTriangle className="w-4 h-4 mx-auto mb-1 text-red-400" />
              <p className="text-lg font-bold text-white">{status.failed_jobs || 0}</p>
              <p className="text-[10px] text-zinc-500">Failed</p>
            </div>
          </div>
        )}

        {/* Add Job Section */}
        <div className="mb-4 p-3 rounded-lg bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-medium text-white">Add Build Job</span>
          </div>
          <div className="flex gap-2 flex-wrap mb-2">
            {JOB_TYPES.map(type => (
              <button
                key={type.id}
                onClick={() => setSelectedJobType(type.id)}
                className={`px-2 py-1 text-xs rounded border transition-colors ${
                  selectedJobType === type.id 
                    ? 'bg-blue-500 border-blue-500 text-white' 
                    : 'bg-zinc-800 border-zinc-700 text-zinc-400 hover:border-zinc-600'
                }`}
              >
                {type.name} <span className="text-[10px] opacity-70">{type.time}</span>
              </button>
            ))}
          </div>
          <Button
            onClick={() => addJob(selectedJobType, 5)}
            disabled={adding || !projectId}
            className="w-full bg-blue-500 hover:bg-blue-600"
            size="sm"
            data-testid="add-job-btn"
          >
            {adding ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Plus className="w-4 h-4 mr-1" />}
            Queue {JOB_TYPES.find(t => t.id === selectedJobType)?.name || 'Build'}
          </Button>
        </div>

        {/* Active Builds */}
        {status?.active_builds?.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-white mb-2 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-amber-400" /> Active Builds
            </h4>
            <div className="space-y-2">
              {status.active_builds.map((build) => (
                <div key={build.job_id} className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/30">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-white font-medium">{build.project_name}</span>
                    <span className="text-xs text-amber-400">{Math.round(build.progress)}%</span>
                  </div>
                  <Progress value={build.progress} className="h-2 mb-1" />
                  <p className="text-[10px] text-zinc-500">{build.stage}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Workers Grid */}
        <div className="mb-4">
          <h4 className="text-sm font-medium text-white mb-2 flex items-center gap-2">
            <Server className="w-4 h-4 text-blue-400" /> Workers ({workers.length})
          </h4>
          <div className="grid grid-cols-2 gap-2">
            {workers.map((worker) => (
              <div key={worker.id} className={`p-3 rounded-lg border ${getWorkerStatusColor(worker.status)}`}>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-sm">{worker.name}</span>
                  <div className="flex items-center gap-1">
                    <Badge className={`text-[10px] ${getStatusColor(worker.status)}`}>{worker.status}</Badge>
                    {worker.status === "idle" && (
                      <button onClick={() => pauseWorker(worker.id)} className="p-1 hover:bg-zinc-700 rounded">
                        <Pause className="w-3 h-3" />
                      </button>
                    )}
                    {worker.status === "paused" && (
                      <button onClick={() => resumeWorker(worker.id)} className="p-1 hover:bg-zinc-700 rounded">
                        <Play className="w-3 h-3" />
                      </button>
                    )}
                  </div>
                </div>
                <div className="flex flex-wrap gap-1 mb-1">
                  {worker.capabilities?.slice(0, 3).map((cap, i) => (
                    <span key={i} className="text-[10px] px-1 py-0.5 rounded bg-zinc-800">{cap}</span>
                  ))}
                </div>
                <div className="text-[10px] text-zinc-500">
                  {worker.jobs_completed || 0} jobs • {worker.success_rate || 100}%
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Job Queue */}
        <div>
          <h4 className="text-sm font-medium text-white mb-2 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-purple-400" /> Job Queue ({jobs.length})
          </h4>
          {jobs.length === 0 ? (
            <div className="text-center py-6 text-zinc-500 bg-zinc-900/50 rounded-lg border border-zinc-800">
              <Clock className="w-6 h-6 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No jobs in queue</p>
              <p className="text-xs">Add a build job to get started</p>
            </div>
          ) : (
            <div className="space-y-2">
              {jobs.slice(0, 10).map((job) => (
                <div key={job.id} className="p-3 rounded-lg bg-zinc-900 border border-zinc-800">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm text-white">{job.project_name}</span>
                        <Badge className={`text-[10px] ${getStatusColor(job.status)}`}>{job.status}</Badge>
                        <Badge variant="outline" className="text-[10px] border-zinc-700">P{job.priority}</Badge>
                      </div>
                      <p className="text-[10px] text-zinc-500">
                        {job.job_type} • {job.current_stage || (job.assigned_worker ? `Worker: ${job.assigned_worker}` : 'Waiting')}
                      </p>
                      {job.status === "building" && (
                        <Progress value={job.progress || 0} className="h-1 mt-2" />
                      )}
                    </div>
                    <div className="flex items-center gap-1 ml-2">
                      {job.status === "queued" && (
                        <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => startJob(job.id)}>
                          <Play className="w-3 h-3 text-emerald-400" />
                        </Button>
                      )}
                      {["queued", "building"].includes(job.status) && (
                        <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => cancelJob(job.id)}>
                          <X className="w-3 h-3 text-red-400" />
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Queue Wait Time */}
        {status?.queue_wait_minutes > 0 && (
          <div className="mt-4 p-2 rounded bg-zinc-900/50 border border-zinc-800 text-center">
            <p className="text-xs text-zinc-500">
              Estimated queue wait: <span className="text-cyan-400">{status.queue_wait_minutes} min</span>
            </p>
          </div>
        )}
      </ScrollArea>
    </div>
  );
};

export default BuildFarmPanel;
