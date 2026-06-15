<template>
  <div class="border-b border-surface-border bg-surface">
    <div class="scrollbar-hide mx-auto flex max-w-[1400px] gap-1 overflow-x-auto px-4 py-3 lg:px-6">
      <button
        v-for="cat in topCategories"
        :key="cat.slug"
        class="flex shrink-0 flex-col items-center gap-1.5 rounded-xl px-3 py-2 transition"
        :class="activeCategory === cat.slug ? 'bg-surface-raised' : 'hover:bg-surface-hover'"
        @click="emit('select', activeCategory === cat.slug ? '' : cat.slug)"
      >
        <span class="flex h-12 w-12 items-center justify-center rounded-2xl text-2xl" :class="cat.bg">{{ cat.emoji }}</span>
        <span class="text-xs font-medium text-gray-300">{{ cat.label }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ activeCategory?: string }>()
const emit = defineEmits<{ select: [slug: string] }>()

const topCategories = [
  { slug: '', label: 'All', emoji: '🍽️', bg: 'bg-surface-raised' },
  { slug: 'indian', label: 'Indian', emoji: '🍛', bg: 'bg-orange-500/20' },
  { slug: 'italian', label: 'Italian', emoji: '🍝', bg: 'bg-red-500/20' },
  { slug: 'street-food', label: 'Street food', emoji: '🌮', bg: 'bg-yellow-500/20' },
  { slug: 'cafe', label: 'Cafés', emoji: '☕', bg: 'bg-amber-500/20' },
  { slug: 'healthy', label: 'Healthy', emoji: '🥗', bg: 'bg-green-500/20' },
  { slug: 'bakery', label: 'Bakery', emoji: '🥐', bg: 'bg-orange-400/20' },
  { slug: 'asian-fusion', label: 'Asian', emoji: '🍜', bg: 'bg-pink-500/20' },
  { slug: 'mexican', label: 'Mexican', emoji: '🌯', bg: 'bg-lime-500/20' },
  { slug: 'fast-casual', label: 'Fast casual', emoji: '🍔', bg: 'bg-yellow-600/20' },
]
</script>
