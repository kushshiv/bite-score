<template>
  <div class="flex min-h-screen flex-col">
    <DiscoverHeader />

    <div class="mx-auto flex w-full max-w-[1400px] flex-1 gap-0 lg:gap-6 lg:px-6 lg:py-4">
      <DiscoverFilterSidebar
        class="hidden w-56 shrink-0 lg:block xl:w-64"
        :facets="facets"
        :filters="filters"
        :category-count="categoryCount"
        @update="(p) => emit('update:filters', p)"
        @clear="emit('clear')"
      />

      <main class="min-w-0 flex-1 px-4 pb-10 lg:px-0">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { BusinessFacets, DiscoverFilters } from '~/composables/useDiscoverFilters'

defineProps<{
  filters: DiscoverFilters
  facets?: BusinessFacets | null
  categoryCount: (slug: string) => number
}>()

const emit = defineEmits<{
  'update:filters': [partial: Partial<DiscoverFilters>]
  clear: []
}>()
</script>
