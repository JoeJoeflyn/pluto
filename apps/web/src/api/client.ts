// Typed fetch wrapper for the FastAPI backend.
// In dev, Vite proxies /api -> http://127.0.0.1:8765.
// In prod, set VITE_API_BASE to the deployed origin.

const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined) ?? "/api";

export class ApiError extends Error {
  status: number;
  detail: unknown;
  constructor(status: number, detail: unknown) {
    super(`API ${status}`);
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...init.headers },
    ...init,
  });
  if (!res.ok) {
    let detail: unknown;
    try {
      detail = await res.json();
    } catch {
      detail = await res.text();
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export type LineItemIn = {
  name: string;
  price: number;
  quantity?: number;
  category?: string | null;
};

export type LineItem = LineItemIn & {
  id: number;
  order_index: number;
};

export type Expense = {
  id: number;
  date: string;
  time: string | null;
  amount: number;
  currency: string;
  subtotal: number | null;
  tax: number | null;
  tip: number | null;
  discount: number | null;
  payment_method: string | null;
  card_type: string | null;
  card_last4: string | null;
  cashier: string | null;
  transaction_id: string | null;
  reference_id: string | null;
  auth_id: string | null;
  address: string | null;
  phone: string | null;
  email: string | null;
  category: string;
  merchant: string;
  merchant_id: number | null;
  notes: string;
  image_path: string;
  raw_text: string | null;
  created_at: string;
  updated_at: string;
  synced_at: string | null;
  line_items: LineItem[];
};

export type ExpenseCreate = {
  date: string;
  amount: number;
  currency?: string;
  category: string;
  merchant: string;
  notes?: string;
  image_path?: string;
  time?: string | null;
  subtotal?: number | null;
  tax?: number | null;
  tip?: number | null;
  discount?: number | null;
  payment_method?: string | null;
  card_type?: string | null;
  card_last4?: string | null;
  cashier?: string | null;
  transaction_id?: string | null;
  reference_id?: string | null;
  auth_id?: string | null;
  address?: string | null;
  phone?: string | null;
  email?: string | null;
  raw_text?: string | null;
  line_items?: LineItemIn[];
};

export type ExpenseUpdate = Partial<ExpenseCreate>;

export type Category = { id: number; name: string; icon: string };

export type Merchant = {
  id: number;
  name: string;
  address: string | null;
  phone: string | null;
  email: string | null;
  first_seen: string | null;
  last_seen: string | null;
  visit_count: number;
};

export type CategoryBreakdown = {
  category: string;
  total: number;
  count: number;
};

export type Stats = {
  total: number;
  count: number;
  by_category: CategoryBreakdown[];
  filters: { month: number | null; year: number | null; category_breakdown: boolean };
};

export type ScanResult = {
  image_path: string;
  extracted: {
    date: string | null;
    amount: number | null;
    currency: string;
    merchant: string | null;
    address?: string | null;
    phone?: string | null;
    category?: string;
    items?: { name: string; price: number }[];
    confidence?: string;
  };
  errors: string[];
  needs_review: string[];
};

export const api = {
  health: () => request<{ status: string }>("/health"),

  categories: () => request<Category[]>("/categories"),

  merchants: () => request<Merchant[]>("/merchants"),

  expenses: (params: { category?: string; month?: number; year?: number; limit?: number } = {}) => {
    const q = new URLSearchParams();
    if (params.category) q.set("category", params.category);
    if (params.month) q.set("month", String(params.month));
    if (params.year) q.set("year", String(params.year));
    if (params.limit) q.set("limit", String(params.limit));
    const qs = q.toString();
    return request<Expense[]>(`/expenses${qs ? `?${qs}` : ""}`);
  },

  expense: (id: number) => request<Expense>(`/expenses/${id}`).catch(async () => {
    // No GET /expenses/{id} endpoint — fetch list and find. Rare path.
    const all = await request<Expense[]>("/expenses?limit=500");
    const e = all.find((x) => x.id === id);
    if (!e) throw new ApiError(404, { detail: "Expense not found" });
    return e;
  }),

  expenseItems: (id: number) => request<LineItem[]>(`/expenses/${id}/items`),

  createExpense: (body: ExpenseCreate) =>
    request<Expense>("/expenses", { method: "POST", body: JSON.stringify(body) }),

  updateExpense: (id: number, body: ExpenseUpdate) =>
    request<Expense>(`/expenses/${id}`, { method: "PUT", body: JSON.stringify(body) }),

  deleteExpense: (id: number) =>
    request<{ detail: string }>(`/expenses/${id}`, { method: "DELETE" }),

  stats: (params: { month?: number; year?: number; category?: boolean } = {}) => {
    const q = new URLSearchParams();
    if (params.month) q.set("month", String(params.month));
    if (params.year) q.set("year", String(params.year));
    if (params.category) q.set("category", "true");
    const qs = q.toString();
    return request<Stats>(`/stats${qs ? `?${qs}` : ""}`);
  },

  scan: async (file: File): Promise<ScanResult> => {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${API_BASE}/scan`, { method: "POST", body: form });
    if (!res.ok) {
      let detail: unknown;
      try { detail = await res.json(); } catch { detail = await res.text(); }
      throw new ApiError(res.status, detail);
    }
    return (await res.json()) as ScanResult;
  },
};
