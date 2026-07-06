<template>
  <div class="mx-auto max-w-4xl px-4 py-10 sm:px-6">
    <h1 class="text-2xl font-bold text-slate-900">My account</h1>
    <p class="mt-2 text-slate-500">Your reviews, claimed businesses, and profile settings.</p>

    <div class="mt-8 grid gap-4 sm:grid-cols-2">
      <NuxtLink to="/dashboard" class="card block transition hover:border-trust-200">
        <h2 class="font-semibold text-slate-900">My reviews</h2>
        <p class="mt-2 text-sm text-slate-500">Places you've reviewed and observation history.</p>
      </NuxtLink>

      <NuxtLink
        v-if="hasClaimedBusiness"
        to="/business-dashboard"
        class="card block transition hover:border-trust-200"
      >
        <h2 class="font-semibold text-slate-900">{{ claimedBusiness?.name }}</h2>
        <p class="mt-2 text-sm text-slate-500">Manage your claimed profile and respond to reviews.</p>
      </NuxtLink>

      <NuxtLink
        v-else-if="pendingClaims.length"
        to="/business-dashboard"
        class="card block transition hover:border-trust-200"
      >
        <h2 class="font-semibold text-slate-900">Business claim pending</h2>
        <p class="mt-2 text-sm text-slate-500">
          {{ pendingClaims.length }} claim{{ pendingClaims.length === 1 ? '' : 's' }} awaiting moderator review.
        </p>
      </NuxtLink>

      <NuxtLink
        v-else-if="auth.isModerator"
        to="/admin"
        class="card block transition hover:border-trust-200"
      >
        <h2 class="font-semibold text-slate-900">Moderation</h2>
        <p class="mt-2 text-sm text-slate-500">Review claims, certifications, flags, and queue items.</p>
      </NuxtLink>

      <NuxtLink
        v-else-if="auth.isBusinessOwner"
        to="/business-dashboard#claim"
        class="card block transition hover:border-trust-200"
      >
        <h2 class="font-semibold text-slate-900">Claim a business profile</h2>
        <p class="mt-2 text-sm text-slate-500">Own a restaurant or vendor? Request to manage your public page.</p>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useSeoMeta({ title: 'My Account — BiteScore' })

const auth = useAuthStore()
const { hasClaimedBusiness, claimedBusiness, pendingClaims } = useBusinessAccount()
</script>
