<template>
  <NuxtLink :to="`/business/${business.slug}`" class="card block transition hover:border-trust-500 hover:shadow-md">
    <div class="flex items-start justify-between gap-4">
      <div>
        <h3 class="font-semibold text-slate-900">{{ business.name }}</h3>
        <p class="mt-1 text-sm text-slate-500">
          {{ business.location?.city }}, {{ business.location?.country }}
          <span v-if="business.category"> · {{ business.category.name }}</span>
        </p>
      </div>
      <ScoreBadge :score="business.overall_percent" />
    </div>
    <div v-if="business.badges?.length" class="mt-3 flex flex-wrap gap-2">
      <TrustBadge v-for="badge in business.badges" :key="badge.badge_type" :type="badge.badge_type" />
    </div>
  </NuxtLink>
</template>

<script setup lang="ts">
defineProps<{
  business: {
    name: string
    slug: string
    overall_percent: number
    location?: { city: string; country: string } | null
    category?: { name: string } | null
    badges?: { badge_type: string }[]
  }
}>()
</script>
