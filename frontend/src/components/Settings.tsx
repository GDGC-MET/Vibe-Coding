import React, { useMemo, useState } from "react";
import type { Settings } from "../types";

export default function SettingsPanel({
  personalities,
  providers,
  current,
  onApply,
}: Pick<Settings, "personalities" | "providers" | "current"> & {
  onApply: (update: Partial<Settings["current"]>) => void;
}) {
  const [personality, setPersonality] = useState(current.personality);
  const [provider, setProvider] = useState(current.provider);
  const [memory, setMemory] = useState(current.memory);

  const providerOptions = useMemo(() => providers.map((p) => (
    <option key={p} value={p}>{p}</option>
  )), [providers]);

  const personalityOptions = useMemo(() => personalities.map((p) => (
    <option key={p} value={p}>{p}</option>
  )), [personalities]);

  function submit(e: React.FormEvent) {
    e.preventDefault();
    onApply({ personality, provider, memory });
  }

  return (
    <section className="settings">
      <form onSubmit={submit}>
        <label>
          Personality
          <select value={personality} onChange={(e) => setPersonality(e.target.value)}>
            {personalityOptions}
          </select>
        </label>
        <label>
          Provider
          <select value={provider} onChange={(e) => setProvider(e.target.value)}>
            {providerOptions}
          </select>
        </label>
        <label className="checkbox">
          <input type="checkbox" checked={memory} onChange={(e) => setMemory(e.target.checked)} />
          Memory
        </label>
        <button type="submit">Apply</button>
      </form>
    </section>
  );
}
