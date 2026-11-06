import { apiFetch } from "@/services/api";
import type { LoginInput, RegisterInput } from "@/lib/validations/auth";
import type { TokenResponse, User } from "@/types/auth";

export const register = (data: RegisterInput) =>
  apiFetch<User>("/auth/register", { method: "POST", body: JSON.stringify(data) });

export const login = ({ email, password }: LoginInput) =>
  apiFetch<TokenResponse>("/auth/login", {
    method: "POST",
    body: new URLSearchParams({ username: email, password }),
  });

export const getMe = () => apiFetch<User>("/users/me");
