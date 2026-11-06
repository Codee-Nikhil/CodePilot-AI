"use client";

import { useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { ChatMessage } from "@/components/chat/chat-message";
import { Button } from "@/components/ui/button";
import { useChat } from "@/hooks/use-chat";
import { streamChat } from "@/services/chat";
import type { UiMessage } from "@/types/chat";

const SUGGESTIONS = ["What does this project do?", "Where is the entry point?", "How is the code organised?"];

interface Props {
  repoId: number;
  initialChatId: number | null;
  onChatStarted: (chatId: number) => void;
}

export function ChatPanel({ repoId, initialChatId, onChatStarted }: Props) {
  const queryClient = useQueryClient();
  const { data: existing } = useChat(initialChatId);
  const [messages, setMessages] = useState<UiMessage[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const streamingRef = useRef(false);
  const chatIdRef = useRef<number | null>(initialChatId);
  const abortRef = useRef<AbortController | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (existing && !streamingRef.current) {
      setMessages(existing.messages.map((m) => ({ id: String(m.id), role: m.role, content: m.content, sources: m.sources })));
    }
  }, [existing]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: "end" });
  }, [messages]);

  useEffect(() => () => abortRef.current?.abort(), []);

  async function send() {
    const text = input.trim();
    if (!text || streaming) return;

    setInput("");
    setError(null);
    setStreaming(true);
    streamingRef.current = true;

    const assistantId = crypto.randomUUID();
    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: "user", content: text },
      { id: assistantId, role: "assistant", content: "", sources: [] },
    ]);
    const patchAssistant = (fn: (m: UiMessage) => UiMessage) =>
      setMessages((prev) => prev.map((m) => (m.id === assistantId ? fn(m) : m)));

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      await streamChat(
        { repo_id: repoId, chat_id: chatIdRef.current, message: text },
        (event) => {
          if (event.type === "meta") {
            if (chatIdRef.current === null) onChatStarted(event.chat_id);
            chatIdRef.current = event.chat_id;
            patchAssistant((m) => ({ ...m, sources: event.sources }));
          } else if (event.type === "token") {
            patchAssistant((m) => ({ ...m, content: m.content + event.text }));
          } else if (event.type === "error") {
            setError(event.message);
          }
        },
        controller.signal
      );
    } catch (e) {
      if (!controller.signal.aborted) setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      streamingRef.current = false;
      setStreaming(false);
      setMessages((prev) => prev.filter((m) => m.id !== assistantId || m.content !== ""));
      queryClient.invalidateQueries({ queryKey: ["chats", repoId] });
      if (chatIdRef.current !== null) queryClient.invalidateQueries({ queryKey: ["chat", chatIdRef.current] });
    }
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex-1 space-y-4 overflow-y-auto p-4" aria-live="polite">
        {messages.length === 0 && (
          <div className="space-y-3 text-sm text-muted-foreground">
            <p>Ask anything about this repository. Answers are grounded in its code and cite their sources.</p>
            <div className="flex flex-wrap gap-2">
              {SUGGESTIONS.map((q) => <Button key={q} variant="outline" size="sm" onClick={() => setInput(q)}>{q}</Button>)}
            </div>
          </div>
        )}
        {messages.map((m) => <ChatMessage key={m.id} message={m} />)}
        {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
        <div ref={bottomRef} />
      </div>

      <form
        onSubmit={(e) => { e.preventDefault(); void send(); }}
        className="flex gap-2 border-t p-3"
      >
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              void send();
            }
          }}
          rows={2}
          maxLength={4000}
          aria-label="Ask a question about this repository"
          placeholder="Ask about this repo… (Enter to send, Shift+Enter for a new line)"
          className="flex-1 resize-none rounded-md border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        />
        <Button type="submit" disabled={streaming || !input.trim()}>{streaming ? "…" : "Send"}</Button>
      </form>
    </div>
  );
}
