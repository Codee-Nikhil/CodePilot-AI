"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useDeleteAccount } from "@/hooks/use-settings";

export function DeleteAccountDialog() {
  const [open, setOpen] = useState(false);
  const [password, setPassword] = useState("");
  const { mutate, isPending, error } = useDeleteAccount();

  if (!open) {
    return <Button variant="destructive" onClick={() => setOpen(true)}>Delete account</Button>;
  }

  return (
    <div className="space-y-3 rounded-lg border border-destructive p-4">
      <p className="text-sm">This permanently deletes your account, repositories, reviews and chats. Enter your password to confirm.</p>
      <div className="space-y-2">
        <Label htmlFor="delete-password">Password</Label>
        <Input id="delete-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      </div>
      {error && <p role="alert" className="text-sm text-destructive">{error.message}</p>}
      <div className="flex gap-2">
        <Button variant="destructive" disabled={!password || isPending} onClick={() => mutate(password)}>
          {isPending ? "Deleting…" : "Permanently delete"}
        </Button>
        <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
      </div>
    </div>
  );
}
