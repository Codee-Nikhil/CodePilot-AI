import { useQuery } from "@tanstack/react-query";
import { getDashboardStats } from "@/services/dashboard";

export const useDashboardStats = () => useQuery({ queryKey: ["dashboard-stats"], queryFn: getDashboardStats });
