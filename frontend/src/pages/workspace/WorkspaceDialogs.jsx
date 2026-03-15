/**
 * WorkspaceDialogs — Simulation + Demo dialogs extracted from ProjectWorkspace
 * Pure presentation — all state and handlers passed as props.
 */
import { Loader2, Radio, Sparkles, FileCode, Clock, AlertTriangle, Rocket,
  Gamepad2, Globe, Monitor, Play, RefreshCw, Package } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
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
  // Simulation
  simulationDialog, setSimulationDialog,
  openWorldSystems, targetEngine, setTargetEngine,
  selectedSystems, toggleSystem, simulating, simulationResult,
  runSimulation, scheduleBuild, setScheduleBuild,
  scheduleTime, setScheduleTime, buildRunning, startAutonomousBuild,
  // Build status
  currentBuild, startScheduledBuildNow, cancelBuild, pauseBuild,
  // Demo
  demoDialogOpen, setDemoDialogOpen,
  currentDemo, openWebDemo, files,
  setRightTab, setSelectedFile, setEditorContent,
  regenerateDemo, regeneratingDemo,
}) {
  return (
    <>
      {/* ── Simulation Dialog (controlled — opened via Settings dropdown) ───── */}
      <Dialog open={simulationDialog} onOpenChange={setSimulationDialog}>
        <DialogContent className="bg-[#18181b] border-zinc-700 max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="font-rajdhani text-white flex items-center gap-2">
              <Radio className="w-5 h-5 text-cyan-400" />Build Simulation (Dry Run)
            </DialogTitle>
          </DialogHeader>
          <div className="py-4 space-y-4">
            {/* Engine Selection */}
            <div className="flex gap-4">
              <Button variant={targetEngine === "unreal" ? "default" : "outline"}
                className={targetEngine === "unreal" ? "bg-blue-500" : "border-zinc-700"}
                onClick={() => setTargetEngine("unreal")}>Unreal Engine 5</Button>
              <Button variant={targetEngine === "unity" ? "default" : "outline"}
                className={targetEngine === "unity" ? "bg-blue-500" : "border-zinc-700"}
                onClick={() => setTargetEngine("unity")}>Unity</Button>
            </div>

            {/* System Selection */}
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

            <Button onClick={runSimulation} disabled={simulating || selectedSystems.length === 0}
              className="w-full bg-cyan-500 hover:bg-cyan-600">
              {simulating ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Simulating...</> : <><Radio className="w-4 h-4 mr-2" />Run Simulation</>}
            </Button>

            {simulationResult && (
              <div className="space-y-4 border-t border-zinc-700 pt-4">
                <h4 className="font-rajdhani font-bold text-white">Simulation Results</h4>
                <div className="grid grid-cols-4 gap-3">
                  <div className="p-3 rounded bg-zinc-900 border border-zinc-800">
                    <Clock className="w-5 h-5 text-blue-400 mb-1" />
                    <p className="text-lg font-bold text-white">{simulationResult.estimated_build_time}</p>
                    <p className="text-[10px] text-zinc-500">Build Time</p>
                  </div>
                  <div className="p-3 rounded bg-zinc-900 border border-zinc-800">
                    <FileCode className="w-5 h-5 text-emerald-400 mb-1" />
                    <p className="text-lg font-bold text-white">{simulationResult.file_count}</p>
                    <p className="text-[10px] text-zinc-500">Files</p>
                  </div>
                  <div className="p-3 rounded bg-zinc-900 border border-zinc-800">
                    <Package className="w-5 h-5 text-amber-400 mb-1" />
                    <p className="text-lg font-bold text-white">{simulationResult.total_size_kb}KB</p>
                    <p className="text-[10px] text-zinc-500">Total Size</p>
                  </div>
                  <div className="p-3 rounded bg-zinc-900 border border-zinc-800">
                    <Sparkles className="w-5 h-5 text-purple-400 mb-1" />
                    <p className="text-lg font-bold text-white">{simulationResult.feasibility_score}%</p>
                    <p className="text-[10px] text-zinc-500">Feasibility</p>
                  </div>
                </div>

                {simulationResult.warnings?.length > 0 && (
                  <div className="space-y-2">
                    <h5 className="text-sm font-medium text-amber-400 flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4" />Warnings ({simulationResult.warnings.length})
                    </h5>
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
                      <input type="checkbox" id="schedule-build" checked={scheduleBuild}
                        onChange={(e) => setScheduleBuild(e.target.checked)} className="rounded" />
                      <label htmlFor="schedule-build" className="text-sm text-white flex items-center gap-2">
                        <Clock className="w-4 h-4 text-purple-400" />Schedule for tonight (12+ hour build)
                      </label>
                    </div>
                    {scheduleBuild && (
                      <div className="mt-3">
                        <label className="text-xs text-zinc-400 mb-2 block">Start build at:</label>
                        <Input type="datetime-local" value={scheduleTime}
                          onChange={(e) => setScheduleTime(e.target.value)}
                          className="bg-zinc-900 border-zinc-700" data-testid="schedule-time-input" />
                        <p className="text-[10px] text-zinc-500 mt-2">Set it before bed and wake up to a complete project!</p>
                      </div>
                    )}
                  </div>
                )}

                <div className="flex gap-2">
                  {scheduleBuild ? (
                    <Button onClick={() => startAutonomousBuild(true)}
                      disabled={!simulationResult.ready_to_build || buildRunning || !scheduleTime}
                      className={`flex-1 ${simulationResult.ready_to_build && scheduleTime ? 'bg-purple-500 hover:bg-purple-600' : 'bg-zinc-700 cursor-not-allowed'}`}>
                      {buildRunning ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Scheduling...</> : <><Clock className="w-4 h-4 mr-2" />Schedule Overnight Build</>}
                    </Button>
                  ) : (
                    <Button onClick={() => startAutonomousBuild(false)}
                      disabled={!simulationResult.ready_to_build || buildRunning}
                      className={`flex-1 ${simulationResult.ready_to_build ? 'bg-emerald-500 hover:bg-emerald-600' : 'bg-zinc-700 cursor-not-allowed'}`}>
                      {buildRunning ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Starting...</> :
                        simulationResult.ready_to_build ? <><Rocket className="w-4 h-4 mr-2" />Start Build Now</> :
                        <><AlertTriangle className="w-4 h-4 mr-2" />Resolve Warnings First</>}
                    </Button>
                  )}
                </div>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* ── Build Status Badges ────────────────────────────────────── */}
      {currentBuild?.status === "scheduled" && (
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-purple-500/20 border border-purple-500/50">
          <Clock className="w-4 h-4 text-purple-400" />
          <span className="text-xs text-purple-400">
            Scheduled {currentBuild.scheduled_at ? new Date(currentBuild.scheduled_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
          </span>
          <Button variant="ghost" size="icon" className="h-5 w-5" onClick={startScheduledBuildNow} title="Start Now">
            <Play className="w-3 h-3" />
          </Button>
          <Button variant="ghost" size="icon" className="h-5 w-5" onClick={cancelBuild} title="Cancel">
            <span className="text-red-400">✕</span>
          </Button>
        </div>
      )}
      {currentBuild?.status === "running" && (
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/20 border border-blue-500/50">
          <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
          <span className="text-xs text-blue-400">Building {currentBuild.progress_percent}%</span>
          <Progress value={currentBuild.progress_percent || 0} className="w-16 h-1.5" />
          <Button variant="ghost" size="icon" className="h-5 w-5" onClick={pauseBuild}>
            <span className="text-blue-400">⏸</span>
          </Button>
        </div>
      )}

      {/* ── Demo Dialog ────────────────────────────────────────────── */}
      {currentDemo?.status === "ready" && (
        <Dialog open={demoDialogOpen} onOpenChange={setDemoDialogOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm" className="border-emerald-700 text-emerald-400 hover:bg-emerald-500/10" data-testid="demo-btn">
              <Gamepad2 className="w-4 h-4 mr-1" />Play Demo
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-[#18181b] border-zinc-700 max-w-2xl">
            <DialogHeader>
              <DialogTitle className="font-rajdhani text-white flex items-center gap-2">
                <Gamepad2 className="w-5 h-5 text-emerald-400" />Playable Demo Ready!
              </DialogTitle>
            </DialogHeader>
            <div className="py-4 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/30">
                  <div className="flex items-center gap-2 mb-3">
                    <Globe className="w-6 h-6 text-blue-400" />
                    <h4 className="font-rajdhani font-bold text-white">Web Demo</h4>
                  </div>
                  <p className="text-xs text-zinc-400 mb-4">Play instantly in your browser.</p>
                  <Button onClick={openWebDemo} className="w-full bg-blue-500 hover:bg-blue-600">
                    <Play className="w-4 h-4 mr-2" />Play in Browser
                  </Button>
                </div>
                <div className="p-4 rounded-lg bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/30">
                  <div className="flex items-center gap-2 mb-3">
                    <Monitor className="w-6 h-6 text-purple-400" />
                    <h4 className="font-rajdhani font-bold text-white">Executable</h4>
                  </div>
                  <p className="text-xs text-zinc-400 mb-4">Build configs for {currentDemo.target_engine?.toUpperCase() || 'UE5'}.</p>
                  <Button variant="outline" className="w-full border-purple-500 text-purple-400" onClick={() => {
                    setRightTab("code"); setDemoDialogOpen(false);
                    const f = files.find(f => f.filepath?.includes("demo/"));
                    if (f) { setSelectedFile(f); setEditorContent(f.content); }
                  }}>
                    <FileCode className="w-4 h-4 mr-2" />View Demo Files
                  </Button>
                </div>
              </div>

              {currentDemo.demo_features?.length > 0 && (
                <div className="p-3 rounded bg-zinc-900 border border-zinc-800">
                  <h5 className="text-sm font-medium text-white mb-2">Demo Features</h5>
                  <div className="flex flex-wrap gap-2">
                    {currentDemo.demo_features.map((f, i) => (
                      <Badge key={i} variant="outline" className="text-xs border-zinc-700 text-zinc-400">{f}</Badge>
                    ))}
                  </div>
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
    </>
  );
}
