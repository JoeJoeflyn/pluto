<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from "vue";
import { Check, ChevronDown } from "lucide-vue-next";
import type { Component } from "vue";

export type SelectOption = {
  value: string;
  label: string;
  icon?: Component;
};

const props = withDefaults(
  defineProps<{
    value: string;
    options: SelectOption[];
    id?: string;
    placeholder?: string;
    allowEmpty?: boolean;
    emptyLabel?: string;
  }>(),
  { placeholder: "— SELECT —", allowEmpty: false, emptyLabel: "— ALL —" },
);

const emit = defineEmits<{ change: [value: string] }>();

const open = ref(false);
const wrapRef = ref<HTMLDivElement | null>(null);

function onClickOutside(e: MouseEvent) {
  if (wrapRef.value && !wrapRef.value.contains(e.target as Node)) open.value = false;
}
function onKeydown(e: KeyboardEvent) {
  if (e.key === "Escape") open.value = false;
}

onMounted(() => {
  document.addEventListener("mousedown", onClickOutside);
  document.addEventListener("keydown", onKeydown);
});
onUnmounted(() => {
  document.removeEventListener("mousedown", onClickOutside);
  document.removeEventListener("keydown", onKeydown);
});

const allOpts = computed<SelectOption[]>(() =>
  props.allowEmpty
    ? [{ value: "", label: props.emptyLabel }, ...props.options]
    : props.options,
);

const current = computed(() => allOpts.value.find((o) => o.value === props.value));

const triggerLabel = computed(() =>
  current.value ? current.value.label.toUpperCase() : props.placeholder.toUpperCase(),
);
</script>

<template>
  <div class="relative w-full" ref="wrapRef">
    <button
      type="button"
      :id="id"
      class="flex items-center p-[8px_10px] w-full text-left font-mono font-semibold tracking-[0.08em] border-ink border cursor-pointer gap-2 outline-hidden uppercase hover:bg-paper-dim"
      :class="open ? 'bg-ink text-paper' : ''"
      aria-haspopup="listbox"
      :aria-expanded="open"
      @click="open = !open"
    >
      <span
        class="inline-flex items-center justify-center h-3.5 w-3.5 shrink-0"
        aria-hidden="true"
      >
        <component :is="current?.icon" v-if="current?.icon" :size="14" :stroke-width="1.5" />
      </span>
      <span class="flex-1 min-w-0 overflow-hidden whitespace-nowrap">
        {{ triggerLabel }}
      </span>
      <ChevronDown
        :size="14"
        :stroke-width="1.5"
        class="duration-100 shrink-0 transition-transform"
        :class="open ? 'rotate-180' : ''"
        aria-hidden="true"
      />
    </button>
    <ul
      v-if="open"
      class="absolute left-0 right-0 top-[calc(100%+4px)] z-[100] py-1 m-0 max-h-50 max-h-70 min-w-55 bg-paper border-ink shadow-[2px_2px_0_ink] border list-none overflow-y-auto"
    >
      <li
        v-for="o in allOpts"
        :key="o.value || '__empty__'"
        class="flex items-center p-[8px_10px] text-xs tracking-[0.06em] cursor-pointer gap-2 select-none uppercase hover:text-paper hover:bg-ink"
        :class="o.value === value ? 'bg-ink text-paper' : ''"
        role="option"
        :aria-selected="o.value === value"
        @click="emit('change', o.value); open = false"
      >
        <span
          class="inline-flex items-center justify-center h-3.5 w-3.5 shrink-0"
          aria-hidden="true"
        >
          <component :is="o.icon" v-if="o.icon" :size="14" :stroke-width="1.5" />
        </span>
        <span class="flex-1 min-w-[2rem] overflow-hidden whitespace-nowrap">
          {{ o.label.toUpperCase() }}
        </span>
        <Check v-if="o.value === value" :size="12" :stroke-width="2" aria-hidden="true" />
      </li>
    </ul>
  </div>
</template>
