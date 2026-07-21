import type { Metadata, Viewport } from "next";
import { Inter, Geist_Mono } from "next/font/google";
import "@/app/globals.css";
import { GlobalProviders } from "@/providers/global-providers";
import { Toaster } from "@/components/ui/sonner";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    template: "%s | SpeakLift",
    default: "SpeakLift - Your AI Career Coach",
  },
  description: "Prepare for your next interview with an elite AI Career Coach.",
  icons: {
    // Placeholder for actual icons
    icon: "/favicon.ico",
  },
  openGraph: {
    // Placeholder for future SEO readiness
    type: "website",
    locale: "en_US",
    siteName: "SpeakLift",
  },
  twitter: {
    card: "summary_large_image",
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f9fafb" },
    { media: "(prefers-color-scheme: dark)", color: "#0a0a0a" },
  ],
  width: "device-width",
  initialScale: 1,
  maximumScale: 1, // Prevents iOS input zoom
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${geistMono.variable} min-h-screen bg-background text-foreground font-sans antialiased`}
      >
        <GlobalProviders>
          <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:p-4 focus:bg-background">
            Skip to content
          </a>
          <main id="main-content" className="flex-1 flex flex-col min-h-screen">
            {children}
          </main>
          <Toaster />
        </GlobalProviders>
      </body>
    </html>
  );
}
