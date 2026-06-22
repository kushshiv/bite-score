<template>
  <DiscoverShell
    :filters="filters"
    :facets="facets"
    :category-count="categoryCount"
    @update:filters="applyFilters"
    @clear="clearAll"
  >
    <DiscoverToolbar
      v-model="filters.q"
      :sort="filters.sort"
      :view-mode="viewMode"
      @search="applyFilters()"
      @update:sort="(s) => applyFilters({ sort: s as 'nearby' | 'score' })"
      @update:view-mode="toggleView"
    />

    <!-- Mobile filters -->
    <details class="mt-4 rounded-2xl border border-surface-border bg-surface-raised p-4 lg:hidden">
      <summary class="cursor-pointer text-sm font-medium text-discover-fg">
        Filters & cuisine
        <span v-if="facets" class="text-discover-muted">({{ facets.total }} places)</span>
      </summary>
      <div class="mt-4 space-y-3">
        <FilterToggle
          :label="`Highly rated (${facets?.high_trust ?? 0})`"
          :active="filters.high_trust"
          @toggle="applyFilters({ high_trust: !filters.high_trust })"
        />
        <FilterToggle
          :label="`Safe to eat (${facets?.safe_to_eat ?? 0})`"
          :active="filters.safe_only"
          @toggle="applyFilters({ safe_only: !filters.safe_only })"
        />
        <FilterToggle
          :label="`Verified (${facets?.verified ?? 0})`"
          :active="filters.verified_only"
          @toggle="applyFilters({ verified_only: !filters.verified_only })"
        />
      </div>
    </details>

    <div v-if="viewMode === 'list'" class="mt-5">
      <CuisineRow :active-category="filters.category" @select="(s) => applyFilters({ category: s })" />
    </div>

    <div v-if="viewMode === 'list'" class="mt-6">
      <DiscoverPromoRow />
    </div>

    <section class="mt-8">
      <h2 class="text-xl font-bold text-discover-fg">
        <template v-if="viewMode === 'map'">Map view</template>
        <template v-else-if="filters.q">Results for "{{ filters.q }}"</template>
        <template v-else>Top rated nearby</template>
      </h2>
      <p v-if="!pending && facets" class="mt-1 text-sm text-discover-muted">
        {{ facets.total }} place{{ facets.total === 1 ? '' : 's' }} in {{ location.label }}
      </p>

      <div v-if="pending" class="mt-8 text-discover-muted">Loading places...</div>
      <div
        v-else-if="viewMode === 'map'"
        class="mt-6"
      >
        <DiscoverMap
          :businesses="results ?? []"
          :center="{ lat: location.lat, lng: location.lng }"
          :selected-slug="selectedMapSlug"
          @select="(slug) => { selectedMapSlug = slug; navigateTo(`/business/${slug}`) }"
        />
      </div>
      <div
        v-else-if="!results?.length"
        class="mt-8 rounded-2xl border border-dashed border-surface-border p-12 text-center"
      >
        <p class="text-4xl">🍽️</p>
        <p class="mt-3 font-medium text-discover-fg">No places found</p>
        <p class="mt-1 text-sm text-discover-muted">Try another search, change location, or clear filters.</p>
        <div class="mt-4 flex flex-wrap items-center justify-center gap-3">
          <button class="btn-primary" @click="clearAll">Clear filters</button>
          <NuxtLink to="/add-place" class="btn-discover-ghost">
            Can't find it? Add a place
          </NuxtLink>
        </div>
      </div>
      <div v-else class="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <RestaurantCard v-for="b in results" :key="b.id" :business="b" variant="grid" />
      </div>
    </section>
  </DiscoverShell>
</template>

<script setup lang="ts">
const {
  filters,
  facets,
  results,
  pending,
  viewMode,
  selectedMapSlug,
  applyFilters,
  clearAll,
  toggleView,
  categoryCount,
  location,
} = useDiscoverFilters()
</script>
