"use client";

import { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { FilePicker } from "@/components/reviews/file-picker";
import { ReviewHistory } from "@/components/reviews/review-history";
import { ReviewResult } from "@/components/reviews/review-result";
import { useRepo, useRepoTree } from "@/hooks/use-repositories";
import { useReview, useStartReview } from "@/hooks/use-reviews";

export default function RepoReviewPage() {
  const id = Number(useParams<{ id: string }>().id);
  const { data: repo } = useRepo(id);
  const { data: tree } = useRepoTree(id);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [activeId, setActiveId] = useState<number | null>(null);
  const start = useStartReview(id);
  const { data: review, error } = useReview(activeId);

  const toggle = (path: string) =>
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });

  if (!repo || !tree) return <p className="text-muted-foreground">Loading…</p>;

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-4">
      <header className="space-y-1">
        <Link href={`/repositories/${id}`} className="text-sm text-muted-foreground hover:underline">← {repo.full_name}</Link>
        <h1 className="text-xl font-semibold">AI Code Review</h1>
      </header>

      <div className="grid gap-4 lg:grid-cols-[320px_minmax(0,1fr)]">
        <div className="space-y-4">
          <FilePicker
            files={tree}
            selected={selected}
            onToggle={toggle}
            starting={start.isPending}
            onStart={() =>
              start.mutate(Array.from(selected), {
                onSuccess: (review) => {
                  setActiveId(review.id);
                  setSelected(new Set());
                },
              })
            }
          />
          {start.error && <p role="alert" className="text-sm text-destructive">{start.error.message}</p>}
          <div className="rounded-lg border p-3">
            <p className="mb-2 text-sm font-medium">History</p>
            <ReviewHistory repoId={id} activeId={activeId} onSelect={setActiveId} />
          </div>
        </div>

        <section className="min-w-0 rounded-lg border p-4">
          {!activeId && <p className="text-sm text-muted-foreground">Select files and start a review, or pick one from history.</p>}
          {error && <p role="alert" className="text-sm text-destructive">{error.message}</p>}
          {review && <ReviewResult review={review} />}
        </section>
      </div>
    </div>
  );
}
