import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  Lightbulb, Sparkles, Rocket, Gamepad2, Globe, Code, Smartphone, Loader2, Plus, ArrowRight
} from "lucide-react";
import { API } from "@/App";

const CATEGORY_ICONS = {
  game: Gamepad2,
  saas: Globe,
  tool: Code,
  website: Globe,
  mobile: Smartphone
};

const COMPLEXITY_COLORS = {
  simple: "bg-emerald-500",
  medium: "bg-amber-500",
  complex: "bg-red-500",
  massive: "bg-purple-500"
};

const IdeaEnginePanel = ({ onBuildIdea }) => {
  const [prompt, setPrompt] = useState("");
  const [category, setCategory] = useState("game");
  const [count, setCount] = useState(5);
  const [batch, setBatch] = useState(null);
  const [batches, setBatches] = useState([]);
  const [generating, setGenerating] = useState(false);
  const [building, setBuilding] = useState(null);

  useEffect(() => {
    fetchBatches();
  }, []);

  const fetchBatches = async () => {
    try {
      const res = await axios.get(`${API}/ideas/batches`);
      setBatches(res.data || []);
    } catch (e) {}
  };

  const generateIdeas = async () => {
    if (!prompt) {
      toast.error("Enter a prompt");
      return;
    }
    setGenerating(true);
    try {
      const res = await axios.post(`${API}/ideas/generate`, null, {
        params: { prompt, category, count }
      });
      setBatch(res.data);
      toast.success(`Generated ${res.data.ideas?.length} ideas!`);
      fetchBatches();
    } catch (e) {
      toast.error("Generation failed");
    } finally {
      setGenerating(false);
    }
  };

  const buildIdea = async (ideaId) => {
    setBuilding(ideaId);
    try {
      const res = await axios.post(`${API}/ideas/${ideaId}/build`);
      toast.success(`Project created: ${res.data.project_name}`);
      if (onBuildIdea) onBuildIdea(res.data.project_id);
    } catch (e) {
      toast.error("Failed to build idea");
    } finally {
      setBuilding(null);
    }
  };

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]" data-testid="idea-engine-panel">
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Lightbulb className="w-4 h-4 text-amber-400" />
          <span className="font-rajdhani font-bold text-white">Idea Engine</span>
          <Badge variant="outline" className="text-xs border-zinc-700">AI-Powered</Badge>
        </div>
      </div>

      {/* Generator */}
      <div className="flex-shrink-0 px-4 py-4 border-b border-zinc-800 space-y-3">
        <Input
          placeholder="Describe your idea... (e.g., 'AI marketing assistant for small businesses')"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="bg-zinc-900 border-zinc-700"
          data-testid="idea-prompt"
        />
        <div className="flex gap-2">
          <Select value={category} onValueChange={setCategory}>
            <SelectTrigger className="w-32 bg-zinc-900 border-zinc-700">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-zinc-900 border-zinc-700">
              <SelectItem value="game">Game</SelectItem>
              <SelectItem value="saas">SaaS</SelectItem>
              <SelectItem value="tool">Tool</SelectItem>
            </SelectContent>
          </Select>
          <Select value={String(count)} onValueChange={(v) => setCount(parseInt(v))}>
            <SelectTrigger className="w-24 bg-zinc-900 border-zinc-700">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-zinc-900 border-zinc-700">
              <SelectItem value="3">3 ideas</SelectItem>
              <SelectItem value="5">5 ideas</SelectItem>
              <SelectItem value="10">10 ideas</SelectItem>
            </SelectContent>
          </Select>
          <Button
            onClick={generateIdeas}
            disabled={generating}
            className="flex-1 bg-amber-500 hover:bg-amber-600"
            data-testid="generate-ideas-btn"
          >
            {generating ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <Sparkles className="w-4 h-4 mr-1" />}
            Generate Ideas
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1 p-4">
        {!batch && batches.length === 0 ? (
          <div className="text-center py-12">
            <Lightbulb className="w-12 h-12 mx-auto mb-4 text-zinc-700" />
            <h3 className="font-rajdhani text-lg text-white mb-2">Generate Wild Ideas</h3>
            <p className="text-sm text-zinc-500">
              Enter a prompt and let AI generate unique project concepts
            </p>
          </div>
        ) : batch ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-sm text-zinc-400">Generated {batch.ideas?.length} ideas from: "{batch.prompt}"</h4>
              <Button variant="ghost" size="sm" onClick={() => setBatch(null)} className="text-zinc-500">
                Clear
              </Button>
            </div>
            
            {batch.ideas?.map((idea, i) => {
              const Icon = CATEGORY_ICONS[idea.category] || Lightbulb;
              return (
                <div key={idea.id || i} className="p-4 rounded-lg bg-zinc-900 border border-zinc-800 hover:border-zinc-700">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Icon className="w-4 h-4 text-amber-400" />
                        <h4 className="font-medium text-white">{idea.title}</h4>
                        <Badge className={`text-xs ${COMPLEXITY_COLORS[idea.complexity]}`}>
                          {idea.complexity}
                        </Badge>
                      </div>
                      <p className="text-sm text-zinc-400 mb-3">{idea.description}</p>
                      <div className="flex flex-wrap gap-1 mb-2">
                        {idea.unique_features?.map((f, j) => (
                          <Badge key={j} variant="outline" className="text-xs border-zinc-700">
                            {f}
                          </Badge>
                        ))}
                      </div>
                      <div className="flex items-center gap-3 text-xs text-zinc-500">
                        <span>Est: {idea.estimated_build_time}</span>
                        <span>Tech: {idea.tech_stack_suggestion?.slice(0, 2).join(", ")}</span>
                      </div>
                    </div>
                    <Button
                      onClick={() => buildIdea(idea.id)}
                      disabled={building === idea.id}
                      size="sm"
                      className="ml-4 bg-emerald-500 hover:bg-emerald-600"
                    >
                      {building === idea.id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <>
                          <Rocket className="w-3 h-3 mr-1" />Build
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="space-y-3">
            <h4 className="text-sm text-zinc-400 mb-4">Previous Batches</h4>
            {batches.map((b) => (
              <div key={b.id} className="p-3 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-between">
                <div>
                  <p className="text-sm text-white truncate max-w-xs">{b.prompt}</p>
                  <p className="text-xs text-zinc-500">{b.count} ideas • {new Date(b.created_at).toLocaleDateString()}</p>
                </div>
                <Button variant="ghost" size="sm" onClick={async () => {
                  const res = await axios.get(`${API}/ideas/batch/${b.id}`);
                  setBatch(res.data);
                }}>
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  );
};

export default IdeaEnginePanel;
