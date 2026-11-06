import { Badge } from "@/components/ui/badge";
import type { Finding } from "@/types/review";

const SEVERITY_VARIANT = { critical: "destructive", warning: "secondary", suggestion: "outline" } as const;

export function FindingCard({ finding }: { finding: Finding }) {
  return (
    <div className="rounded-lg border p-4">
      <div className="flex flex-wrap items-center gap-2">
        <Badge variant={SEVERITY_VARIANT[finding.severity]}>{finding.severity}</Badge>
        <Badge variant="outline">{finding.category}</Badge>
        <span className="font-mono text-xs text-muted-foreground">
          {finding.path}{finding.line ? `:${finding.line}` : ""}
        </span>
      </div>
      <p className="mt-2 font-medium">{finding.title}</p>
      <p className="mt-1 text-sm text-muted-foreground">{finding.description}</p>
      {finding.suggestion && (
        <p className="mt-2 rounded-md bg-muted p-2 text-sm">
          <span className="font-medium">Suggestion: </span>{finding.suggestion}
        </p>
      )}
    </div>
  );
}
