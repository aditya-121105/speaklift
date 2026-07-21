import { GuestRoute } from "@/features/auth/components/guest-route";
import Link from "next/link";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <GuestRoute>
      <div className="flex min-h-screen flex-col items-center justify-center bg-background px-4 py-12 sm:px-6 lg:px-8">
        <div className="absolute top-8 left-8">
          <Link href="/" className="text-xl font-bold tracking-tight text-primary">
            SpeakLift
          </Link>
        </div>
        {children}
      </div>
    </GuestRoute>
  );
}
