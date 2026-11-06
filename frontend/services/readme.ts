import { apiFetch, ApiError } from "@/services/api";
import type { ReadmeDoc } from "@/types/readme";

export async function getReadme(repoId: number): Promise<ReadmeDoc | null> {
  try {
    return await apiFetch<ReadmeDoc>(`/readme/${repoId}`);
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return null;
    throw e;
  }
}
export const generateReadme = (repoId: number) =>
  apiFetch<ReadmeDoc>(`/readme/${repoId}/generate`, { method: "POST" });
