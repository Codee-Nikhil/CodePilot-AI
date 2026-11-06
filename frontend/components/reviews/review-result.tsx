import { FindingCard } from "@/components/reviews/finding-card";
import type { ReviewDetail } from "@/types/review";

export function ReviewResult({ review }: { review: ReviewDetail }) {
  if (review.status === "pending" || review.status === "running") {
    return <p className="text-sm text-muted-foreground">Running review on {review.paths.length} file(s)…</p>;
  }
  if (review.status === "failed") {
    return <p role="alert" className="text-sm text-destructive">{review.error ?? "The review failed."}</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        {review.score !== null && (
          <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full border text-xl font-semibold">
            {review.score}
          </div>
        )}
        <p className="text-sm text-muted-foreground">{review.summary}</p>
      </div>
      {review.findings.length === 0 ? (
        <p className="text-sm text-muted-foreground">No issues found. Nice work.</p>
      ) : (
        <div className="space-y-3">
          {review.findings.map((f) => <FindingCard key={f.id} finding={f} />)}
        </div>
      )}
    </div>
  );
}
