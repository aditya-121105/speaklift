import Link from "next/link";
import { FileQuestion } from "lucide-react";

export default function NotFound() {
  return (
    <div className="flex min-h-[calc(100vh-100px)] flex-col items-center justify-center p-6 text-center">
      <FileQuestion className="mb-4 h-16 w-16 text-muted-foreground" />
      <h2 className="mb-2 text-3xl font-bold tracking-tight">404 - Page Not Found</h2>
      <p className="mb-8 max-w-md text-muted-foreground">
        The page you&apos;re looking for doesn&apos;t exist or has been moved.
      </p>
      <Link
        href="/"
        className="rounded-md bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary-hover focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
      >
        Return Home
      </Link>
    </div>
  );
}
