import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "@/lib/utils";
import type { UiMessage } from "@/types/chat";

const MARKDOWN_STYLES =
  "[&_p]:my-2 [&_pre]:my-2 [&_pre]:overflow-x-auto [&_pre]:rounded-md [&_pre]:bg-background [&_pre]:p-3 " +
  "[&_code]:font-mono [&_code]:text-[0.85em] [&_ul]:list-disc [&_ul]:pl-5 [&_ol]:list-decimal [&_ol]:pl-5";

export function ChatMessage({ message }: { message: UiMessage }) {
  const isUser = message.role === "user";
  const sources = message.sources ?? [];

  return (
    <div className={cn("flex", isUser && "justify-end")}>
      <div className={cn("max-w-[90%] rounded-lg px-4 py-2 text-sm", isUser ? "bg-primary text-primary-foreground" : "bg-muted")}>
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : message.content ? (
          <div className={MARKDOWN_STYLES}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
          </div>
        ) : (
          <span className="text-muted-foreground">Thinking…</span>
        )}
        {!isUser && sources.length > 0 && (
          <details className="mt-2 text-xs text-muted-foreground">
            <summary className="cursor-pointer">Sources ({sources.length})</summary>
            <ul className="mt-1 space-y-0.5 font-mono">
              {sources.map((s, i) => <li key={i}>{s.path}:{s.start_line}-{s.end_line}</li>)}
            </ul>
          </details>
        )}
      </div>
    </div>
  );
}
