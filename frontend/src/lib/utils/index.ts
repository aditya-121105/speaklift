import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Merges Tailwind classes efficiently without style conflicts.
 * Uses clsx for conditional classes and tailwind-merge to handle Tailwind specifics.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
