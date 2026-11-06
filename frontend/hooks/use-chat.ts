import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { deleteChat, getChat, listChats } from "@/services/chat";

export const useChats = (repoId: number) => useQuery({ queryKey: ["chats", repoId], queryFn: () => listChats(repoId) });

export const useChat = (chatId: number | null) =>
  useQuery({
    queryKey: ["chat", chatId],
    queryFn: () => getChat(chatId as number),
    enabled: chatId !== null,
    staleTime: 0,
  });

export function useDeleteChat(repoId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteChat,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["chats", repoId] }),
  });
}
