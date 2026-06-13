export function formatMoney(n: number, currency = "USD"): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(n);
}

export function pad(n: number, len = 2): string {
  return n.toString().padStart(len, "0");
}
