"use client";

import { Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useDeleteReview, useReviews } from "@/hooks/use-reviews";
import { cn } from "@/lib/utils";

const STATUS_VARIANT = { completed: "secondary", failed: "destructive", running: "outline", pending: "outline" } as const;

interface Props {
  repoId: number;
  activeId: number | null;
  onSelect: (id: number) => void;
}

export function ReviewHistory({ repoId, activeId, onSelect }: Props) {
  const { data: reviews } = useReviews(repoId);
  const remove = useDeleteReview(repoId);

  if (!reviews?.length) return <p className="text-sm text-muted-foreground">No reviews yet.</p>;

  return (
    <ul className="space-y-1">
      {reviews.map((r) => (
        <li key={r.id} className="flex items-center gap-1">
          <button
            type="button"
            onClick={() => onSelect(r.id)}
            className={cn("flex min-w-0 flex-1 items-center justify-between gap-2 rounded px-2 py-1.5 text-left text-sm hover:bg-accent", activeId === r.id && "bg-accent font-medium")}
          >
            <span className="truncate font-mono text-xs">{r.paths.length} file{r.paths.length > 1 ? "s" : ""}</span>
            <Badge variant={STATUS_VARIANT[r.status]}>{r.score ?? r.status}</Badge>
          </button>
          <button
            type="button"
            aria-label="Delete review"
            className="rounded p-1.5 text-muted-foreground hover:bg-accent"
            onClick={() => remove.mutate(r.id)}
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </li>
      ))}
    </ul>
  );
}
