<template>
  <div class="mx-auto max-w-3xl px-4 py-12 sm:px-6">
    <h1 class="text-3xl font-bold text-slate-900">{{ title }}</h1>
    <p class="mt-2 text-sm text-slate-500">Last updated: June 2026. MVP policy — consult legal counsel before production launch.</p>
    <div class="mt-8 space-y-8">
      <section v-for="section in sections" :key="section.heading">
        <h2 class="text-lg font-semibold text-slate-900">{{ section.heading }}</h2>
        <p class="mt-2 text-slate-600">{{ section.body }}</p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  sections: { heading: string; body: string }[]
}>()
</script>
