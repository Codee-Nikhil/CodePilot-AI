import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { deleteReview, getReview, listReviews, startReview } from "@/services/reviews";

export const useReviews = (repoId: number) => useQuery({ queryKey: ["reviews", repoId], queryFn: () => listReviews(repoId) });

export const useReview = (id: number | null) =>
  useQuery({
    queryKey: ["review", id],
    queryFn: () => getReview(id as number),
    enabled: id !== null,
    refetchInterval: (query) => (["pending", "running"].includes(query.state.data?.status ?? "") ? 2000 : false),
  });

export function useStartReview(repoId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (paths: string[]) => startReview(repoId, paths),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["reviews", repoId] }),
  });
}

export function useDeleteReview(repoId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteReview,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["reviews", repoId] }),
  });
}
