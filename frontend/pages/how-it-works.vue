<template>
  <div class="mx-auto max-w-3xl px-4 py-12 sm:px-6">
    <h1 class="text-3xl font-bold text-slate-900">How BiteScore works</h1>
    <p class="mt-3 text-slate-600">
      We help you answer one question: <strong>is it safe to eat here?</strong>
    </p>
    <div class="mt-8 space-y-6">
      <section class="card">
        <h2 class="text-lg font-semibold text-slate-900">1. Diners share what they saw</h2>
        <p class="mt-2 text-slate-600">
          After eating somewhere, people leave structured reviews about cleanliness, food handling,
          staff hygiene, and more — not just "food was good."
        </p>
      </section>
      <section class="card">
        <h2 class="text-lg font-semibold text-slate-900">2. We turn that into a hygiene score</h2>
        <p class="mt-2 text-slate-600">Each place gets a score from 0–100 based on:</p>
        <ul class="mt-3 list-inside list-disc space-y-1 text-slate-600">
          <li>30% cleanliness</li>
          <li>20% food handling</li>
          <li>15% staff hygiene</li>
          <li>10% packaging</li>
          <li>10% water safety</li>
          <li>10% photo evidence quality</li>
          <li>5% consistency across reviews</li>
        </ul>
      </section>
      <section class="card">
        <h2 class="text-lg font-semibold text-slate-900">3. You get a clear answer</h2>
        <p class="mt-2 text-slate-600">
          Scores of 80+ mean <strong>safe to eat</strong>. 60–79 means <strong>use caution</strong>.
          Below 60 means <strong>low confidence</strong>. We also flag when there aren't enough reviews yet.
        </p>
      </section>
      <section class="card border-dashed">
        <h2 class="text-lg font-semibold text-slate-900">For restaurant owners</h2>
        <p class="mt-2 text-slate-600">
          You can claim your profile, respond to reviews, and request verification.
          <NuxtLink to="/business-dashboard" class="text-trust-600 hover:text-trust-700">Learn more →</NuxtLink>
        </p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'How it works — BiteScore',
  description: 'See how BiteScore helps you check restaurant hygiene before you eat.',
})
</script>
