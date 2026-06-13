<script setup lang="ts">
import { computed, type Component } from "vue";
import type { Category } from "@/api/client";
import Select, { type SelectOption } from "./Select.vue";
import { iconForCategory } from "@/constants/categories";

const props = withDefaults(
  defineProps<{
    value: string;
    categories: Category[];
    id?: string;
    placeholder?: string;
    allowEmpty?: boolean;
  }>(),
  { placeholder: "— SELECT —", allowEmpty: false },
);

const emit = defineEmits<{ change: [name: string] }>();

const options = computed<SelectOption[]>(() =>
  props.categories.map((c) => ({
    value: c.name,
    label: c.name,
    icon: iconForCategory(c.name) as Component,
  })),
);
</script>

<template>
  <Select
    :value="value"
    @change="(v: string) => emit('change', v)"
    :options="options"
    :id="id"
    :placeholder="placeholder"
    :allow-empty="allowEmpty"
    empty-label="— ALL CATEGORIES —"
  />
</template>
