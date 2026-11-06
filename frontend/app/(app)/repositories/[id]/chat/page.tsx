"use client";

import { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ChatList } from "@/components/chat/chat-list";
import { ChatPanel } from "@/components/chat/chat-panel";
import { IndexStatus } from "@/components/explorer/index-status";
import { useRepo } from "@/hooks/use-repositories";

export default function RepoChatPage() {
  const id = Number(useParams<{ id: string }>().id);
  const { data: repo, error } = useRepo(id);
  const [session, setSession] = useState<{ key: number; chatId: number | null }>({ key: 0, chatId: null });
  const [activeId, setActiveId] = useState<number | null>(null);

  if (error) return <p role="alert" className="text-destructive">{error.message}</p>;
  if (!repo) return <p className="text-muted-foreground">Loading…</p>;

  const open = (chatId: number | null) => {
    setSession((s) => ({ key: s.key + 1, chatId }));
    setActiveId(chatId);
  };

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-4">
      <header className="space-y-2">
        <Link href={`/repositories/${id}`} className="text-sm text-muted-foreground hover:underline">← {repo.full_name}</Link>
        <h1 className="text-xl font-semibold">Chat with {repo.name}</h1>
        <IndexStatus repo={repo} />
      </header>

      {repo.index_status === "ready" ? (
        <div className="grid gap-4 lg:grid-cols-[240px_minmax(0,1fr)]">
          <aside className="rounded-lg border p-2">
            <ChatList repoId={id} activeId={activeId} onSelect={open} onNew={() => open(null)} />
          </aside>
          <section className="flex h-[70vh] min-w-0 flex-col rounded-lg border">
            <ChatPanel key={session.key} repoId={id} initialChatId={session.chatId} onChatStarted={setActiveId} />
          </section>
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">
          {repo.index_status === "indexing" ? "Indexing… chat unlocks when it finishes." : "Index this repository to start chatting."}
        </p>
      )}
    </div>
  );
}
