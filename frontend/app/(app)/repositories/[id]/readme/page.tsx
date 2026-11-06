"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { ReadmePreview } from "@/components/readme/readme-preview";
import { Button } from "@/components/ui/button";
import { useRepo } from "@/hooks/use-repositories";
import { useGenerateReadme, useReadme } from "@/hooks/use-readme";

export default function RepoReadmePage() {
  const id = Number(useParams<{ id: string }>().id);
  const { data: repo } = useRepo(id);
  const { data: doc, isPending } = useReadme(id);
  const generate = useGenerateReadme(id);

  if (!repo) return <p className="text-muted-foreground">Loading…</p>;

  const content = generate.data?.content ?? doc?.content ?? null;

  return (
    <div className="mx-auto max-w-4xl space-y-4">
      <header className="space-y-1">
        <Link href={`/repositories/${id}`} className="text-sm text-muted-foreground hover:underline">← {repo.full_name}</Link>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h1 className="text-xl font-semibold">README Generator</h1>
          <Button onClick={() => generate.mutate()} disabled={generate.isPending}>
            {generate.isPending ? "Generating…" : content ? "Regenerate" : "Generate README"}
          </Button>
        </div>
      </header>

      {generate.error && <p role="alert" className="text-sm text-destructive">{generate.error.message}</p>}
      {isPending && !content && <p className="text-sm text-muted-foreground">Loading…</p>}
      {!isPending && !content && !generate.isPending && (
        <p className="text-sm text-muted-foreground">No README generated yet. Click Generate to create one from this repository&apos;s files.</p>
      )}
      {content && <ReadmePreview content={content} />}
    </div>
  );
}
