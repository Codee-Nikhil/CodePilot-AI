import { GuestGuard } from "@/components/auth/route-guards";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <GuestGuard>
      <main className="flex min-h-screen items-center justify-center p-4">{children}</main>
    </GuestGuard>
  );
}
