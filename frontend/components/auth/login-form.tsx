"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { FormField } from "@/components/auth/form-field";
import { Button } from "@/components/ui/button";
import { useLogin } from "@/hooks/use-auth-actions";
import { loginSchema, type LoginInput } from "@/lib/validations/auth";

export function LoginForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<LoginInput>({ resolver: zodResolver(loginSchema) });
  const { mutate, isPending, error } = useLogin();

  return (
    <form onSubmit={handleSubmit((values) => mutate(values))} className="space-y-4" noValidate>
      <FormField id="email" label="Email" type="email" autoComplete="email" error={errors.email?.message} {...register("email")} />
      <FormField id="password" label="Password" type="password" autoComplete="current-password" error={errors.password?.message} {...register("password")} />
      {error && <p role="alert" className="text-sm text-destructive">{error.message}</p>}
      <Button type="submit" className="w-full" disabled={isPending}>
        {isPending ? "Signing in…" : "Sign in"}
      </Button>
    </form>
  );
}
