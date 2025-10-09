import React, { useMemo, useRef } from "react";
import type { Message } from "../App";

export default function Chat({
  messages,
  onSend,
}: {
  messages: Message[];
  onSend: (text: string) => void;
}) {
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const rendered = useMemo(
    () => (
      <div className="messages">
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}> 
            <span className="role">{m.role === "user" ? "You" : "Bot"}:</span>
            <span>{m.text}</span>
          </div>
        ))}
      </div>
    ),
    [messages]
  );

  function submit(e: React.FormEvent) {
    e.preventDefault();
    const text = inputRef.current?.value || "";
    if (text.trim()) {
      onSend(text);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <section className="chat">
      {rendered}
      <form onSubmit={submit} className="composer">
        <textarea ref={inputRef} placeholder="Type a message…" rows={3} />
        <button type="submit">Send</button>
      </form>
    </section>
  );
}
