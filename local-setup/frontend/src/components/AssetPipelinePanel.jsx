import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { 
  Package, Image, Volume2, Grid3X3, Layers, Box, Palette, Play, Type, Film, Code,
  Plus, Trash2, Download, RefreshCw, Link, Unlink, Search, Filter, Loader2,
  FolderTree, BarChart3, Upload
} from "lucide-react";
import { API } from "@/App";

const TYPE_ICONS = {
  image: Image,
  audio: Volume2,
  texture: Grid3X3,
  sprite: Layers,
  model_3d: Box,
  material: Palette,
  animation: Play,
  font: Type,
  video: Film,
  script: Code
};

const TYPE_COLORS = {
  image: "blue",
  audio: "purple",
  texture: "amber",
  sprite: "cyan",
  model_3d: "emerald",
  material: "pink",
  animation: "orange",
  font: "zinc",
  video: "red",
  script: "green"
};

const AssetPipelinePanel = ({ projectId }) => {
  const [assets, setAssets] = useState([]);
  const [assetTypes, setAssetTypes] = useState({});
  const [categories, setCategories] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  
  const [filterType, setFilterType] = useState("all");
  const [filterCategory, setFilterCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [importForm, setImportForm] = useState({
    name: "",
    asset_type: "image",
    category: "general",
    url: "",
    tags: ""
  });

  useEffect(() => {
    fetchAssetTypes();
    fetchCategories();
    fetchAssets();
    fetchSummary();
  }, [projectId]);

  useEffect(() => {
    fetchAssets();
  }, [filterType, filterCategory]);

  const fetchAssetTypes = async () => {
    try {
      const res = await axios.get(`${API}/assets/types`);
      setAssetTypes(res.data);
    } catch (e) {}
  };

  const fetchCategories = async () => {
    try {
      const res = await axios.get(`${API}/assets/categories`);
      setCategories(res.data);
    } catch (e) {}
  };

  const fetchAssets = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filterType !== "all") params.asset_type = filterType;
      if (filterCategory !== "all") params.category = filterCategory;
      
      const res = await axios.get(`${API}/assets/${projectId}`, { params });
      setAssets(res.data);
    } catch (e) {}
    finally { setLoading(false); }
  };

  const fetchSummary = async () => {
    try {
      const res = await axios.get(`${API}/assets/${projectId}/summary`);
      setSummary(res.data);
    } catch (e) {}
  };

  const syncFromFiles = async () => {
    setSyncing(true);
    try {
      const res = await axios.post(`${API}/assets/${projectId}/sync-from-files`);
      toast.success(`Synced ${res.data.synced_assets} assets from files!`);
      fetchAssets();
      fetchSummary();
    } catch (e) {
      toast.error("Sync failed");
    } finally {
      setSyncing(false);
    }
  };

  const importAsset = async () => {
    if (!importForm.name || !importForm.asset_type) {
      toast.error("Name and type required");
      return;
    }
    try {
      await axios.post(`${API}/assets/import`, {
        project_id: projectId,
        name: importForm.name,
        asset_type: importForm.asset_type,
        category: importForm.category,
        url: importForm.url,
        tags: importForm.tags.split(",").map(t => t.trim()).filter(Boolean)
      });
      toast.success("Asset imported!");
      setImportDialogOpen(false);
      setImportForm({ name: "", asset_type: "image", category: "general", url: "", tags: "" });
      fetchAssets();
      fetchSummary();
    } catch (e) {
      toast.error("Import failed");
    }
  };

  const deleteAsset = async (assetId) => {
    try {
      await axios.delete(`${API}/assets/${assetId}`);
      setAssets(assets.filter(a => a.id !== assetId));
      fetchSummary();
    } catch (e) {
      toast.error("Delete failed");
    }
  };

  const filteredAssets = assets.filter(asset => {
    if (searchQuery && !asset.name.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    return true;
  });

  const getTypeIcon = (type) => TYPE_ICONS[type] || Package;
  const getTypeColor = (type) => TYPE_COLORS[type] || "zinc";

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]" data-testid="asset-pipeline-panel">
      {/* Header */}
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Package className="w-4 h-4 text-amber-400" />
            <span className="font-rajdhani font-bold text-white">Asset Pipeline</span>
            {summary && (
              <Badge variant="outline" className="text-xs border-zinc-700">
                {summary.total_assets} assets • {summary.total_size_mb}MB
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Button
              onClick={syncFromFiles}
              disabled={syncing}
              variant="outline"
              size="sm"
              className="border-zinc-700"
              data-testid="sync-assets-btn"
            >
              {syncing ? <Loader2 className="w-4 h-4 animate-spin mr-1" /> : <RefreshCw className="w-4 h-4 mr-1" />}
              Sync Files
            </Button>
            <Dialog open={importDialogOpen} onOpenChange={setImportDialogOpen}>
              <DialogTrigger asChild>
                <Button size="sm" className="bg-amber-500 hover:bg-amber-600" data-testid="import-asset-btn">
                  <Plus className="w-4 h-4 mr-1" />Import
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-[#18181b] border-zinc-700">
                <DialogHeader>
                  <DialogTitle className="font-rajdhani text-white flex items-center gap-2">
                    <Upload className="w-5 h-5 text-amber-400" />Import Asset
                  </DialogTitle>
                </DialogHeader>
                <div className="py-4 space-y-4">
                  <Input
                    placeholder="Asset name"
                    value={importForm.name}
                    onChange={(e) => setImportForm({ ...importForm, name: e.target.value })}
                    className="bg-zinc-900 border-zinc-700"
                  />
                  <div className="grid grid-cols-2 gap-3">
                    <Select value={importForm.asset_type} onValueChange={(v) => setImportForm({ ...importForm, asset_type: v })}>
                      <SelectTrigger className="bg-zinc-900 border-zinc-700">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-zinc-900 border-zinc-700">
                        {Object.keys(assetTypes).map(type => (
                          <SelectItem key={type} value={type}>{type.replace("_", " ")}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Select value={importForm.category} onValueChange={(v) => setImportForm({ ...importForm, category: v })}>
                      <SelectTrigger className="bg-zinc-900 border-zinc-700">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-zinc-900 border-zinc-700">
                        {categories.map(cat => (
                          <SelectItem key={cat.id} value={cat.id}>{cat.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <Input
                    placeholder="URL (optional)"
                    value={importForm.url}
                    onChange={(e) => setImportForm({ ...importForm, url: e.target.value })}
                    className="bg-zinc-900 border-zinc-700"
                  />
                  <Input
                    placeholder="Tags (comma separated)"
                    value={importForm.tags}
                    onChange={(e) => setImportForm({ ...importForm, tags: e.target.value })}
                    className="bg-zinc-900 border-zinc-700"
                  />
                </div>
                <DialogFooter>
                  <Button onClick={importAsset} className="bg-amber-500 hover:bg-amber-600">
                    <Plus className="w-4 h-4 mr-2" />Import Asset
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="browse" className="flex-1 flex flex-col">
        <TabsList className="flex-shrink-0 bg-transparent border-b border-zinc-800 rounded-none px-4 h-10">
          <TabsTrigger value="browse" className="text-xs">Browse</TabsTrigger>
          <TabsTrigger value="summary" className="text-xs">Summary</TabsTrigger>
          <TabsTrigger value="dependencies" className="text-xs">Dependencies</TabsTrigger>
        </TabsList>

        {/* Browse Tab */}
        <TabsContent value="browse" className="flex-1 flex flex-col m-0 overflow-hidden">
          {/* Filters */}
          <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800 flex items-center gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
              <Input
                placeholder="Search assets..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 bg-zinc-900 border-zinc-700"
                data-testid="asset-search"
              />
            </div>
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger className="w-36 bg-zinc-900 border-zinc-700">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-zinc-900 border-zinc-700">
                <SelectItem value="all">All Types</SelectItem>
                {Object.keys(assetTypes).map(type => (
                  <SelectItem key={type} value={type}>{type.replace("_", " ")}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={filterCategory} onValueChange={setFilterCategory}>
              <SelectTrigger className="w-36 bg-zinc-900 border-zinc-700">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-zinc-900 border-zinc-700">
                <SelectItem value="all">All Categories</SelectItem>
                {categories.map(cat => (
                  <SelectItem key={cat.id} value={cat.id}>{cat.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Asset Grid */}
          <ScrollArea className="flex-1 p-4">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-zinc-500" />
              </div>
            ) : filteredAssets.length === 0 ? (
              <div className="text-center py-12">
                <Package className="w-12 h-12 mx-auto mb-4 text-zinc-700" />
                <h3 className="font-rajdhani text-lg text-white mb-2">No Assets</h3>
                <p className="text-sm text-zinc-500 mb-4">Import assets or sync from project files</p>
                <Button onClick={syncFromFiles} variant="outline" className="border-zinc-700">
                  <RefreshCw className="w-4 h-4 mr-2" />Sync from Files
                </Button>
              </div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                {filteredAssets.map(asset => {
                  const TypeIcon = getTypeIcon(asset.asset_type);
                  const color = getTypeColor(asset.asset_type);
                  return (
                    <div
                      key={asset.id}
                      className="p-3 rounded-lg bg-zinc-900/50 border border-zinc-800 hover:border-zinc-700 group"
                    >
                      {/* Thumbnail/Icon */}
                      <div className={`h-24 rounded bg-${color}-500/10 flex items-center justify-center mb-3`}>
                        {asset.thumbnail_url || asset.url ? (
                          asset.asset_type === "image" || asset.asset_type === "texture" || asset.asset_type === "sprite" ? (
                            <img src={asset.thumbnail_url || asset.url} alt={asset.name} className="h-full w-full object-cover rounded" />
                          ) : (
                            <TypeIcon className={`w-10 h-10 text-${color}-400`} />
                          )
                        ) : (
                          <TypeIcon className={`w-10 h-10 text-${color}-400`} />
                        )}
                      </div>
                      
                      {/* Info */}
                      <h4 className="text-sm text-white font-medium truncate">{asset.name}</h4>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="outline" className={`text-[10px] border-${color}-500/30 text-${color}-400`}>
                          {asset.asset_type.replace("_", " ")}
                        </Badge>
                        {asset.format && (
                          <span className="text-[10px] text-zinc-500 uppercase">{asset.format}</span>
                        )}
                      </div>
                      
                      {/* Tags */}
                      {asset.tags?.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {asset.tags.slice(0, 3).map((tag, i) => (
                            <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-500">
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                      
                      {/* Actions */}
                      <div className="flex gap-1 mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
                        {asset.url && (
                          <a href={asset.url} target="_blank" rel="noopener noreferrer" className="p-1.5 hover:bg-zinc-800 rounded">
                            <Download className="w-3.5 h-3.5 text-zinc-400" />
                          </a>
                        )}
                        <button onClick={() => deleteAsset(asset.id)} className="p-1.5 hover:bg-red-500/20 rounded">
                          <Trash2 className="w-3.5 h-3.5 text-red-400" />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </ScrollArea>
        </TabsContent>

        {/* Summary Tab */}
        <TabsContent value="summary" className="flex-1 p-4 m-0 overflow-auto">
          {summary ? (
            <div className="space-y-6">
              {/* Overview */}
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
                  <Package className="w-6 h-6 text-amber-400 mb-2" />
                  <p className="text-2xl font-bold text-white">{summary.total_assets}</p>
                  <p className="text-xs text-zinc-500">Total Assets</p>
                </div>
                <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
                  <BarChart3 className="w-6 h-6 text-blue-400 mb-2" />
                  <p className="text-2xl font-bold text-white">{summary.total_size_mb}MB</p>
                  <p className="text-xs text-zinc-500">Total Size</p>
                </div>
                <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
                  <FolderTree className="w-6 h-6 text-emerald-400 mb-2" />
                  <p className="text-2xl font-bold text-white">{Object.keys(summary.by_type).length}</p>
                  <p className="text-xs text-zinc-500">Asset Types</p>
                </div>
              </div>

              {/* By Type */}
              <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
                <h4 className="font-medium text-white mb-4">Assets by Type</h4>
                <div className="space-y-2">
                  {Object.entries(summary.by_type).map(([type, count]) => {
                    const TypeIcon = getTypeIcon(type);
                    const color = getTypeColor(type);
                    const percentage = Math.round((count / summary.total_assets) * 100);
                    return (
                      <div key={type} className="flex items-center gap-3">
                        <TypeIcon className={`w-4 h-4 text-${color}-400`} />
                        <span className="text-sm text-zinc-400 w-24">{type.replace("_", " ")}</span>
                        <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
                          <div className={`h-full bg-${color}-500`} style={{ width: `${percentage}%` }} />
                        </div>
                        <span className="text-sm text-white w-8 text-right">{count}</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* By Category */}
              <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
                <h4 className="font-medium text-white mb-4">Assets by Category</h4>
                <div className="grid grid-cols-3 gap-3">
                  {Object.entries(summary.by_category).map(([cat, count]) => (
                    <div key={cat} className="p-3 rounded bg-zinc-800/50 text-center">
                      <p className="text-lg font-bold text-white">{count}</p>
                      <p className="text-xs text-zinc-500 capitalize">{cat}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-zinc-500" />
            </div>
          )}
        </TabsContent>

        {/* Dependencies Tab */}
        <TabsContent value="dependencies" className="flex-1 p-4 m-0 overflow-auto">
          <div className="text-center py-12">
            <Link className="w-12 h-12 mx-auto mb-4 text-zinc-700" />
            <h3 className="font-rajdhani text-lg text-white mb-2">Dependency Graph</h3>
            <p className="text-sm text-zinc-500 mb-4">
              Link assets together to track dependencies
            </p>
            <p className="text-xs text-zinc-600">
              Select an asset and use "Add Dependency" to create links
            </p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AssetPipelinePanel;
