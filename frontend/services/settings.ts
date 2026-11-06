import { apiFetch } from "@/services/api";
import type { User } from "@/types/auth";

export const updateProfile = (full_name: string) =>
  apiFetch<User>("/settings/profile", { method: "PUT", body: JSON.stringify({ full_name }) });

export const changePassword = (current_password: string, new_password: string) =>
  apiFetch<void>("/settings/password", {
    method: "PUT",
    body: JSON.stringify({ current_password, new_password }),
  });

export const deleteAccount = (password: string) =>
  apiFetch<void>("/settings/delete-account", { method: "POST", body: JSON.stringify({ password }) });
