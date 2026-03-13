import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Cloud, Server, Database, Globe, Shield, Cpu, 
  RefreshCw, Plus, Trash2, Play, Settings, Download,
  DollarSign, Box, Network, Zap
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { API } from '@/App';

const CloudBuilderPanel = () => {
  const [activeTab, setActiveTab] = useState('infra');
  const [infrastructures, setInfrastructures] = useState([]);
  const [providers, setProviders] = useState({});
  const [templates, setTemplates] = useState({});
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  
  // Form state
  const [infraName, setInfraName] = useState('');
  const [infraDesc, setInfraDesc] = useState('');
  const [provider, setProvider] = useState('aws');
  const [region, setRegion] = useState('us-east-1');
  const [selectedInfra, setSelectedInfra] = useState(null);
  const [selectedComponents, setSelectedComponents] = useState(['compute', 'database']);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [infrasRes, providersRes, templatesRes] = await Promise.all([
        axios.get(`${API}/cloud-builder/infrastructures`),
        axios.get(`${API}/cloud-builder/providers`),
        axios.get(`${API}/cloud-builder/templates`)
      ]);
      setInfrastructures(infrasRes.data || []);
      setProviders(providersRes.data || {});
      setTemplates(templatesRes.data || {});
    } catch (e) {
      console.error('Failed to fetch data:', e);
    }
    setLoading(false);
  };

  const createInfra = async () => {
    if (!infraName) return;
    
    setCreating(true);
    try {
      await axios.post(`${API}/cloud-builder/infrastructures`, {
        name: infraName,
        description: infraDesc,
        provider: provider,
        iac_tool: 'terraform',
        region: region,
        components: selectedComponents,
        environment: 'development'
      });
      setInfraName('');
      setInfraDesc('');
      fetchData();
      setActiveTab('infra');
    } catch (e) {
      console.error('Failed to create infrastructure:', e);
    }
    setCreating(false);
  };

  const deployInfra = async (infraId) => {
    try {
      await axios.post(`${API}/cloud-builder/infrastructures/${infraId}/deploy`);
      fetchData();
    } catch (e) {
      console.error('Failed to deploy:', e);
    }
  };

  const deleteInfra = async (infraId) => {
    try {
      await axios.delete(`${API}/cloud-builder/infrastructures/${infraId}`);
      fetchData();
    } catch (e) {
      console.error('Failed to delete:', e);
    }
  };

  const toggleComponent = (comp) => {
    setSelectedComponents(prev => 
      prev.includes(comp) 
        ? prev.filter(c => c !== comp)
        : [...prev, comp]
    );
  };

  const getProviderIcon = (p) => {
    switch (p) {
      case 'aws': return <div className="w-6 h-6 rounded bg-orange-500 flex items-center justify-center text-[10px] font-bold text-white">AWS</div>;
      case 'gcp': return <div className="w-6 h-6 rounded bg-blue-500 flex items-center justify-center text-[10px] font-bold text-white">GCP</div>;
      case 'azure': return <div className="w-6 h-6 rounded bg-cyan-500 flex items-center justify-center text-[10px] font-bold text-white">AZ</div>;
      default: return <Cloud className="w-6 h-6 text-zinc-400" />;
    }
  };

  const getComponentIcon = (comp) => {
    switch (comp) {
      case 'compute': return <Server className="w-4 h-4" />;
      case 'database': return <Database className="w-4 h-4" />;
      case 'storage': return <Box className="w-4 h-4" />;
      case 'networking': return <Network className="w-4 h-4" />;
      case 'cdn': return <Globe className="w-4 h-4" />;
      case 'serverless': return <Zap className="w-4 h-4" />;
      case 'container': return <Cpu className="w-4 h-4" />;
      default: return <Cloud className="w-4 h-4" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ready': return 'bg-green-500/20 text-green-400';
      case 'generating': return 'bg-blue-500/20 text-blue-400';
      case 'deploying': return 'bg-yellow-500/20 text-yellow-400';
      default: return 'bg-zinc-500/20 text-zinc-400';
    }
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-orange-950/20 to-black" data-testid="cloud-builder-panel">
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 border-b border-zinc-800/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center">
              <Cloud className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">CLOUD BUILDER</h2>
              <p className="text-xs text-zinc-500">Multi-cloud infrastructure</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {Object.keys(providers).map(p => (
              <Badge key={p} className="bg-zinc-800 text-zinc-400 text-xs uppercase">
                {p}
              </Badge>
            ))}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col overflow-hidden">
        <TabsList className="flex-shrink-0 mx-6 mt-4 bg-zinc-900/50 p-1">
          <TabsTrigger value="infra" className="flex-1 data-[state=active]:bg-orange-600">
            <Server className="w-4 h-4 mr-2" />
            Infrastructure
          </TabsTrigger>
          <TabsTrigger value="create" className="flex-1 data-[state=active]:bg-orange-600">
            <Plus className="w-4 h-4 mr-2" />
            Create
          </TabsTrigger>
          <TabsTrigger value="templates" className="flex-1 data-[state=active]:bg-orange-600">
            <Box className="w-4 h-4 mr-2" />
            Architectures
          </TabsTrigger>
        </TabsList>

        <div className="flex-1 overflow-auto p-6">
          {/* Infrastructure Tab */}
          <TabsContent value="infra" className="m-0 space-y-4">
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <RefreshCw className="w-8 h-8 text-orange-500 animate-spin" />
              </div>
            ) : infrastructures.length === 0 ? (
              <div className="text-center py-12">
                <Cloud className="w-12 h-12 text-zinc-600 mx-auto mb-4" />
                <p className="text-zinc-500">No infrastructure yet</p>
                <Button 
                  onClick={() => setActiveTab('create')} 
                  className="mt-4 bg-orange-600 hover:bg-orange-700"
                >
                  Create Infrastructure
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {infrastructures.map(infra => (
                  <div
                    key={infra.id}
                    className={`p-4 bg-zinc-900/50 rounded-xl border transition-all cursor-pointer ${
                      selectedInfra?.id === infra.id 
                        ? 'border-orange-500' 
                        : 'border-zinc-800 hover:border-zinc-700'
                    }`}
                    onClick={() => setSelectedInfra(infra)}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        {getProviderIcon(infra.provider)}
                        <div>
                          <p className="text-sm font-medium text-white">{infra.name}</p>
                          <p className="text-xs text-zinc-500">{infra.provider_info?.name} • {infra.region}</p>
                        </div>
                      </div>
                      <Badge className={getStatusColor(infra.status)}>
                        {infra.status}
                      </Badge>
                    </div>

                    {/* Components */}
                    {infra.components?.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-3">
                        {infra.components.map((comp, i) => (
                          <div key={i} className="flex items-center gap-1 px-2 py-1 bg-zinc-800/50 rounded text-xs">
                            {getComponentIcon(comp.type)}
                            <span className="text-zinc-400">{comp.name}</span>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Cost Estimate */}
                    {infra.estimated_cost && (
                      <div className="flex items-center gap-2 mb-3 text-xs text-zinc-400">
                        <DollarSign className="w-3 h-3" />
                        <span>~${infra.estimated_cost.total}/month estimated</span>
                      </div>
                    )}

                    {/* Actions */}
                    {selectedInfra?.id === infra.id && (
                      <div className="flex items-center gap-2 pt-3 border-t border-zinc-800">
                        <Button
                          size="sm"
                          onClick={(e) => { e.stopPropagation(); deployInfra(infra.id); }}
                          className="bg-orange-600 hover:bg-orange-700"
                        >
                          <Play className="w-3 h-3 mr-1" />
                          Deploy
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="border-zinc-700"
                        >
                          <Download className="w-3 h-3 mr-1" />
                          Terraform
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={(e) => { e.stopPropagation(); deleteInfra(infra.id); }}
                          className="text-red-400 hover:text-red-300 ml-auto"
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Create Tab */}
          <TabsContent value="create" className="m-0 space-y-6">
            <div className="bg-zinc-900/50 rounded-xl p-6 border border-zinc-800">
              <h3 className="text-sm font-medium text-white mb-4">Create Infrastructure</h3>
              
              <div className="space-y-4">
                {/* Provider Selection */}
                <div>
                  <label className="text-xs text-zinc-400 mb-2 block">Cloud Provider</label>
                  <div className="grid grid-cols-3 gap-3">
                    {Object.entries(providers).map(([key, prov]) => (
                      <button
                        key={key}
                        onClick={() => {
                          setProvider(key);
                          setRegion(prov.regions?.[0] || 'us-east-1');
                        }}
                        className={`p-4 rounded-xl border transition-all ${
                          provider === key
                            ? 'border-orange-500 bg-orange-500/10'
                            : 'border-zinc-800 hover:border-zinc-700'
                        }`}
                      >
                        <div className="flex flex-col items-center gap-2">
                          {getProviderIcon(key)}
                          <span className="text-sm font-medium text-white">{prov.name}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Region */}
                <div>
                  <label className="text-xs text-zinc-400 mb-2 block">Region</label>
                  <Select value={region} onValueChange={setRegion}>
                    <SelectTrigger className="bg-zinc-800/50 border-zinc-700">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {providers[provider]?.regions?.map(r => (
                        <SelectItem key={r} value={r}>{r}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Components */}
                <div>
                  <label className="text-xs text-zinc-400 mb-2 block">Components</label>
                  <div className="grid grid-cols-4 gap-2">
                    {['compute', 'database', 'storage', 'cache', 'cdn', 'serverless', 'container'].map(comp => (
                      <button
                        key={comp}
                        onClick={() => toggleComponent(comp)}
                        className={`p-3 rounded-lg border transition-all ${
                          selectedComponents.includes(comp)
                            ? 'border-orange-500 bg-orange-500/10'
                            : 'border-zinc-800 hover:border-zinc-700'
                        }`}
                      >
                        <div className="flex flex-col items-center gap-1">
                          {getComponentIcon(comp)}
                          <span className="text-xs capitalize">{comp}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                <Input
                  value={infraName}
                  onChange={(e) => setInfraName(e.target.value)}
                  placeholder="Infrastructure Name"
                  className="bg-zinc-800/50 border-zinc-700"
                />
                
                <Input
                  value={infraDesc}
                  onChange={(e) => setInfraDesc(e.target.value)}
                  placeholder="Description (optional)"
                  className="bg-zinc-800/50 border-zinc-700"
                />

                <Button
                  onClick={createInfra}
                  disabled={creating || !infraName}
                  className="w-full bg-orange-600 hover:bg-orange-700"
                >
                  {creating ? (
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Cloud className="w-4 h-4 mr-2" />
                  )}
                  Generate Infrastructure
                </Button>
              </div>
            </div>
          </TabsContent>

          {/* Templates Tab */}
          <TabsContent value="templates" className="m-0 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              {Object.entries(templates).map(([key, template]) => (
                <div
                  key={key}
                  className="p-4 bg-zinc-900/50 rounded-xl border border-zinc-800 hover:border-orange-500/50 transition-all cursor-pointer"
                >
                  <h4 className="text-sm font-medium text-white mb-2">{template.name}</h4>
                  <p className="text-xs text-zinc-500 mb-3">{template.description}</p>
                  <div className="flex flex-wrap gap-1">
                    {template.components?.slice(0, 4).map((comp, i) => (
                      <Badge key={i} variant="outline" className="text-[10px]">
                        {comp.replace('_', ' ')}
                      </Badge>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
};

export default CloudBuilderPanel;
