<template>
  <div class="mx-auto max-w-4xl px-4 py-10 sm:px-6">
    <h1 class="text-2xl font-bold text-slate-900">My reviews</h1>
    <p class="mt-2 text-slate-500">
      Places you've reviewed and their status.
      <NuxtLink to="/account" class="text-trust-600 hover:underline">Back to account</NuxtLink>
    </p>

    <div
      v-if="showSubmittedBanner"
      class="mt-6 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      Your observation was submitted and is <strong>pending moderator review</strong>. It will appear on the
      public profile once approved.
    </div>

    <div v-if="pending" class="mt-8 text-slate-500">Loading...</div>
    <div v-else-if="!reviews?.length" class="mt-8 card text-center text-slate-500">
      <p>You haven't reviewed any places yet.</p>
      <NuxtLink to="/search" class="btn-primary mt-4 inline-block">Find a place</NuxtLink>
    </div>
    <div v-else class="mt-8 space-y-4">
      <div v-for="review in reviews" :key="review.id" class="card">
        <div class="flex items-center justify-between gap-2">
          <span class="font-medium text-slate-900">Business #{{ review.business_id }}</span>
          <span class="text-xs text-slate-400">{{ review.visit_date }}</span>
        </div>
        <p v-if="review.notes" class="mt-2 text-sm text-slate-600">{{ review.notes }}</p>
        <div v-if="review.structured_score" class="mt-3 flex flex-wrap gap-3 text-xs text-slate-500">
          <span>Cleanliness: {{ review.structured_score.cleanliness }}</span>
          <span>Food handling: {{ review.structured_score.food_handling }}</span>
          <span>Staff: {{ review.structured_score.staff_hygiene }}</span>
        </div>
        <span class="mt-2 inline-block rounded-full px-2 py-0.5 text-xs" :class="statusClass(review.status)">
          {{ formatStatus(review.status) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useSeoMeta({ title: 'Dashboard — BiteScore' })

const route = useRoute()
const router = useRouter()
const api = useApi()
const showSubmittedBanner = ref(route.query.submitted === '1')

const { data: reviews, pending } = await useAsyncData('my-reviews', () => api.get('/reviews/me'))

onMounted(() => {
  if (route.query.submitted === '1') {
    router.replace({ query: {} })
  }
})

function formatStatus(status: string) {
  return status.replace(/_/g, ' ')
}

function statusClass(status: string) {
  switch (status) {
    case 'pending':
      return 'bg-amber-100 text-amber-800'
    case 'approved':
      return 'bg-trust-100 text-trust-800'
    case 'hidden':
    case 'flagged':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-slate-100 text-slate-600'
  }
}
</script>
