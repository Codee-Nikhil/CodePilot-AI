import { apiFetch } from "@/services/api";
import type { DashboardStats } from "@/types/dashboard";

export const getDashboardStats = () => apiFetch<DashboardStats>("/dashboard/stats");
