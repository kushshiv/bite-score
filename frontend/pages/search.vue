<template>
  <div class="bg-slate-50">
    <LocationBar />

    <div class="mx-auto max-w-7xl px-4 py-6 sm:px-6">
      <!-- Active filters -->
      <div v-if="activeFilters.length" class="mb-4 flex flex-wrap gap-2">
        <span
          v-for="f in activeFilters"
          :key="f.key"
          class="inline-flex items-center gap-1 rounded-full bg-trust-100 px-3 py-1 text-xs font-medium text-trust-800"
        >
          {{ f.label }}
          <button class="hover:text-trust-900" @click="clearFilter(f.key)">×</button>
        </span>
      </div>

      <!-- Quick filters -->
      <div class="scrollbar-hide -mx-4 mb-6 flex gap-2 overflow-x-auto px-4 sm:mx-0 sm:flex-wrap sm:px-0">
        <button
          v-for="chip in filterChips"
          :key="chip.key"
          class="shrink-0 rounded-full border px-3 py-1.5 text-sm transition"
          :class="chip.active ? 'border-trust-500 bg-trust-50 font-medium text-trust-800' : 'border-slate-200 bg-white text-slate-700 hover:border-trust-400'"
          @click="chip.toggle()"
        >
          {{ chip.label }}
        </button>
      </div>

      <CategoryScroller :active-category="filters.category" />

      <!-- Results -->
      <div class="mt-6">
        <h1 class="text-xl font-bold text-slate-900">
          <template v-if="filters.q">Results for "{{ filters.q }}"</template>
          <template v-else-if="filters.category">{{ categoryLabel }} near {{ location.label }}</template>
          <template v-else>Places near {{ location.label }}</template>
        </h1>
        <p v-if="!pending && results?.length" class="mt-1 text-sm text-slate-500">
          {{ results.length }} place{{ results.length === 1 ? '' : 's' }} found
        </p>
      </div>

      <div v-if="pending" class="mt-8 text-slate-500">Searching...</div>
      <div
        v-else-if="!results?.length"
        class="mt-8 rounded-2xl border border-dashed border-slate-200 bg-white p-10 text-center"
      >
        <p class="text-3xl">🍽️</p>
        <p class="mt-3 font-medium text-slate-800">No places found</p>
        <p class="mt-1 text-sm text-slate-500">Try another search, change your location, or remove filters.</p>
        <button class="btn-primary mt-4" @click="clearAll">Clear filters</button>
      </div>
      <div v-else class="mt-6 space-y-3">
        <RestaurantCard v-for="b in results" :key="b.id" :business="b" variant="compact" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { CATEGORIES } from '~/composables/useCategoryMeta'

useSeoMeta({
  title: 'Search restaurants — BiteScore',
  description: 'Find restaurants and food vendors near you. Check hygiene scores before you eat.',
})

const route = useRoute()
const api = useApi()
const { location, businessParams } = useUserLocation()

const filters = reactive({
  q: (route.query.q as string) || '',
  category: (route.query.category as string) || '',
  high_trust: route.query.high_trust === 'true',
  verified_only: route.query.verified_only === 'true',
  sort: (route.query.sort as string) || 'nearby',
})

const categoryLabel = computed(() => CATEGORIES.find((c) => c.slug === filters.category)?.label || filters.category)

const activeFilters = computed(() => {
  const list: { key: string; label: string }[] = []
  if (filters.q) list.push({ key: 'q', label: `"${filters.q}"` })
  if (filters.category) list.push({ key: 'category', label: categoryLabel.value })
  if (filters.high_trust) list.push({ key: 'high_trust', label: 'Highly rated' })
  if (filters.verified_only) list.push({ key: 'verified_only', label: 'Verified' })
  if (filters.sort === 'score') list.push({ key: 'sort', label: 'Top rated' })
  return list
})

const filterChips = computed(() => [
  {
    key: 'high_trust',
    label: 'Highly rated',
    active: filters.high_trust,
    toggle: () => { filters.high_trust = !filters.high_trust; applyFilters() },
  },
  {
    key: 'verified_only',
    label: 'Verified',
    active: filters.verified_only,
    toggle: () => { filters.verified_only = !filters.verified_only; applyFilters() },
  },
  {
    key: 'sort_nearby',
    label: 'Nearest first',
    active: filters.sort === 'nearby',
    toggle: () => { filters.sort = 'nearby'; applyFilters() },
  },
  {
    key: 'sort_score',
    label: 'Top rated',
    active: filters.sort === 'score',
    toggle: () => { filters.sort = 'score'; applyFilters() },
  },
])

function buildQuery() {
  return {
    q: filters.q || undefined,
    category: filters.category || undefined,
    high_trust: filters.high_trust || undefined,
    verified_only: filters.verified_only || undefined,
    sort: filters.sort !== 'nearby' ? filters.sort : undefined,
  }
}

const { data: results, pending, refresh } = await useAsyncData(
  'search-results',
  () => {
    const params = new URLSearchParams(
      businessParams({
        q: filters.q,
        category: filters.category,
        high_trust: filters.high_trust,
        verified_only: filters.verified_only,
        sort: filters.sort,
        limit: 30,
      }),
    )
    return api.get(`/businesses?${params}`)
  },
  { watch: [location, () => route.query] },
)

watch(
  () => route.query,
  (q) => {
    filters.q = (q.q as string) || ''
    filters.category = (q.category as string) || ''
    filters.high_trust = q.high_trust === 'true'
    filters.verified_only = q.verified_only === 'true'
    filters.sort = (q.sort as string) || 'nearby'
    refresh()
  },
)

function applyFilters() {
  navigateTo({ path: '/search', query: buildQuery() })
}

function clearFilter(key: string) {
  if (key === 'q') filters.q = ''
  else if (key === 'category') filters.category = ''
  else if (key === 'high_trust') filters.high_trust = false
  else if (key === 'verified_only') filters.verified_only = false
  else if (key === 'sort') filters.sort = 'nearby'
  applyFilters()
}

function clearAll() {
  filters.q = ''
  filters.category = ''
  filters.high_trust = false
  filters.verified_only = false
  filters.sort = 'nearby'
  applyFilters()
}
</script>
