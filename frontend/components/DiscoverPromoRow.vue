<template>
  <div class="grid gap-3 sm:grid-cols-2">
    <div class="card-dark overflow-hidden p-5 sm:col-span-1">
      <p class="text-xs font-semibold uppercase tracking-wide text-trust-400">Know before you eat</p>
      <h3 class="mt-2 text-xl font-bold text-white">Check hygiene scores</h3>
      <p class="mt-2 text-sm text-gray-400">Real diner reviews on cleanliness, food handling & more.</p>
      <NuxtLink to="/how-it-works" class="mt-4 inline-block text-sm font-medium text-trust-400 hover:text-trust-300">
        How it works →
      </NuxtLink>
    </div>
    <div class="card-dark overflow-hidden p-5 sm:col-span-1">
      <p class="text-xs font-semibold uppercase tracking-wide text-trust-400">Help the community</p>
      <h3 class="mt-2 text-xl font-bold text-white">Ate somewhere recently?</h3>
      <p class="mt-2 text-sm text-gray-400">Share a quick hygiene review — takes about 2 minutes.</p>
      <button class="btn-primary mt-4 text-sm" @click="openAuth('register')">Write a review</button>
    </div>
  </div>
</template>

<script setup lang="ts">
const { open: openAuth } = useAuthModal()
</script>
