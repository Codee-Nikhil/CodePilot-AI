import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/auth-provider";
import { login, register } from "@/services/auth";

export function useLogin() {
  const { signIn } = useAuth();
  const router = useRouter();

  return useMutation({
    mutationFn: login,
    onSuccess: ({ access_token }) => {
      signIn(access_token);
      router.replace("/dashboard");
    },
  });
}

export function useRegister() {
  const { signIn } = useAuth();
  const router = useRouter();

  return useMutation({
    mutationFn: async (data: Parameters<typeof register>[0]) => {
      await register(data);
      return login({ email: data.email, password: data.password });
    },
    onSuccess: ({ access_token }) => {
      signIn(access_token);
      router.replace("/dashboard");
    },
  });
}
