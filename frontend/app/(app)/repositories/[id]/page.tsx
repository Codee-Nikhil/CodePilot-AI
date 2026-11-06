"use client";

import { useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { CodeViewer } from "@/components/explorer/code-viewer";
import { FileTree } from "@/components/explorer/file-tree";
import { IndexStatus } from "@/components/explorer/index-status";
import { Button } from "@/components/ui/button";
import { useDeleteRepo, useRepo, useRepoTree, useSyncRepo } from "@/hooks/use-repositories";

export default function RepoExplorerPage() {
  const id = Number(useParams<{ id: string }>().id);
  const router = useRouter();
  const { data: repo, error } = useRepo(id);
  const { data: tree } = useRepoTree(id);
  const sync = useSyncRepo(id);
  const remove = useDeleteRepo();
  const [selected, setSelected] = useState<string | null>(null);

  if (error) {
    return (
      <div className="space-y-2">
        <p role="alert" className="text-destructive">{error.message}</p>
        <Link href="/repositories" className="underline">Back to repositories</Link>
      </div>
    );
  }
  if (!repo) return <p className="text-muted-foreground">Loading…</p>;

  const handleDelete = () => {
    if (!window.confirm("Delete this repository and its imported files?")) return;
    remove.mutate(id, { onSuccess: () => router.replace("/repositories") });
  };

  return (
    <div className="mx-auto flex max-w-7xl flex-col gap-4">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div className="min-w-0">
          <Link href="/repositories" className="text-sm text-muted-foreground hover:underline">← Repositories</Link>
          <h1 className="truncate text-xl font-semibold">{repo.full_name}</h1>
          <p className="text-sm text-muted-foreground">
            {tree?.length ?? 0} files
            {repo.last_synced_at && ` · synced ${new Date(repo.last_synced_at).toLocaleString()}`}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button asChild variant="outline"><Link href={`/repositories/${id}/chat`}>Chat</Link></Button>
          <Button asChild variant="outline"><Link href={`/repositories/${id}/review`}>Review</Link></Button>
          <Button asChild variant="outline"><Link href={`/repositories/${id}/readme`}>README</Link></Button>
          <Button onClick={() => sync.mutate()} disabled={sync.isPending}>{sync.isPending ? "Syncing…" : "Sync"}</Button>
          <Button variant="outline" onClick={handleDelete} disabled={remove.isPending}>Delete</Button>
        </div>
      </header>

      <IndexStatus repo={repo} />

      {sync.data && (
        <p role="status" className="text-sm text-muted-foreground">
          Synced: {sync.data.added} added, {sync.data.updated} updated, {sync.data.removed} removed.
        </p>
      )}
      {(sync.error || remove.error) && (
        <p role="alert" className="text-sm text-destructive">{(sync.error ?? remove.error)?.message}</p>
      )}

      <div className="grid gap-4 lg:grid-cols-[320px_minmax(0,1fr)]">
        <aside className="rounded-lg border">
          {tree ? <FileTree files={tree} selected={selected} onSelect={setSelected} /> : <p className="p-4 text-sm text-muted-foreground">Loading files…</p>}
        </aside>
        <section className="min-w-0 rounded-lg border">
          <CodeViewer repoId={id} path={selected} />
        </section>
      </div>
    </div>
  );
}
