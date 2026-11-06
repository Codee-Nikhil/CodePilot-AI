import { AppHeader } from "@/components/app-header";
import { AuthGuard } from "@/components/auth/route-guards";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <div className="flex min-h-screen flex-col">
        <AppHeader />
        <main className="flex-1 p-4 sm:p-6">{children}</main>
      </div>
    </AuthGuard>
  );
}
