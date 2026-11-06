import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/services/api";

interface HealthResponse {
  status: string;
  database: string;
}

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: () => apiFetch<HealthResponse>("/health"),
    retry: false,
  });
}
