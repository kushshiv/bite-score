export interface ClaimSearchResult {
  id: number
  name: string
  slug: string
  city: string | null
  category_name: string | null
  is_claimed: boolean
}

export function useBusinessClaimSearch() {
  const api = useApi()
  const query = ref('')
  const city = ref('')
  const results = ref<ClaimSearchResult[]>([])
  const searching = ref(false)
  const searchError = ref('')
  let debounceTimer: ReturnType<typeof setTimeout> | null = null

  async function runSearch() {
    const trimmed = query.value.trim()
    if (trimmed.length < 2) {
      results.value = []
      searchError.value = ''
      return
    }

    searching.value = true
    searchError.value = ''
    try {
      const params = new URLSearchParams({ q: trimmed })
      if (city.value.trim()) params.set('city', city.value.trim())
      results.value = await api.get<ClaimSearchResult[]>(
        `/business-dashboard/claim-search?${params.toString()}`,
      )
    } catch (e: unknown) {
      results.value = []
      searchError.value = e instanceof Error ? e.message : 'Could not search businesses'
    } finally {
      searching.value = false
    }
  }

  function scheduleSearch() {
    if (debounceTimer) clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
      runSearch()
    }, 300)
  }

  watch(query, scheduleSearch)
  watch(city, scheduleSearch)

  onBeforeUnmount(() => {
    if (debounceTimer) clearTimeout(debounceTimer)
  })

  return {
    query,
    city,
    results,
    searching,
    searchError,
    runSearch,
  }
}
