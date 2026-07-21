import * as React from "react";
import { cn } from "@/lib/utils";

interface PageContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export function PageContainer({ children, className, ...props }: PageContainerProps) {
  return (
    <div 
      className={cn("mx-auto w-full max-w-7xl p-4 sm:p-6 lg:p-8", className)} 
      {...props}
    >
      {children}
    </div>
  );
}
