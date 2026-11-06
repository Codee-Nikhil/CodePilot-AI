import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { disconnectGitHub, getConnectUrl, listRemoteRepos } from "@/services/github";

export function useConnectGitHub() {
  return useMutation({
    mutationFn: getConnectUrl,
    onSuccess: ({ url }) => window.location.assign(url),
  });
}

export function useDisconnectGitHub() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: disconnectGitHub,
    onSuccess: () => {
      queryClient.removeQueries({ queryKey: ["remote-repos"] });
      queryClient.invalidateQueries({ queryKey: ["me"] });
    },
  });
}

export const useRemoteRepos = () =>
  useQuery({ queryKey: ["remote-repos"], queryFn: listRemoteRepos, retry: false, staleTime: 60_000 });
