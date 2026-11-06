"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/components/auth-provider";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/repositories", label: "Repositories" },
  { href: "/settings", label: "Settings" },
];

export function AppHeader() {
  const { user, logout } = useAuth();
  const pathname = usePathname();

  return (
    <header className="flex flex-wrap items-center justify-between gap-2 border-b px-4 py-3 sm:px-6">
      <div className="flex items-center gap-4">
        <span className="font-semibold">CodePilot AI</span>
        <nav aria-label="Main" className="flex items-center gap-1">
          {NAV.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className={cn(
                "rounded-md px-3 py-1.5 text-sm hover:bg-accent",
                pathname.startsWith(href) && "bg-accent font-medium"
              )}
            >
              {label}
            </Link>
          ))}
        </nav>
      </div>
      <div className="flex items-center gap-3">
        <span className="hidden text-sm text-muted-foreground sm:inline">{user?.full_name}</span>
        <ThemeToggle />
        <Button variant="outline" size="sm" onClick={logout}>Log out</Button>
      </div>
    </header>
  );
}
