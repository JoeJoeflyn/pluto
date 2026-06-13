import type { Category } from "@/api/client";

export function pickCategory(ai: string | undefined, cats: Category[]): string {
  if (!ai) return "Other";
  const norm = ai.toLowerCase();
  const hit = cats.find((c) => norm.includes(c.name.toLowerCase()));
  return hit?.name ?? "Other";
}
