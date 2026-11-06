export interface Repo {
  id: number;
  github_id: number;
  full_name: string;
  name: string;
  description: string | null;
  language: string | null;
  default_branch: string;
  html_url: string;
  is_private: boolean;
  stars: number;
  last_synced_at: string | null;
  created_at: string;
  index_status: "pending" | "indexing" | "ready" | "failed";
  index_error: string | null;
  indexed_at: string | null;
}

export interface RemoteRepo {
  github_id: number;
  full_name: string;
  description: string | null;
  language: string | null;
  is_private: boolean;
  stars: number;
  updated_at: string | null;
  imported: boolean;
}

export interface FileNode {
  path: string;
  size: number;
  language: string | null;
}

export interface FileContent extends FileNode {
  content: string;
}

export interface SyncResult {
  added: number;
  updated: number;
  removed: number;
}
