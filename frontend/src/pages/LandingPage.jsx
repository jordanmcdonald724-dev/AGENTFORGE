import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { 
  Bot, 
  Code2, 
  GitBranch, 
  Layers, 
  Zap, 
  ArrowRight,
  Cpu,
  Users,
  Rocket,
  Shield,
  Gamepad2,
  Globe,
  Smartphone,
  Palette,
  Sparkles,
  CheckCircle
} from "lucide-react";

const LandingPage = () => {
  const navigate = useNavigate();

  const agents = [
    { name: "COMMANDER", role: "Lead", icon: Users, color: "text-blue-400", desc: "Project Director & Coordinator" },
    { name: "ATLAS", role: "Architect", icon: Layers, color: "text-cyan-400", desc: "System Design & Architecture" },
    { name: "FORGE", role: "Developer", icon: Code2, color: "text-emerald-400", desc: "C++, C#, Blueprints Expert" },
    { name: "SENTINEL", role: "Reviewer", icon: Shield, color: "text-amber-400", desc: "Code Quality & Security" },
    { name: "PROBE", role: "Tester", icon: Zap, color: "text-purple-400", desc: "QA & Test Automation" },
    { name: "PRISM", role: "Artist", icon: Palette, color: "text-pink-400", desc: "UI/UX & Shader Expert" },
  ];

  const features = [
    {
      icon: Gamepad2,
      title: "AAA Game Development",
      description: "Unreal Engine 5, Unity, Godot - build professional games"
    },
    {
      icon: Globe,
      title: "Web Applications",
      description: "Full-stack apps with modern frameworks"
    },
    {
      icon: Smartphone,
      title: "Mobile Apps",
      description: "iOS & Android development"
    },
    {
      icon: GitBranch,
      title: "Export & Deploy",
      description: "Download as ZIP or push to GitHub"
    }
  ];

  const workflow = [
    { step: "01", title: "Describe", desc: "Tell COMMANDER your vision in detail" },
    { step: "02", title: "Clarify", desc: "Answer questions to refine the scope" },
    { step: "03", title: "Plan", desc: "Review and approve the architecture" },
    { step: "04", title: "Build", desc: "Watch agents create your project" },
  ];

  return (
    <div className="min-h-screen bg-[#09090b] overflow-hidden">
      {/* Hero */}
      <div className="hero-bg relative">
        <nav className="absolute top-0 left-0 right-0 z-50 px-6 py-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-blue-400" />
              </div>
              <span className="font-rajdhani text-xl font-bold text-white">
                AGENT<span className="text-blue-400">FORGE</span>
              </span>
            </div>
            <Button 
              data-testid="nav-start-btn"
              onClick={() => navigate("/dashboard")}
              className="bg-blue-500 hover:bg-blue-600"
            >
              Launch Studio
            </Button>
          </div>
        </nav>

        <div className="max-w-7xl mx-auto px-6 pt-32 pb-24">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 mb-8">
              <Sparkles className="w-4 h-4 text-blue-400" />
              <span className="text-sm text-blue-400">Personal AI Development Studio</span>
            </div>
            
            <h1 className="font-rajdhani text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight">
              YOUR <span className="text-blue-400">6-AGENT</span><br />
              DEV TEAM
            </h1>
            <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10">
              Build AAA games, full-stack apps, and everything in between. 
              Six specialized AI agents. One unified workflow. Complete control.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                data-testid="hero-start-btn"
                onClick={() => navigate("/dashboard")}
                size="lg"
                className="bg-blue-500 hover:bg-blue-600 text-white px-10 py-6 text-lg font-medium glow-blue btn-glow"
              >
                Start Building <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </div>
          </motion.div>

          {/* Agent Grid */}
          <motion.div 
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mt-20 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4"
          >
            {agents.map((agent, index) => (
              <motion.div
                key={agent.name}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.4 + index * 0.08 }}
                data-testid={`landing-agent-${agent.name.toLowerCase()}`}
                className="glass rounded-lg p-4 text-center group hover:border-blue-500/50 transition-all"
              >
                <div className={`w-12 h-12 mx-auto mb-3 rounded-lg bg-zinc-800 flex items-center justify-center ${agent.color} group-hover:scale-110 transition-transform`}>
                  <agent.icon className="w-6 h-6" />
                </div>
                <h3 className="font-rajdhani font-bold text-white text-sm">{agent.name}</h3>
                <p className="text-xs text-zinc-500 mt-1">{agent.role}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>

      {/* Workflow Section */}
      <section className="py-20 px-6 bg-[#0d0d0f]">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="font-rajdhani text-3xl md:text-4xl font-bold text-white mb-4">
              HOW IT <span className="text-cyan-400">WORKS</span>
            </h2>
            <p className="text-zinc-400">You stay in complete control at every step</p>
          </motion.div>

          <div className="grid md:grid-cols-4 gap-6">
            {workflow.map((item, idx) => (
              <motion.div
                key={item.step}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
                className="relative"
              >
                <div className="bg-[#18181b] border border-zinc-800 rounded-lg p-6 text-center hover:border-blue-500/30 transition-colors h-full">
                  <div className="text-4xl font-rajdhani font-bold text-blue-500/30 mb-2">{item.step}</div>
                  <h3 className="font-rajdhani font-bold text-white text-lg mb-2">{item.title}</h3>
                  <p className="text-sm text-zinc-500">{item.desc}</p>
                </div>
                {idx < workflow.length - 1 && (
                  <div className="hidden md:block absolute top-1/2 -right-3 transform -translate-y-1/2 text-zinc-700">
                    <ArrowRight className="w-6 h-6" />
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="font-rajdhani text-3xl md:text-4xl font-bold text-white mb-4">
              BUILD <span className="text-emerald-400">ANYTHING</span>
            </h2>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, idx) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
                className="bg-[#18181b] border border-zinc-800 rounded-lg p-6 hover:border-blue-500/30 transition-colors"
              >
                <div className="w-12 h-12 rounded-lg bg-blue-500/10 flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-blue-400" />
                </div>
                <h3 className="font-rajdhani font-bold text-white text-lg mb-2">{feature.title}</h3>
                <p className="text-sm text-zinc-500">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Key Benefits */}
      <section className="py-20 px-6 bg-[#0d0d0f]">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="glass rounded-2xl p-10"
          >
            <h2 className="font-rajdhani text-2xl md:text-3xl font-bold text-white mb-8 text-center">
              WHY AGENTFORGE?
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              {[
                "Clarifies before coding - no guessing",
                "You approve every major decision",
                "Full code editor with Monaco",
                "Export projects anytime",
                "Six specialized agents working together",
                "Supports AAA game engines"
              ].map((benefit, idx) => (
                <div key={idx} className="flex items-center gap-3 text-zinc-300">
                  <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                  <span>{benefit}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
          >
            <h2 className="font-rajdhani text-3xl md:text-4xl font-bold text-white mb-4">
              READY TO BUILD?
            </h2>
            <p className="text-zinc-400 mb-8">Your AI dev team is standing by.</p>
            <Button 
              data-testid="cta-btn"
              onClick={() => navigate("/dashboard")}
              size="lg"
              className="bg-blue-500 hover:bg-blue-600 px-12 py-6 text-lg glow-blue btn-glow"
            >
              Launch Studio <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-zinc-800">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-400" />
            <span className="font-rajdhani font-bold text-white">AGENTFORGE</span>
          </div>
          <p className="text-sm text-zinc-500">Powered by fal.ai • Your Personal Dev Studio</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
