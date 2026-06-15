<template>
  <div
    class="flex flex-col items-center justify-center rounded-xl text-center"
    :class="[scoreClass, size === 'lg' ? 'h-20 w-20' : 'h-14 w-14']"
  >
    <span :class="size === 'lg' ? 'text-2xl' : 'text-lg'" class="font-bold leading-none">{{ Math.round(score) }}</span>
    <span class="text-[10px] uppercase tracking-wide opacity-80">Score</span>
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{ score: number; size?: 'sm' | 'lg' }>(), { size: 'sm' })

const scoreClass = computed(() => {
  if (props.score >= 80) return 'bg-trust-100 text-trust-700'
  if (props.score >= 60) return 'bg-caution-100 text-amber-700'
  return 'bg-slate-100 text-slate-600'
})
</script>
