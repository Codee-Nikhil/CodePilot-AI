import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { Repo } from "@/types/repo";

export function RepoCard({ repo }: { repo: Repo }) {
  return (
    <Link href={`/repositories/${repo.id}`} className="block rounded-xl focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
      <Card className="h-full transition-colors hover:bg-accent/50">
        <CardHeader>
          <CardTitle className="truncate text-base">{repo.full_name}</CardTitle>
          <CardDescription className="line-clamp-2">{repo.description ?? "No description"}</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
          {repo.language && <Badge variant="secondary">{repo.language}</Badge>}
          {repo.is_private && <Badge variant="outline">Private</Badge>}
          <span>★ {repo.stars}</span>
        </CardContent>
      </Card>
    </Link>
  );
}
