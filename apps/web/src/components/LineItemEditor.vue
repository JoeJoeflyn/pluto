<script setup lang="ts">
import { computed } from "vue";

type Item = {
  name: string;
  price: number;
  quantity: number;
  category?: string | null;
};

const props = defineProps<{ items: Item[] }>();
const emit = defineEmits<{ change: [items: Item[]] }>();

function update(idx: number, patch: Partial<Item>) {
  emit("change", props.items.map((it, i) => (i === idx ? { ...it, ...patch } : it)));
}
function add() {
  emit("change", [...props.items, { name: "", price: 0, quantity: 1, category: null }]);
}
function remove(idx: number) {
  emit("change", props.items.filter((_, i) => i !== idx));
}

const total = computed(() =>
  props.items.reduce((s, it) => s + (Number(it.price) || 0) * (Number(it.quantity) || 1), 0),
);
</script>

<template>
  <div>
    <table>
      <thead>
        <tr>
          <th>ITEM</th>
          <th class="num" style="width: 70px">QTY</th>
          <th class="num" style="width: 110px">PRICE</th>
          <th style="width: 140px">CATEGORY</th>
          <th style="width: 50px"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="items.length === 0">
          <td colSpan="5" class="text-ink-dim" style="padding: 14px">
            — NO LINE ITEMS DECLARED —
          </td>
        </tr>
        <tr v-for="(it, idx) in items" :key="idx">
          <td>
            <input
              :value="it.name"
              placeholder="ITEM NAME"
              @input="update(idx, { name: ($event.target as HTMLInputElement).value })"
            />
          </td>
          <td>
            <input
              type="number"
              min="1"
              :value="it.quantity"
              class="text-right"
              @input="update(idx, { quantity: Number(($event.target as HTMLInputElement).value) || 1 })"
            />
          </td>
          <td>
            <input
              type="number"
              step="0.01"
              :value="it.price"
              class="text-right"
              @input="update(idx, { price: Number(($event.target as HTMLInputElement).value) || 0 })"
            />
          </td>
          <td>
            <input
              :value="it.category ?? ''"
              placeholder="OPT"
              @input="update(idx, { category: ($event.target as HTMLInputElement).value || null })"
            />
          </td>
          <td style="text-align: center">
            <button type="button" class="ghost" @click="remove(idx)" aria-label="REMOVE" style="padding: 2px 6px">
              ✕
            </button>
          </td>
        </tr>
      </tbody>
      <tfoot v-if="items.length > 0">
        <tr>
          <td colSpan="3" class="text-xs font-semibold tracking-[0.14em] uppercase">
            ▌ ITEMS SUBTOTAL
          </td>
          <td class="text-start font-bold num">{{ total.toFixed(2) }}</td>
          <td></td>
        </tr>
      </tfoot>
    </table>
    <div style="margin-top: 10px">
      <button type="button" class="ghost" @click="add">+ ADD LINE ITEM</button>
    </div>
  </div>
</template>
