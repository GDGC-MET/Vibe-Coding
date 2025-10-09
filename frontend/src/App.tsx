import React, { useEffect, useMemo, useState } from "react";
import { api } from "./api";
import type { Settings } from "./types";
import Chat from "./components/Chat";
import SettingsPanel from "./components/Settings";

export type Message = { role: "user" | "bot"; text: string };

export default function App() {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get<Settings>("/settings");
        setSettings(res.data);
      } catch (e: any) {
        setError(e?.response?.data?.error || e?.message || "Failed to load settings");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const title = useMemo(() => {
    if (!settings) return "AI Vibe Chat";
    const { personality, provider } = settings.current;
    return `AI Vibe Chat — ${personality} via ${provider}`;
  }, [settings]);

  async function sendMessage(text: string) {
    if (!text.trim()) return;
    setMessages((prev) => [...prev, { role: "user", text }]);
    try {
      const res = await api.post<{ reply: string }>("/chat", { text });
      setMessages((prev) => [...prev, { role: "bot", text: res.data.reply }]);
    } catch (e: any) {
      const msg = e?.response?.data?.error || e?.message || "Request failed";
      setMessages((prev) => [...prev, { role: "bot", text: `Error: ${msg}` }]);
    }
  }

  async function applySettings(update: { personality?: string; provider?: string; memory?: boolean }) {
    try {
      const res = await api.post<Settings & { ok: boolean }>("/settings", update);
      // Reload settings
      const refreshed = await api.get<Settings>("/settings");
      setSettings(refreshed.data);
    } catch (e: any) {
      const msg = e?.response?.data?.error || e?.message || "Failed to save settings";
      setError(msg);
    }
  }

  if (loading) return <div className="container">Loading…</div>;
  if (error) return <div className="container error">{error}</div>;
  if (!settings) return <div className="container">No settings available.</div>;

  return (
    <div className="container">
      <header>
        <h1>{title}</h1>
      </header>
      <SettingsPanel
        personalities={settings.personalities}
        providers={settings.providers}
        current={settings.current}
        onApply={applySettings}
      />
      <Chat messages={messages} onSend={sendMessage} />
    </div>
  );
}
