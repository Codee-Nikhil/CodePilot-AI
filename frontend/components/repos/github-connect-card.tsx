"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useConnectGitHub } from "@/hooks/use-github";

export function GitHubConnectCard() {
  const { mutate, isPending, error } = useConnectGitHub();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Connect GitHub</CardTitle>
        <CardDescription>Link your account to import repositories. CodePilot only reads code; it never writes to your repos.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <Button onClick={() => mutate()} disabled={isPending}>{isPending ? "Redirecting…" : "Connect GitHub"}</Button>
        {error && <p role="alert" className="text-sm text-destructive">{error.message}</p>}
      </CardContent>
    </Card>
  );
}
