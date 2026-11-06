"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { FormField } from "@/components/auth/form-field";
import { Button } from "@/components/ui/button";
import { useRegister } from "@/hooks/use-auth-actions";
import { registerSchema, type RegisterInput } from "@/lib/validations/auth";

export function RegisterForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<RegisterInput>({ resolver: zodResolver(registerSchema) });
  const { mutate, isPending, error } = useRegister();

  return (
    <form onSubmit={handleSubmit((values) => mutate(values))} className="space-y-4" noValidate>
      <FormField id="full_name" label="Full name" autoComplete="name" error={errors.full_name?.message} {...register("full_name")} />
      <FormField id="email" label="Email" type="email" autoComplete="email" error={errors.email?.message} {...register("email")} />
      <FormField id="password" label="Password" type="password" autoComplete="new-password" error={errors.password?.message} {...register("password")} />
      {error && <p role="alert" className="text-sm text-destructive">{error.message}</p>}
      <Button type="submit" className="w-full" disabled={isPending}>
        {isPending ? "Creating account…" : "Create account"}
      </Button>
    </form>
  );
}
