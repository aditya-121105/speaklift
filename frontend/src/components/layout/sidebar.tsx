"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { MAIN_NAVIGATION, BOTTOM_NAVIGATION, NavItem } from "@/config/navigation";

export function Sidebar() {
  const pathname = usePathname();

  const NavLink = ({ item }: { item: NavItem }) => {
    const isActive = pathname.startsWith(item.href);
    return (
      <Link
        href={item.disabled ? "#" : item.href}
        className={cn(
          "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
          isActive 
            ? "bg-primary/10 text-primary" 
            : "text-muted-foreground hover:bg-surface-elevated hover:text-foreground",
          item.disabled && "cursor-not-allowed opacity-60"
        )}
      >
        <item.icon className="h-4 w-4" />
        {item.title}
      </Link>
    );
  };

  return (
    <aside className="hidden lg:flex w-64 flex-col border-r border-border/50 bg-background h-screen sticky top-0">
      <div className="flex h-16 shrink-0 items-center px-6">
        <Link href="/dashboard" className="text-xl font-bold tracking-tight text-primary">
          SpeakLift
        </Link>
      </div>
      
      <div className="flex flex-1 flex-col overflow-y-auto px-3 py-4">
        <nav className="flex-1 space-y-1">
          {MAIN_NAVIGATION.map((item) => (
            <NavLink key={item.title} item={item} />
          ))}
        </nav>
        
        <div className="mt-8">
          <nav className="space-y-1">
            {BOTTOM_NAVIGATION.map((item) => (
              <NavLink key={item.title} item={item} />
            ))}
          </nav>
        </div>
      </div>
    </aside>
  );
}
