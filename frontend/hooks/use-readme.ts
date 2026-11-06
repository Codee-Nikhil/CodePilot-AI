import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { generateReadme, getReadme } from "@/services/readme";

export const useReadme = (repoId: number) => useQuery({ queryKey: ["readme", repoId], queryFn: () => getReadme(repoId) });

export function useGenerateReadme(repoId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => generateReadme(repoId),
    onSuccess: (doc) => queryClient.setQueryData(["readme", repoId], doc),
  });
}
