import { Car, Circle, CircleDollarSign, Film, HeartPulse, Home, ShoppingBag, UtensilsCrossed, Zap } from "lucide-vue-next";
import type { Component } from "vue";

export const CATEGORY_ICONS: Record<string, Component> = {
  "Food & Dining": UtensilsCrossed,
  "Shopping": ShoppingBag,
  "Transportation": Car,
  "Housing": Home,
  "Health": HeartPulse,
  "Entertainment": Film,
  "Utilities": Zap,
  "Other": CircleDollarSign,
};

export function iconForCategory(name: string): Component {
  return CATEGORY_ICONS[name] ?? Circle;
}
