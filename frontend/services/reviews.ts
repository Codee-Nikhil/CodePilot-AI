import { apiFetch } from "@/services/api";
import type { ReviewDetail, ReviewSummary } from "@/types/review";

export const listReviews = (repoId: number) => apiFetch<ReviewSummary[]>(`/reviews?repo_id=${repoId}`);
export const getReview = (id: number) => apiFetch<ReviewDetail>(`/reviews/${id}`);
export const startReview = (repoId: number, paths: string[]) =>
  apiFetch<ReviewSummary>("/reviews", { method: "POST", body: JSON.stringify({ repo_id: repoId, paths }) });
export const deleteReview = (id: number) => apiFetch<void>(`/reviews/${id}`, { method: "DELETE" });
