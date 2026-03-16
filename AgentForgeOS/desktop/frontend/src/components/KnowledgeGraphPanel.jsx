import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Brain, Plus, Search, TrendingUp, Code, Star, RefreshCw, Loader2,
  Database, Shield, Layout, Server, GitBranch
} from "lucide-react";
import { API } from "@/App";

const CATEGORY_ICONS = {
  auth: Shield,
  api: Server,
  database: Database,
  ui: Layout,
  game: GitBranch,
  general: Code
};

const KnowledgeGraphPanel = ({ projectId }) => {
  const [entries, setEntries] = useState([]);
  const [stats, setStats] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [extracting, setExtracting] = useState(false);

  useEffect(() => {
    fetchEntries();
    fetchStats();
  }, []);

  const fetchEntries = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/knowledge/all`);
      setEntries(res.data || []);
    } catch (e) {}
    finally { setLoading(false); }
  };

  const fetchStats = async () => {
    try {
      const res = await axios.get(`${API}/knowledge/stats`);
      setStats(res.data);
    } catch (e) {}
  };

  const searchKnowledge = async () => {
    if (!searchQuery.trim()) {
      fetchEntries();
      return;
    }
    setLoading(true);
    try {
      const res = await axios.get(`${API}/knowledge/search`, {
        params: { query: searchQuery }
      });
      setEntries(res.data || []);
    } catch (e) {}
    finally { setLoading(false); }
  };

  const extractFromProject = async () => {
    if (!projectId) {
      toast.error("No project selected");
      return;
    }
    setExtracting(true);
    try {
      const res = await axios.post(`${API}/knowledge/extract/${projectId}`);
      toast.success(`Extracted ${res.data.count} patterns!`);
      fetchEntries();
      fetchStats();
    } catch (e) {
      toast.error("Extraction failed");
    } finally {
      setExtracting(false);
    }
  };

  const filteredEntries = entries.filter(e => 
    !searchQuery || 
    e.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    e.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]" data-testid="knowledge-graph-panel">
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="w-4 h-4 text-pink-400" />
            <span className="font-rajdhani font-bold text-white">Global Knowledge Graph</span>
            {stats && (
              <Badge variant="outline" className="text-xs border-zinc-700">
                {stats.total_entries} patterns • {stats.total_reuses} reuses
              </Badge>
            )}
          </div>
          <Button
            onClick={extractFromProject}
            disabled={extracting || !projectId}
            variant="outline"
            size="sm"
            className="border-pink-500/30 text-pink-400"
            data-testid="extract-knowledge-btn"
          >
            {extracting ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <RefreshCw className="w-4 h-4 mr-1" />}
            Extract Patterns
          </Button>
        </div>
      </div>

      {/* Search */}
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
            <Input
              placeholder="Search patterns, solutions, components..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && searchKnowledge()}
              className="pl-9 bg-zinc-900 border-zinc-700"
            />
          </div>
          <Button onClick={searchKnowledge} variant="outline" className="border-zinc-700">
            <Search className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800">
          <div className="flex gap-3 overflow-x-auto">
            {Object.entries(stats.by_category || {}).map(([cat, count]) => {
              const Icon = CATEGORY_ICONS[cat] || Code;
              return (
                <div key={cat} className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-zinc-900 border border-zinc-800">
                  <Icon className="w-3 h-3 text-pink-400" />
                  <span className="text-xs text-zinc-400">{cat}</span>
                  <Badge variant="secondary" className="text-xs">{count}</Badge>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <ScrollArea className="flex-1 p-4">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-zinc-500" />
          </div>
        ) : filteredEntries.length === 0 ? (
          <div className="text-center py-12">
            <Brain className="w-12 h-12 mx-auto mb-4 text-zinc-700" />
            <h3 className="font-rajdhani text-lg text-white mb-2">Cross-Project Intelligence</h3>
            <p className="text-sm text-zinc-500 mb-4">
              Patterns and solutions learned from all projects
            </p>
            <p className="text-xs text-zinc-600">
              Click "Extract Patterns" to learn from current project
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredEntries.map((entry) => {
              const Icon = CATEGORY_ICONS[entry.category] || Code;
              return (
                <div key={entry.id} className="p-4 rounded-lg bg-zinc-900 border border-zinc-800 hover:border-zinc-700">
                  <div className="flex items-start gap-3">
                    <div className="p-2 rounded-lg bg-pink-500/10">
                      <Icon className="w-4 h-4 text-pink-400" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium text-white">{entry.title}</h4>
                        <Badge variant="outline" className="text-xs border-zinc-700">{entry.entry_type}</Badge>
                      </div>
                      <p className="text-sm text-zinc-500 mb-2">{entry.description}</p>
                      <div className="flex flex-wrap gap-1 mb-2">
                        {entry.tags?.map((tag, i) => (
                          <span key={i} className="text-xs px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400">{tag}</span>
                        ))}
                      </div>
                      <div className="flex items-center gap-4 text-xs text-zinc-600">
                        <span className="flex items-center gap-1">
                          <TrendingUp className="w-3 h-3" /> {entry.reuse_count || 0} reuses
                        </span>
                        <span className="flex items-center gap-1">
                          <Star className="w-3 h-3" /> {entry.success_count || 0} successes
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </ScrollArea>
    </div>
  );
};

export default KnowledgeGraphPanel;
