"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useRemoteRepos } from "@/hooks/use-github";
import { useImportRepo } from "@/hooks/use-repositories";

const FULL_NAME = /^[\w.-]+\/[\w.-]+$/;

export function ImportPanel() {
  const [query, setQuery] = useState("");
  const { data: remote, isPending, error: listError } = useRemoteRepos();
  const importRepo = useImportRepo();

  const trimmed = query.trim();
  const q = trimmed.toLowerCase();
  const visible = (remote ?? []).filter((r) => r.full_name.toLowerCase().includes(q));
  const canImportByName = FULL_NAME.test(trimmed) && !remote?.some((r) => r.full_name.toLowerCase() === q);
  const importing = importRepo.isPending ? importRepo.variables : null;
  const error = importRepo.error ?? listError;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Import a repository</CardTitle>
        <CardDescription>Pick one of yours, or type owner/name for any public repo.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <Input type="search" aria-label="Search repositories" placeholder="Search or type owner/name…" value={query} onChange={(e) => setQuery(e.target.value)} />
        {error && <p role="alert" className="text-sm text-destructive">{error.message}</p>}
        {canImportByName && (
          <Button variant="outline" disabled={importRepo.isPending} onClick={() => importRepo.mutate(trimmed)}>
            {importing === trimmed ? "Importing…" : `Import ${trimmed}`}
          </Button>
        )}
        {isPending ? (
          <p className="text-sm text-muted-foreground">Loading your repositories…</p>
        ) : (
          <ul className="max-h-96 divide-y overflow-y-auto">
            {visible.map((r) => (
              <li key={r.github_id} className="flex items-center justify-between gap-3 py-3">
                <div className="min-w-0">
                  <p className="truncate font-medium">{r.full_name} {r.is_private && <Badge variant="secondary">Private</Badge>}</p>
                  {r.description && <p className="truncate text-sm text-muted-foreground">{r.description}</p>}
                </div>
                <Button size="sm" variant={r.imported ? "outline" : "default"} disabled={r.imported || importRepo.isPending} onClick={() => importRepo.mutate(r.full_name)}>
                  {r.imported ? "Imported" : importing === r.full_name ? "Importing…" : "Import"}
                </Button>
              </li>
            ))}
            {!visible.length && <li className="py-3 text-sm text-muted-foreground">No matches.</li>}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
