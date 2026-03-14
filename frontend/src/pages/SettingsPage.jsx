import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, Settings, Save, FolderOpen, Monitor, Gamepad2, 
  Zap, CheckCircle, XCircle, RefreshCw, Download, ExternalLink,
  Terminal, Cpu, HardDrive
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { API } from '@/App';
import axios from 'axios';

const SettingsPage = () => {
  const navigate = useNavigate();
  const [bridgeConnected, setBridgeConnected] = useState(false);
  const [bridgeConfig, setBridgeConfig] = useState({
    unrealProjectPath: '',
    unityProjectPath: '',
    unrealEnginePath: '',
    unityEditorPath: '',
    autoOpenEditor: true,
    autoBuild: false
  });
  const [userSettings, setUserSettings] = useState({
    defaultEngine: 'unreal',
    theme: 'dark',
    autoSaveFiles: true,
    streamingMode: 'sse'
  });
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    // Check bridge connection status
    checkBridgeStatus();
    
    // Listen for bridge status events
    const handleBridgeStatus = (e) => {
      setBridgeConnected(e.detail.connected);
      if (e.detail.connected) {
        toast.success('Local Bridge Connected!');
      }
    };
    
    window.addEventListener('agentforge-bridge-status', handleBridgeStatus);
    
    // Load saved settings
    loadSettings();
    
    return () => {
      window.removeEventListener('agentforge-bridge-status', handleBridgeStatus);
    };
  }, []);

  const checkBridgeStatus = () => {
    // Dispatch event to check bridge status
    window.dispatchEvent(new CustomEvent('agentforge-get-status'));
  };

  const loadSettings = async () => {
    try {
      const res = await axios.get(`${API}/settings`);
      if (res.data) {
        setUserSettings(prev => ({ ...prev, ...res.data }));
      }
    } catch (error) {
      // Settings endpoint might not exist yet, use defaults
    }
  };

  const saveSettings = async () => {
    setIsSaving(true);
    try {
      // Save to backend
      await axios.post(`${API}/settings`, userSettings);
      
      // Save bridge config to extension
      if (bridgeConnected) {
        window.dispatchEvent(new CustomEvent('agentforge-set-config', {
          detail: bridgeConfig
        }));
      }
      
      toast.success('Settings saved successfully!');
    } catch (error) {
      toast.error('Failed to save settings');
    }
    setIsSaving(false);
  };

  const testBridgeConnection = () => {
    checkBridgeStatus();
    toast.info('Checking bridge connection...');
  };

  const downloadBridge = () => {
    // Create download for bridge files
    window.open(`${API}/local-bridge/download`, '_blank');
  };

  return (
    <div className="min-h-screen bg-[#09090b] text-white">
      {/* Header */}
      <header className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-lg sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-zinc-700 to-zinc-800 flex items-center justify-center">
                <Settings className="w-5 h-5" />
              </div>
              <div>
                <h1 className="font-bold text-xl">Settings</h1>
                <p className="text-sm text-zinc-500">Configure AgentForge & Local Bridge</p>
              </div>
            </div>
          </div>
          
          <Button 
            onClick={saveSettings}
            className="bg-yellow-500 hover:bg-yellow-400 text-black font-semibold"
            disabled={isSaving}
            data-testid="save-settings-btn"
          >
            <Save className="w-4 h-4 mr-2" />
            {isSaving ? 'Saving...' : 'Save Settings'}
          </Button>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-6 py-8">
        <Tabs defaultValue="local-bridge" className="space-y-6">
          <TabsList className="bg-zinc-900 border border-zinc-800">
            <TabsTrigger value="local-bridge" className="data-[state=active]:bg-yellow-500 data-[state=active]:text-black">
              <Cpu className="w-4 h-4 mr-2" />
              Local Bridge
            </TabsTrigger>
            <TabsTrigger value="general" className="data-[state=active]:bg-yellow-500 data-[state=active]:text-black">
              <Settings className="w-4 h-4 mr-2" />
              General
            </TabsTrigger>
          </TabsList>

          {/* Local Bridge Settings */}
          <TabsContent value="local-bridge" className="space-y-6">
            {/* Connection Status */}
            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <Zap className="w-5 h-5 text-yellow-400" />
                      Local Bridge Status
                    </CardTitle>
                    <CardDescription>
                      Connect AgentForge to your local Unreal Engine & Unity projects
                    </CardDescription>
                  </div>
                  <Badge 
                    className={bridgeConnected 
                      ? 'bg-green-500/20 text-green-400 border-green-500/50' 
                      : 'bg-red-500/20 text-red-400 border-red-500/50'
                    }
                  >
                    {bridgeConnected ? (
                      <><CheckCircle className="w-3 h-3 mr-1" /> Connected</>
                    ) : (
                      <><XCircle className="w-3 h-3 mr-1" /> Disconnected</>
                    )}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-3">
                  <Button variant="outline" onClick={testBridgeConnection} className="border-zinc-700">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Test Connection
                  </Button>
                  <Button variant="outline" onClick={downloadBridge} className="border-zinc-700">
                    <Download className="w-4 h-4 mr-2" />
                    Download Bridge
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => window.open('https://chrome.google.com/webstore', '_blank')}
                    className="border-zinc-700"
                  >
                    <ExternalLink className="w-4 h-4 mr-2" />
                    Get Extension
                  </Button>
                </div>
                
                {!bridgeConnected && (
                  <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
                    <h4 className="font-semibold text-yellow-400 mb-2">Setup Instructions:</h4>
                    <ol className="text-sm text-zinc-400 space-y-2 list-decimal list-inside">
                      <li>Download and install the Local Bridge using the button above</li>
                      <li>Install the AgentForge browser extension</li>
                      <li>Run the installer script to register the native messaging host</li>
                      <li>Refresh this page and the bridge should connect automatically</li>
                    </ol>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Project Paths */}
            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FolderOpen className="w-5 h-5 text-blue-400" />
                  Project Paths
                </CardTitle>
                <CardDescription>
                  Configure paths to your local game engine projects
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Unreal Engine */}
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Gamepad2 className="w-5 h-5 text-orange-400" />
                    <Label className="text-base font-semibold">Unreal Engine Project</Label>
                  </div>
                  <Input
                    placeholder="C:\Projects\MyGame"
                    value={bridgeConfig.unrealProjectPath}
                    onChange={(e) => setBridgeConfig(prev => ({ ...prev, unrealProjectPath: e.target.value }))}
                    className="bg-zinc-800 border-zinc-700"
                    data-testid="unreal-path-input"
                  />
                  <Input
                    placeholder="C:\Program Files\Epic Games\UE_5.4 (optional)"
                    value={bridgeConfig.unrealEnginePath}
                    onChange={(e) => setBridgeConfig(prev => ({ ...prev, unrealEnginePath: e.target.value }))}
                    className="bg-zinc-800 border-zinc-700 text-sm"
                  />
                  <p className="text-xs text-zinc-500">
                    Point to your .uproject file location. Engine path is optional for auto-build.
                  </p>
                </div>

                {/* Unity */}
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Monitor className="w-5 h-5 text-blue-400" />
                    <Label className="text-base font-semibold">Unity Project</Label>
                  </div>
                  <Input
                    placeholder="C:\Projects\MyUnityGame"
                    value={bridgeConfig.unityProjectPath}
                    onChange={(e) => setBridgeConfig(prev => ({ ...prev, unityProjectPath: e.target.value }))}
                    className="bg-zinc-800 border-zinc-700"
                    data-testid="unity-path-input"
                  />
                  <Input
                    placeholder="C:\Program Files\Unity\Hub\Editor\2023.2.0f1 (optional)"
                    value={bridgeConfig.unityEditorPath}
                    onChange={(e) => setBridgeConfig(prev => ({ ...prev, unityEditorPath: e.target.value }))}
                    className="bg-zinc-800 border-zinc-700 text-sm"
                  />
                  <p className="text-xs text-zinc-500">
                    Point to your Unity project root folder (contains Assets folder).
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Build Options */}
            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Terminal className="w-5 h-5 text-green-400" />
                  Build Options
                </CardTitle>
                <CardDescription>
                  Configure how AgentForge interacts with your local IDE
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="font-medium">Auto Open Editor</Label>
                    <p className="text-sm text-zinc-500">Open Unreal/Unity after pushing files</p>
                  </div>
                  <Switch
                    checked={bridgeConfig.autoOpenEditor}
                    onCheckedChange={(checked) => setBridgeConfig(prev => ({ ...prev, autoOpenEditor: checked }))}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="font-medium">Auto Build</Label>
                    <p className="text-sm text-zinc-500">Automatically compile after file changes</p>
                  </div>
                  <Switch
                    checked={bridgeConfig.autoBuild}
                    onCheckedChange={(checked) => setBridgeConfig(prev => ({ ...prev, autoBuild: checked }))}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* General Settings */}
          <TabsContent value="general" className="space-y-6">
            <Card className="bg-zinc-900 border-zinc-800">
              <CardHeader>
                <CardTitle>Default Preferences</CardTitle>
                <CardDescription>
                  Configure default behavior for new projects
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Default Game Engine</Label>
                  <div className="flex gap-2">
                    <Button
                      variant={userSettings.defaultEngine === 'unreal' ? 'default' : 'outline'}
                      onClick={() => setUserSettings(prev => ({ ...prev, defaultEngine: 'unreal' }))}
                      className={userSettings.defaultEngine === 'unreal' ? 'bg-orange-500' : 'border-zinc-700'}
                    >
                      Unreal Engine 5
                    </Button>
                    <Button
                      variant={userSettings.defaultEngine === 'unity' ? 'default' : 'outline'}
                      onClick={() => setUserSettings(prev => ({ ...prev, defaultEngine: 'unity' }))}
                      className={userSettings.defaultEngine === 'unity' ? 'bg-blue-500' : 'border-zinc-700'}
                    >
                      Unity
                    </Button>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label className="font-medium">Auto-Save Generated Files</Label>
                    <p className="text-sm text-zinc-500">Automatically save files as they're generated</p>
                  </div>
                  <Switch
                    checked={userSettings.autoSaveFiles}
                    onCheckedChange={(checked) => setUserSettings(prev => ({ ...prev, autoSaveFiles: checked }))}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Streaming Mode</Label>
                  <p className="text-xs text-zinc-500 mb-2">
                    How God Mode streams content (WebSocket is more stable for large builds)
                  </p>
                  <div className="flex gap-2">
                    <Button
                      variant={userSettings.streamingMode === 'sse' ? 'default' : 'outline'}
                      onClick={() => setUserSettings(prev => ({ ...prev, streamingMode: 'sse' }))}
                      className={userSettings.streamingMode === 'sse' ? 'bg-yellow-500 text-black' : 'border-zinc-700'}
                    >
                      SSE (Default)
                    </Button>
                    <Button
                      variant={userSettings.streamingMode === 'websocket' ? 'default' : 'outline'}
                      onClick={() => setUserSettings(prev => ({ ...prev, streamingMode: 'websocket' }))}
                      className={userSettings.streamingMode === 'websocket' ? 'bg-yellow-500 text-black' : 'border-zinc-700'}
                    >
                      WebSocket (Stable)
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default SettingsPage;
