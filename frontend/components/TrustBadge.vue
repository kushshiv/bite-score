<template>
  <span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium" :class="badgeClass">
    {{ label }}
  </span>
</template>

<script setup lang="ts">
const props = defineProps<{ type: string }>()

const labels: Record<string, string> = {
  claimed: 'Claimed',
  verified: 'Verified',
  high_confidence: 'High confidence',
  under_review: 'Under review',
}

const label = computed(() => labels[props.type] || props.type)

const badgeClass = computed(() => {
  switch (props.type) {
    case 'verified':
      return 'bg-trust-100 text-trust-700'
    case 'high_confidence':
      return 'bg-trust-50 text-trust-600'
    case 'under_review':
      return 'bg-caution-100 text-amber-700'
    default:
      return 'bg-slate-100 text-slate-600'
  }
})
</script>
