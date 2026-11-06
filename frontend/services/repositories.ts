import { apiFetch } from "@/services/api";
import type { FileContent, FileNode, Repo, SyncResult } from "@/types/repo";

export const listRepos = () => apiFetch<Repo[]>("/repositories");
export const getRepo = (id: number) => apiFetch<Repo>(`/repositories/${id}`);
export const importRepo = (full_name: string) =>
  apiFetch<Repo>("/repositories", { method: "POST", body: JSON.stringify({ full_name }) });
export const syncRepo = (id: number) => apiFetch<SyncResult>(`/repositories/${id}/sync`, { method: "POST" });
export const reindexRepo = (id: number) => apiFetch<Repo>(`/repositories/${id}/index`, { method: "POST" });
export const deleteRepo = (id: number) => apiFetch<void>(`/repositories/${id}`, { method: "DELETE" });
export const getTree = (id: number) => apiFetch<FileNode[]>(`/repositories/${id}/tree`);
export const getFile = (id: number, path: string) =>
  apiFetch<FileContent>(`/repositories/${id}/file?path=${encodeURIComponent(path)}`);
