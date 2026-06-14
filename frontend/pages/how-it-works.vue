<template>
  <div class="mx-auto max-w-3xl px-4 py-12 sm:px-6">
    <h1 class="text-3xl font-bold text-slate-900">How BiteScore works</h1>
    <div class="mt-8 space-y-8">
      <section class="card">
        <h2 class="text-lg font-semibold text-slate-900">1. Structured observations</h2>
        <p class="mt-2 text-slate-600">
          Community members submit structured reviews across hygiene dimensions — not unstructured rants.
          Users confirm their observations are honest before submission.
        </p>
      </section>
      <section class="card">
        <h2 class="text-lg font-semibold text-slate-900">2. Transparent scoring</h2>
        <p class="mt-2 text-slate-600">Scores are weighted across:</p>
        <ul class="mt-3 list-inside list-disc space-y-1 text-slate-600">
          <li>30% hygiene / cleanliness</li>
          <li>20% food handling</li>
          <li>15% staff hygiene</li>
          <li>10% packaging</li>
          <li>10% water safety confidence</li>
          <li>10% evidence credibility</li>
          <li>5% consistency weighting</li>
        </ul>
      </section>
      <section class="card">
        <h2 class="text-lg font-semibold text-slate-900">3. Trust indicators</h2>
        <p class="mt-2 text-slate-600">
          We surface confidence signals like low sample size, verified evidence, owner-claimed profiles,
          moderation review status, and recent improvement trends.
        </p>
      </section>
      <section class="card">
        <h2 class="text-lg font-semibold text-slate-900">4. Business participation</h2>
        <p class="mt-2 text-slate-600">
          Business owners can claim profiles, respond to observations, upload certifications,
          and request verification through our moderation process.
        </p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'How it works — BiteScore',
  description: 'Understand how BiteScore calculates food trust scores from structured community observations.',
})
</script>
