"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useReindexRepo } from "@/hooks/use-repositories";
import type { Repo } from "@/types/repo";

const LABELS = { pending: "Not indexed", indexing: "Indexing…", ready: "Ready for chat", failed: "Indexing failed" } as const;

export function IndexStatus({ repo }: { repo: Repo }) {
  const reindex = useReindexRepo(repo.id);
  const status = repo.index_status;

  return (
    <div className="flex flex-wrap items-center gap-2">
      <Badge variant={status === "failed" ? "destructive" : "secondary"}>{LABELS[status]}</Badge>
      {status === "failed" && repo.index_error && <span className="text-sm text-destructive">{repo.index_error}</span>}
      {status !== "indexing" && (
        <Button size="sm" variant="outline" onClick={() => reindex.mutate()} disabled={reindex.isPending}>
          {status === "ready" ? "Re-index" : "Index now"}
        </Button>
      )}
      {reindex.error && <span role="alert" className="text-sm text-destructive">{reindex.error.message}</span>}
    </div>
  );
}
