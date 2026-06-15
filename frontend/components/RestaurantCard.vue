<template>
  <NuxtLink
    :to="`/business/${business.slug}`"
    class="group block overflow-hidden rounded-2xl border border-surface-border bg-surface-raised transition hover:border-gray-600"
    :class="variant === 'compact' ? 'flex' : ''"
  >
    <div
      class="relative shrink-0 overflow-hidden bg-surface-hover"
      :class="variant === 'compact' ? 'h-24 w-24 sm:h-28 sm:w-28' : variant === 'grid' ? 'h-44 w-full' : 'h-36 w-full'"
    >
      <img
        :src="coverUrl"
        :alt="business.name"
        class="h-full w-full object-cover transition duration-300 group-hover:scale-105"
        loading="lazy"
      />
      <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
      <span
        v-if="variant === 'grid'"
        class="absolute left-3 top-3 rounded-md bg-black/60 px-2 py-0.5 text-xs font-semibold text-trust-400"
      >
        {{ verdict.shortLabel }}
      </span>
      <div class="absolute right-2 top-2">
        <ScoreBadge :score="business.overall_percent" />
      </div>
      <div
        v-if="variant === 'grid'"
        class="absolute bottom-3 left-3 flex h-10 w-10 items-center justify-center rounded-lg bg-white/95 text-lg shadow"
      >
        {{ categoryMeta.emoji }}
      </div>
    </div>

    <div class="flex min-w-0 flex-1 flex-col justify-center p-3 sm:p-4">
      <h3 class="truncate font-semibold text-white group-hover:text-trust-400">
        {{ business.name }}
      </h3>
      <div class="mt-1 flex items-center gap-2 text-sm">
        <span class="font-medium text-trust-400">★ {{ Math.round(business.overall_percent) }}</span>
        <span v-if="business.review_count" class="text-gray-500">({{ business.review_count }})</span>
        <span class="text-gray-600">·</span>
        <span class="truncate text-gray-500">{{ distanceLabel || business.location?.city }}</span>
      </div>
      <div v-if="variant !== 'grid'" class="mt-2 flex flex-wrap items-center gap-2">
        <span
          v-if="variant === 'compact'"
          class="rounded-full px-2 py-0.5 text-xs font-medium"
          :class="verdict.badgeClass"
        >
          {{ verdict.shortLabel }}
        </span>
        <TrustBadge
          v-for="badge in business.badges?.slice(0, 1)"
          :key="badge.badge_type"
          :type="badge.badge_type"
        />
      </div>
    </div>
  </NuxtLink>
</template>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    business: {
      name: string
      slug: string
      overall_percent: number
      review_count?: number
      cover_image_url?: string | null
      distance_km?: number | null
      location?: { city: string; country: string } | null
      category?: { name: string; slug?: string } | null
      badges?: { badge_type: string }[]
    }
    variant?: 'featured' | 'compact' | 'grid'
  }>(),
  { variant: 'featured' },
)

const categoryMeta = computed(() => useCategoryMeta(props.business.category?.slug))
const verdict = computed(() => useTrustVerdict(props.business.overall_percent))
const coverUrl = computed(() => businessCoverUrl(props.business))

const distanceLabel = computed(() => {
  const km = props.business.distance_km
  if (km == null) return null
  if (km < 1) return `${Math.round(km * 1000)} m`
  return `${km.toFixed(1)} km`
})
</script>
