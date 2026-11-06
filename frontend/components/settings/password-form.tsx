"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { FormField } from "@/components/auth/form-field";
import { Button } from "@/components/ui/button";
import { useChangePassword } from "@/hooks/use-settings";
import { passwordSchema, type PasswordInput } from "@/lib/validations/settings";

export function PasswordForm() {
  const { register, handleSubmit, reset, formState: { errors } } = useForm<PasswordInput>({ resolver: zodResolver(passwordSchema) });
  const { mutate, isPending, error, isSuccess } = useChangePassword();

  return (
    <form
      onSubmit={handleSubmit((values) =>
        mutate({ current: values.current_password, next: values.new_password }, { onSuccess: () => reset() })
      )}
      className="space-y-4"
      noValidate
    >
      <FormField id="current_password" label="Current password" type="password" autoComplete="current-password" error={errors.current_password?.message} {...register("current_password")} />
      <FormField id="new_password" label="New password" type="password" autoComplete="new-password" error={errors.new_password?.message} {...register("new_password")} />
      <FormField id="confirm_password" label="Confirm new password" type="password" autoComplete="new-password" error={errors.confirm_password?.message} {...register("confirm_password")} />
      {error && <p role="alert" className="text-sm text-destructive">{error.message}</p>}
      {isSuccess && <p role="status" className="text-sm text-muted-foreground">Password updated.</p>}
      <Button type="submit" disabled={isPending}>{isPending ? "Updating…" : "Change password"}</Button>
    </form>
  );
}
