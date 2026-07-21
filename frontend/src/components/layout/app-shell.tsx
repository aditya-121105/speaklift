"use client";

import * as React from "react";
import { Sidebar } from "./sidebar";
import { Header } from "./header";
import { Sheet, SheetContent, SheetTitle } from "@/components/ui/sheet";
import { MAIN_NAVIGATION, BOTTOM_NAVIGATION, NavItem } from "@/config/navigation";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

export function AppShell({ children }: { children: React.ReactNode }) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);
  const pathname = usePathname();



  const MobileNavLink = ({ item }: { item: NavItem }) => {
    const isActive = pathname.startsWith(item.href);
    return (
      <Link
        href={item.disabled ? "#" : item.href}
        onClick={() => setIsMobileMenuOpen(false)}
        className={cn(
          "flex items-center gap-3 rounded-md px-3 py-2 text-base font-medium transition-colors",
          isActive 
            ? "bg-primary/10 text-primary" 
            : "text-muted-foreground hover:bg-surface-elevated hover:text-foreground",
          item.disabled && "cursor-not-allowed opacity-60"
        )}
      >
        <item.icon className="h-5 w-5" />
        {item.title}
      </Link>
    );
  };

  return (
    <div className="flex min-h-screen w-full bg-background">
      <Sidebar />
      
      {/* Mobile Drawer */}
      <Sheet open={isMobileMenuOpen} onOpenChange={setIsMobileMenuOpen}>
        <SheetContent side="left" className="w-[280px] p-0 border-r border-border/50 bg-background">
          <SheetTitle className="sr-only">Navigation Menu</SheetTitle>
          <div className="flex h-16 shrink-0 items-center px-6">
            <Link href="/dashboard" className="text-xl font-bold tracking-tight text-primary">
              SpeakLift
            </Link>
          </div>
          <div className="flex flex-1 flex-col overflow-y-auto px-3 py-4">
            <nav className="flex-1 space-y-1">
              {MAIN_NAVIGATION.map((item) => (
                <MobileNavLink key={item.title} item={item} />
              ))}
            </nav>
            <div className="mt-8">
              <nav className="space-y-1">
                {BOTTOM_NAVIGATION.map((item) => (
                  <MobileNavLink key={item.title} item={item} />
                ))}
              </nav>
            </div>
          </div>
        </SheetContent>
      </Sheet>

      <div className="flex flex-1 flex-col">
        <Header onMenuClick={() => setIsMobileMenuOpen(true)} />
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
