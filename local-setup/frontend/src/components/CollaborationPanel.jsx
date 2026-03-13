import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Users, Send, Circle, Lock, Unlock, MessageCircle, 
  UserPlus, LogOut, MousePointer2
} from "lucide-react";
import { API } from "@/App";

const CURSOR_COLORS = {
  blue: "#3b82f6",
  emerald: "#10b981",
  purple: "#8b5cf6",
  amber: "#f59e0b",
  pink: "#ec4899",
  cyan: "#06b6d4"
};

const CollaborationPanel = ({ projectId, currentUser, onFileSelect, activeFileId }) => {
  const [collaborators, setCollaborators] = useState([]);
  const [messages, setMessages] = useState([]);
  const [locks, setLocks] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [isJoined, setIsJoined] = useState(false);
  const chatEndRef = useRef(null);
  const pollIntervalRef = useRef(null);

  useEffect(() => {
    if (isJoined) {
      // Poll for updates
      pollIntervalRef.current = setInterval(fetchUpdates, 2000);
      fetchUpdates();
    }
    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, [isJoined, projectId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchUpdates = async () => {
    try {
      const [collabRes, chatRes, locksRes] = await Promise.all([
        axios.get(`${API}/collab/${projectId}/online`),
        axios.get(`${API}/collab/${projectId}/chat?limit=30`),
        axios.get(`${API}/collab/${projectId}/locks`)
      ]);
      setCollaborators(collabRes.data);
      setMessages(chatRes.data);
      setLocks(locksRes.data);
    } catch (e) {}
  };

  const joinProject = async () => {
    if (!currentUser?.id || !currentUser?.username) {
      toast.error("User info required to join");
      return;
    }
    try {
      await axios.post(`${API}/collab/${projectId}/join`, null, {
        params: { user_id: currentUser.id, username: currentUser.username }
      });
      setIsJoined(true);
      toast.success("Joined collaboration!");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to join");
    }
  };

  const leaveProject = async () => {
    try {
      await axios.post(`${API}/collab/${projectId}/leave`, null, {
        params: { user_id: currentUser.id }
      });
      setIsJoined(false);
      toast.info("Left collaboration");
    } catch (e) {}
  };

  const sendMessage = async () => {
    if (!chatInput.trim()) return;
    try {
      await axios.post(`${API}/collab/${projectId}/chat`, null, {
        params: {
          user_id: currentUser.id,
          username: currentUser.username,
          content: chatInput
        }
      });
      setChatInput("");
      fetchUpdates();
    } catch (e) {
      toast.error("Failed to send message");
    }
  };

  const lockFile = async (fileId) => {
    try {
      await axios.post(`${API}/collab/${projectId}/lock-file`, null, {
        params: {
          file_id: fileId,
          user_id: currentUser.id,
          username: currentUser.username
        }
      });
      fetchUpdates();
      toast.success("File locked");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to lock file");
    }
  };

  const unlockFile = async (fileId) => {
    try {
      await axios.post(`${API}/collab/${projectId}/unlock-file`, null, {
        params: { file_id: fileId, user_id: currentUser.id }
      });
      fetchUpdates();
    } catch (e) {}
  };

  const getFileLock = (fileId) => locks.find(l => l.file_id === fileId);
  const isFileLocked = (fileId) => {
    const lock = getFileLock(fileId);
    return lock && lock.locked_by_user_id !== currentUser?.id;
  };

  if (!isJoined) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-6 bg-[#0a0a0c]">
        <Users className="w-16 h-16 text-zinc-700 mb-4" />
        <h3 className="font-rajdhani text-lg text-white mb-2">Real-time Collaboration</h3>
        <p className="text-sm text-zinc-500 text-center mb-4">
          Work together with up to 3 collaborators.<br />
          See live cursors, chat, and file locks.
        </p>
        <Button onClick={joinProject} className="bg-blue-500 hover:bg-blue-600">
          <UserPlus className="w-4 h-4 mr-2" />Join Collaboration
        </Button>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]">
      {/* Header */}
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Users className="w-4 h-4 text-blue-400" />
          <span className="font-rajdhani font-bold text-white">Collaborators</span>
          <Badge className="bg-emerald-500/20 text-emerald-400 text-xs">{collaborators.length}/3</Badge>
        </div>
        <Button variant="ghost" size="sm" onClick={leaveProject} className="text-zinc-500 hover:text-red-400">
          <LogOut className="w-4 h-4" />
        </Button>
      </div>

      {/* Collaborators List */}
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800">
        <div className="flex gap-2">
          {collaborators.map((collab) => (
            <div key={collab.id} className="flex items-center gap-2 px-2 py-1 rounded-full bg-zinc-800/50 border border-zinc-700">
              <div className="relative">
                <Avatar className="w-6 h-6">
                  <AvatarFallback style={{ backgroundColor: CURSOR_COLORS[collab.color] || '#666' }} className="text-[10px] text-white">
                    {collab.username?.[0]?.toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <Circle className="w-2 h-2 text-emerald-400 fill-emerald-400 absolute -bottom-0.5 -right-0.5" />
              </div>
              <span className="text-xs text-zinc-300">{collab.username}</span>
              {collab.user_id === currentUser?.id && (
                <Badge className="text-[8px] bg-blue-500/20 text-blue-400">you</Badge>
              )}
            </div>
          ))}
          {collaborators.length === 0 && (
            <span className="text-xs text-zinc-600">No one else online</span>
          )}
        </div>
      </div>

      {/* Active File Lock Status */}
      {activeFileId && (
        <div className="flex-shrink-0 px-4 py-2 border-b border-zinc-800 bg-zinc-900/50">
          {isFileLocked(activeFileId) ? (
            <div className="flex items-center gap-2 text-amber-400">
              <Lock className="w-4 h-4" />
              <span className="text-xs">Locked by {getFileLock(activeFileId)?.locked_by_username}</span>
            </div>
          ) : getFileLock(activeFileId) ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-emerald-400">
                <Lock className="w-4 h-4" />
                <span className="text-xs">You have this file locked</span>
              </div>
              <Button variant="ghost" size="sm" className="h-6 text-xs" onClick={() => unlockFile(activeFileId)}>
                <Unlock className="w-3 h-3 mr-1" />Release
              </Button>
            </div>
          ) : (
            <Button variant="outline" size="sm" className="w-full h-7 text-xs border-zinc-700" onClick={() => lockFile(activeFileId)}>
              <Lock className="w-3 h-3 mr-1" />Lock for Editing
            </Button>
          )}
        </div>
      )}

      {/* Chat Messages */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-3">
          {messages.length === 0 ? (
            <div className="text-center py-8">
              <MessageCircle className="w-10 h-10 mx-auto mb-2 text-zinc-700" />
              <p className="text-sm text-zinc-600">No messages yet</p>
            </div>
          ) : (
            messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-2 ${msg.message_type === 'system' ? 'justify-center' : ''}`}
              >
                {msg.message_type === 'system' ? (
                  <span className="text-[10px] text-zinc-600 italic">{msg.content}</span>
                ) : (
                  <>
                    <Avatar className="w-6 h-6 flex-shrink-0">
                      <AvatarFallback className="text-[10px] bg-zinc-800 text-zinc-400">
                        {msg.username?.[0]?.toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-zinc-300">{msg.username}</span>
                        <span className="text-[10px] text-zinc-600">
                          {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                      <p className="text-sm text-zinc-400">{msg.content}</p>
                    </div>
                  </>
                )}
              </motion.div>
            ))
          )}
          <div ref={chatEndRef} />
        </div>
      </ScrollArea>

      {/* Chat Input */}
      <div className="flex-shrink-0 p-3 border-t border-zinc-800">
        <div className="flex gap-2">
          <Input
            placeholder="Message collaborators..."
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            className="bg-zinc-900 border-zinc-700 text-sm"
          />
          <Button onClick={sendMessage} size="icon" className="bg-blue-500 hover:bg-blue-600">
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default CollaborationPanel;
