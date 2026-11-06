export interface Finding {
  id: number;
  path: string;
  line: number | null;
  severity: "critical" | "warning" | "suggestion";
  category: string;
  title: string;
  description: string;
  suggestion: string | null;
}

export interface ReviewSummary {
  id: number;
  repo_id: number;
  paths: string[];
  status: "pending" | "running" | "completed" | "failed";
  error: string | null;
  summary: string | null;
  score: number | null;
  created_at: string;
  completed_at: string | null;
}

export interface ReviewDetail extends ReviewSummary {
  findings: Finding[];
}
