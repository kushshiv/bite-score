<template>
  <div class="scrollbar-hide -mx-1 flex gap-3 overflow-x-auto px-1 pb-1">
    <button
      v-for="cat in cuisines"
      :key="cat.slug"
      class="flex shrink-0 flex-col items-center gap-1.5"
      @click="emit('select', cat.slug)"
    >
      <span
        class="flex h-14 w-14 items-center justify-center rounded-full border-2 text-xl transition"
        :class="activeCategory === cat.slug ? 'border-trust-500 bg-trust-600/10' : 'border-surface-border bg-surface-raised hover:border-gray-500'"
      >
        {{ cat.emoji }}
      </span>
      <span class="max-w-[4.5rem] truncate text-center text-xs text-gray-400">{{ cat.label }}</span>
    </button>
    <button class="flex shrink-0 flex-col items-center gap-1.5" @click="emit('select', '')">
      <span class="flex h-14 w-14 items-center justify-center rounded-full border border-surface-border bg-surface-raised text-xs font-medium text-gray-400 hover:border-gray-500">
        All
      </span>
      <span class="text-xs text-gray-500">Show all</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { CATEGORIES } from '~/composables/useCategoryMeta'

defineProps<{ activeCategory?: string }>()
const emit = defineEmits<{ select: [slug: string] }>()

const cuisines = CATEGORIES.slice(0, 8)
</script>
