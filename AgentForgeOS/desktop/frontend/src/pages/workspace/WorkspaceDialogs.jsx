/**
 * WorkspaceDialogs — All workspace modal dialogs extracted from ProjectWorkspace
 * Pure presentation — all state and handlers passed as props.
 * Dialogs: Simulation, Demo, GitHub Push, Image Gen, Memory Viewer, Duplicate Project
 */
import { Loader2, Radio, Sparkles, FileCode, Clock, AlertTriangle, Rocket,
  Gamepad2, Globe, Monitor, Play, RefreshCw, Package, Github, Image,
  Brain, CopyPlus, Trash2, Search, Replace, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Mountain, Users, Map, Car, Sun, Swords, Hammer, Coins, Ghost,
  Timer, Camera, Wifi } from "lucide-react";

const SYSTEM_ICONS = {
  terrain: Mountain, npc_population: Users, quest_system: Map, vehicle_system: Car,
  day_night_cycle: Sun, combat_system: Swords, crafting_system: Hammer,
  economy_system: Coins, stealth_system: Ghost, mount_system: Gamepad2,
  building_system: FileCode, skill_tree: Sparkles, fast_travel: Timer,
  photo_mode: Camera, multiplayer: Wifi
};

export default function WorkspaceDialogs({
  // ── Simulation ────────────────────────────────────────────────────────
  simulationDialog, setSimulationDialog,
  openWorldSystems, targetEngine, setTargetEngine,
  selectedSystems, toggleSystem, simulating, simulationResult,
  runSimulation, scheduleBuild, setScheduleBuild,
  scheduleTime, setScheduleTime, buildRunning, startAutonomousBuild,
  // ── Build status chips ────────────────────────────────────────────────
  currentBuild, startScheduledBuildNow, cancelBuild, pauseBuild,
  // ── Demo ──────────────────────────────────────────────────────────────
  demoDialogOpen, setDemoDialogOpen,
  currentDemo, openWebDemo, files,
  setRightTab, setSelectedFile, setEditorContent,
  regenerateDemo, regeneratingDemo,
  // ── GitHub push ───────────────────────────────────────────────────────
  githubDialogOpen, setGithubDialogOpen,
  githubToken, setGithubToken,
  githubRepoName, setGithubRepoName,
  githubCreateNew, setGithubCreateNew,
  pushing, pushToGithub, projectRepoUrl,
  // ── Image generation ──────────────────────────────────────────────────
  imageDialogOpen, setImageDialogOpen,
  imagePrompt, setImagePrompt,
  imageCategory, setImageCategory,
  generatingImage, generateImage,
  // ── Memory viewer ─────────────────────────────────────────────────────
  memoryDialog, setMemoryDialog,
  memories, extractMemories, deleteMemory,
  // ── Duplicate project ─────────────────────────────────────────────────
  duplicateDialog, setDuplicateDialog,
  duplicateName, setDuplicateName, duplicateProject,
  // ── Code refactor (find/replace) ──────────────────────────────────────
  refactorDialog, setRefactorDialog,
  refactorData, setRefactorData,
  refactorPreview, setRefactorPreview,
  previewRefactor, applyRefactor,
}) {
  return (
    <>
      {/* ── Simulation Dialog ─────────────────────────────────────────── */}
      <Dialog open={simulationDialog} onOpenChange={setSimulationDialog}>
        <DialogContent className="bg-[#18181b] border-zinc-700 max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="font-rajdhani text-white flex items-center gap-2">
              <Radio className="w-5 h-5 text-cyan-400" />Build Simulation (Dry Run)
            </DialogTitle>
          </DialogHeader>
          <div className="py-4 space-y-4">
            <div className="flex gap-4">
              <Button variant={targetEngine === "unreal" ? "default" : "outline"} className={targetEngine === "unreal" ? "bg-blue-500" : "border-zinc-700"} onClick={() => setTargetEngine("unreal")}>Unreal Engine 5</Button>
              <Button variant={targetEngine === "unity" ? "default" : "outline"} className={targetEngine === "unity" ? "bg-blue-500" : "border-zinc-700"} onClick={() => setTargetEngine("unity")}>Unity</Button>
            </div>
            <div>
              <h4 className="text-sm font-medium text-white mb-3">Select Game Systems</h4>
              <div className="grid grid-cols-3 gap-2">
                {openWorldSystems.map((system) => {
                  const Icon = SYSTEM_ICONS[system.id] || Sparkles;
                  const isSelected = selectedSystems.includes(system.id);
                  return (
                    <button key={system.id} onClick={() => toggleSystem(system.id)}
                      className={`p-3 rounded-lg border text-left transition-all ${isSelected ? 'bg-cyan-500/20 border-cyan-500/50' : 'bg-zinc-900 border-zinc-700 hover:border-zinc-600'}`}>
                      <div className="flex items-center gap-2 mb-1">
                        <Icon className={`w-4 h-4 ${isSelected ? 'text-cyan-400' : 'text-zinc-500'}`} />
                        <span className={`text-sm font-medium ${isSelected ? 'text-cyan-400' : 'text-zinc-300'}`}>{system.name}</span>
                      </div>
                      <p className="text-[10px] text-zinc-500 line-clamp-1">{system.description}</p>
                      <div className="flex gap-2 mt-2 text-[10px] text-zinc-600">
                        <span>{system.files_estimate} files</span>
                        <span>~{system.time_estimate_minutes}m</span>
                      </div>
                    </button>
                  );
                })}
              </div>
              <p className="text-xs text-zinc-500 mt-2">{selectedSystems.length} systems selected</p>
            </div>
            <Button onClick={runSimulation} disabled={simulating || selectedSystems.length === 0} className="w-full bg-cyan-500 hover:bg-cyan-600">
              {simulating ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Simulating...</> : <><Radio className="w-4 h-4 mr-2" />Run Simulation</>}
            </Button>
            {simulationResult && (
              <div className="space-y-4 border-t border-zinc-700 pt-4">
                <h4 className="font-rajdhani font-bold text-white">Simulation Results</h4>
                <div className="grid grid-cols-4 gap-3">
                  {[
                    { icon: Clock, color: "text-blue-400", value: simulationResult.estimated_build_time, label: "Build Time" },
                    { icon: FileCode, color: "text-emerald-400", value: simulationResult.file_count, label: "Files" },
                    { icon: Package, color: "text-amber-400", value: `${simulationResult.total_size_kb}KB`, label: "Total Size" },
                    { icon: Sparkles, color: "text-purple-400", value: `${simulationResult.feasibility_score}%`, label: "Feasibility" },
                  ].map(({ icon: Icon, color, value, label }) => (
                    <div key={label} className="p-3 rounded bg-zinc-900 border border-zinc-800">
                      <Icon className={`w-5 h-5 ${color} mb-1`} />
                      <p className="text-lg font-bold text-white">{value}</p>
                      <p className="text-[10px] text-zinc-500">{label}</p>
                    </div>
                  ))}
                </div>
                {simulationResult.warnings?.length > 0 && (
                  <div className="space-y-2">
                    <h5 className="text-sm font-medium text-amber-400 flex items-center gap-2"><AlertTriangle className="w-4 h-4" />Warnings ({simulationResult.warnings.length})</h5>
                    {simulationResult.warnings.map((w, i) => (
                      <div key={i} className={`p-3 rounded border ${w.severity === 'high' ? 'bg-red-500/10 border-red-500/30' : w.severity === 'medium' ? 'bg-amber-500/10 border-amber-500/30' : 'bg-zinc-800 border-zinc-700'}`}>
                        <p className="text-sm text-zinc-200">{w.message}</p>
                        <p className="text-xs text-zinc-500 mt-1">{w.suggestion}</p>
                      </div>
                    ))}
                  </div>
                )}
                <div className="p-3 rounded bg-zinc-900 border border-zinc-800">
                  <h5 className="text-sm font-medium text-white mb-2">Architecture Summary</h5>
                  <p className="text-xs text-zinc-400">{simulationResult.architecture_summary}</p>
                </div>
                {simulationResult.ready_to_build && (
                  <div className="p-4 rounded-lg bg-gradient-to-r from-purple-500/10 to-blue-500/10 border border-purple-500/30">
                    <div className="flex items-center gap-2 mb-3">
                      <Checkbox id="schedule-build" checked={scheduleBuild} onCheckedChange={setScheduleBuild} />
                      <label htmlFor="schedule-build" className="text-sm text-white flex items-center gap-2 cursor-pointer">
                        <Clock className="w-4 h-4 text-purple-400" />Schedule for tonight (12+ hour build)
                      </label>
                    </div>
                    {scheduleBuild && (
                      <div className="mt-3">
                        <label className="text-xs text-zinc-400 mb-2 block">Start build at:</label>
                        <Input type="datetime-local" value={scheduleTime} onChange={(e) => setScheduleTime(e.target.value)} className="bg-zinc-900 border-zinc-700" data-testid="schedule-time-input" />
                        <p className="text-[10px] text-zinc-500 mt-2">Set it before bed and wake up to a complete project!</p>
                      </div>
                    )}
                  </div>
                )}
                <Button
                  onClick={() => startAutonomousBuild(scheduleBuild)}
                  disabled={!simulationResult.ready_to_build || buildRunning || (scheduleBuild && !scheduleTime)}
                  className={`w-full ${simulationResult.ready_to_build ? (scheduleBuild ? 'bg-purple-500 hover:bg-purple-600' : 'bg-emerald-500 hover:bg-emerald-600') : 'bg-zinc-700 cursor-not-allowed'}`}>
                  {buildRunning ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Starting...</> :
                    !simulationResult.ready_to_build ? <><AlertTriangle className="w-4 h-4 mr-2" />Resolve Warnings First</> :
                    scheduleBuild ? <><Clock className="w-4 h-4 mr-2" />Schedule Overnight Build</> :
                    <><Rocket className="w-4 h-4 mr-2" />Start Build Now</>}
                </Button>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* ── Build Status Chips ────────────────────────────────────────── */}
      {currentBuild?.status === "scheduled" && (
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-purple-500/20 border border-purple-500/50">
          <Clock className="w-4 h-4 text-purple-400" />
          <span className="text-xs text-purple-400">Scheduled {currentBuild.scheduled_at ? new Date(currentBuild.scheduled_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}</span>
          <Button variant="ghost" size="icon" className="h-5 w-5" onClick={startScheduledBuildNow}><Play className="w-3 h-3" /></Button>
          <Button variant="ghost" size="icon" className="h-5 w-5" onClick={cancelBuild}><span className="text-red-400 text-xs">✕</span></Button>
        </div>
      )}
      {currentBuild?.status === "running" && (
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/20 border border-blue-500/50">
          <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
          <span className="text-xs text-blue-400">Building {currentBuild.progress_percent}%</span>
          <Button variant="ghost" size="icon" className="h-5 w-5" onClick={pauseBuild}><span className="text-blue-400 text-xs">⏸</span></Button>
        </div>
      )}

      {/* ── Demo Dialog ───────────────────────────────────────────────── */}
      {currentDemo?.status === "ready" && (
        <Dialog open={demoDialogOpen} onOpenChange={setDemoDialogOpen}>
          <DialogContent className="bg-[#18181b] border-zinc-700 max-w-2xl">
            <DialogHeader>
              <DialogTitle className="font-rajdhani text-white flex items-center gap-2">
                <Gamepad2 className="w-5 h-5 text-emerald-400" />Playable Demo Ready!
              </DialogTitle>
            </DialogHeader>
            <div className="py-4 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/30">
                  <div className="flex items-center gap-2 mb-3"><Globe className="w-6 h-6 text-blue-400" /><h4 className="font-rajdhani font-bold text-white">Web Demo</h4></div>
                  <p className="text-xs text-zinc-400 mb-4">Play instantly in your browser.</p>
                  <Button onClick={openWebDemo} className="w-full bg-blue-500 hover:bg-blue-600"><Play className="w-4 h-4 mr-2" />Play in Browser</Button>
                </div>
                <div className="p-4 rounded-lg bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/30">
                  <div className="flex items-center gap-2 mb-3"><Monitor className="w-6 h-6 text-purple-400" /><h4 className="font-rajdhani font-bold text-white">Executable</h4></div>
                  <p className="text-xs text-zinc-400 mb-4">Build configs for {currentDemo.target_engine?.toUpperCase() || 'UE5'}.</p>
                  <Button variant="outline" className="w-full border-purple-500 text-purple-400" onClick={() => { setRightTab("code"); setDemoDialogOpen(false); const f = files.find(f => f.filepath?.includes("demo/")); if (f) { setSelectedFile(f); setEditorContent(f.content); } }}>
                    <FileCode className="w-4 h-4 mr-2" />View Demo Files
                  </Button>
                </div>
              </div>
              {currentDemo.demo_features?.length > 0 && (
                <div className="p-3 rounded bg-zinc-900 border border-zinc-800">
                  <h5 className="text-sm font-medium text-white mb-2">Demo Features</h5>
                  <div className="flex flex-wrap gap-2">{currentDemo.demo_features.map((f, i) => <Badge key={i} variant="outline" className="text-xs border-zinc-700 text-zinc-400">{f}</Badge>)}</div>
                </div>
              )}
              {currentDemo.controls_guide && (
                <div className="p-3 rounded bg-zinc-900 border border-zinc-800">
                  <h5 className="text-sm font-medium text-white mb-2">Controls</h5>
                  <pre className="text-xs text-zinc-400 whitespace-pre-wrap max-h-32 overflow-y-auto">{currentDemo.controls_guide.slice(0, 500)}</pre>
                </div>
              )}
              <Button variant="outline" className="w-full border-zinc-700" onClick={regenerateDemo} disabled={regeneratingDemo}>
                {regeneratingDemo ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Regenerating...</> : <><RefreshCw className="w-4 h-4 mr-2" />Regenerate Demo</>}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* ── GitHub Push Dialog ────────────────────────────────────────── */}
      <Dialog open={githubDialogOpen} onOpenChange={setGithubDialogOpen}>
        <DialogContent className="bg-[#18181b] border-zinc-700 max-w-lg">
          <DialogHeader>
            <DialogTitle className="font-rajdhani text-white flex items-center gap-2">
              <Github className="w-5 h-5" />Push to GitHub
            </DialogTitle>
          </DialogHeader>
          <div className="py-4 space-y-4">
            {projectRepoUrl && (
              <div className="flex items-center gap-2 p-3 rounded bg-emerald-500/10 border border-emerald-500/30">
                <Github className="w-4 h-4 text-emerald-400" />
                <a href={projectRepoUrl} target="_blank" rel="noopener noreferrer" className="text-xs text-emerald-400 hover:underline truncate">{projectRepoUrl}</a>
              </div>
            )}
            <div className="space-y-3">
              <div>
                <label className="text-xs text-zinc-400 mb-1.5 block">GitHub Personal Access Token</label>
                <Input
                  type="password"
                  placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                  value={githubToken}
                  onChange={(e) => setGithubToken(e.target.value)}
                  className="bg-zinc-900 border-zinc-700"
                  data-testid="github-token-input"
                />
                <p className="text-[10px] text-zinc-600 mt-1">Create at github.com → Settings → Developer settings → Personal access tokens</p>
              </div>
              <div>
                <label className="text-xs text-zinc-400 mb-1.5 block">Repository Name</label>
                <Input
                  placeholder="my-game-project"
                  value={githubRepoName}
                  onChange={(e) => setGithubRepoName(e.target.value)}
                  className="bg-zinc-900 border-zinc-700"
                  data-testid="github-repo-input"
                />
              </div>
              <div className="flex items-center gap-2">
                <Checkbox id="create-new-repo" checked={githubCreateNew} onCheckedChange={setGithubCreateNew} />
                <label htmlFor="create-new-repo" className="text-sm text-zinc-300 cursor-pointer">Create new repository (if it doesn't exist)</label>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" className="border-zinc-700" onClick={() => setGithubDialogOpen(false)}>Cancel</Button>
            <Button onClick={pushToGithub} disabled={pushing || !githubToken || !githubRepoName} className="bg-zinc-100 text-zinc-900 hover:bg-white" data-testid="github-push-btn">
              {pushing ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Pushing...</> : <><Github className="w-4 h-4 mr-2" />Push Files</>}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ── Image Generation Dialog ───────────────────────────────────── */}
      <Dialog open={imageDialogOpen} onOpenChange={setImageDialogOpen}>
        <DialogContent className="bg-[#18181b] border-zinc-700 max-w-lg">
          <DialogHeader>
            <DialogTitle className="font-rajdhani text-white flex items-center gap-2">
              <Image className="w-5 h-5 text-pink-400" />Generate Asset Image
            </DialogTitle>
          </DialogHeader>
          <div className="py-4 space-y-4">
            <div>
              <label className="text-xs text-zinc-400 mb-1.5 block">Image Prompt</label>
              <Textarea
                placeholder="Describe the image: 'dark fantasy warrior character concept art, highly detailed, cinematic lighting'"
                value={imagePrompt}
                onChange={(e) => setImagePrompt(e.target.value)}
                className="bg-zinc-900 border-zinc-700 min-h-[100px]"
                data-testid="image-prompt-input"
              />
            </div>
            <div>
              <label className="text-xs text-zinc-400 mb-1.5 block">Category</label>
              <Select value={imageCategory} onValueChange={setImageCategory}>
                <SelectTrigger className="bg-zinc-900 border-zinc-700">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-zinc-900 border-zinc-700">
                  {['concept', 'character', 'environment', 'ui', 'texture', 'icon'].map(c => (
                    <SelectItem key={c} value={c} className="capitalize">{c}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" className="border-zinc-700" onClick={() => setImageDialogOpen(false)}>Cancel</Button>
            <Button onClick={generateImage} disabled={generatingImage || !imagePrompt.trim()} className="bg-pink-500 hover:bg-pink-600" data-testid="generate-image-btn">
              {generatingImage ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Generating...</> : <><Sparkles className="w-4 h-4 mr-2" />Generate</>}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ── Memory Viewer Dialog ──────────────────────────────────────── */}
      <Dialog open={memoryDialog} onOpenChange={setMemoryDialog}>
        <DialogContent className="bg-[#18181b] border-zinc-700 max-w-2xl">
          <DialogHeader>
            <DialogTitle className="font-rajdhani text-white flex items-center gap-2">
              <Brain className="w-5 h-5 text-purple-400" />Agent Memories
            </DialogTitle>
          </DialogHeader>
          <div className="py-4 space-y-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-zinc-400">{memories?.length || 0} memories stored</p>
              <Button size="sm" variant="outline" className="border-purple-500/30 text-purple-400" onClick={extractMemories}>
                <Brain className="w-3.5 h-3.5 mr-1.5" />Extract from Chat
              </Button>
            </div>
            <ScrollArea className="h-80">
              {!memories?.length ? (
                <div className="text-center py-12">
                  <Brain className="w-12 h-12 mx-auto mb-3 text-zinc-700" />
                  <p className="text-sm text-zinc-500">No memories yet. Use "Extract from Chat" to create them.</p>
                </div>
              ) : (
                <div className="space-y-2 pr-2">
                  {memories.map((mem) => (
                    <div key={mem.id} className="p-3 rounded-lg bg-zinc-800/50 border border-zinc-700 group flex items-start gap-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-medium text-purple-400">{mem.agent_name || 'SYSTEM'}</span>
                          <Badge variant="outline" className="text-[10px] border-zinc-600 text-zinc-500">{mem.category || 'general'}</Badge>
                        </div>
                        <p className="text-sm text-zinc-300 leading-relaxed">{mem.content}</p>
                      </div>
                      <Button variant="ghost" size="icon" className="h-6 w-6 opacity-0 group-hover:opacity-100 flex-shrink-0" onClick={() => deleteMemory(mem.id)}>
                        <Trash2 className="w-3 h-3 text-red-400" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </div>
          <DialogFooter>
            <Button variant="outline" className="border-zinc-700" onClick={() => setMemoryDialog(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ── Duplicate Project Dialog ──────────────────────────────────── */}
      <Dialog open={duplicateDialog} onOpenChange={setDuplicateDialog}>
        <DialogContent className="bg-[#18181b] border-zinc-700 max-w-md">
          <DialogHeader>
            <DialogTitle className="font-rajdhani text-white flex items-center gap-2">
              <CopyPlus className="w-5 h-5 text-blue-400" />Duplicate Project
            </DialogTitle>
          </DialogHeader>
          <div className="py-4 space-y-4">
            <p className="text-sm text-zinc-400">Creates a copy of this project with all files included.</p>
            <div>
              <label className="text-xs text-zinc-400 mb-1.5 block">New Project Name</label>
              <Input
                placeholder="My Project Copy"
                value={duplicateName}
                onChange={(e) => setDuplicateName(e.target.value)}
                className="bg-zinc-900 border-zinc-700"
                data-testid="duplicate-name-input"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" className="border-zinc-700" onClick={() => setDuplicateDialog(false)}>Cancel</Button>
            <Button onClick={duplicateProject} disabled={!duplicateName.trim()} className="bg-blue-500 hover:bg-blue-600" data-testid="duplicate-project-btn">
              <CopyPlus className="w-4 h-4 mr-2" />Duplicate
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ── Code Refactor Dialog (Find & Replace / Rename) ────────────── */}
      <Dialog open={refactorDialog} onOpenChange={(open) => { setRefactorDialog(open); if (!open) setRefactorPreview(null); }}>
        <DialogContent className="bg-[#18181b] border-zinc-700 max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="font-rajdhani text-white flex items-center gap-2">
              <Search className="w-5 h-5 text-orange-400" />Code Refactor
            </DialogTitle>
          </DialogHeader>
          <div className="py-4 space-y-4">
            {/* Type selector */}
            <div>
              <label className="text-xs text-zinc-400 mb-1.5 block">Refactor Type</label>
              <Select value={refactorData?.type} onValueChange={(v) => { setRefactorData(d => ({ ...d, type: v })); setRefactorPreview(null); }}>
                <SelectTrigger className="bg-zinc-900 border-zinc-700">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-zinc-900 border-zinc-700">
                  <SelectItem value="find_replace">Find & Replace (exact text)</SelectItem>
                  <SelectItem value="rename">Rename Symbol (class/function)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Target + New Value */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-zinc-400 mb-1.5 block">
                  {refactorData?.type === 'rename' ? 'Symbol to Rename' : 'Find Text'}
                </label>
                <Input
                  placeholder={refactorData?.type === 'rename' ? "PlayerController" : "TODO: fix this"}
                  value={refactorData?.target || ''}
                  onChange={(e) => { setRefactorData(d => ({ ...d, target: e.target.value })); setRefactorPreview(null); }}
                  className="bg-zinc-900 border-zinc-700 font-mono text-sm"
                  data-testid="refactor-target-input"
                />
              </div>
              <div>
                <label className="text-xs text-zinc-400 mb-1.5 block">
                  {refactorData?.type === 'rename' ? 'New Name' : 'Replace With'}
                </label>
                <Input
                  placeholder={refactorData?.type === 'rename' ? "CharacterController" : "FIXME: fixed"}
                  value={refactorData?.new_value || ''}
                  onChange={(e) => { setRefactorData(d => ({ ...d, new_value: e.target.value })); setRefactorPreview(null); }}
                  className="bg-zinc-900 border-zinc-700 font-mono text-sm"
                  data-testid="refactor-newvalue-input"
                />
              </div>
            </div>

            <Button onClick={previewRefactor} disabled={!refactorData?.target?.trim()} variant="outline" className="border-orange-500/50 text-orange-400 hover:bg-orange-500/10" data-testid="refactor-preview-btn">
              <Search className="w-4 h-4 mr-2" />Preview Changes
            </Button>

            {/* Preview Results */}
            {refactorPreview && (
              <div className="space-y-3 border-t border-zinc-700 pt-4">
                <div className="flex items-center justify-between">
                  <h5 className="text-sm font-medium text-white flex items-center gap-2">
                    <Replace className="w-4 h-4 text-orange-400" />
                    {refactorPreview.files_affected} file(s) will change
                    <span className="text-zinc-500 text-xs">/ {refactorPreview.total_files_scanned} scanned</span>
                  </h5>
                  {refactorPreview.files_affected === 0 && (
                    <Badge className="bg-zinc-800 text-zinc-400 text-xs">No matches found</Badge>
                  )}
                </div>

                {refactorPreview.changes?.length > 0 && (
                  <ScrollArea className="h-48">
                    <div className="space-y-2 pr-2">
                      {refactorPreview.changes.map((change, i) => (
                        <div key={i} className="p-3 rounded-lg bg-zinc-800/50 border border-zinc-700">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-mono text-zinc-300">{change.filepath}</span>
                            <Badge variant="outline" className="text-[10px] border-orange-500/30 text-orange-400">
                              {change.occurrences} occurrence{change.occurrences !== 1 ? 's' : ''}
                            </Badge>
                          </div>
                          <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
                            <div className="p-2 rounded bg-red-500/10 border border-red-500/20">
                              <span className="text-red-400 block mb-1">— before</span>
                              <span className="text-zinc-400 line-clamp-2 whitespace-pre-wrap">{change.preview?.before?.substring(0, 120)}</span>
                            </div>
                            <div className="p-2 rounded bg-emerald-500/10 border border-emerald-500/20">
                              <span className="text-emerald-400 block mb-1">+ after</span>
                              <span className="text-zinc-400 line-clamp-2 whitespace-pre-wrap">{change.preview?.after?.substring(0, 120)}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                )}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" className="border-zinc-700" onClick={() => { setRefactorDialog(false); setRefactorPreview(null); setRefactorData({ type: "find_replace", target: "", new_value: "" }); }}>Cancel</Button>
            <Button
              onClick={applyRefactor}
              disabled={!refactorPreview || refactorPreview.files_affected === 0}
              className="bg-orange-500 hover:bg-orange-600"
              data-testid="refactor-apply-btn"
            >
              <CheckCircle className="w-4 h-4 mr-2" />Apply to {refactorPreview?.files_affected || 0} File(s)
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
