import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Music, Volume2, Mic, Play, Pause, Trash2, Download, 
  Loader2, Sparkles, Package
} from "lucide-react";
import { API } from "@/App";

const AUDIO_TYPES = [
  { id: "sfx", name: "Sound Effects", icon: Volume2, color: "blue" },
  { id: "music", name: "Music", icon: Music, color: "purple" },
  { id: "voice", name: "Voice/TTS", icon: Mic, color: "emerald" }
];

const PROVIDERS = [
  { id: "elevenlabs", name: "ElevenLabs", description: "High-quality audio" },
  { id: "openai", name: "OpenAI TTS", description: "Fast & reliable" }
];

const VOICE_IDS = [
  { id: "alloy", name: "Alloy (Neutral)" },
  { id: "echo", name: "Echo (Male)" },
  { id: "fable", name: "Fable (British)" },
  { id: "onyx", name: "Onyx (Deep)" },
  { id: "nova", name: "Nova (Female)" },
  { id: "shimmer", name: "Shimmer (Soft)" }
];

const AudioGeneratorPanel = ({ projectId }) => {
  const [categories, setCategories] = useState({});
  const [assets, setAssets] = useState([]);
  const [generating, setGenerating] = useState(false);
  const [generatingPack, setGeneratingPack] = useState(false);
  const [playing, setPlaying] = useState(null);
  const [audioElement, setAudioElement] = useState(null);
  
  const [form, setForm] = useState({
    name: "",
    audio_type: "sfx",
    prompt: "",
    provider: "elevenlabs",
    voice_id: "alloy"
  });

  useEffect(() => {
    fetchCategories();
    fetchAssets();
  }, [projectId]);

  const fetchCategories = async () => {
    try {
      const res = await axios.get(`${API}/audio/categories`);
      setCategories(res.data);
    } catch (e) {}
  };

  const fetchAssets = async () => {
    try {
      const res = await axios.get(`${API}/audio/${projectId}`);
      setAssets(res.data);
    } catch (e) {}
  };

  const generateAudio = async () => {
    if (!form.name || !form.prompt) {
      toast.error("Name and prompt required");
      return;
    }
    setGenerating(true);
    try {
      const res = await axios.post(`${API}/audio/generate`, null, {
        params: {
          project_id: projectId,
          ...form
        }
      });
      setAssets([res.data, ...assets]);
      toast.success("Audio generated!");
      setForm({ ...form, name: "", prompt: "" });
    } catch (e) {
      toast.error("Generation failed");
    } finally {
      setGenerating(false);
    }
  };

  const generatePack = async (packType) => {
    setGeneratingPack(true);
    try {
      const res = await axios.post(`${API}/audio/generate-pack`, null, {
        params: { project_id: projectId, pack_type: packType }
      });
      toast.success(`Generated ${res.data.generated} audio assets!`);
      fetchAssets();
    } catch (e) {
      toast.error("Pack generation failed");
    } finally {
      setGeneratingPack(false);
    }
  };

  const deleteAsset = async (assetId) => {
    await axios.delete(`${API}/audio/${assetId}`);
    setAssets(assets.filter(a => a.id !== assetId));
  };

  const playAudio = (asset) => {
    if (playing === asset.id) {
      audioElement?.pause();
      setPlaying(null);
    } else {
      if (audioElement) audioElement.pause();
      const audio = new Audio(asset.url);
      audio.play();
      audio.onended = () => setPlaying(null);
      setAudioElement(audio);
      setPlaying(asset.id);
    }
  };

  const applyPreset = (presetKey, type) => {
    const prompt = categories[type]?.[presetKey];
    if (prompt) {
      setForm({
        ...form,
        name: presetKey.replace(/_/g, ' '),
        audio_type: type,
        prompt
      });
    }
  };

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]">
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Music className="w-4 h-4 text-purple-400" />
            <span className="font-rajdhani font-bold text-white">Audio Generator</span>
            <Badge variant="outline" className="text-xs border-zinc-700">{assets.length} assets</Badge>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-hidden flex">
        {/* Left: Generator */}
        <div className="w-1/2 border-r border-zinc-800 flex flex-col">
          <Tabs defaultValue="custom" className="flex-1 flex flex-col">
            <TabsList className="flex-shrink-0 bg-transparent border-b border-zinc-800 rounded-none px-4 h-10">
              <TabsTrigger value="custom" className="text-xs">Custom</TabsTrigger>
              <TabsTrigger value="presets" className="text-xs">Presets</TabsTrigger>
              <TabsTrigger value="packs" className="text-xs">Packs</TabsTrigger>
            </TabsList>

            <TabsContent value="custom" className="flex-1 p-4 space-y-4 overflow-y-auto m-0">
              <Input
                placeholder="Asset name"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="bg-zinc-900 border-zinc-700"
              />
              
              <div className="grid grid-cols-3 gap-2">
                {AUDIO_TYPES.map((type) => (
                  <button
                    key={type.id}
                    onClick={() => setForm({ ...form, audio_type: type.id })}
                    className={`p-2 rounded border text-center transition-all ${
                      form.audio_type === type.id
                        ? `bg-${type.color}-500/20 border-${type.color}-500/50`
                        : 'bg-zinc-900 border-zinc-700 hover:border-zinc-600'
                    }`}
                  >
                    <type.icon className={`w-5 h-5 mx-auto mb-1 ${form.audio_type === type.id ? `text-${type.color}-400` : 'text-zinc-500'}`} />
                    <span className="text-xs text-zinc-400">{type.name}</span>
                  </button>
                ))}
              </div>

              <Textarea
                placeholder="Describe the audio you want to generate..."
                value={form.prompt}
                onChange={(e) => setForm({ ...form, prompt: e.target.value })}
                className="bg-zinc-900 border-zinc-700 min-h-[100px]"
              />

              <div className="grid grid-cols-2 gap-2">
                <Select value={form.provider} onValueChange={(v) => setForm({ ...form, provider: v })}>
                  <SelectTrigger className="bg-zinc-900 border-zinc-700">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-zinc-900 border-zinc-700">
                    {PROVIDERS.map(p => (
                      <SelectItem key={p.id} value={p.id}>{p.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                {form.audio_type === "voice" && (
                  <Select value={form.voice_id} onValueChange={(v) => setForm({ ...form, voice_id: v })}>
                    <SelectTrigger className="bg-zinc-900 border-zinc-700">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-zinc-900 border-zinc-700">
                      {VOICE_IDS.map(v => (
                        <SelectItem key={v.id} value={v.id}>{v.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              </div>

              <Button onClick={generateAudio} disabled={generating} className="w-full bg-purple-500 hover:bg-purple-600">
                {generating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Sparkles className="w-4 h-4 mr-2" />}
                Generate Audio
              </Button>
            </TabsContent>

            <TabsContent value="presets" className="flex-1 p-4 overflow-y-auto m-0">
              <div className="space-y-4">
                {Object.entries(categories).map(([type, presets]) => (
                  <div key={type}>
                    <h4 className="text-sm font-medium text-white mb-2 capitalize">{type}</h4>
                    <div className="grid grid-cols-2 gap-1">
                      {Object.keys(presets).map((key) => (
                        <button
                          key={key}
                          onClick={() => applyPreset(key, type)}
                          className="p-2 text-left rounded bg-zinc-800/50 hover:bg-zinc-800 text-xs text-zinc-400 truncate"
                        >
                          {key.replace(/_/g, ' ')}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="packs" className="flex-1 p-4 overflow-y-auto m-0">
              <div className="space-y-3">
                {[
                  { id: "basic_sfx", name: "Basic SFX", desc: "UI clicks, pickups, level up" },
                  { id: "combat_sfx", name: "Combat SFX", desc: "Sword, hits, damage, heal" },
                  { id: "movement_sfx", name: "Movement SFX", desc: "Footsteps, jump, land" },
                  { id: "ambient_music", name: "Ambient Music", desc: "Menu, exploration, village" },
                  { id: "battle_music", name: "Battle Music", desc: "Combat, boss, victory" }
                ].map(pack => (
                  <button
                    key={pack.id}
                    onClick={() => generatePack(pack.id)}
                    disabled={generatingPack}
                    className="w-full p-4 rounded-lg bg-zinc-900 border border-zinc-800 hover:border-purple-500/50 text-left transition-all"
                  >
                    <div className="flex items-center gap-3">
                      <Package className="w-6 h-6 text-purple-400" />
                      <div>
                        <h5 className="font-medium text-white">{pack.name}</h5>
                        <p className="text-xs text-zinc-500">{pack.desc}</p>
                      </div>
                    </div>
                  </button>
                ))}
                {generatingPack && (
                  <div className="text-center py-4">
                    <Loader2 className="w-6 h-6 animate-spin mx-auto text-purple-400" />
                    <p className="text-xs text-zinc-500 mt-2">Generating audio pack...</p>
                  </div>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </div>

        {/* Right: Assets */}
        <ScrollArea className="w-1/2 p-4">
          <div className="space-y-2">
            {assets.length === 0 ? (
              <div className="text-center py-12">
                <Music className="w-12 h-12 mx-auto mb-4 text-zinc-700" />
                <p className="text-sm text-zinc-500">No audio assets yet</p>
              </div>
            ) : (
              assets.map((asset) => (
                <div key={asset.id} className="p-3 rounded-lg bg-zinc-900/50 border border-zinc-800 group">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => playAudio(asset)}
                        className={`p-2 rounded-full ${playing === asset.id ? 'bg-purple-500' : 'bg-zinc-800 hover:bg-zinc-700'}`}
                      >
                        {playing === asset.id ? <Pause className="w-4 h-4 text-white" /> : <Play className="w-4 h-4 text-white" />}
                      </button>
                      <div>
                        <h5 className="text-sm text-white font-medium">{asset.name}</h5>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-[10px] border-zinc-700">{asset.audio_type}</Badge>
                          <span className="text-[10px] text-zinc-500">{asset.provider}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      {asset.url && (
                        <a href={asset.url} download className="p-1 hover:bg-zinc-800 rounded">
                          <Download className="w-4 h-4 text-zinc-400" />
                        </a>
                      )}
                      <button onClick={() => deleteAsset(asset.id)} className="p-1 hover:bg-red-500/20 rounded">
                        <Trash2 className="w-4 h-4 text-red-400" />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
};

export default AudioGeneratorPanel;
