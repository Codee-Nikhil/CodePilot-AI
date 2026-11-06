"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useAuth } from "@/components/auth-provider";
import { FormField } from "@/components/auth/form-field";
import { Button } from "@/components/ui/button";
import { useUpdateProfile } from "@/hooks/use-settings";
import { profileSchema, type ProfileInput } from "@/lib/validations/settings";

export function ProfileForm() {
  const { user } = useAuth();
  const { register, handleSubmit, formState: { errors } } = useForm<ProfileInput>({
    resolver: zodResolver(profileSchema),
    defaultValues: { full_name: user?.full_name ?? "" },
  });
  const { mutate, isPending, error, isSuccess } = useUpdateProfile();

  return (
    <form onSubmit={handleSubmit((values) => mutate(values.full_name))} className="space-y-4" noValidate>
      <FormField id="full_name" label="Full name" error={errors.full_name?.message} {...register("full_name")} />
      {error && <p role="alert" className="text-sm text-destructive">{error.message}</p>}
      {isSuccess && <p role="status" className="text-sm text-muted-foreground">Saved.</p>}
      <Button type="submit" disabled={isPending}>{isPending ? "Saving…" : "Save changes"}</Button>
    </form>
  );
}
