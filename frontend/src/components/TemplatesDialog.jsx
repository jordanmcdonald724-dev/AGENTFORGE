import { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { X, Sparkles, Check, Loader2 } from "lucide-react";
import { API } from "@/App";

const TemplateCard = ({ template, onSelect }) => {
  return (
    <motion.div
      whileHover={{ y: -4 }}
      className="group relative bg-gradient-to-br from-white/5 to-white/[0.02] border border-white/10 rounded-xl p-6 cursor-pointer hover:border-blue-500/50 transition-all"
      onClick={() => onSelect(template)}
    >
      {/* Icon */}
      <div className="text-5xl mb-4">{template.icon}</div>
      
      {/* Name */}
      <h3 className="text-xl font-semibold text-white mb-2 group-hover:text-blue-400 transition-colors">
        {template.name}
      </h3>
      
      {/* Description */}
      <p className="text-sm text-zinc-400 mb-4 line-clamp-2">
        {template.description}
      </p>
      
      {/* Category Badge */}
      <Badge variant="outline" className="mb-4 capitalize">
        {template.category}
      </Badge>
      
      {/* Tech Stack */}
      <div className="flex flex-wrap gap-1.5 mb-4">
        {template.tech_stack.slice(0, 3).map((tech, i) => (
          <span key={i} className="text-xs px-2 py-1 rounded bg-white/5 text-zinc-400">
            {tech}
          </span>
        ))}
        {template.tech_stack.length > 3 && (
          <span className="text-xs px-2 py-1 rounded bg-white/5 text-zinc-400">
            +{template.tech_stack.length - 3}
          </span>
        )}
      </div>
      
      {/* Hover Effect */}
      <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-blue-500/10 to-cyan-500/10 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
    </motion.div>
  );
};

const TemplateDetailDialog = ({ template, open, onClose, onCreate }) => {
  const [projectName, setProjectName] = useState(template?.name || "");
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    if (template) {
      setProjectName(template.name);
    }
  }, [template]);

  const handleCreate = async () => {
    if (!projectName.trim()) {
      toast.error("Please enter a project name");
      return;
    }

    setCreating(true);
    try {
      await onCreate(template.id, projectName);
    } finally {
      setCreating(false);
    }
  };

  if (!template) return null;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="bg-zinc-900 border-white/10 max-w-2xl max-h-[80vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3 text-2xl">
            <span className="text-4xl">{template.icon}</span>
            <span className="text-white">{template.name}</span>
          </DialogTitle>
        </DialogHeader>

        <ScrollArea className="flex-1 pr-4">
          {/* Description */}
          <p className="text-zinc-300 mb-6">{template.description}</p>

          {/* Tech Stack */}
          <div className="mb-6">
            <h4 className="text-sm font-medium text-zinc-400 mb-2">Tech Stack</h4>
            <div className="flex flex-wrap gap-2">
              {template.tech_stack.map((tech, i) => (
                <Badge key={i} variant="secondary" className="bg-white/5 text-white border-white/10">
                  {tech}
                </Badge>
              ))}
            </div>
          </div>

          {/* Features */}
          <div className="mb-6">
            <h4 className="text-sm font-medium text-zinc-400 mb-3">What's Included</h4>
            <div className="space-y-2">
              {template.features.map((feature, i) => (
                <div key={i} className="flex items-start gap-2 text-sm text-zinc-300">
                  <Check className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                  <span>{feature}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Project Name Input */}
          <div className="mb-4">
            <label className="text-sm font-medium text-zinc-400 mb-2 block">
              Project Name
            </label>
            <Input
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="My Awesome Project"
              className="bg-white/5 border-white/10 text-white"
            />
          </div>
        </ScrollArea>

        {/* Actions */}
        <div className="flex gap-3 pt-4 border-t border-white/10">
          <Button
            variant="outline"
            onClick={onClose}
            className="flex-1"
            disabled={creating}
          >
            Cancel
          </Button>
          <Button
            onClick={handleCreate}
            disabled={creating || !projectName.trim()}
            className="flex-1 bg-blue-500 hover:bg-blue-600"
          >
            {creating ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Create Project
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default function TemplatesDialog({ open, onClose }) {
  const navigate = useNavigate();
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [detailOpen, setDetailOpen] = useState(false);

  useEffect(() => {
    if (open) {
      fetchTemplates();
    }
  }, [open]);

  const fetchTemplates = async () => {
    try {
      const res = await axios.get(`${API}/templates`);
      setTemplates(res.data);
    } catch (error) {
      toast.error("Failed to load templates");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectTemplate = (template) => {
    setSelectedTemplate(template);
    setDetailOpen(true);
  };

  const handleCreateProject = async (templateId, projectName) => {
    try {
      const res = await axios.post(
        `${API}/templates/${templateId}/create`,
        null,
        { params: { project_name: projectName } }
      );

      toast.success("Project created from template!", {
        description: `${res.data.files_created} files created`
      });

      // Navigate to the new project
      navigate(`/project/${res.data.project.id}`);
      
      setDetailOpen(false);
      onClose();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to create project");
    }
  };

  return (
    <>
      <Dialog open={open} onOpenChange={onClose}>
        <DialogContent className="bg-zinc-900 border-white/10 max-w-6xl max-h-[85vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-2xl">
              <Sparkles className="w-6 h-6 text-blue-400" />
              <span className="text-white">Start from Template</span>
            </DialogTitle>
            <p className="text-sm text-zinc-400">
              Choose a pre-built, production-ready template to start instantly
            </p>
          </DialogHeader>

          <ScrollArea className="flex-1">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
              </div>
            ) : templates.length === 0 ? (
              <div className="text-center py-12 text-zinc-400">
                No templates available
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-1">
                {templates.map((template) => (
                  <TemplateCard
                    key={template.id}
                    template={template}
                    onSelect={handleSelectTemplate}
                  />
                ))}
              </div>
            )}
          </ScrollArea>
        </DialogContent>
      </Dialog>

      <TemplateDetailDialog
        template={selectedTemplate}
        open={detailOpen}
        onClose={() => setDetailOpen(false)}
        onCreate={handleCreateProject}
      />
    </>
  );
}
