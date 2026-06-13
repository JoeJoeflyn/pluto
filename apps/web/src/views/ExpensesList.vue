<script setup lang="ts">
import { ref, computed } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { api } from "@/api/client";
import CategorySelect from "@/components/CategorySelect.vue";
import Select from "@/components/Select.vue";
import { formatMoney, pad } from "@/utils/format";
import { MONTHS } from "@/constants/months";

const category = ref("");
const month = ref("");
const year = ref("");

const queryParams = computed(() => ({
  category: category.value || undefined,
  month: month.value ? Number(month.value) : undefined,
  year: year.value ? Number(year.value) : undefined,
}));

const { data: cats } = useQuery({ queryKey: ["categories"], queryFn: api.categories });

const { data: expenses, isLoading } = useQuery({
  queryKey: ["expenses", queryParams],
  queryFn: () => api.expenses(queryParams.value),
});

const total = computed(() => (expenses.value ?? []).reduce((s, e) => s + (e.amount || 0), 0));

const years = computed(() => {
  const ys = new Set<number>();
  (expenses.value ?? []).forEach((e) => {
    const d = new Date(e.date);
    if (!Number.isNaN(d.getTime())) ys.add(d.getFullYear());
  });
  return Array.from(ys).sort((a, b) => b - a);
});

const list = computed(() => expenses.value ?? []);
</script>

<template>
  <div>
    <div class="my-3">
      <div class="mt-1 text-ink-mid tracking-[0.2em] uppercase">═══ SECTION B · THE EXPENDITURE REGISTER ═══</div>
      <h2 style="font-size:18px;margin:4px 0 0;letter-spacing:0.08em">► ALL RECEIPTS, FILED &amp; INDEXED</h2>
      <div class="text-ink-dim" style="font-size:11px;margin-top:4px">
        {{ list.length }} SHOWN · AGGREGATE: <span class="text-start font-bold">{{ formatMoney(total) }}</span>
      </div>
    </div>

    <hr class="dotted" />

    <div class="my-3">
      <h2 class="mb-2 text-start font-bold tracking-[0.2em] uppercase">═══ FILTERS ═══</h2>
      <div class="grid grid-cols-2 gap-3 max-tablet:grid-cols-1">
        <div>
          <label>CATEGORY</label>
          <CategorySelect :value="category" @change="(v: string) => category = v" :categories="cats ?? []" placeholder="— ALL CATEGORIES —" :allow-empty="true" />
        </div>
        <div>
          <label>MONTH</label>
          <Select :value="month" @change="(v: string) => month = v" placeholder="— ALL MONTHS —" :allow-empty="true" empty-label="— ALL MONTHS —" :options="MONTHS.map((m, i) => ({ value: String(i + 1), label: m }))" />
        </div>
      </div>
      <div class="grid grid-cols-2 gap-3 max-tablet:grid-cols-1" style="margin-top:14px">
        <div>
          <label>YEAR</label>
          <Select :value="year" @change="(v: string) => year = v" placeholder="— ALL YEARS —" :allow-empty="true" empty-label="— ALL YEARS —" :options="years.map((y) => ({ value: String(y), label: String(y) }))" />
        </div>
        <div style="display:flex;align-items:flex-end">
          <button v-if="category || month || year" class="ghost" @click="category = ''; month = ''; year = ''">✕ CLEAR ALL FILTERS</button>
        </div>
      </div>
    </div>

    <hr class="dotted" />

    <div class="my-3">
      <h2 class="mb-2 text-start font-bold tracking-[0.2em] uppercase">═══ THE REGISTER ═══</h2>

      <div v-if="isLoading" class="p-2 my-2 text-center text-xs tracking-[0.14em] border-dashed border-ink border uppercase">
        <span class="inline-block h-2.5 w-2.5 border-2 border-ink-dim border-t-stamp rounded-full align-middle animate-spin" /> FETCHING THE LEDGER…
      </div>

      <div v-else-if="list.length === 0" class="p-2 my-2 text-center text-xs tracking-[0.14em] border-dashed border-ink border uppercase">
        — NO MATCHING RECEIPTS —<br />
        <span class="text-ink-dim" style="font-size:10px">LOOSEN FILTERS OR FILE A NEW EXPENSE</span>
      </div>

      <table v-else>
        <thead>
          <tr>
            <th style="width:60px">№</th>
            <th>MERCHANT</th>
            <th>DATE</th>
            <th class="num">AMOUNT</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="e in list" :key="e.id" style="cursor:pointer" @click="$router.push(`/expenses/${e.id}`)">
            <td class="text-ink-dim">#{{ pad(e.id) }}</td>
            <td class="font-bold">
              <router-link :to="`/expenses/${e.id}`" class="border-b-0">{{ e.merchant.toUpperCase() }}</router-link>
              <div class="text-ink-dim" style="font-size:9px;margin-top:2px">{{ e.category.toUpperCase() }}{{ e.line_items?.length ? ` · ${e.line_items.length} ITEMS` : '' }}</div>
            </td>
            <td class="text-ink-dim" style="font-size:11px">{{ new Date(e.date).toLocaleDateString("en-US", { year: "numeric", month: "2-digit", day: "2-digit" }) }}</td>
            <td class="text-start font-bold num">{{ formatMoney(e.amount, e.currency) }}</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td colSpan="3" class="text-xs font-semibold tracking-[0.14em] uppercase">▌ REGISTER TOTAL</td>
            <td class="text-start font-bold num">{{ formatMoney(total) }}</td>
          </tr>
        </tfoot>
      </table>
    </div>
  </div>
</template>
