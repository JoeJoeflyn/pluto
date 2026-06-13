<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useMutation, useQueryClient } from "@tanstack/vue-query";
import { api } from "@/api/client";
import ReceiptUploader from "@/components/ReceiptUploader.vue";
import ExpenseForm from "@/components/ExpenseForm.vue";
import type { ExpenseFormValues } from "@/constants/expense-form";

const router = useRouter();
const queryClient = useQueryClient();

const file = ref<File | null>(null);
const previewUrl = ref<string | null>(null);
const extracted = ref<{
  image_path: string;
  values: Partial<ExpenseFormValues>;
  needs_review: string[];
  errors: string[];
} | null>(null);

const scan = useMutation({
  mutationFn: (f: File) => api.scan(f),
});

const create = useMutation({
  mutationFn: api.createExpense,
  onSuccess: (saved) => {
    queryClient.invalidateQueries({ queryKey: ["expenses"] });
    queryClient.invalidateQueries({ queryKey: ["merchants"] });
    queryClient.invalidateQueries({ queryKey: ["stats"] });
    router.push(`/expenses/${saved.id}`);
  },
});

async function onFile(f: File) {
  file.value = f;
  previewUrl.value = URL.createObjectURL(f);
  extracted.value = null;
  try {
    const r = await scan.mutateAsync(f);
    extracted.value = {
      image_path: r.image_path,
      values: {
        date: r.extracted.date ?? new Date().toISOString().slice(0, 10),
        amount: r.extracted.amount ?? 0,
        currency: r.extracted.currency ?? "USD",
        category: r.extracted.category ?? "Other",
        merchant: r.extracted.merchant ?? "",
        notes: "",
        time: null,
        subtotal: null,
        tax: null,
        tip: null,
        address: r.extracted.address ?? null,
        phone: r.extracted.phone ?? null,
        payment_method: null,
        card_type: null,
        card_last4: null,
        cashier: null,
        transaction_id: null,
        line_items: (r.extracted.items ?? []).map((it) => ({ name: it.name, price: it.price, quantity: 1, category: null })),
      },
      needs_review: r.needs_review,
      errors: r.errors,
    };
  } catch (e) {
    extracted.value = {
      image_path: "",
      values: {
        date: new Date().toISOString().slice(0, 10),
        amount: 0,
        currency: "USD",
        category: "Other",
        merchant: "",
        notes: "",
        time: null,
        subtotal: null,
        tax: null,
        tip: null,
        address: null,
        phone: null,
        payment_method: null,
        card_type: null,
        card_last4: null,
        cashier: null,
        transaction_id: null,
        line_items: [],
      },
      needs_review: [],
      errors: [e instanceof Error ? e.message : "SCAN FAILED"],
    };
  }
}

async function onSubmit(v: ExpenseFormValues & { image_path: string }) {
  await create.mutateAsync({
    date: v.date,
    amount: v.amount,
    currency: v.currency,
    category: v.category,
    merchant: v.merchant,
    notes: v.notes,
    image_path: v.image_path,
    time: v.time,
    subtotal: v.subtotal,
    tax: v.tax,
    tip: v.tip,
    address: v.address,
    phone: v.phone,
    payment_method: v.payment_method,
    card_type: v.card_type,
    card_last4: v.card_last4,
    cashier: v.cashier,
    transaction_id: v.transaction_id,
    line_items: v.line_items.filter((it) => it.name && it.price >= 0),
  });
}
</script>

<template>
  <div>
    <div class="my-3">
      <div class="mt-1 text-ink-mid tracking-[0.2em] uppercase">═══ SECTION A · THE FILING DESK ═══</div>
      <h2 style="font-size:18px;margin:4px 0 0;letter-spacing:0.08em">► SUBMIT A RECEIPT</h2>
      <div class="text-ink-dim" style="font-size:11px;margin-top:4px">HAND A PHOTOGRAPH TO THE DESK CLERK · LOCAL OLLAMA WILL READ THE PARTICULARS</div>
    </div>

    <hr class="dotted" />

    <div v-if="!file" class="my-3">
      <h2 class="mb-2 text-start font-bold tracking-[0.2em] uppercase">═══ FEED MEDIA ═══</h2>
      <ReceiptUploader :on-file="onFile" :disabled="scan.isPending.value" />
    </div>

    <template v-if="file && !extracted">
      <div class="my-3">
        <h2 class="mb-2 text-start font-bold tracking-[0.2em] uppercase">═══ PROCESSING ═══</h2>
        <div class="p-2 my-2 text-center text-xs tracking-[0.14em] border-dashed border-ink border uppercase">
          <span class="inline-block h-2.5 w-2.5 border-2 border-ink-dim border-t-stamp rounded-full align-middle animate-spin" /> THE CLERK IS READING YOUR RECEIPT…
        </div>
        <div v-if="scan.error.value" class="p-2 my-2 text-stamp text-xs font-semibold tracking-[0.14em] border-stamp border uppercase">
          ⚠ {{ scan.error.value.message.toUpperCase() }}
        </div>
      </div>
    </template>

    <template v-if="file && extracted">
      <div v-if="extracted.errors.length > 0" class="p-2 my-2 text-stamp text-xs font-semibold tracking-[0.14em] border-stamp border uppercase">
        ⚠ THE CLERK COULD NOT FULLY READ THIS RECEIPT: <strong>{{ extracted.errors.join("; ").toUpperCase() }}</strong>
      </div>
      <div v-if="extracted.needs_review.length > 0" class="p-2 my-2 text-ink-mid text-xs tracking-[0.14em] border-dashed border-ink border uppercase">
        ✦ PLEASE CONFIRM: <strong>{{ extracted.needs_review.join(", ").toUpperCase() }}</strong>
      </div>

      <div class="my-3">
        <h2 class="mb-2 text-start font-bold tracking-[0.2em] uppercase">═══ PREVIEW ═══</h2>
        <div v-if="previewUrl" style="text-align:center">
          <img :src="previewUrl" alt="Receipt preview" class="block max-w-full bg-white border-ink -z-auto border" />
        </div>
      </div>

      <hr class="dotted" />

      <ExpenseForm
        :initial="extracted.values"
        :image-path="extracted.image_path"
        submit-label="File with the Ledger"
        :on-submit="onSubmit"
        :busy="create.isPending.value"
      />

      <hr class="dotted" />

      <div class="text-center">
        <button class="ghost" @click="file = null; previewUrl = null; extracted = null">✕ DISCARD &amp; START OVER</button>
      </div>
    </template>
  </div>
</template>
