"use client";

import { Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useChats, useDeleteChat } from "@/hooks/use-chat";
import { cn } from "@/lib/utils";

interface Props {
  repoId: number;
  activeId: number | null;
  onSelect: (id: number) => void;
  onNew: () => void;
}

export function ChatList({ repoId, activeId, onSelect, onNew }: Props) {
  const { data: chats } = useChats(repoId);
  const remove = useDeleteChat(repoId);

  return (
    <div className="space-y-2">
      <Button variant="outline" size="sm" className="w-full" onClick={onNew}>New chat</Button>
      <ul className="max-h-[55vh] space-y-1 overflow-y-auto">
        {chats?.map((chat) => (
          <li key={chat.id} className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => onSelect(chat.id)}
              className={cn("min-w-0 flex-1 truncate rounded px-2 py-1.5 text-left text-sm hover:bg-accent", activeId === chat.id && "bg-accent font-medium")}
            >
              {chat.title}
            </button>
            <button
              type="button"
              aria-label={`Delete chat ${chat.title}`}
              className="rounded p-1.5 text-muted-foreground hover:bg-accent"
              onClick={() => remove.mutate(chat.id, { onSuccess: () => activeId === chat.id && onNew() })}
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </li>
        ))}
        {chats?.length === 0 && <li className="px-2 py-1.5 text-sm text-muted-foreground">No chats yet.</li>}
      </ul>
    </div>
  );
}
