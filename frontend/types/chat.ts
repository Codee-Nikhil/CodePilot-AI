export interface Source {
  path: string;
  start_line: number;
  end_line: number;
}

export interface ChatSummary {
  id: number;
  repo_id: number;
  title: string;
  created_at: string;
}

export interface ChatMessageData {
  id: number;
  role: "user" | "assistant";
  content: string;
  sources: Source[] | null;
  created_at: string;
}

export interface ChatDetail extends ChatSummary {
  messages: ChatMessageData[];
}

export type ChatEvent =
  | { type: "meta"; chat_id: number; sources: Source[] }
  | { type: "token"; text: string }
  | { type: "error"; message: string }
  | { type: "done" };

export interface UiMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[] | null;
}
