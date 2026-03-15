/**
 * WorkspaceChatPanel — Chat messages list + input bar
 * All state lives in ProjectWorkspace; this is pure presentation.
 */
import { motion } from "framer-motion";
import { Bot, Loader2, X, Send, Plus, FileCode, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import FileDropZone from "@/components/FileDropZone";

const ROLE_COLORS = {
  lead: "text-blue-400", architect: "text-cyan-400", developer: "text-emerald-400",
  reviewer: "text-amber-400", tester: "text-purple-400", artist: "text-pink-400",
  level_designer: "text-green-400", animator: "text-orange-400",
  audio_engineer: "text-cyan-300", game_designer: "text-indigo-400",
  writer: "text-yellow-400", technical_artist: "text-teal-400"
};

export default function WorkspaceChatPanel({
  messages,
  streamingContent,
  streamingAgent,
  sending,
  agents,
  project,
  selectedAgent,
  chatInput,
  attachedFiles,
  chatEndRef,
  onSendMessage,
  onSetAttachedFiles,
  onSetChatInput,
  onClearSelectedAgent,
  parseContent,
}) {
  const selectedAgentName = agents?.find(a => a.id === selectedAgent)?.name;

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Messages list */}
      <div className="flex-1 overflow-y-auto p-4" style={{ backgroundColor: 'var(--bg-primary)' }}>
        <div className="space-y-4 pb-4">
          {messages.length === 0 && !streamingContent ? (
            <div className="text-center py-12">
              <Sparkles className="w-12 h-12 mx-auto mb-4" style={{ color: 'color-mix(in srgb, var(--accent) 50%, transparent)' }} />
              <h3 className="font-rajdhani text-xl mb-2" style={{ color: 'var(--text-primary)' }}>Ready to Build</h3>
              <p className="text-sm max-w-md mx-auto mb-4" style={{ color: 'var(--text-muted)' }}>
                Describe your project or use Quick Actions above.
              </p>
            </div>
          ) : (
            <>
              {messages.map((msg) => {
                const isUser = msg.agent_role === "user";
                const agent = agents?.find(a => a.id === msg.agent_id);
                const roleColor = ROLE_COLORS[msg.agent_role] || "text-zinc-400";
                return (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}
                  >
                    {!isUser && (
                      <Avatar className="w-8 h-8 flex-shrink-0 mt-1" style={{ borderColor: 'var(--border-color)' }}>
                        <AvatarImage src={agent?.avatar} />
                        <AvatarFallback style={{ backgroundColor: 'var(--bg-tertiary)' }}>
                          <Bot className={`w-4 h-4 ${roleColor}`} />
                        </AvatarFallback>
                      </Avatar>
                    )}
                    <div className={`max-w-[85%] ${isUser ? 'ml-auto' : ''}`}>
                      {!isUser && (
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-rajdhani font-bold text-sm" style={{ color: 'var(--accent)' }}>
                            {msg.agent_name}
                          </span>
                          <Badge variant="outline" className="text-[10px]" style={{ borderColor: 'var(--border-color)', color: 'var(--text-muted)' }}>
                            {msg.agent_role}
                          </Badge>
                        </div>
                      )}
                      <div
                        className="rounded-lg px-4 py-3"
                        style={{
                          backgroundColor: isUser ? 'var(--accent)' : 'var(--bg-secondary)',
                          color: isUser ? 'white' : 'var(--text-primary)'
                        }}
                      >
                        {isUser
                          ? <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                          : parseContent(msg.content, msg.id, msg.delegations)
                        }
                      </div>
                    </div>
                  </motion.div>
                );
              })}

              {/* Streaming bubble */}
              {streamingContent && streamingAgent && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-3">
                  <Avatar className="w-8 h-8 mt-1" style={{ borderColor: 'var(--border-color)' }}>
                    <AvatarFallback style={{ backgroundColor: 'var(--bg-tertiary)' }}>
                      <Bot className="w-4 h-4 animate-pulse" style={{ color: 'var(--accent)' }} />
                    </AvatarFallback>
                  </Avatar>
                  <div className="max-w-[85%]">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-rajdhani font-bold text-sm" style={{ color: 'var(--accent)' }}>
                        {streamingAgent.name}
                      </span>
                      <Badge className="text-[10px] animate-pulse" style={{ backgroundColor: 'color-mix(in srgb, var(--warning) 20%, transparent)', color: 'var(--warning)' }}>
                        streaming
                      </Badge>
                    </div>
                    <div className="rounded-lg px-4 py-3" style={{ backgroundColor: 'var(--bg-secondary)' }}>
                      {parseContent(streamingContent, 'streaming')}
                    </div>
                  </div>
                </motion.div>
              )}
            </>
          )}

          {/* Typing indicator when waiting (no stream yet) */}
          {sending && !streamingContent && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ backgroundColor: 'var(--bg-tertiary)' }}>
                <Loader2 className="w-4 h-4 animate-spin" style={{ color: 'var(--accent)' }} />
              </div>
              <div className="rounded-lg px-4 py-3" style={{ backgroundColor: 'var(--bg-secondary)' }}>
                <div className="typing-indicator"><span /><span /><span /></div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
      </div>

      {/* Input bar */}
      <div className="flex-shrink-0 p-4 border-t" style={{ borderColor: 'var(--border-color)', backgroundColor: 'var(--bg-secondary)' }}>
        {selectedAgentName && (
          <div className="mb-2 flex items-center gap-2">
            <span className="text-xs" style={{ color: 'var(--text-muted)' }}>Speaking to:</span>
            <Badge style={{ backgroundColor: 'color-mix(in srgb, var(--accent) 20%, transparent)', color: 'var(--accent)' }}>
              {selectedAgentName}
            </Badge>
            <Button variant="ghost" size="sm" className="h-5 px-2" onClick={onClearSelectedAgent}>
              <X className="w-3 h-3" />
            </Button>
          </div>
        )}

        {/* Attached files */}
        {attachedFiles.length > 0 && (
          <div className="mb-3 flex flex-wrap gap-2">
            {attachedFiles.map((file, idx) => (
              <div key={idx} className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm"
                style={{ backgroundColor: 'var(--bg-tertiary)', border: '1px solid var(--border-color)' }}>
                <FileCode className="w-4 h-4" style={{ color: 'var(--text-muted)' }} />
                <span className="max-w-[150px] truncate" style={{ color: 'var(--text-secondary)' }}>{file.name}</span>
                <button onClick={() => onSetAttachedFiles(prev => prev.filter((_, i) => i !== idx))}
                  className="p-0.5 rounded hover:bg-zinc-700/50 transition-colors">
                  <X className="w-3 h-3" style={{ color: 'var(--text-muted)' }} />
                </button>
              </div>
            ))}
          </div>
        )}

        <FileDropZone onFilesAdded={(f) => onSetAttachedFiles(prev => [...prev, ...f])} className="rounded-lg">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <textarea
                placeholder={project?.phase === "clarification" ? "Describe your project..." : "What would you like to build?"}
                value={chatInput}
                onChange={(e) => onSetChatInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); onSendMessage(); } }}
                className="w-full min-h-[120px] text-sm rounded-lg p-4 pb-12 outline-none focus:ring-2"
                style={{
                  backgroundColor: 'var(--bg-tertiary)',
                  border: '2px solid var(--border-color)',
                  color: 'var(--text-primary)',
                  resize: 'vertical',
                  maxHeight: '400px'
                }}
                data-testid="chat-input"
              />
              <button type="button"
                onClick={() => document.getElementById('file-input-chat')?.click()}
                className="absolute bottom-3 left-1 p-2 rounded-lg transition-colors hover:bg-zinc-700/50"
                style={{ color: 'var(--text-muted)' }} title="Attach files">
                <Plus className="w-5 h-5" />
              </button>
              <input id="file-input-chat" type="file" multiple className="hidden"
                onChange={(e) => { if (e.target.files) onSetAttachedFiles(prev => [...prev, ...Array.from(e.target.files)]); }} />
            </div>
            <Button onClick={onSendMessage} disabled={sending || !chatInput.trim()}
              className="self-end h-14 px-6 rounded-lg text-white font-medium"
              style={{ backgroundColor: 'var(--accent)' }} data-testid="send-btn">
              {sending ? <Loader2 className="w-5 h-5 animate-spin" /> : <><Send className="w-5 h-5 mr-2" />Send</>}
            </Button>
          </div>
        </FileDropZone>
      </div>
    </div>
  );
}
