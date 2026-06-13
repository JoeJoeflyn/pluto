import { EMPTY_EXPENSE_VALUES } from "@/constants/expense-form";

export function toDateInput(s: string | null | undefined): string {
  if (!s) return EMPTY_EXPENSE_VALUES.date;
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return s;
  const d = new Date(s);
  if (!Number.isNaN(d.getTime())) return d.toISOString().slice(0, 10);
  return EMPTY_EXPENSE_VALUES.date;
}
