<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/vue-query";
import { api } from "@/api/client";
import ExpenseForm from "@/components/ExpenseForm.vue";
import { formatMoney, pad } from "@/utils/format";
import type { ExpenseFormValues } from "@/constants/expense-form";

const route = useRoute();
const router = useRouter();
const queryClient = useQueryClient();

const expenseId = computed(() => Number(route.params.id));

const { data: expense, isLoading } = useQuery({
  queryKey: ["expense", expenseId],
  queryFn: () => api.expense(expenseId.value),
  enabled: computed(() => Number.isFinite(expenseId.value)),
});

const winConfirm = (msg: string) => window.confirm(msg);
const winAlert = (msg: string) => alert(msg);
function handleDelete() {
  if (!e.value) return;
  if (winConfirm('STRIKE THIS ENTRY FROM THE LEDGER? THIS CANNOT BE UNDONE.')) del.mutate(e.value.id);
}

const del = useMutation({
  mutationFn: (id: number) => api.deleteExpense(id),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ["expenses"] });
    queryClient.invalidateQueries({ queryKey: ["merchants"] });
    queryClient.invalidateQueries({ queryKey: ["stats"] });
    router.push("/expenses");
  },
});

const e = computed(() => expense.value);

const initial = computed<Partial<ExpenseFormValues> | undefined>(() => {
  if (!e.value) return undefined;
  return {
    date: e.value.date,
    amount: e.value.amount,
    currency: e.value.currency,
    category: e.value.category,
    merchant: e.value.merchant,
    notes: e.value.notes,
    time: e.value.time,
    subtotal: e.value.subtotal,
    tax: e.value.tax,
    tip: e.value.tip,
    address: e.value.address,
    phone: e.value.phone,
    payment_method: e.value.payment_method,
    card_type: e.value.card_type,
    card_last4: e.value.card_last4,
    cashier: e.value.cashier,
    transaction_id: e.value.transaction_id,
    line_items: (e.value.line_items ?? []).map((it) => ({
      name: it.name,
      price: it.price,
      quantity: it.quantity ?? 1,
      category: it.category ?? null,
    })),
  };
});
</script>

<template>
  <div>
    <template v-if="isLoading">
      <div class="p-2 my-2 text-ink-mid tracking-[0.14em] border-dashed border-ink border uppercase">
        <span class="inline-block h-2.5 w-2.5 border-2 border-ink-dim border-t-stamp rounded-full align-middle animate-spin" /> FETCHING ENTRY FROM THE LEDGER…
      </div>
    </template>

    <template v-else-if="!e">
      <div>
        <div class="p-2 my-2 text-start font-semibold tracking-[0.14em] border-stamp border uppercase">— ENTRY №{{ pad(expenseId) }} COULD NOT BE LOCATED —</div>
        <div class="text-center" style="margin-top:12px"><button class="ghost" @click="router.push('/expenses')">◂ RETURN TO THE REGISTER</button></div>
      </div>
    </template>

    <template v-else>
      <div class="my-3">
        <div class="mt-1 text-ink-mid tracking-[0.2em] uppercase">═══ ENTRY №{{ pad(e.id) }} · {{ e.category.toUpperCase() }} ═══</div>
        <h2 style="font-size:22px;margin:4px 0 0;letter-spacing:0.06em">► {{ e.merchant.toUpperCase() }}</h2>
        <div class="text-ink-dim" style="font-size:11px;margin-top:4px">
          FILED ON {{ new Date(e.date).toLocaleDateString("en-US", { year: "numeric", month: "2-digit", day: "2-digit" }) }}{{ e.merchant_id != null ? ` · MERCHANT №${e.merchant_id}` : '' }}
        </div>
      </div>

      <hr class="dotted" />

      <div class="my-3">
        <div class="flex items-baseline justify-between py-0.75 font-bold gap-3" style="border-top:none;border-bottom:none;font-size:14px">
          <span class="text-xs font-semibold tracking-[0.14em] uppercase" style="font-size:12px">▌ GRAND TOTAL</span>
          <span class="text-start font-bold tabular-nums whitespace-nowrap" style="font-size:28px;font-weight:700">{{ formatMoney(e.amount, e.currency) }}</span>
        </div>
      </div>

      <template v-if="e.image_path">
        <hr class="dotted" />
        <div class="my-3">
          <h2 class="mb-2 text-start font-bold tracking-[0.2em] uppercase">═══ THE ORIGINAL DOCUMENT ═══</h2>
          <div class="text-ink-dim" style="font-size:10px;margin-bottom:8px">
            <a :href="`/api/${e.image_path}`" target="_blank" rel="noopener noreferrer" style="border-bottom:1px dotted var(--color-ink)">► VIEW FULL SIZE ({{ e.image_path }})</a>
          </div>
          <img :src="`/api/${e.image_path}`" alt="Receipt" class="block max-w-full bg-white border-ink -z-auto border" />
        </div>
      </template>

      <hr class="dotted" />

      <ExpenseForm
        :initial="initial"
        :image-path="e.image_path"
        submit-label="Save changes"
        :on-submit="async () => { winAlert('EDITING EXISTING ENTRIES IS NOT WIRED IN THIS BUILD. STRIKE & RE-FILE TO CHANGE.'); }"
        :busy="false"
      />

      <hr class="double" />

      <div class="my-3">
        <h2 class="mb-2 text-start font-bold tracking-[0.2em] uppercase">═══ DANGER ZONE ═══</h2>
        <div class="flex items-baseline justify-between py-0.75 gap-3">
          <span class="text-ink-dim" style="font-size:10px">STRIKING THIS ENTRY WILL REMOVE THE RECEIPT AND IMAGE</span>
          <button class="stamp" :disabled="del.isPending.value" @click="handleDelete">
            {{ del.isPending.value ? "STRIKING…" : "✕ STRIKE FROM LEDGER" }}
          </button>
        </div>
      </div>
    </template>
  </div>
</template>
