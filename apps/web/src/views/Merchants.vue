<script setup lang="ts">
import { computed } from "vue";
import { useQuery } from "@tanstack/vue-query";
import { api } from "@/api/client";

const { data: merchants, isLoading } = useQuery({
  queryKey: ["merchants"],
  queryFn: api.merchants,
});

const data = computed(() => merchants.value ?? []);
const max = computed(() => Math.max(...data.value.map((m) => m.visit_count), 1));
</script>

<template>
  <div>
    <div class="my-3">
      <div class="mt-1 text-ink-mid tracking-[0.2em] uppercase">═══ SECTION D · THE MERCHANT INDEX ═══</div>
      <h2 style="font-size:18px;margin:4px 0 0;letter-spacing:0.08em">► STORES, RANKED BY FREQUENCY</h2>
      <div class="text-ink-dim" style="font-size:11px;margin-top:4px">EVERY DISTINCT MERCHANT YOU HAVE TRANSACTED WITH</div>
    </div>

    <hr class="dotted" />

    <div v-if="isLoading" class="p-2 my-2 text-center text-xs tracking-[0.14em] border-dashed border-ink border uppercase">
      <span class="inline-block h-2.5 w-2.5 border-2 border-ink-dim border-t-stamp rounded-full align-middle animate-spin" /> CONSULTING THE INDEX…
    </div>

    <div v-else-if="data.length === 0" class="p-2 my-2 text-center text-xs tracking-[0.14em] border-dashed border-ink border uppercase">
      — THE INDEX IS EMPTY —<br />
      <span class="text-ink-dim" style="font-size:10px">FILE A FEW RECEIPTS TO BEGIN BUILDING THE REGISTER</span>
    </div>

    <div v-else class="my-3">
      <h2 class="mb-2 text-start font-bold tracking-[0.2em] uppercase">═══ THE INDEX ═══</h2>
      <table>
        <thead>
          <tr>
            <th style="width:40px">№</th>
            <th>MERCHANT</th>
            <th>FIRST SEEN</th>
            <th>LAST SEEN</th>
            <th class="num" style="width:80px">VISITS</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(m, i) in data" :key="m.id">
            <td class="text-ink-dim">#{{ String(i + 1).padStart(3, "0") }}</td>
            <td>
              <div class="font-bold">{{ m.name.toUpperCase() }}</div>
              <div v-if="m.address" class="text-ink-dim" style="font-size:10px;margin-top:2px">{{ m.address }}</div>
              <div v-if="m.phone" class="text-ink-dim" style="font-size:10px">{{ m.phone }}</div>
            </td>
            <td class="text-ink-dim" style="font-size:11px">{{ m.first_seen }}</td>
            <td class="text-ink-dim" style="font-size:11px">{{ m.last_seen }}</td>
            <td class="num">
              <div class="flex items-center h-2 bg-paper border-ink border" style="margin-bottom:4px">
                <div class="h-full bg-ink" :style="{ width: `${(m.visit_count / max) * 100}%` }"></div>
              </div>
              <span class="font-bold">{{ m.visit_count }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
