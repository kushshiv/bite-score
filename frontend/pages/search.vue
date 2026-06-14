<template>
  <div class="mx-auto max-w-7xl px-4 py-10 sm:px-6">
    <h1 class="text-3xl font-bold text-slate-900">Search food businesses</h1>
    <p class="mt-2 text-slate-500">Filter by city, cuisine, trust score, and verification status.</p>

    <form class="mt-8 card grid gap-4 sm:grid-cols-2 lg:grid-cols-4" @submit.prevent="search">
      <div>
        <label class="label">Search</label>
        <input v-model="filters.q" class="input" placeholder="Name or keyword" />
      </div>
      <div>
        <label class="label">City</label>
        <select v-model="filters.city" class="input">
          <option value="">All cities</option>
          <option value="Berlin">Berlin</option>
          <option value="Mumbai">Mumbai</option>
          <option value="Austin">Austin</option>
        </select>
      </div>
      <div>
        <label class="label">Category</label>
        <select v-model="filters.category" class="input">
          <option value="">All cuisines</option>
          <option value="indian">Indian</option>
          <option value="italian">Italian</option>
          <option value="healthy">Healthy</option>
          <option value="street-food">Street Food</option>
          <option value="cafe">Cafe</option>
        </select>
      </div>
      <div class="flex items-end gap-3">
        <label class="flex items-center gap-2 text-sm">
          <input v-model="filters.high_trust" type="checkbox" class="accent-trust-600" />
          High trust only
        </label>
        <label class="flex items-center gap-2 text-sm">
          <input v-model="filters.verified_only" type="checkbox" class="accent-trust-600" />
          Verified
        </label>
      </div>
      <div class="sm:col-span-2 lg:col-span-4">
        <button class="btn-primary" type="submit">Search</button>
      </div>
    </form>

    <div v-if="pending" class="mt-8 text-slate-500">Searching...</div>
    <div v-else-if="!results?.length" class="mt-8 text-slate-500">No businesses found. Try different filters.</div>
    <div v-else class="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <BusinessCard v-for="b in results" :key="b.id" :business="b" />
    </div>
  </div>
</template>

<script setup lang="ts">
useSeoMeta({ title: 'Search — BiteScore' })

const route = useRoute()
const api = useApi()
const filters = reactive({
  q: (route.query.q as string) || '',
  city: (route.query.city as string) || '',
  category: (route.query.category as string) || '',
  high_trust: route.query.high_trust === 'true',
  verified_only: route.query.verified_only === 'true',
})

const { data: results, pending, refresh } = await useAsyncData('search', () => {
  const params = new URLSearchParams()
  if (filters.q) params.set('q', filters.q)
  if (filters.city) params.set('city', filters.city)
  if (filters.category) params.set('category', filters.category)
  if (filters.high_trust) params.set('high_trust', 'true')
  if (filters.verified_only) params.set('verified_only', 'true')
  return api.get(`/businesses?${params.toString()}`)
})

function search() {
  navigateTo({ path: '/search', query: { ...filters, high_trust: filters.high_trust || undefined, verified_only: filters.verified_only || undefined } })
  refresh()
}
</script>
