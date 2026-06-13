<script setup lang="ts">
import { useRoute } from "vue-router";
import { pad } from "@/utils/format";
import { NAV_ITEMS } from "@/constants/nav";

function timestamp(): string {
  const d = new Date();
  return `${d.getFullYear()}.${pad(d.getMonth() + 1)}.${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

const route = useRoute();

function isActive(to: string): boolean {
  if (to === "/") return route.path === "/";
  return route.path.startsWith(to);
}
</script>

<template>
  <div class="relative p-[18px_22px] mb-6 bg-paper border-ink border receipt">
    <div class="pb-3 mb-3 text-center border-dashed border-ink border">
      <div class="mt-1 text-ink-mid tracking-[0.2em] uppercase">
        ═══ THERMAL RECEIPT PRINTER ═══
      </div>
      <router-link to="/" class="block border-b-0">
        <div class="text-xl font-bold tracking-[0.18em] uppercase">
          █▓▒░ PLUTO ░▒▓█
        </div>
      </router-link>
      <div class="mt-1 text-ink-mid tracking-[0.2em] uppercase">
        RECEIPT MANAGEMENT TERMINAL · v1.0
      </div>
    </div>

    <div
      class="flex items-center justify-between py-1 mb-4 text-ink-mid font-semibold tracking-[0.18em] border-ink border uppercase"
    >
      <span>
        <span
          class="inline-block mr-1.5 h-1.75 w-1.75 bg-stamp rounded-full align-middle"
        />
        SYS:READY
      </span>
      <span>CH:01</span>
      <span>{{ timestamp() }}</span>
      <span>USD</span>
    </div>

    <div class="flex mb-0 border-ink border" role="navigation">
      <router-link
        v-for="n in NAV_ITEMS"
        :key="n.to"
        :to="n.to"
        :aria-current="isActive(n.to) ? 'page' : undefined"
        class="flex-1 px-1 py-2 text-xs font-semibold tracking-[0.14em] border-0 border-ink border-r uppercase hover:text-paper max-tablet:tracking-[0.08em] hover:bg-ink last:border-r-0"
        :class="isActive(n.to) ? 'bg-ink text-paper' : ''"
      >
        {{ n.label }}
      </router-link>
    </div>

    <div class="my-3" style="margin-top: 16px">
      <router-view />
    </div>

    <hr class="dotted" />
    <div
      class="mt-1 text-ink-mid tracking-[0.2em] uppercase"
      style="margin-top: 8px"
    >
      — END OF RECEIPT —<br />
      <span class="text-ink-dim"
        >THANK YOU · KEEP THIS STUB FOR YOUR RECORDS</span
      >
    </div>
  </div>
</template>
