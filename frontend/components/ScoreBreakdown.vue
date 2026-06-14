<template>
  <div class="space-y-3">
    <div v-for="(value, key) in breakdown" :key="key" class="flex items-center gap-3">
      <span class="w-36 text-sm capitalize text-slate-600">{{ formatKey(key) }}</span>
      <div class="h-2 flex-1 overflow-hidden rounded-full bg-slate-100">
        <div
          class="h-full rounded-full bg-trust-500 transition-all"
          :style="{ width: `${(value / 5) * 100}%` }"
        />
      </div>
      <span class="w-8 text-right text-sm font-medium text-slate-700">{{ value.toFixed(1) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ breakdown: Record<string, number> }>()

function formatKey(key: string) {
  return key.replace(/_/g, ' ')
}
</script>
