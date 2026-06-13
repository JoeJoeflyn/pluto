<script setup lang="ts">
import { ref, computed } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { api } from "@/api/client";
import { formatMoney } from "@/utils/format";
import { MONTHS } from "@/constants/months";
import Select from "@/components/Select.vue";

const month = ref("");
const year = ref("");

const queryParams = computed(() => ({
  month: month.value ? Number(month.value) : undefined,
  year: year.value ? Number(year.value) : undefined,
}));

const { data: stats } = useQuery({
  queryKey: ["stats", queryParams],
  queryFn: () =>
    api.stats({
      ...queryParams.value,
      category: true,
    }),
});

const total = computed(() => stats.value?.total ?? 0);
const count = computed(() => stats.value?.count ?? 0);
const breakdown = computed(() => stats.value?.by_category ?? []);
const max = computed(() => Math.max(...breakdown.value.map((b) => b.total), 1));
const avgAll = computed(() => (count.value > 0 ? total.value / count.value : 0));

const { data: expenses } = useQuery({
  queryKey: ["stats-expenses", queryParams],
  queryFn: () => api.expenses({
    ...queryParams.value,
    limit: 500,
  }),
});

const nonZero = computed(() => (expenses.value ?? []).filter((e) => e.amount > 0));
const zeroCount = computed(() => (expenses.value ?? []).length - nonZero.value.length);
const avgNZ = computed(() => {
  const n = nonZero.value.length;
  return n > 0 ? nonZero.value.reduce((s, e) => s + e.amount, 0) / n : 0;
});
</script>

<template>
  <div>
    <div class="my-3">
      <div class="mt-1 text-ink-mid tracking-[0.2em] uppercase">═══ SECTION C · THE STATISTICAL ABSTRACT ═══</div>
      <h2 style="font-size:18px;margin:4px 0 0;letter-spacing:0.08em">► SPENDING, BY PERIOD &amp; CATEGORY</h2>
      <div class="text-ink-dim" style="font-size:11px;margin-top:4px">AN AGGREGATE VIEW OF YOUR FILED RECEIPTS</div>
    </div>

    <hr class="dotted" />

    <div class="my-3">
      <h2 class="mb-2 text-start font-bold tracking-[0.2em] uppercase">═══ FILTERS ═══</h2>
      <div class="grid grid-cols-2 gap-3 max-tablet:grid-cols-1">
        <div>
          <label>MONTH</label>
          <Select :value="month" @change="(v: string) => month = v" placeholder="— ALL MONTHS —" :allow-empty="true" empty-label="— ALL MONTHS —" :options="MONTHS.map((m, i) => ({ value: String(i + 1), label: m }))" />
        </div>
        <div>
          <label>YEAR</label>
          <input type="number" :value="year" @input="year = ($event.target as HTMLInputElement).value" placeholder="e.g. 2026" min="2000" max="2100" />
        </div>
      </div>
      <div v-if="month || year" style="margin-top:14px">
        <button class="ghost" @click="month = ''; year = ''">✕ CLEAR FILTERS</button>
      </div>
    </div>

    <hr class="dotted" />

    <div class="my-3">
      <h2 class="mb-2 text-start font-bold tracking-[0.2em] uppercase">═══ HEADLINE FIGURES ═══</h2>
      <div class="flex items-baseline justify-between py-1.5 text-sm font-bold border-dashed border-ink border gap-3">
        <span class="text-xs font-semibold tracking-[0.14em] uppercase">▌ TOTAL EXPENDED</span>
        <span class="text-start font-bold tabular-nums whitespace-nowrap" style="font-size:16px">{{ formatMoney(total) }}</span>
      </div>
      <div class="flex items-baseline justify-between py-0.75 gap-3">
        <span class="text-xs font-semibold tracking-[0.14em] uppercase">▌ RECEIPTS FILED</span>
        <span class="text-right tabular-nums whitespace-nowrap">{{ count }}</span>
      </div>
      <div class="flex items-baseline justify-between py-0.75 gap-3">
        <span class="text-xs font-semibold tracking-[0.14em] uppercase">▌ MEAN (ALL RECEIPTS)</span>
        <span class="text-right tabular-nums whitespace-nowrap">{{ formatMoney(avgAll) }}</span>
      </div>
      <div class="flex items-baseline justify-between py-0.75 gap-3">
        <span class="text-xs font-semibold tracking-[0.14em] uppercase">▌ MEAN (NON-ZERO)</span>
        <span class="text-right tabular-nums whitespace-nowrap">{{ formatMoney(avgNZ) }}</span>
      </div>
      <div v-if="zeroCount > 0" class="flex items-baseline justify-between py-0.75 gap-3">
        <span class="text-xs font-semibold tracking-[0.14em] uppercase">▌ FREE ENTRIES</span>
        <span class="text-right tabular-nums whitespace-nowrap">{{ zeroCount }}</span>
      </div>
    </div>

    <hr class="dotted" />

    <div class="my-3">
      <h2 class="mb-2 text-start font-bold tracking-[0.2em] uppercase">═══ BY CATEGORY ═══</h2>

      <div v-if="breakdown.length === 0" class="p-2 my-2 text-center text-xs tracking-[0.14em] border-dashed border-ink border uppercase">
        — NO DATA FOR THIS PERIOD —<br />
        <span class="text-ink-dim" style="font-size:10px">ADJUST THE FILTERS OR FILE A FEW RECEIPTS</span>
      </div>

      <table v-else>
        <thead>
          <tr>
            <th>CATEGORY</th>
            <th style="width:40%">DISTRIBUTION</th>
            <th class="num">TOTAL</th>
            <th class="num" style="width:90px">COUNT</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in breakdown" :key="b.category">
            <td class="font-bold">{{ b.category.toUpperCase() }}</td>
            <td>
              <div class="flex items-center h-2 bg-paper border-ink border">
                <div class="h-full bg-ink" :style="{ width: `${(b.total / max) * 100}%` }"></div>
              </div>
            </td>
            <td class="font-bold num">{{ formatMoney(b.total) }}</td>
            <td class="text-ink-dim num">{{ b.count }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
