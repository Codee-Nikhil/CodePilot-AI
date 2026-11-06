import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/auth-provider";
import { changePassword, deleteAccount, updateProfile } from "@/services/settings";

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (full_name: string) => updateProfile(full_name),
    onSuccess: (user) => queryClient.setQueryData(["me"], user),
  });
}

export function useChangePassword() {
  return useMutation({
    mutationFn: ({ current, next }: { current: string; next: string }) => changePassword(current, next),
  });
}

export function useDeleteAccount() {
  const { logout } = useAuth();
  const router = useRouter();
  return useMutation({
    mutationFn: (password: string) => deleteAccount(password),
    onSuccess: () => {
      logout();
      router.replace("/login");
    },
  });
}
