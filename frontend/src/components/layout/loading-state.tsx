import * as React from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface LoadingStateProps extends React.HTMLAttributes<HTMLDivElement> {
  text?: string;
}

export function LoadingState({ text = "Loading...", className, ...props }: LoadingStateProps) {
  return (
    <div 
      className={cn("flex min-h-[400px] flex-col items-center justify-center space-y-4 animate-in fade-in-50", className)} 
      {...props}
    >
      <Loader2 className="h-10 w-10 animate-spin text-primary/80" />
      <p className="text-sm font-medium text-muted-foreground">{text}</p>
    </div>
  );
}
