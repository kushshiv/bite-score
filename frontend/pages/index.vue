<template>
  <div>
    <!-- Hero -->
    <section class="bg-gradient-to-b from-trust-50 to-slate-50">
      <div class="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:py-28">
        <div class="mx-auto max-w-3xl text-center">
          <h1 class="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
            Discover food businesses you can trust
          </h1>
          <p class="mt-6 text-lg text-slate-600">
            BiteScore combines structured hygiene observations, evidence-backed reviews, and transparent scoring — not opinion-only rants.
          </p>
          <form class="mt-10 flex flex-col gap-3 sm:flex-row sm:justify-center" @submit.prevent="goSearch">
            <input
              v-model="query"
              class="input max-w-md flex-1"
              placeholder="Search places, cities, or cuisines..."
              type="search"
            />
            <button class="btn-primary" type="submit">Search</button>
          </form>
          <div class="mt-6 flex flex-wrap justify-center gap-4">
            <NuxtLink to="/how-it-works" class="btn-secondary">How scoring works</NuxtLink>
            <button class="btn-primary" @click="openAuth('register')">Submit a review</button>
          </div>
        </div>
      </div>
    </section>

    <!-- Example places -->
    <section class="mx-auto max-w-7xl px-4 py-16 sm:px-6">
      <h2 class="text-2xl font-bold text-slate-900">Trusted places</h2>
      <p class="mt-2 text-slate-500">Community-reviewed businesses with transparent BiteScores.</p>
      <div v-if="pending" class="mt-8 text-slate-500">Loading...</div>
      <div v-else class="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <BusinessCard v-for="b in businesses" :key="b.id" :business="b" />
      </div>
    </section>

    <!-- Scoring explainer -->
    <section class="border-t border-slate-200 bg-white">
      <div class="mx-auto max-w-7xl px-4 py-16 sm:px-6">
        <h2 class="text-2xl font-bold text-slate-900">Transparent scoring</h2>
        <p class="mt-4 max-w-2xl text-slate-600">
          Every BiteScore is calculated from structured community observations — hygiene, food handling, staff practices, packaging, water confidence, and evidence credibility. Scores are platform-derived, not government certifications.
        </p>
        <div class="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div v-for="item in weights" :key="item.label" class="card">
            <p class="text-2xl font-bold text-trust-600">{{ item.weight }}</p>
            <p class="mt-1 font-medium text-slate-900">{{ item.label }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="bg-slate-850 text-white">
      <div class="mx-auto max-w-7xl px-4 py-16 text-center sm:px-6">
        <h2 class="text-2xl font-bold">For consumers and business owners</h2>
        <p class="mx-auto mt-4 max-w-xl text-slate-300">
          Submit structured observations or claim your business profile to respond to community feedback.
        </p>
        <div class="mt-8 flex flex-wrap justify-center gap-4">
          <NuxtLink to="/search" class="btn-primary">Explore places</NuxtLink>
          <NuxtLink to="/business-dashboard" class="btn-secondary !text-slate-900">Business dashboard</NuxtLink>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'BiteScore — Food Trust Platform',
  description: 'Discover food businesses you can trust with structured hygiene observations and transparent scoring.',
  ogTitle: 'BiteScore — Food Trust Platform',
})

const api = useApi()
const query = ref('')
const { open: openAuth } = useAuthModal()

const { data: businesses, pending } = await useAsyncData('home-businesses', () =>
  api.get('/businesses?high_trust=true&limit=6')
)

const weights = [
  { label: 'Hygiene / Cleanliness', weight: '30%' },
  { label: 'Food Handling', weight: '20%' },
  { label: 'Staff Hygiene', weight: '15%' },
  { label: 'Packaging & Water', weight: '20%' },
]

function goSearch() {
  navigateTo({ path: '/search', query: query.value ? { q: query.value } : {} })
}
</script>
