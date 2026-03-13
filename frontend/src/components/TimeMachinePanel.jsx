import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { 
  History, Plus, RotateCcw, Trash2, GitCompare, Loader2, Save, Clock, FileCode
} from "lucide-react";
import { API } from "@/App";

const TimeMachinePanel = ({ projectId }) => {
  const [checkpoints, setCheckpoints] = useState([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [restoring, setRestoring] = useState(null);
  
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newCheckpoint, setNewCheckpoint] = useState({ name: "", description: "" });

  useEffect(() => {
    fetchCheckpoints();
  }, [projectId]);

  const fetchCheckpoints = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/checkpoints/${projectId}`);
      setCheckpoints(res.data || []);
    } catch (e) {}
    finally { setLoading(false); }
  };

  const createCheckpoint = async () => {
    if (!newCheckpoint.name) {
      toast.error("Name required");
      return;
    }
    setCreating(true);
    try {
      await axios.post(`${API}/checkpoints/${projectId}/create`, null, {
        params: { name: newCheckpoint.name, description: newCheckpoint.description }
      });
      toast.success("Checkpoint created!");
      setCreateDialogOpen(false);
      setNewCheckpoint({ name: "", description: "" });
      fetchCheckpoints();
    } catch (e) {
      toast.error("Failed to create checkpoint");
    } finally {
      setCreating(false);
    }
  };

  const restoreCheckpoint = async (checkpointId, name) => {
    setRestoring(checkpointId);
    try {
      const res = await axios.post(`${API}/checkpoints/${checkpointId}/restore`);
      toast.success(`Restored to: ${name}`);
      fetchCheckpoints();
    } catch (e) {
      toast.error("Restore failed");
    } finally {
      setRestoring(null);
    }
  };

  const deleteCheckpoint = async (checkpointId) => {
    try {
      await axios.delete(`${API}/checkpoints/${checkpointId}`);
      toast.success("Checkpoint deleted");
      fetchCheckpoints();
    } catch (e) {
      toast.error("Delete failed");
    }
  };

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]" data-testid="time-machine-panel">
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-purple-400" />
            <span className="font-rajdhani font-bold text-white">Time Machine</span>
            <Badge variant="outline" className="text-xs border-zinc-700">
              {checkpoints.length} checkpoints
            </Badge>
          </div>
          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button className="bg-purple-500 hover:bg-purple-600" data-testid="create-checkpoint-btn">
                <Plus className="w-4 h-4 mr-1" />Save Checkpoint
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-[#18181b] border-zinc-700">
              <DialogHeader>
                <DialogTitle className="font-rajdhani text-white flex items-center gap-2">
                  <Save className="w-5 h-5 text-purple-400" />Create Checkpoint
                </DialogTitle>
              </DialogHeader>
              <div className="py-4 space-y-4">
                <Input
                  placeholder="Checkpoint name (e.g., 'Before refactor')"
                  value={newCheckpoint.name}
                  onChange={(e) => setNewCheckpoint({ ...newCheckpoint, name: e.target.value })}
                  className="bg-zinc-900 border-zinc-700"
                />
                <Input
                  placeholder="Description (optional)"
                  value={newCheckpoint.description}
                  onChange={(e) => setNewCheckpoint({ ...newCheckpoint, description: e.target.value })}
                  className="bg-zinc-900 border-zinc-700"
                />
              </div>
              <DialogFooter>
                <Button onClick={createCheckpoint} disabled={creating} className="bg-purple-500 hover:bg-purple-600">
                  {creating ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Save className="w-4 h-4 mr-1" />}
                  Create Checkpoint
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <ScrollArea className="flex-1 p-4">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-zinc-500" />
          </div>
        ) : checkpoints.length === 0 ? (
          <div className="text-center py-12">
            <History className="w-12 h-12 mx-auto mb-4 text-zinc-700" />
            <h3 className="font-rajdhani text-lg text-white mb-2">No Checkpoints</h3>
            <p className="text-sm text-zinc-500 mb-4">
              Save checkpoints to travel back in time
            </p>
          </div>
        ) : (
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-zinc-800" />
            
            <div className="space-y-4">
              {checkpoints.map((cp, i) => (
                <div key={cp.id} className="relative pl-10">
                  {/* Timeline dot */}
                  <div className={`absolute left-2.5 w-3 h-3 rounded-full ${i === 0 ? 'bg-purple-500' : 'bg-zinc-600'} ring-4 ring-[#0a0a0c]`} />
                  
                  <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800 hover:border-zinc-700">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="font-medium text-white">{cp.name}</h4>
                          <Badge variant="outline" className="text-xs border-zinc-700">
                            Step {cp.step_number}
                          </Badge>
                          {cp.auto_created && (
                            <Badge variant="outline" className="text-xs border-amber-500/30 text-amber-400">
                              Auto
                            </Badge>
                          )}
                        </div>
                        {cp.description && (
                          <p className="text-sm text-zinc-500 mt-1">{cp.description}</p>
                        )}
                        <div className="flex items-center gap-3 mt-2 text-xs text-zinc-600">
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {new Date(cp.created_at).toLocaleString()}
                          </span>
                          <span className="flex items-center gap-1">
                            <FileCode className="w-3 h-3" />
                            {cp.files_snapshot?.length || '?'} files
                          </span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          onClick={() => restoreCheckpoint(cp.id, cp.name)}
                          disabled={restoring === cp.id}
                          variant="outline"
                          size="sm"
                          className="border-purple-500/30 text-purple-400 hover:bg-purple-500/10"
                        >
                          {restoring === cp.id ? (
                            <Loader2 className="w-3 h-3 animate-spin" />
                          ) : (
                            <RotateCcw className="w-3 h-3" />
                          )}
                        </Button>
                        <Button
                          onClick={() => deleteCheckpoint(cp.id)}
                          variant="outline"
                          size="sm"
                          className="border-red-500/30 text-red-400 hover:bg-red-500/10"
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </ScrollArea>
    </div>
  );
};

export default TimeMachinePanel;
