import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import {
  deleteRepo, getFile, getRepo, getTree, importRepo, listRepos, reindexRepo, syncRepo,
} from "@/services/repositories";

export const useRepos = () => useQuery({ queryKey: ["repos"], queryFn: listRepos });

export const useRepo = (id: number) =>
  useQuery({
    queryKey: ["repos", id],
    queryFn: () => getRepo(id),
    retry: false,
    refetchInterval: (query) => (query.state.data?.index_status === "indexing" ? 3000 : false),
  });

export const useRepoTree = (id: number) => useQuery({ queryKey: ["repos", id, "tree"], queryFn: () => getTree(id) });

export const useRepoFile = (id: number, path: string | null) =>
  useQuery({
    queryKey: ["repos", id, "file", path],
    queryFn: () => getFile(id, path as string),
    enabled: !!path,
  });

export function useImportRepo() {
  const queryClient = useQueryClient();
  const router = useRouter();
  return useMutation({
    mutationFn: importRepo,
    onSuccess: (repo) => {
      queryClient.invalidateQueries({ queryKey: ["repos"] });
      queryClient.invalidateQueries({ queryKey: ["remote-repos"] });
      router.push(`/repositories/${repo.id}`);
    },
  });
}

export function useSyncRepo(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => syncRepo(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["repos", id] }),
  });
}

export function useReindexRepo(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => reindexRepo(id),
    onSuccess: (repo) => {
      queryClient.setQueryData(["repos", id], repo);
      queryClient.invalidateQueries({ queryKey: ["repos"], exact: true });
    },
  });
}

export function useDeleteRepo() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteRepo,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["repos"] });
      queryClient.invalidateQueries({ queryKey: ["remote-repos"] });
    },
  });
}
