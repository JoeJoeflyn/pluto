<script setup lang="ts">
import { reactive, watch, computed } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { api } from "@/api/client";
import LineItemEditor from "./LineItemEditor.vue";
import CategorySelect from "./CategorySelect.vue";
import { EMPTY_EXPENSE_VALUES, type ExpenseFormValues, type Item } from "@/constants/expense-form";
import { toDateInput } from "@/utils/date";
import { pickCategory } from "@/utils/category";

const props = withDefaults(
  defineProps<{
    initial?: Partial<ExpenseFormValues>;
    imagePath?: string;
    submitLabel: string;
    onSubmit: (v: ExpenseFormValues & { image_path: string }) => void | Promise<void>;
    busy?: boolean;
  }>(),
  { imagePath: "", busy: false },
);

const { data: cats } = useQuery({
  queryKey: ["categories"],
  queryFn: api.categories,
});

const v = reactive<ExpenseFormValues>({ ...EMPTY_EXPENSE_VALUES });

watch(
  [() => props.initial, () => cats.value],
  ([init, _cats]) => {
    if (!init) return;
    v.date = toDateInput(init.date);
    v.amount = init.amount ?? 0;
    v.currency = init.currency ?? "USD";
    v.category = pickCategory(init.category, _cats ?? []);
    v.merchant = init.merchant ?? "";
    v.notes = init.notes ?? "";
    v.time = init.time ?? null;
    v.subtotal = init.subtotal ?? null;
    v.tax = init.tax ?? null;
    v.tip = init.tip ?? null;
    v.address = init.address ?? null;
    v.phone = init.phone ?? null;
    v.payment_method = init.payment_method ?? null;
    v.card_type = init.card_type ?? null;
    v.card_last4 = init.card_last4 ?? null;
    v.cashier = init.cashier ?? null;
    v.transaction_id = init.transaction_id ?? null;
    v.line_items = (init.line_items ?? []).map((it) => ({
      name: it.name ?? "",
      price: it.price ?? 0,
      quantity: it.quantity ?? 1,
      category: it.category ?? null,
    }));
  },
  { deep: true, immediate: true },
);

const itemsTotal = computed(() =>
  v.line_items.reduce((s, it) => s + (Number(it.price) || 0) * (Number(it.quantity) || 1), 0),
);

async function submit(e: Event) {
  e.preventDefault();
  await props.onSubmit({ ...v, image_path: props.imagePath });
}
</script>

<template>
  <form @submit="submit">
    <hr class="dotted" />
    <div class="my-3">
      <h2 class="mb-2 text-ink font-bold tracking-[0.2em] uppercase">
        ═══ THE PARTICULARS ═══
      </h2>

      <div class="grid grid-cols-2 gap-3 max-tablet:grid-cols-1">
        <div>
          <label>MERCHANT</label>
          <input required :value="v.merchant" @input="v.merchant = ($event.target as HTMLInputElement).value" placeholder="e.g. STARBUCKS COFFEE" />
        </div>
        <div>
          <label>DATE</label>
          <input type="date" required :value="v.date" @input="v.date = ($event.target as HTMLInputElement).value" />
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3 max-tablet:grid-cols-1" style="margin-top: 14px">
        <div>
          <label>TOTAL</label>
          <input type="number" step="0.01" required :value="v.amount || ''" @input="v.amount = Number(($event.target as HTMLInputElement).value) || 0" />
        </div>
        <div>
          <label>CURRENCY</label>
          <input :value="v.currency" @input="v.currency = ($event.target as HTMLInputElement).value.toUpperCase()" maxlength="3" placeholder="USD" />
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3 max-tablet:grid-cols-1" style="margin-top: 14px">
        <div>
          <label>CATEGORY</label>
          <CategorySelect :value="v.category" @change="(name: string) => v.category = name" :categories="cats ?? []" />
        </div>
        <div>
          <label>TIME</label>
          <input :value="v.time ?? ''" @input="v.time = ($event.target as HTMLInputElement).value || null" placeholder="14:30" />
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3 max-tablet:grid-cols-1" style="margin-top: 14px">
        <div>
          <label>PAYMENT METHOD</label>
          <input :value="v.payment_method ?? ''" @input="v.payment_method = ($event.target as HTMLInputElement).value || null" placeholder="CREDIT / CASH / ..." />
        </div>
        <div>
          <label>CARD LAST 4</label>
          <input :value="v.card_last4 ?? ''" @input="v.card_last4 = ($event.target as HTMLInputElement).value || null" maxlength="4" placeholder="0000" />
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3 max-tablet:grid-cols-1" style="margin-top: 14px">
        <div>
          <label>SUBTOTAL</label>
          <input type="number" step="0.01" :value="v.subtotal ?? ''" @input="v.subtotal = ($event.target as HTMLInputElement).value === '' ? null : Number(($event.target as HTMLInputElement).value)" />
        </div>
        <div>
          <label>TAX</label>
          <input type="number" step="0.01" :value="v.tax ?? ''" @input="v.tax = ($event.target as HTMLInputElement).value === '' ? null : Number(($event.target as HTMLInputElement).value)" />
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3 max-tablet:grid-cols-1" style="margin-top: 14px">
        <div>
          <label>ADDRESS</label>
          <input :value="v.address ?? ''" @input="v.address = ($event.target as HTMLInputElement).value || null" placeholder="STORE STREET" />
        </div>
        <div>
          <label>PHONE</label>
          <input :value="v.phone ?? ''" @input="v.phone = ($event.target as HTMLInputElement).value || null" placeholder="STORE PHONE" />
        </div>
      </div>

      <div style="margin-top: 14px">
        <label>NOTES</label>
        <input :value="v.notes" @input="v.notes = ($event.target as HTMLInputElement).value" placeholder="OPTIONAL" />
      </div>
    </div>

    <hr class="dotted" />
    <div class="my-3">
      <h2 class="mb-2 text-ink font-bold tracking-[0.2em] uppercase">
        ═══ LINE ITEMS ═══
      </h2>
      <LineItemEditor :items="v.line_items" @change="(items: Item[]) => v.line_items = items" />
    </div>

    <hr class="double" />
    <div class="flex items-baseline justify-between py-1.5 text-sm font-bold border-dashed border-ink border gap-3">
      <span class="text-xs font-semibold tracking-[0.14em] uppercase">▌ ITEMS TOTAL</span>
      <span class="text-start font-bold tabular-nums whitespace-nowrap">{{ itemsTotal.toFixed(2) }} {{ v.currency }}</span>
    </div>
    <div class="flex items-baseline justify-between py-1.5 text-sm font-bold border-dashed border-ink border gap-3">
      <span class="text-xs font-semibold tracking-[0.14em] uppercase">▌ RECEIPT TOTAL</span>
      <span class="text-start font-bold tabular-nums whitespace-nowrap">{{ (v.amount || 0).toFixed(2) }} {{ v.currency }}</span>
    </div>

    <div class="flex items-baseline justify-between py-0.75 gap-3" style="margin-top: 18px">
      <span class="text-ink-dim" style="font-size: 10px">{{ v.line_items.length }} ITEM{{ v.line_items.length === 1 ? "" : "S" }} · {{ v.currency }}</span>
      <button type="submit" :disabled="busy || !v.merchant || !v.amount">
        {{ busy ? "▌▌ PRINTING…" : `▸ ${submitLabel.toUpperCase()}` }}
      </button>
    </div>
  </form>
</template>
