export type Item = {
  name: string;
  price: number;
  quantity: number;
  category?: string | null;
};

export type ExpenseFormValues = {
  date: string;
  amount: number;
  currency: string;
  category: string;
  merchant: string;
  notes: string;
  time: string | null;
  subtotal: number | null;
  tax: number | null;
  tip: number | null;
  address: string | null;
  phone: string | null;
  payment_method: string | null;
  card_type: string | null;
  card_last4: string | null;
  cashier: string | null;
  transaction_id: string | null;
  line_items: Item[];
};

export const EMPTY_EXPENSE_VALUES: ExpenseFormValues = {
  date: new Date().toISOString().slice(0, 10),
  amount: 0,
  currency: "USD",
  category: "Other",
  merchant: "",
  notes: "",
  time: null,
  subtotal: null,
  tax: null,
  tip: null,
  address: null,
  phone: null,
  payment_method: null,
  card_type: null,
  card_last4: null,
  cashier: null,
  transaction_id: null,
  line_items: [],
};
