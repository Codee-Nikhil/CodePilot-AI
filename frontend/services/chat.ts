import { apiFetch, apiStream } from "@/services/api";
import type { ChatDetail, ChatEvent, ChatSummary } from "@/types/chat";

export const listChats = (repoId: number) => apiFetch<ChatSummary[]>(`/chat?repo_id=${repoId}`);
export const getChat = (chatId: number) => apiFetch<ChatDetail>(`/chat/${chatId}`);
export const deleteChat = (chatId: number) => apiFetch<void>(`/chat/${chatId}`, { method: "DELETE" });

interface StreamBody {
  repo_id: number;
  chat_id: number | null;
  message: string;
}

export async function streamChat(body: StreamBody, onEvent: (event: ChatEvent) => void, signal?: AbortSignal) {
  const res = await apiStream("/chat/stream", body, signal);
  const reader = res.body?.getReader();
  if (!reader) throw new Error("Streaming is not supported in this browser");

  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) {
      if (line.trim()) onEvent(JSON.parse(line) as ChatEvent);
    }
  }
}
