import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { 
  AppWindow, Globe, Gamepad2, Server, Smartphone,
  Plus, Trash2, Play, Clock, Loader2, CheckCircle, XCircle,
  Calendar
} from "lucide-react";
import { API } from "@/App";

const CATEGORY_ICONS = {
  app: AppWindow,
  webpage: Globe,
  game: Gamepad2,
  api: Server,
  mobile: Smartphone
};

const CATEGORY_COLORS = {
  app: "blue",
  webpage: "cyan",
  game: "purple",
  api: "emerald",
  mobile: "amber"
};

const BuildQueuePanel = ({ projectId, onBuildStart }) => {
  const [queue, setQueue] = useState({});
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [scheduleTime, setScheduleTime] = useState("");
  const [addingBuild, setAddingBuild] = useState(false);

  useEffect(() => {
    fetchQueue();
    fetchCategories();
  }, [projectId]);

  const fetchQueue = async () => {
    try {
      const res = await axios.get(`${API}/build-queue/${projectId}`);
      setQueue(res.data);
    } catch (e) {} 
    finally { setLoading(false); }
  };

  const fetchCategories = async () => {
    try {
      const res = await axios.get(`${API}/build-queue/categories`);
      setCategories(res.data);
    } catch (e) {}
  };

  const addToQueue = async () => {
    if (!selectedCategory) {
      toast.error("Select a category");
      return;
    }
    setAddingBuild(true);
    try {
      await axios.post(`${API}/build-queue/add`, null, {
        params: {
          project_id: projectId,
          category: selectedCategory,
          scheduled_at: scheduleTime || undefined
        }
      });
      toast.success(`Added ${selectedCategory} to build queue`);
      setAddDialogOpen(false);
      setSelectedCategory(null);
      setScheduleTime("");
      fetchQueue();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to add to queue");
    } finally {
      setAddingBuild(false);
    }
  };

  const removeFromQueue = async (itemId) => {
    try {
      await axios.delete(`${API}/build-queue/${itemId}`);
      toast.info("Removed from queue");
      fetchQueue();
    } catch (e) {
      toast.error("Failed to remove");
    }
  };

  const startBuild = async (itemId) => {
    try {
      const res = await axios.post(`${API}/build-queue/${itemId}/start`);
      toast.success("Build started!");
      fetchQueue();
      onBuildStart?.(res.data.build_id);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to start build");
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'queued': return <Clock className="w-4 h-4 text-zinc-400" />;
      case 'building': return <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />;
      case 'completed': return <CheckCircle className="w-4 h-4 text-emerald-400" />;
      case 'failed': return <XCircle className="w-4 h-4 text-red-400" />;
      default: return null;
    }
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]">
      {/* Header */}
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-purple-400" />
          <span className="font-rajdhani font-bold text-white">Build Queue</span>
          <Badge variant="outline" className="text-xs border-zinc-700 text-zinc-400">
            1 per category
          </Badge>
        </div>
        <Dialog open={addDialogOpen} onOpenChange={setAddDialogOpen}>
          <DialogTrigger asChild>
            <Button size="sm" className="bg-purple-500 hover:bg-purple-600">
              <Plus className="w-4 h-4 mr-1" />Add Build
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-[#18181b] border-zinc-700">
            <DialogHeader>
              <DialogTitle className="font-rajdhani text-white">Add to Build Queue</DialogTitle>
            </DialogHeader>
            <div className="py-4 space-y-4">
              <div>
                <label className="text-sm text-zinc-400 mb-2 block">Select Category</label>
                <div className="grid grid-cols-5 gap-2">
                  {categories.map((cat) => {
                    const Icon = CATEGORY_ICONS[cat.id] || AppWindow;
                    const isDisabled = queue[cat.id]?.has_build;
                    const isSelected = selectedCategory === cat.id;
                    return (
                      <button
                        key={cat.id}
                        onClick={() => !isDisabled && setSelectedCategory(cat.id)}
                        disabled={isDisabled}
                        className={`p-3 rounded-lg border text-center transition-all ${
                          isDisabled 
                            ? 'bg-zinc-900 border-zinc-800 opacity-50 cursor-not-allowed' 
                            : isSelected 
                              ? `bg-${CATEGORY_COLORS[cat.id]}-500/20 border-${CATEGORY_COLORS[cat.id]}-500/50` 
                              : 'bg-zinc-900 border-zinc-700 hover:border-zinc-600'
                        }`}
                      >
                        <Icon className={`w-6 h-6 mx-auto mb-1 ${isSelected ? `text-${CATEGORY_COLORS[cat.id]}-400` : 'text-zinc-500'}`} />
                        <span className={`text-xs ${isSelected ? 'text-white' : 'text-zinc-400'}`}>{cat.name}</span>
                        {isDisabled && <Badge className="mt-1 text-[8px] bg-amber-500/20 text-amber-400">In Queue</Badge>}
                      </button>
                    );
                  })}
                </div>
              </div>
              <div>
                <label className="text-sm text-zinc-400 mb-2 block">Schedule (optional)</label>
                <Input
                  type="datetime-local"
                  value={scheduleTime}
                  onChange={(e) => setScheduleTime(e.target.value)}
                  className="bg-zinc-900 border-zinc-700"
                />
                <p className="text-[10px] text-zinc-600 mt-1">Leave empty to add without scheduling</p>
              </div>
            </div>
            <DialogFooter>
              <Button onClick={addToQueue} disabled={!selectedCategory || addingBuild} className="bg-purple-500 hover:bg-purple-600">
                {addingBuild ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Plus className="w-4 h-4 mr-2" />}
                Add to Queue
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Queue by Category */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {Object.entries(queue).map(([catId, catData]) => {
            const Icon = CATEGORY_ICONS[catId] || AppWindow;
            const color = CATEGORY_COLORS[catId] || "zinc";
            const hasItems = catData.items?.length > 0;

            return (
              <div key={catId} className={`rounded-lg border ${hasItems ? `border-${color}-500/30 bg-${color}-500/5` : 'border-zinc-800 bg-zinc-900/30'}`}>
                <div className="px-4 py-3 flex items-center justify-between border-b border-zinc-800/50">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg bg-${color}-500/20`}>
                      <Icon className={`w-5 h-5 text-${color}-400`} />
                    </div>
                    <div>
                      <h4 className="font-rajdhani font-bold text-white">{catData.name}</h4>
                      <p className="text-[10px] text-zinc-500">{catData.description}</p>
                    </div>
                  </div>
                  {!hasItems && (
                    <Badge variant="outline" className="border-zinc-700 text-zinc-500">Empty</Badge>
                  )}
                </div>

                {hasItems && (
                  <div className="p-3">
                    <AnimatePresence>
                      {catData.items.map((item) => (
                        <motion.div
                          key={item.id}
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          className="flex items-center justify-between p-3 rounded bg-zinc-800/50"
                        >
                          <div className="flex items-center gap-3">
                            {getStatusIcon(item.status)}
                            <div>
                              <p className="text-sm text-white font-medium">
                                {item.status === 'queued' ? 'Ready to build' : item.status}
                              </p>
                              {item.scheduled_at && (
                                <p className="text-[10px] text-zinc-500">
                                  <Clock className="w-3 h-3 inline mr-1" />
                                  {new Date(item.scheduled_at).toLocaleString()}
                                </p>
                              )}
                            </div>
                          </div>
                          <div className="flex gap-2">
                            {item.status === 'queued' && (
                              <>
                                <Button
                                  size="sm"
                                  className="h-7 bg-emerald-500 hover:bg-emerald-600"
                                  onClick={() => startBuild(item.id)}
                                >
                                  <Play className="w-3 h-3 mr-1" />Start
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-7 w-7 hover:bg-red-500/20"
                                  onClick={() => removeFromQueue(item.id)}
                                >
                                  <Trash2 className="w-3 h-3 text-red-400" />
                                </Button>
                              </>
                            )}
                          </div>
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </ScrollArea>
    </div>
  );
};

export default BuildQueuePanel;
