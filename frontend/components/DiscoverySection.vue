<template>
  <section>
    <div class="flex items-end justify-between gap-4">
      <div>
        <h2 class="text-lg font-bold text-slate-900 sm:text-xl">{{ title }}</h2>
        <p v-if="subtitle" class="mt-0.5 text-sm text-slate-500">{{ subtitle }}</p>
      </div>
      <NuxtLink v-if="seeAllLink" :to="seeAllLink" class="shrink-0 text-sm font-medium text-trust-600 hover:text-trust-700">
        See all →
      </NuxtLink>
    </div>

    <div v-if="pending" class="mt-4 text-sm text-slate-500">Loading...</div>
    <div v-else-if="!items?.length" class="mt-4 rounded-xl border border-dashed border-slate-200 bg-white p-6 text-center text-sm text-slate-500">
      {{ emptyText }}
    </div>
  <!-- Horizontal scroll on mobile, grid on larger screens -->
    <div
      v-else
      class="mt-4"
      :class="layout === 'scroll' ? 'scrollbar-hide -mx-4 flex gap-4 overflow-x-auto px-4 pb-2 sm:mx-0 sm:px-0' : 'grid gap-4 sm:grid-cols-2 lg:grid-cols-3'"
    >
      <div
        v-for="b in items"
        :key="b.id"
        :class="layout === 'scroll' ? 'w-64 shrink-0 sm:w-72' : ''"
      >
        <RestaurantCard :business="b" :variant="cardVariant" />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string
    subtitle?: string
    items?: Array<Record<string, unknown>>
    pending?: boolean
    seeAllLink?: string | { path: string; query?: Record<string, string> }
    emptyText?: string
    layout?: 'scroll' | 'grid'
    cardVariant?: 'featured' | 'compact'
  }>(),
  {
    emptyText: 'Nothing here yet — try another area or category.',
    layout: 'scroll',
    cardVariant: 'featured',
  },
)
</script>
