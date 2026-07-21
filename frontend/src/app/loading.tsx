export default function Loading() {
  return (
    <div className="flex h-[calc(100vh-100px)] w-full items-center justify-center">
      <div className="flex flex-col items-center space-y-4">
        {/* Subtle pulsing skeleton indicator */}
        <div className="h-8 w-8 animate-pulse rounded-full bg-primary/20"></div>
        <p className="text-sm font-medium text-muted-foreground animate-pulse">Loading...</p>
      </div>
    </div>
  );
}
