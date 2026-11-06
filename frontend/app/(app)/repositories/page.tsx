"use client";

import { Suspense } from "react";
import { useAuth } from "@/components/auth-provider";
import { CallbackNotice } from "@/components/repos/callback-notice";
import { GitHubConnectCard } from "@/components/repos/github-connect-card";
import { ImportPanel } from "@/components/repos/import-panel";
import { RepoCard } from "@/components/repos/repo-card";
import { Button } from "@/components/ui/button";
import { useDisconnectGitHub } from "@/hooks/use-github";
import { useRepos } from "@/hooks/use-repositories";

export default function RepositoriesPage() {
  const { user } = useAuth();
  const login = user?.github_login;
  const { data: repos, isPending, error } = useRepos();
  const disconnect = useDisconnectGitHub();

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">Repositories</h1>
        {login && (
          <Button variant="outline" size="sm" disabled={disconnect.isPending} onClick={() => disconnect.mutate()}>
            Disconnect @{login}
          </Button>
        )}
      </div>

      <Suspense><CallbackNotice /></Suspense>

      <section aria-label="Imported repositories">
        {isPending && <p className="text-muted-foreground">Loading…</p>}
        {error && <p role="alert" className="text-destructive">{error.message}</p>}
        {repos?.length === 0 && <p className="text-muted-foreground">No repositories yet. Import one below.</p>}
        <div className="grid gap-4 sm:grid-cols-2">
          {repos?.map((repo) => <RepoCard key={repo.id} repo={repo} />)}
        </div>
      </section>

      {login ? <ImportPanel /> : <GitHubConnectCard />}
    </div>
  );
}
