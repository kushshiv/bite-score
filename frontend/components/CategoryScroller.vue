<template>
  <div class="scrollbar-hide -mx-4 flex gap-3 overflow-x-auto px-4 pb-1 sm:mx-0 sm:px-0">
    <NuxtLink
      v-for="cat in categories"
      :key="cat.slug"
      :to="{ path: '/search', query: { category: cat.slug } }"
      class="flex shrink-0 flex-col items-center gap-1.5 rounded-2xl border border-slate-200 bg-white px-4 py-3 transition hover:border-trust-500 hover:shadow-sm"
      :class="activeCategory === cat.slug ? 'border-trust-500 bg-trust-50' : ''"
    >
      <span class="text-2xl">{{ cat.emoji }}</span>
      <span class="text-xs font-medium text-slate-700">{{ cat.label }}</span>
    </NuxtLink>
  </div>
</template>

<script setup lang="ts">
import { CATEGORIES } from '~/composables/useCategoryMeta'

defineProps<{ activeCategory?: string }>()

const categories = CATEGORIES
</script>
