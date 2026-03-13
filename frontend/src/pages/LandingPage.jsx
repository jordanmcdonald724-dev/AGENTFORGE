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
  Shield
} from "lucide-react";

const LandingPage = () => {
  const navigate = useNavigate();

  const agents = [
    { name: "NEXUS", role: "Project Manager", icon: Users, color: "text-blue-400" },
    { name: "ATLAS", role: "Architect", icon: Layers, color: "text-cyan-400" },
    { name: "FORGE", role: "Developer", icon: Code2, color: "text-emerald-400" },
    { name: "SENTINEL", role: "Reviewer", icon: Shield, color: "text-amber-400" },
    { name: "PROBE", role: "Tester", icon: Zap, color: "text-purple-400" },
  ];

  const features = [
    {
      icon: Bot,
      title: "AI-Powered Dev Team",
      description: "Five specialized AI agents working together to build your projects"
    },
    {
      icon: GitBranch,
      title: "Git Integration",
      description: "Full version control workflow with automatic commits and branches"
    },
    {
      icon: Cpu,
      title: "Unreal Engine Ready",
      description: "Build AAA game projects with Ubisoft-style architecture"
    },
    {
      icon: Rocket,
      title: "Rapid Deployment",
      description: "From concept to production in record time"
    }
  ];

  return (
    <div className="min-h-screen bg-[#09090b] overflow-hidden">
      {/* Hero Section */}
      <div className="hero-bg relative">
        {/* Navigation */}
        <nav className="absolute top-0 left-0 right-0 z-50 px-6 py-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded bg-blue-500/20 flex items-center justify-center">
                <Bot className="w-6 h-6 text-blue-400" />
              </div>
              <span className="font-rajdhani text-xl font-bold tracking-tight text-white">
                AGENT<span className="text-blue-400">FORGE</span>
              </span>
            </div>
            <Button 
              data-testid="nav-get-started-btn"
              onClick={() => navigate("/dashboard")}
              className="bg-blue-500 hover:bg-blue-600 text-white px-6"
            >
              Get Started
            </Button>
          </div>
        </nav>

        {/* Hero Content */}
        <div className="max-w-7xl mx-auto px-6 pt-32 pb-20">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <h1 className="font-rajdhani text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight">
              YOUR AI <span className="text-blue-400">DEV TEAM</span>
              <br />
              <span className="text-zinc-400">AWAITS</span>
            </h1>
            <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-10">
              Five specialized AI agents. One unified team. Build games, apps, and 
              full-stack projects with Ubisoft-level architecture.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                data-testid="hero-start-building-btn"
                onClick={() => navigate("/dashboard")}
                size="lg"
                className="bg-blue-500 hover:bg-blue-600 text-white px-8 py-6 text-lg font-medium glow-blue btn-glow"
              >
                Start Building <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
              <Button 
                data-testid="hero-view-agents-btn"
                variant="outline"
                size="lg"
                className="border-zinc-700 text-zinc-300 hover:bg-zinc-800 px-8 py-6 text-lg"
              >
                View Agent Roster
              </Button>
            </div>
          </motion.div>

          {/* Agent Cards */}
          <motion.div 
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="mt-20 grid grid-cols-2 md:grid-cols-5 gap-4"
          >
            {agents.map((agent, index) => (
              <motion.div
                key={agent.name}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.4, delay: 0.4 + index * 0.1 }}
                data-testid={`agent-card-${agent.name.toLowerCase()}`}
                className="glass rounded-lg p-4 text-center group hover:border-blue-500/50 transition-all duration-300"
              >
                <div className={`w-12 h-12 mx-auto mb-3 rounded-lg bg-zinc-800 flex items-center justify-center ${agent.color} group-hover:scale-110 transition-transform duration-300`}>
                  <agent.icon className="w-6 h-6" />
                </div>
                <h3 className="font-rajdhani font-bold text-white text-sm">{agent.name}</h3>
                <p className="text-xs text-zinc-500 mt-1">{agent.role}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>

      {/* Features Section */}
      <section className="py-20 px-6 bg-[#0d0d0f]">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="font-rajdhani text-3xl md:text-5xl font-bold text-white mb-4">
              BUILT FOR <span className="text-cyan-400">PROFESSIONALS</span>
            </h2>
            <p className="text-zinc-400 max-w-xl mx-auto">
              Enterprise-grade AI development workflow designed for studios and teams
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                data-testid={`feature-card-${index}`}
                className="bg-[#18181b] border border-zinc-800 rounded-lg p-6 hover:border-blue-500/50 transition-colors duration-300"
              >
                <div className="w-12 h-12 rounded-lg bg-blue-500/10 flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-blue-400" />
                </div>
                <h3 className="font-rajdhani font-bold text-white text-lg mb-2">{feature.title}</h3>
                <p className="text-sm text-zinc-400">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="glass rounded-2xl p-12"
          >
            <h2 className="font-rajdhani text-3xl md:text-4xl font-bold text-white mb-4">
              READY TO BUILD?
            </h2>
            <p className="text-zinc-400 mb-8">
              Your AI dev team is standing by. Start your first project in seconds.
            </p>
            <Button 
              data-testid="cta-launch-dashboard-btn"
              onClick={() => navigate("/dashboard")}
              size="lg"
              className="bg-blue-500 hover:bg-blue-600 text-white px-10 py-6 text-lg font-medium glow-blue btn-glow"
            >
              Launch Dashboard <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-zinc-800">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Bot className="w-5 h-5 text-blue-400" />
            <span className="font-rajdhani font-bold text-white">AGENTFORGE</span>
          </div>
          <p className="text-sm text-zinc-500">
            Powered by fal.ai • Built for builders
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
