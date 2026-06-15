<template>
  <NuxtLink
    :to="`/business/${business.slug}`"
    class="group block overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:border-trust-400 hover:shadow-md"
    :class="variant === 'compact' ? 'flex' : ''"
  >
    <!-- Image / visual header -->
    <div
      class="relative shrink-0 bg-gradient-to-br"
      :class="[
        categoryMeta.gradient,
        variant === 'compact' ? 'h-24 w-24 sm:h-28 sm:w-28' : 'h-36 w-full',
      ]"
    >
      <span
        class="absolute left-3 top-3"
        :class="variant === 'compact' ? 'text-2xl' : 'text-3xl'"
        aria-hidden="true"
      >
        {{ categoryMeta.emoji }}
      </span>
      <div class="absolute right-2 top-2">
        <ScoreBadge :score="business.overall_percent" />
      </div>
      <span
        v-if="variant !== 'compact'"
        class="absolute bottom-3 left-3 rounded-full px-2.5 py-0.5 text-xs font-semibold"
        :class="verdict.badgeClass"
      >
        {{ verdict.label }}
      </span>
    </div>

    <!-- Details -->
    <div class="flex min-w-0 flex-1 flex-col justify-center p-4">
      <h3 class="truncate font-semibold text-slate-900 group-hover:text-trust-700">
        {{ business.name }}
      </h3>
      <p class="mt-0.5 truncate text-sm text-slate-500">
        <span v-if="business.category">{{ business.category.name }}</span>
        <span v-if="business.category && (distanceLabel || business.location)"> · </span>
        <span>{{ distanceLabel || business.location?.city }}</span>
      </p>
      <div class="mt-2 flex flex-wrap items-center gap-2">
        <span
          v-if="variant === 'compact'"
          class="rounded-full px-2 py-0.5 text-xs font-medium"
          :class="verdict.badgeClass"
        >
          {{ verdict.shortLabel }}
        </span>
        <span v-if="business.review_count" class="text-xs text-slate-400">
          {{ business.review_count }} review{{ business.review_count === 1 ? '' : 's' }}
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
      distance_km?: number | null
      location?: { city: string; country: string } | null
      category?: { name: string; slug?: string } | null
      badges?: { badge_type: string }[]
    }
    variant?: 'featured' | 'compact'
  }>(),
  { variant: 'featured' },
)

const categoryMeta = computed(() => useCategoryMeta(props.business.category?.slug))
const verdict = computed(() => useTrustVerdict(props.business.overall_percent))

const distanceLabel = computed(() => {
  const km = props.business.distance_km
  if (km == null) return null
  if (km < 1) return `${Math.round(km * 1000)} m away`
  return `${km.toFixed(1)} km away`
})
</script>
