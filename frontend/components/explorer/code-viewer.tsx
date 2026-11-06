"use client";

import dynamic from "next/dynamic";
import { useTheme } from "next-themes";
import { useRepoFile } from "@/hooks/use-repositories";

const Highlighter = dynamic(() => import("@/components/explorer/highlighter"), {
  ssr: false,
  loading: () => <p className="p-4 text-sm text-muted-foreground">Loading viewer…</p>,
});

export function CodeViewer({ repoId, path }: { repoId: number; path: string | null }) {
  const { resolvedTheme } = useTheme();
  const { data, isPending, error } = useRepoFile(repoId, path);

  if (!path) return <p className="p-6 text-sm text-muted-foreground">Select a file to view it.</p>;
  if (isPending) return <p className="p-6 text-sm text-muted-foreground">Loading…</p>;
  if (error) return <p role="alert" className="p-6 text-sm text-destructive">{error.message}</p>;

  return (
    <div>
      <div className="flex items-center justify-between gap-3 border-b px-4 py-2 text-sm">
        <span className="truncate font-mono">{data.path}</span>
        <span className="shrink-0 text-muted-foreground">{data.language ?? "text"} · {(data.size / 1024).toFixed(1)} KB</span>
      </div>
      <div className="max-h-[70vh] overflow-auto">
        <Highlighter code={data.content} language={data.language} dark={resolvedTheme === "dark"} />
      </div>
    </div>
  );
}
