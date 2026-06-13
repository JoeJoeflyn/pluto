<script setup lang="ts">
import { computed } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { api } from "@/api/client";
import { formatMoney, pad } from "@/utils/format";

const { data: expenses } = useQuery({
  queryKey: ["expenses", { limit: 5 }],
  queryFn: () => api.expenses({ limit: 5 }),
});

const { data: stats } = useQuery({
  queryKey: ["stats", { category: true }],
  queryFn: () => api.stats({ category: true }),
});

const { data: merchants } = useQuery({
  queryKey: ["merchants"],
  queryFn: api.merchants,
});

const total = computed(() => stats.value?.total ?? 0);
const count = computed(() => stats.value?.count ?? 0);
const recent = computed(() => expenses.value ?? []);
const top = computed(() => merchants.value?.[0]);
const breakdown = computed(() => stats.value?.by_category ?? []);
const max = computed(() => Math.max(...breakdown.value.map((b) => b.total), 1));
</script>

<template>
  <div>
    <div class="my-3">
      <div class="mt-1 text-ink-mid tracking-[0.2em] uppercase">═══ FRONT PAGE · THE STATE OF THE LEDGER ═══</div>
      <h2 style="font-size:18px;margin:4px 0 0;letter-spacing:0.08em">► YOUR EXPENDITURES, SUMMARISED</h2>
      <div class="text-ink-dim" style="font-size:11px;margin-top:4px">A FAITHFUL ACCOUNTING OF EVERY RECEIPT FILED THIS PERIOD</div>
    </div>

    <hr class="dotted" />

    <div class="my-3">
      <h2 class="mb-2 text-start font-bold tracking-[0.2em] uppercase">═══ HEADLINE FIGURES ═══</h2>
      <div class="flex items-baseline justify-between py-1.5 text-sm font-bold border-dashed border-ink border gap-3">
        <span class="text-xs font-semibold tracking-[0.14em] uppercase">▌ GRAND TOTAL SPENT</span>
        <span class="text-start font-bold tabular-nums whitespace-nowrap" style="font-size:16px">{{ formatMoney(total) }}</span>
      </div>
      <div class="flex items-baseline justify-between py-0.75 gap-3">
        <span class="text-xs font-semibold tracking-[0.14em] uppercase">▌ RECEIPTS ON FILE</span>
        <span class="text-right tabular-nums whitespace-nowrap">{{ count }}</span>
      </div>
      <div class="flex items-baseline justify-between py-0.75 gap-3">
        <span class="text-xs font-semibold tracking-[0.14em] uppercase">▌ DISTINCT MERCHANTS</span>
        <span class="text-right tabular-nums whitespace-nowrap">{{ merchants?.length ?? 0 }}</span>
      </div>
      <div class="flex items-baseline justify-between py-0.75 gap-3">
        <span class="text-xs font-semibold tracking-[0.14em] uppercase">▌ MOST-FREQUENTED</span>
        <span class="text-right tabular-nums whitespace-nowrap">{{ top ? `${top.name.toUpperCase()} (${top.visit_count}×)` : "—" }}</span>
      </div>
    </div>

    <hr class="dotted" />

    <div class="my-3">
      <h2 class="mb-2 text-start font-bold tracking-[0.2em] uppercase">═══ RECENT FILINGS ═══</h2>

      <div v-if="recent.length === 0" class="p-2 my-2 text-ink-mid tracking-[0.14em] border-dashed border-ink border uppercase">
        <div class="text-center">— NO RECEIPTS ON FILE —</div>
        <div class="text-ink-dim" style="font-size:10px;margin-top:4px">THE LEDGER AWAITS ITS FIRST ENTRY</div>
        <div class="text-center" style="margin-top:10px">
          <router-link to="/scan"><button>▸ FILE THE FIRST RECEIPT</button></router-link>
        </div>
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
          <tr v-for="e in recent" :key="e.id" style="cursor:pointer" @click="$router.push(`/expenses/${e.id}`)">
            <td class="text-ink-dim">#{{ pad(e.id) }}</td>
            <td class="font-bold">
              <router-link :to="`/expenses/${e.id}`" class="border-b-0">{{ e.merchant.toUpperCase() }}</router-link>
              <div class="text-ink-dim" style="font-size:9px;margin-top:2px">{{ e.category.toUpperCase() }}{{ e.line_items?.length ? ` · ${e.line_items.length} ITEMS` : '' }}</div>
            </td>
            <td class="text-ink-dim" style="font-size:11px">{{ new Date(e.date).toLocaleDateString("en-US", { year: "numeric", month: "2-digit", day: "2-digit" }) }}</td>
            <td class="text-start font-bold num">{{ formatMoney(e.amount, e.currency) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <template v-if="breakdown.length > 0">
      <hr class="dotted" />
      <div class="my-3">
        <h2 class="mb-2 text-start font-bold tracking-[0.2em] uppercase">═══ BY CATEGORY ═══</h2>
        <div v-for="b in breakdown" :key="b.category" class="flex items-baseline justify-between py-0.75 gap-3" style="align-items:center">
          <span class="text-xs font-semibold tracking-[0.14em] uppercase" style="min-width:140px">{{ b.category.toUpperCase() }}</span>
          <span style="flex:1">
            <div class="flex items-center h-2 bg-paper border-ink border">
              <div class="h-full bg-ink" :style="{ width: `${(b.total / max) * 100}%` }"></div>
            </div>
          </span>
          <span class="text-right tabular-nums whitespace-nowrap" style="min-width:90px">{{ formatMoney(b.total) }}</span>
        </div>
      </div>
    </template>

    <hr class="dotted" />
    <div class="text-center">
      <router-link to="/scan"><button class="stamp">▸ FILE A RECEIPT</button></router-link>
    </div>
  </div>
</template>
