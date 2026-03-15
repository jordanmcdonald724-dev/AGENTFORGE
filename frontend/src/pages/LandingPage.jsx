import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { 
  ArrowRight,
  Sparkles,
  Users,
  Layers,
  Code2,
  Shield,
  Zap,
  Palette,
  Gamepad2,
  Globe,
  Smartphone,
  Rocket,
  ChevronRight,
  Brain,
  FlaskConical
} from "lucide-react";

const LandingPage = () => {
  const navigate = useNavigate();

  const agents = [
    { name: "COMMANDER", role: "Lead", icon: Users, color: "#3b82f6" },
    { name: "ATLAS", role: "Architect", icon: Layers, color: "#06b6d4" },
    { name: "FORGE", role: "Developer", icon: Code2, color: "#10b981" },
    { name: "SENTINEL", role: "Reviewer", icon: Shield, color: "#f97316" },
    { name: "PROBE", role: "Tester", icon: Zap, color: "#8b5cf6" },
    { name: "PRISM", role: "Artist", icon: Palette, color: "#ec4899" },
    { name: "SONIC", role: "Audio", icon: Users, color: "#14b8a6" },
    { name: "NEXUS", role: "Designer", icon: Gamepad2, color: "#f59e0b" },
    { name: "CHRONICLE", role: "Writer", icon: Users, color: "#a855f7" },
    { name: "VERTEX", role: "VFX", icon: Sparkles, color: "#22c55e" },
    { name: "TERRA", role: "Level Design", icon: Globe, color: "#84cc16" },
    { name: "KINETIC", role: "Animator", icon: Zap, color: "#06b6d4" },
  ];

  const capabilities = [
    { icon: Gamepad2, label: "AAA Games", desc: "Unreal, Unity, Godot" },
    { icon: Globe, label: "Web Apps", desc: "Full-stack development" },
    { icon: Smartphone, label: "Mobile", desc: "iOS & Android" },
    { icon: Rocket, label: "Deploy", desc: "One-click export" },
  ];

  return (
    <div className="min-h-screen bg-[#09090b] overflow-hidden flex">
      {/* Sidebar */}
      <aside className="relative z-50 w-64 border-r border-white/10 bg-black/40 backdrop-blur-xl flex flex-col">
        <div className="p-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold tracking-tight">
              Agent<span className="text-blue-400">Forge</span>
            </span>
          </div>
        </div>
        
        <nav className="flex-1 p-4">
          <div className="space-y-2">
            <Button
              onClick={() => navigate("/studio")}
              variant="ghost"
              className="w-full justify-start text-white hover:bg-white/10"
            >
              <Rocket className="w-4 h-4 mr-3" />
              Studio
            </Button>
            <Button
              onClick={() => navigate("/god-mode")}
              variant="ghost"
              className="w-full justify-start text-white hover:bg-white/10"
            >
              <Brain className="w-4 h-4 mr-3" />
              God Mode
            </Button>
            <Button
              onClick={() => navigate("/research")}
              variant="ghost"
              className="w-full justify-start text-white hover:bg-white/10"
            >
              <FlaskConical className="w-4 h-4 mr-3" />
              Research Lab
            </Button>
          </div>
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        {/* Background Effects */}
        <div className="fixed inset-0 gradient-mesh opacity-60 pointer-events-none" />
        <div className="fixed inset-0 bg-gradient-to-b from-transparent via-transparent to-[#09090b] pointer-events-none" />

      {/* Hero Section */}
      <main className="relative z-10">
        <div className="max-w-6xl mx-auto px-6 pt-20 pb-32">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            {/* Badge */}
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8"
            >
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-sm text-zinc-400">AI Development Studio</span>
            </motion.div>
            
            {/* Headline */}
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6">
              <span className="text-white">Your </span>
              <span className="bg-gradient-to-r from-blue-400 via-cyan-400 to-emerald-400 bg-clip-text text-transparent">
                12-Agent
              </span>
              <br />
              <span className="text-white">Dev Team</span>
            </h1>
            
            {/* Subheadline */}
            <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-12 leading-relaxed">
              Build AAA games, full-stack apps, and everything in between.
              <br className="hidden md:block" />
              Twelve specialized AI agents. One unified workflow.
            </p>
            
            {/* CTA */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Button 
                onClick={() => navigate("/studio")}
                size="lg"
                className="bg-blue-500 hover:bg-blue-600 text-white px-8 py-6 text-base font-medium rounded-xl shadow-lg shadow-blue-500/25 transition-all hover:shadow-blue-500/40 hover:scale-[1.02]"
                data-testid="hero-start-btn"
              >
                Start Building
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </motion.div>
          </motion.div>

          {/* Agent Cards */}
          <motion.div 
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="mt-24 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3"
          >
            {agents.map((agent, index) => (
              <motion.div
                key={agent.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 + index * 0.05 }}
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
                className="group relative p-5 rounded-2xl bg-white/[0.02] border border-white/[0.05] hover:border-white/10 hover:bg-white/[0.04] transition-all cursor-pointer"
                data-testid={`landing-agent-${agent.name.toLowerCase()}`}
              >
                <div 
                  className="w-10 h-10 rounded-xl flex items-center justify-center mb-4 transition-transform group-hover:scale-110"
                  style={{ backgroundColor: `${agent.color}15` }}
                >
                  <agent.icon className="w-5 h-5" style={{ color: agent.color }} />
                </div>
                <h3 className="font-semibold text-white text-sm tracking-wide">{agent.name}</h3>
                <p className="text-xs text-zinc-500 mt-1">{agent.role}</p>
                
                {/* Glow effect on hover */}
                <div 
                  className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"
                  style={{ boxShadow: `0 0 40px -15px ${agent.color}` }}
                />
              </motion.div>
            ))}
          </motion.div>
        </div>

        {/* Capabilities Section */}
        <section className="relative py-24 border-t border-white/5">
          <div className="max-w-6xl mx-auto px-6">
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                Build Anything
              </h2>
              <p className="text-zinc-500 text-lg">From concept to deployment</p>
            </motion.div>

            <div className="grid md:grid-cols-4 gap-4">
              {capabilities.map((cap, idx) => (
                <motion.div
                  key={cap.label}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: idx * 0.1 }}
                  className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.05] hover:border-white/10 transition-all"
                >
                  <cap.icon className="w-8 h-8 text-zinc-400 mb-4" />
                  <h3 className="text-white font-semibold mb-1">{cap.label}</h3>
                  <p className="text-sm text-zinc-500">{cap.desc}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Workflow Section */}
        <section className="relative py-24 border-t border-white/5">
          <div className="max-w-4xl mx-auto px-6">
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                How It Works
              </h2>
              <p className="text-zinc-500 text-lg">Four simple steps to production</p>
            </motion.div>

            <div className="space-y-4">
              {[
                { step: "01", title: "Describe", desc: "Tell the agents your vision" },
                { step: "02", title: "Plan", desc: "Review the architecture" },
                { step: "03", title: "Build", desc: "Watch agents create your project" },
                { step: "04", title: "Deploy", desc: "Export or push to GitHub" },
              ].map((item, idx) => (
                <motion.div
                  key={item.step}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: idx * 0.1 }}
                  className="flex items-center gap-6 p-5 rounded-xl bg-white/[0.02] border border-white/[0.05] hover:border-white/10 transition-all group"
                >
                  <span className="text-3xl font-bold text-zinc-700 group-hover:text-zinc-500 transition-colors">
                    {item.step}
                  </span>
                  <div className="flex-1">
                    <h3 className="text-white font-semibold">{item.title}</h3>
                    <p className="text-sm text-zinc-500">{item.desc}</p>
                  </div>
                  <ChevronRight className="w-5 h-5 text-zinc-600 group-hover:text-zinc-400 group-hover:translate-x-1 transition-all" />
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Final CTA */}
        <section className="relative py-32">
          <div className="max-w-4xl mx-auto px-6 text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                Ready to build?
              </h2>
              <p className="text-xl text-zinc-400 mb-10">
                Your AI development team is waiting.
              </p>
              <Button 
                onClick={() => navigate("/studio")}
                size="lg"
                className="bg-white text-black hover:bg-zinc-200 px-10 py-6 text-base font-medium rounded-xl transition-all hover:scale-[1.02]"
              >
                Launch Studio
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </motion.div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/5 py-8">
        <div className="max-w-6xl mx-auto px-6 flex items-center justify-between">
          <div className="flex items-center gap-2 text-zinc-500 text-sm">
            <Sparkles className="w-4 h-4" />
            <span>AgentForge</span>
          </div>
          <p className="text-zinc-600 text-sm">AI Development Studio</p>
        </div>
      </footer>
      </div>
    </div>
  );
};

export default LandingPage;
