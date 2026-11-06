import { apiFetch } from "@/services/api";
import type { RemoteRepo } from "@/types/repo";

export const getConnectUrl = () => apiFetch<{ url: string }>("/github/connect");
export const disconnectGitHub = () => apiFetch<void>("/github/connection", { method: "DELETE" });
export const listRemoteRepos = () => apiFetch<RemoteRepo[]>("/github/repos");
