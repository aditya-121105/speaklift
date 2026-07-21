import { Home, FileText, Mic, BarChart, Settings, User } from "lucide-react";

export interface NavItem {
  title: string;
  href: string;
  icon: React.ElementType;
  disabled?: boolean;
}

export const MAIN_NAVIGATION: NavItem[] = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: Home,
  },
  {
    title: "Interviews",
    href: "/interviews",
    icon: Mic,
  },
  {
    title: "Resume",
    href: "/resume",
    icon: FileText,
  },
  {
    title: "Reports",
    href: "/reports",
    icon: BarChart,
  },
];

export const BOTTOM_NAVIGATION: NavItem[] = [
  {
    title: "Profile",
    href: "/profile",
    icon: User,
  },
  {
    title: "Settings",
    href: "/settings",
    icon: Settings,
  },
];
