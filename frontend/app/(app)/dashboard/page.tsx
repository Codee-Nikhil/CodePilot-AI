"use client";

import Link from "next/link";
import { useAuth } from "@/components/auth-provider";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useDashboardStats } from "@/hooks/use-dashboard";

const CARDS = [
  { key: "repositories", label: "Repositories" },
  { key: "files_analyzed", label: "Files Analyzed" },
  { key: "reviews", label: "AI Reviews" },
  { key: "chats", label: "Chats" },
] as const;

export default function DashboardPage() {
  const { user } = useAuth();
  const { data: stats, isPending, error } = useDashboardStats();

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-2xl font-semibold">Welcome, {user?.full_name}</h1>

      {error && <p role="alert" className="text-destructive">{error.message}</p>}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {CARDS.map(({ key, label }) => (
          <Card key={key}>
            <CardHeader className="pb-2">
              <CardDescription>{label}</CardDescription>
              <CardTitle className="text-3xl">{isPending ? "…" : stats?.[key]}</CardTitle>
            </CardHeader>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Get started</CardTitle>
          <CardDescription>Connect GitHub and import a repository to begin.</CardDescription>
        </CardHeader>
        <CardContent>
          <Link href="/repositories" className="text-sm underline underline-offset-4">
            Go to Repositories →
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}
