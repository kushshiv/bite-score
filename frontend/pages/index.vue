<template>
  <div class="bg-slate-50">
    <LocationBar />

    <div class="mx-auto max-w-7xl space-y-10 px-4 py-6 sm:px-6 sm:py-8">
      <!-- Categories -->
      <section>
        <h2 class="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">What are you craving?</h2>
        <CategoryScroller />
      </section>

      <!-- Recommended -->
      <DiscoverySection
        title="Recommended for you"
        :subtitle="`Safe picks based on hygiene scores in ${location.label}`"
        :items="sections?.recommended"
        :pending="pending"
        :see-all-link="{ path: '/search', query: { high_trust: 'true' } }"
      />

      <!-- Nearby -->
      <DiscoverySection
        title="Popular near you"
        subtitle="Restaurants and vendors closest to your location"
        :items="sections?.nearby"
        :pending="pending"
        :see-all-link="{ path: '/search', query: { sort: 'nearby' } }"
      />

      <!-- Top rated -->
      <DiscoverySection
        :title="`Top rated in ${location.city}`"
        subtitle="Highest hygiene scores from diner reviews"
        :items="sections?.topRated"
        :pending="pending"
        :see-all-link="{ path: '/search', query: { sort: 'score' } }"
      />

      <!-- Street food -->
      <DiscoverySection
        title="Safe street food picks"
        subtitle="Street vendors with strong hygiene signals"
        :items="sections?.streetFood"
        :pending="pending"
        :see-all-link="{ path: '/search', query: { category: 'street-food', high_trust: 'true' } }"
      />

      <!-- Full list -->
      <section>
        <h2 class="text-lg font-bold text-slate-900 sm:text-xl">All places near you</h2>
        <p class="mt-0.5 text-sm text-slate-500">Browse every restaurant and vendor in your area</p>
        <div v-if="pending" class="mt-4 text-sm text-slate-500">Loading...</div>
        <div v-else class="mt-4 space-y-3">
          <RestaurantCard
            v-for="b in sections?.allNearby"
            :key="b.id"
            :business="b"
            variant="compact"
          />
        </div>
        <div v-if="!pending && sections?.allNearby?.length" class="mt-6 text-center">
          <NuxtLink to="/search" class="btn-secondary">View all & filter</NuxtLink>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'BiteScore — Find safe restaurants near you',
  description: 'Discover restaurants and food vendors near you. Check hygiene scores before you eat.',
})

const api = useApi()
const { location, businessParams } = useUserLocation()

function qs(extra: Record<string, string | number | boolean | undefined>) {
  return new URLSearchParams(businessParams(extra)).toString()
}

const { data: sections, pending } = await useAsyncData(
  'discovery-sections',
  () =>
    Promise.all([
      api.get(`/businesses?${qs({ high_trust: true, sort: 'score', limit: 8 })}`),
      api.get(`/businesses?${qs({ sort: 'nearby', limit: 8 })}`),
      api.get(`/businesses?${qs({ sort: 'score', limit: 8 })}`),
      api.get(`/businesses?${qs({ category: 'street-food', high_trust: true, limit: 6 })}`),
      api.get(`/businesses?${qs({ sort: 'nearby', limit: 20 })}`),
    ]).then(([recommended, nearby, topRated, streetFood, allNearby]) => ({
      recommended,
      nearby,
      topRated,
      streetFood,
      allNearby,
    })),
  { watch: [location] },
)
</script>
