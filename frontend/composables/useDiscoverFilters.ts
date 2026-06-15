import type { UserLocation } from './useUserLocation'
import { buildBusinessParams } from './useUserLocation'

export interface DiscoverFilters {
  q: string
  category: string
  high_trust: boolean
  verified_only: boolean
  safe_only: boolean
  sort: 'nearby' | 'score'
}

export interface BusinessFacets {
  total: number
  high_trust: number
  verified: number
  safe_to_eat: number
  categories: Array<{ slug: string; name: string; count: number }>
}

export function filtersFromRoute(query: Record<string, string | string[] | undefined>): DiscoverFilters {
  return {
    q: (query.q as string) || '',
    category: (query.category as string) || '',
    high_trust: query.high_trust === 'true',
    verified_only: query.verified_only === 'true',
    safe_only: query.safe_only === 'true',
    sort: (query.sort as string) === 'score' ? 'score' : 'nearby',
  }
}

export function filtersToQuery(filters: DiscoverFilters): Record<string, string | undefined> {
  return {
    q: filters.q || undefined,
    category: filters.category || undefined,
    high_trust: filters.high_trust ? 'true' : undefined,
    verified_only: filters.verified_only ? 'true' : undefined,
    safe_only: filters.safe_only ? 'true' : undefined,
    sort: filters.sort !== 'nearby' ? filters.sort : undefined,
  }
}

export function buildFacetParams(location: UserLocation, q: string) {
  return new URLSearchParams(buildBusinessParams(location, { q: q || undefined })).toString()
}

export function filterSafeResults<T extends { overall_percent: number }>(
  items: T[],
  safeOnly: boolean,
): T[] {
  if (!safeOnly) return items
  return items.filter((b) => b.overall_percent >= 80)
}

export function categoryFacetCount(facets: BusinessFacets | null | undefined, slug: string) {
  return facets?.categories.find((c) => c.slug === slug)?.count ?? 0
}

export function useDiscoverFilters() {
  const route = useRoute()
  const api = useApi()
  const { location, businessParams } = useUserLocation()

  const filters = reactive<DiscoverFilters>(filtersFromRoute(route.query))
  const viewMode = ref<'list' | 'map'>('list')
  const selectedMapSlug = ref<string | null>(null)

  watch(
    () => route.query,
    (q) => Object.assign(filters, filtersFromRoute(q)),
  )

  const { data: results, pending, refresh } = useAsyncData(
    'discover-results',
    () => {
      const params = new URLSearchParams(
        businessParams({
          q: filters.q,
          category: filters.category,
          high_trust: filters.high_trust,
          verified_only: filters.verified_only,
          sort: filters.sort,
          limit: 40,
        }),
      )
      return api.get(`/businesses?${params}`)
    },
    { watch: [location, () => route.query] },
  )

  const { data: facets } = useAsyncData(
    'discover-facets',
    () => api.get(`/businesses/facets?${buildFacetParams(location.value, filters.q)}`),
    { watch: [location, () => route.query.q] },
  )

  const displayedResults = computed(() => filterSafeResults(results.value ?? [], filters.safe_only))

  function categoryCount(slug: string) {
    return categoryFacetCount(facets.value, slug)
  }

  function applyFilters(partial?: Partial<DiscoverFilters>) {
    if (partial) Object.assign(filters, partial)
    navigateTo({ path: route.path, query: filtersToQuery(filters) })
    refresh()
  }

  function clearAll() {
    Object.assign(filters, {
      q: '',
      category: '',
      high_trust: false,
      verified_only: false,
      safe_only: false,
      sort: 'nearby' as const,
    })
    applyFilters()
  }

  function toggleView(mode: 'list' | 'map') {
    viewMode.value = mode
  }

  return {
    filters,
    facets,
    results: displayedResults,
    pending,
    viewMode,
    selectedMapSlug,
    applyFilters,
    clearAll,
    toggleView,
    categoryCount,
    location,
    refresh,
  }
}
