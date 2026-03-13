import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Server, Loader2, Plus, Play, Pause, CheckCircle, AlertTriangle, 
  Clock, Cpu, BarChart3
} from "lucide-react";
import { API } from "@/App";

const BuildFarmPanel = ({ projectId, projectName }) => {
  const [workers, setWorkers] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    fetchWorkers();
    fetchJobs();
    fetchStatus();
  }, []);

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
      await axios.post(`${API}/build-farm/jobs/add`, null, {
        params: { project_id: projectId, project_name: projectName, job_type: jobType, priority }
      });
      toast.success("Job added to build farm!");
      fetchJobs();
      fetchStatus();
    } catch (e) {
      toast.error("Failed to add job");
    } finally {
      setAdding(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "building": return "bg-amber-500";
      case "complete": return "bg-emerald-500";
      case "failed": return "bg-red-500";
      case "queued": return "bg-blue-500";
      default: return "bg-zinc-500";
    }
  };

  const getWorkerStatusColor = (status) => {
    switch (status) {
      case "building": return "text-amber-400 bg-amber-500/10";
      case "idle": return "text-emerald-400 bg-emerald-500/10";
      case "offline": return "text-red-400 bg-red-500/10";
      default: return "text-zinc-400 bg-zinc-500/10";
    }
  };

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]" data-testid="build-farm-panel">
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Server className="w-4 h-4 text-blue-400" />
            <span className="font-rajdhani font-bold text-white">Build Farm</span>
            {status && (
              <Badge variant="outline" className="text-xs border-zinc-700">
                {status.active_workers}/{status.total_workers} active
              </Badge>
            )}
          </div>
          <Button
            onClick={() => addJob("prototype", 5)}
            disabled={adding || !projectId}
            className="bg-blue-500 hover:bg-blue-600"
            data-testid="add-job-btn"
          >
            {adding ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Plus className="w-4 h-4 mr-1" />}
            Add to Farm
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1 p-4">
        {/* Farm Status */}
        {status && (
          <div className="grid grid-cols-4 gap-3 mb-6">
            <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800 text-center">
              <Server className="w-5 h-5 mx-auto mb-1 text-blue-400" />
              <p className="text-xl font-bold text-white">{status.total_workers}</p>
              <p className="text-xs text-zinc-500">Workers</p>
            </div>
            <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800 text-center">
              <Cpu className="w-5 h-5 mx-auto mb-1 text-amber-400" />
              <p className="text-xl font-bold text-white">{status.active_workers}</p>
              <p className="text-xs text-zinc-500">Active</p>
            </div>
            <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800 text-center">
              <Clock className="w-5 h-5 mx-auto mb-1 text-cyan-400" />
              <p className="text-xl font-bold text-white">{status.queued_jobs}</p>
              <p className="text-xs text-zinc-500">Queued</p>
            </div>
            <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800 text-center">
              <CheckCircle className="w-5 h-5 mx-auto mb-1 text-emerald-400" />
              <p className="text-xl font-bold text-white">{status.completed_jobs}</p>
              <p className="text-xs text-zinc-500">Complete</p>
            </div>
          </div>
        )}

        {/* Workers */}
        <div className="mb-6">
          <h4 className="text-sm font-medium text-white mb-3 flex items-center gap-2">
            <Server className="w-4 h-4 text-blue-400" /> Build Workers
          </h4>
          <div className="grid grid-cols-3 gap-3">
            {workers.map((worker) => (
              <div key={worker.id} className={`p-3 rounded-lg border border-zinc-800 ${getWorkerStatusColor(worker.status)}`}>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-sm">{worker.name}</span>
                  <Badge className={getStatusColor(worker.status)}>{worker.status}</Badge>
                </div>
                <div className="flex flex-wrap gap-1 mb-2">
                  {worker.capabilities?.map((cap, i) => (
                    <span key={i} className="text-xs px-1.5 py-0.5 rounded bg-zinc-800">{cap}</span>
                  ))}
                </div>
                <div className="text-xs text-zinc-500">
                  {worker.jobs_completed} jobs • {worker.success_rate}% success
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Job Queue */}
        <div>
          <h4 className="text-sm font-medium text-white mb-3 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-amber-400" /> Job Queue
          </h4>
          {jobs.length === 0 ? (
            <div className="text-center py-8 text-zinc-500">
              <Clock className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No jobs in queue</p>
            </div>
          ) : (
            <div className="space-y-2">
              {jobs.map((job) => (
                <div key={job.id} className="p-3 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-white">{job.project_name}</span>
                      <Badge className={getStatusColor(job.status)}>{job.status}</Badge>
                      <Badge variant="outline" className="text-xs border-zinc-700">P{job.priority}</Badge>
                    </div>
                    <p className="text-xs text-zinc-500 mt-1">
                      {job.job_type} • {job.assigned_worker ? `Worker: ${job.assigned_worker}` : 'Unassigned'}
                    </p>
                  </div>
                  {job.status === "building" && (
                    <div className="text-xs text-amber-400">
                      {Math.round(job.progress || 0)}%
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  );
};

export default BuildFarmPanel;
