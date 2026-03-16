import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { 
  Bell, Mail, MessageSquare, CheckCircle, AlertTriangle, 
  Milestone, Send, Loader2
} from "lucide-react";
import { API } from "@/App";

const NotificationsPanel = ({ projectId }) => {
  const [settings, setSettings] = useState({
    email_enabled: false,
    email_address: "",
    discord_enabled: false,
    discord_webhook_url: "",
    notify_on_complete: true,
    notify_on_milestones: true,
    notify_on_errors: true
  });
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetchSettings();
    fetchHistory();
  }, [projectId]);

  const fetchSettings = async () => {
    try {
      const res = await axios.get(`${API}/notifications/${projectId}/settings`);
      setSettings(res.data);
    } catch (e) {}
  };

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API}/notifications/${projectId}/history`);
      setHistory(res.data);
    } catch (e) {}
  };

  const saveSettings = async () => {
    setSaving(true);
    try {
      await axios.post(`${API}/notifications/${projectId}/settings`, null, { params: settings });
      toast.success("Notification settings saved!");
    } catch (e) {
      toast.error("Failed to save settings");
    } finally {
      setSaving(false);
    }
  };

  const testNotification = async () => {
    setTesting(true);
    try {
      await axios.post(`${API}/notifications/${projectId}/test`);
      toast.success("Test notification sent!");
      fetchHistory();
    } catch (e) {
      toast.error("Failed to send test");
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]">
      <div className="flex-shrink-0 px-4 py-3 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Bell className="w-4 h-4 text-amber-400" />
          <span className="font-rajdhani font-bold text-white">Notifications</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Email Settings */}
        <div className="p-4 rounded-lg bg-zinc-900/50 border border-zinc-800">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Mail className="w-5 h-5 text-blue-400" />
              <span className="font-medium text-white">Email Notifications</span>
            </div>
            <Switch
              checked={settings.email_enabled}
              onCheckedChange={(v) => setSettings({ ...settings, email_enabled: v })}
            />
          </div>
          {settings.email_enabled && (
            <Input
              type="email"
              placeholder="your@email.com"
              value={settings.email_address || ""}
              onChange={(e) => setSettings({ ...settings, email_address: e.target.value })}
              className="bg-zinc-800 border-zinc-700"
            />
          )}
        </div>

        {/* Discord Settings */}
        <div className="p-4 rounded-lg bg-zinc-900/50 border border-zinc-800">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-indigo-400" />
              <span className="font-medium text-white">Discord Notifications</span>
            </div>
            <Switch
              checked={settings.discord_enabled}
              onCheckedChange={(v) => setSettings({ ...settings, discord_enabled: v })}
            />
          </div>
          {settings.discord_enabled && (
            <Input
              type="url"
              placeholder="https://discord.com/api/webhooks/..."
              value={settings.discord_webhook_url || ""}
              onChange={(e) => setSettings({ ...settings, discord_webhook_url: e.target.value })}
              className="bg-zinc-800 border-zinc-700"
            />
          )}
        </div>

        {/* Notification Types */}
        <div className="p-4 rounded-lg bg-zinc-900/50 border border-zinc-800">
          <h4 className="font-medium text-white mb-4">Notify me when:</h4>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-emerald-400" />
                <span className="text-sm text-zinc-300">Build completes</span>
              </div>
              <Switch
                checked={settings.notify_on_complete}
                onCheckedChange={(v) => setSettings({ ...settings, notify_on_complete: v })}
              />
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Milestone className="w-4 h-4 text-amber-400" />
                <span className="text-sm text-zinc-300">Stage milestones</span>
              </div>
              <Switch
                checked={settings.notify_on_milestones}
                onCheckedChange={(v) => setSettings({ ...settings, notify_on_milestones: v })}
              />
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-red-400" />
                <span className="text-sm text-zinc-300">Errors & warnings</span>
              </div>
              <Switch
                checked={settings.notify_on_errors}
                onCheckedChange={(v) => setSettings({ ...settings, notify_on_errors: v })}
              />
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <Button onClick={saveSettings} disabled={saving} className="flex-1 bg-blue-500 hover:bg-blue-600">
            {saving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
            Save Settings
          </Button>
          <Button onClick={testNotification} disabled={testing} variant="outline" className="border-zinc-700">
            {testing ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Send className="w-4 h-4 mr-2" />}
            Test
          </Button>
        </div>

        {/* History */}
        {history.length > 0 && (
          <div>
            <h4 className="font-medium text-white mb-3">Recent Notifications</h4>
            <div className="space-y-2">
              {history.slice(0, 5).map((n) => (
                <div key={n.id} className="p-2 rounded bg-zinc-800/50 text-xs">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-zinc-300">{n.title}</span>
                    <Badge variant="outline" className="text-[10px] border-zinc-700">
                      {n.notification_type}
                    </Badge>
                  </div>
                  <p className="text-zinc-500 truncate">{n.message}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default NotificationsPanel;
