"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

const MESSAGES: Record<string, { text: string; ok: boolean }> = {
  connected: { text: "GitHub connected.", ok: true },
  denied: { text: "GitHub access was not granted.", ok: false },
  in_use: { text: "That GitHub account is already linked to another CodePilot account.", ok: false },
  error: { text: "Could not connect GitHub. Please try again.", ok: false },
};

export function CallbackNotice() {
  const params = useSearchParams();
  const router = useRouter();
  const [notice] = useState(() => MESSAGES[params.get("github") ?? ""]);

  useEffect(() => {
    if (notice) router.replace("/repositories", { scroll: false });
  }, [notice, router]);

  if (!notice) return null;
  return (
    <p role="status" className={`rounded-md border px-3 py-2 text-sm ${notice.ok ? "" : "border-destructive text-destructive"}`}>
      {notice.text}
    </p>
  );
}
