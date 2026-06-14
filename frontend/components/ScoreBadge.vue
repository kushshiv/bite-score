<template>
  <div
    class="flex h-14 w-14 flex-col items-center justify-center rounded-xl text-center"
    :class="scoreClass"
  >
    <span class="text-lg font-bold leading-none">{{ Math.round(score) }}</span>
    <span class="text-[10px] uppercase tracking-wide opacity-80">Score</span>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ score: number }>()

const scoreClass = computed(() => {
  if (props.score >= 80) return 'bg-trust-100 text-trust-700'
  if (props.score >= 60) return 'bg-caution-100 text-amber-700'
  return 'bg-slate-100 text-slate-600'
})
</script>
