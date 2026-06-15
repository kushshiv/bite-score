<template>
  <aside class="sticky top-[72px] h-fit max-h-[calc(100vh-88px)] overflow-y-auto rounded-2xl border border-surface-border bg-surface-raised p-5">
    <h2 class="text-lg font-bold text-white">{{ facets?.total ?? 0 }} places</h2>

    <div class="mt-5 space-y-4">
      <FilterToggle
        :label="`Highly rated (${facets?.high_trust ?? 0})`"
        :active="filters.high_trust"
        @toggle="toggle('high_trust')"
      />
      <FilterToggle
        :label="`Safe to eat (${facets?.safe_to_eat ?? 0})`"
        :active="filters.safe_only"
        @toggle="toggle('safe_only')"
      />
      <FilterToggle
        :label="`Verified (${facets?.verified ?? 0})`"
        :active="filters.verified_only"
        @toggle="toggle('verified_only')"
      />
      <FilterToggle label="Top rated first" :active="filters.sort === 'score'" @toggle="toggleSort" />
    </div>

    <div class="mt-8">
      <h3 class="text-sm font-semibold text-white">Cuisine</h3>
      <ul class="mt-3 space-y-2">
        <li v-for="cat in CATEGORIES" :key="cat.slug">
          <label class="flex cursor-pointer items-center justify-between gap-2 text-sm text-gray-400 hover:text-gray-200">
            <span class="flex items-center gap-2.5">
              <input
                type="checkbox"
                class="h-4 w-4 rounded border-surface-border bg-surface accent-trust-500"
                :checked="filters.category === cat.slug"
                @change="emit('update', { category: filters.category === cat.slug ? '' : cat.slug })"
              />
              <span>{{ cat.emoji }} {{ cat.label }}</span>
            </span>
            <span class="text-xs text-gray-600">({{ categoryCount(cat.slug) }})</span>
          </label>
        </li>
      </ul>
    </div>

    <button
      v-if="hasActiveFilters"
      class="mt-6 w-full rounded-full border border-surface-border py-2 text-sm text-gray-400 transition hover:border-gray-500 hover:text-white"
      @click="emit('clear')"
    >
      Clear all filters
    </button>
  </aside>
</template>

<script setup lang="ts">
import { CATEGORIES } from '~/composables/useCategoryMeta'
import type { BusinessFacets, DiscoverFilters } from '~/composables/useDiscoverFilters'

const props = defineProps<{
  facets?: BusinessFacets | null
  filters: DiscoverFilters
  categoryCount: (slug: string) => number
}>()

const emit = defineEmits<{
  update: [partial: Partial<DiscoverFilters>]
  clear: []
}>()

const hasActiveFilters = computed(
  () =>
    props.filters.high_trust
    || props.filters.safe_only
    || props.filters.verified_only
    || props.filters.category
    || props.filters.sort === 'score',
)

function toggle(key: 'high_trust' | 'safe_only' | 'verified_only') {
  emit('update', { [key]: !props.filters[key] })
}

function toggleSort() {
  emit('update', { sort: props.filters.sort === 'score' ? 'nearby' : 'score' })
}
</script>
