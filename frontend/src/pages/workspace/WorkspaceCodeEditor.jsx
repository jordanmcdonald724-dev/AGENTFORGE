/**
 * WorkspaceCodeEditor — Right panel: file tree + Monaco editor + preview
 * All state lives in ProjectWorkspace; receives data and callbacks via props.
 */
import Editor from "@monaco-editor/react";
import { ResizablePanelGroup, ResizablePanel, ResizableHandle } from "@/components/ui/resizable";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Code2, Eye, FileCode, Folder, FolderOpen, ChevronRight,
  ChevronDown, Save, Trash2, Play
} from "lucide-react";

const LANGUAGE_MAP = {
  cpp: "cpp", "c++": "cpp", csharp: "csharp", "c#": "csharp", cs: "csharp",
  javascript: "javascript", js: "javascript", typescript: "typescript", ts: "typescript",
  python: "python", py: "python", json: "json", html: "html", css: "css",
  yaml: "yaml", yml: "yaml", markdown: "markdown", md: "markdown",
  gdscript: "python", blueprint: "json", hlsl: "cpp", glsl: "cpp"
};

export default function WorkspaceCodeEditor({
  files,
  selectedFile,
  editorContent,
  unsavedChanges,
  rightTab,
  previewHtml,
  isWebProject,
  onFileSelect,
  onEditorChange,
  onSave,
  onDeleteFile,
  onLoadPreview,
  setRightTab,
  expandedFolders,
  toggleFolder,
}) {
  // Build flat file array into a nested tree object
  const buildTree = () => {
    const tree = {};
    files.forEach(f => {
      const parts = f.filepath.split('/').filter(Boolean);
      let cur = tree;
      parts.forEach((p, i) => {
        if (i === parts.length - 1) cur[p] = f;
        else { if (!cur[p]) cur[p] = {}; cur = cur[p]; }
      });
    });
    return tree;
  };

  // Regular render function (not a component) to avoid Babel recursion issues
  const renderTree = (node, path = "", depth = 0) => {
    return Object.entries(node).map(([name, value]) => {
      const fullPath = path ? `${path}/${name}` : name;
      const isFile = value?.id;

      if (isFile) {
        return (
          <div
            key={value.id}
            className={`flex items-center gap-2 px-2 py-1.5 cursor-pointer hover:bg-zinc-800 rounded text-sm group ${selectedFile?.id === value.id ? 'bg-blue-500/20 text-blue-400' : 'text-zinc-400'}`}
            style={{ paddingLeft: `${depth * 12 + 8}px` }}
            onClick={() => onFileSelect(value)}
          >
            <FileCode className="w-4 h-4" />
            <span className="truncate flex-1">{name}</span>
            <Button variant="ghost" size="icon" className="h-6 w-6 opacity-0 group-hover:opacity-100"
              onClick={(e) => { e.stopPropagation(); onDeleteFile(value.id); }}>
              <Trash2 className="w-3 h-3 text-red-400" />
            </Button>
          </div>
        );
      }

      return (
        <div key={fullPath}>
          <div
            className="flex items-center gap-2 px-2 py-1.5 cursor-pointer hover:bg-zinc-800 rounded text-sm text-zinc-300"
            style={{ paddingLeft: `${depth * 12 + 8}px` }}
            onClick={() => toggleFolder(fullPath)}
          >
            {expandedFolders.has(fullPath) ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            {expandedFolders.has(fullPath) ? <FolderOpen className="w-4 h-4 text-amber-400" /> : <Folder className="w-4 h-4 text-amber-400" />}
            <span>{name}</span>
          </div>
          {expandedFolders.has(fullPath) && renderTree(value, fullPath, depth + 1)}
        </div>
      );
    });
  };

  return (
    <div className="h-full flex flex-col bg-[#0d0d0f]">
      {/* Header tabs */}
      <div className="flex-shrink-0 border-b border-zinc-800 bg-[#0a0a0c]">
        <div className="flex items-center justify-between px-4 py-2">
          <Tabs value={rightTab} onValueChange={setRightTab} className="w-full">
            <TabsList className="bg-transparent">
              <TabsTrigger value="code" className="data-[state=active]:bg-zinc-800">
                <Code2 className="w-4 h-4 mr-2" />Code
                {files.length > 0 && <Badge variant="secondary" className="ml-2 text-xs">{files.length}</Badge>}
              </TabsTrigger>
              {isWebProject && (
                <TabsTrigger value="preview" className="data-[state=active]:bg-zinc-800" onClick={onLoadPreview}>
                  <Eye className="w-4 h-4 mr-2" />Preview
                </TabsTrigger>
              )}
            </TabsList>
          </Tabs>
          {selectedFile && rightTab === "code" && (
            <div className="flex items-center gap-2">
              {unsavedChanges && <Badge className="bg-amber-500/20 text-amber-400 text-xs">Unsaved</Badge>}
              <Button size="sm" variant="outline" className="h-7 border-zinc-700" onClick={onSave} disabled={!unsavedChanges}>
                <Save className="w-3 h-3 mr-1" />Save
              </Button>
            </div>
          )}
        </div>
      </div>

      {rightTab === "code" ? (
        <ResizablePanelGroup direction="horizontal" className="flex-1">
          {/* File tree panel */}
          <ResizablePanel defaultSize={25} minSize={15} maxSize={40}>
            <div className="h-full flex flex-col bg-[#0a0a0c] border-r border-zinc-800">
              <div className="flex-shrink-0 px-3 py-2 border-b border-zinc-800">
                <h4 className="text-xs text-zinc-500 uppercase tracking-wider">Files</h4>
              </div>
              <ScrollArea className="flex-1">
                <div className="py-2">
                  {files.length === 0 ? (
                    <div className="px-4 py-8 text-center">
                      <Folder className="w-8 h-8 mx-auto mb-2 text-zinc-700" />
                      <p className="text-xs text-zinc-600">No files yet</p>
                    </div>
                  ) : renderTree(buildTree())}
                </div>
              </ScrollArea>
            </div>
          </ResizablePanel>

          <ResizableHandle className="bg-zinc-800" />

          {/* Monaco editor panel */}
          <ResizablePanel defaultSize={75}>
            <div className="h-full flex flex-col">
              {selectedFile ? (
                <>
                  <div className="flex-shrink-0 px-4 py-2 border-b border-zinc-800 bg-[#0d0d0f] flex items-center gap-2">
                    <FileCode className="w-4 h-4 text-zinc-500" />
                    <span className="text-sm text-zinc-300 font-mono">{selectedFile.filepath}</span>
                    <Badge variant="outline" className="text-[10px] border-zinc-700 ml-auto">v{selectedFile.version || 1}</Badge>
                  </div>
                  <div className="flex-1">
                    <Editor
                      height="100%"
                      language={LANGUAGE_MAP[selectedFile.language] || selectedFile.language}
                      value={editorContent}
                      onChange={(v) => onEditorChange(v || "")}
                      theme="vs-dark"
                      options={{
                        minimap: { enabled: true },
                        fontSize: 13,
                        fontFamily: "'JetBrains Mono', monospace",
                        lineNumbers: 'on',
                        scrollBeyondLastLine: false,
                        automaticLayout: true,
                        tabSize: 2,
                        wordWrap: 'on',
                        padding: { top: 12 }
                      }}
                    />
                  </div>
                </>
              ) : (
                <div className="h-full flex items-center justify-center text-center">
                  <div>
                    <FileCode className="w-16 h-16 mx-auto mb-4 text-zinc-800" />
                    <h3 className="font-rajdhani text-lg text-zinc-600 mb-2">No File Selected</h3>
                    <p className="text-sm text-zinc-700">Select a file or start building</p>
                  </div>
                </div>
              )}
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      ) : (
        <div className="flex-1 flex flex-col">
          <div className="flex-shrink-0 px-4 py-2 border-b border-zinc-800 flex items-center justify-between">
            <span className="text-sm text-zinc-400">Live Preview</span>
            <Button size="sm" variant="outline" className="h-7 border-zinc-700" onClick={onLoadPreview}>
              <Play className="w-3 h-3 mr-1" />Refresh
            </Button>
          </div>
          <div className="flex-1 bg-white">
            {previewHtml
              ? <iframe srcDoc={previewHtml} className="w-full h-full border-0" sandbox="allow-scripts" title="Preview" />
              : <div className="h-full flex items-center justify-center bg-zinc-900"><p className="text-zinc-500">Click Refresh</p></div>
            }
          </div>
        </div>
      )}
    </div>
  );
}
