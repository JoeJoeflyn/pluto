<script setup lang="ts">
import { ref } from "vue";

const props = withDefaults(
  defineProps<{
    onFile: (file: File) => void;
    disabled?: boolean;
  }>(),
  { disabled: false },
);

const dragging = ref(false);
const inputRef = ref<HTMLInputElement | null>(null);

function handleFile(file: File | undefined | null) {
  if (!file) return;
  if (!/^image\//.test(file.type)) return;
  props.onFile(file);
}
</script>

<template>
  <div
    class="relative p-8 text-center text-ink-mid text-xs font-semibold tracking-[0.14em] bg-paper-dim border-dashed border-ink border cursor-pointer uppercase"
    :class="dragging ? 'bg-ink text-paper border-solid' : ''"
    @dragover.prevent="disabled || (dragging = true)"
    @dragleave="dragging = false"
    @drop.prevent="dragging = false; disabled || handleFile($event.dataTransfer?.files[0])"
    @click="disabled || inputRef?.click()"
    role="button"
    tabindex="0"
  >
    <input
      ref="inputRef"
      type="file"
      accept="image/*"
      :disabled="disabled"
      style="display: none"
      @change="handleFile(($event.target as HTMLInputElement).files?.[0])"
    />
    <div class="mb-2 text-ink-dim tracking-[0.3em]">
      ┌──── FEED MEDIA ────┐
    </div>
    <div class="text-xs font-semibold tracking-[0.14em] uppercase">
      {{ dragging ? "▼ RELEASE TO SUBMIT ▼" : "▲ INSERT RECEIPT ▲" }}
    </div>
    <div class="text-ink-dim" style="margin-top: 8px; font-size: 10px">
      OR CLICK TO BROWSE FILESYSTEM
    </div>
    <div
      class="mt-1.5 text-ink-dim font-normal tracking-[0.05em] normal-case"
      style="margin-top: 4px"
    >
      JPG · PNG · WEBP · HEIC
    </div>
    <div class="mb-2 text-ink-dim tracking-[0.3em]" style="margin-top: 12px">
      └─────────────────────┘
    </div>
  </div>
</template>
