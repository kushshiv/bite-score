<template>
  <div v-if="business" class="mx-auto max-w-7xl px-4 py-10 sm:px-6">
    <!-- Verdict banner -->
    <div class="rounded-xl border p-4 sm:p-5" :class="verdict.bannerClass">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p class="text-sm font-medium uppercase tracking-wide text-slate-500">Our take</p>
          <p class="mt-1 text-2xl font-bold text-slate-900">{{ verdict.label }}</p>
          <p class="mt-1 text-sm text-slate-600">{{ verdict.description }}</p>
        </div>
        <div class="flex shrink-0 items-center gap-4">
          <ScoreBadge :score="business.score.overall_percent" size="lg" />
          <div class="text-sm text-slate-600">
            <p class="font-medium">{{ business.score.review_count }} diner review{{ business.score.review_count === 1 ? '' : 's' }}</p>
            <p class="text-slate-500">Hygiene score</p>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-8 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
      <div>
        <div class="flex flex-wrap items-center gap-3">
          <h1 class="text-3xl font-bold text-slate-900">{{ business.name }}</h1>
          <TrustBadge v-for="badge in business.badges" :key="badge.badge_type" :type="badge.badge_type" />
        </div>
        <p class="mt-2 text-slate-500">
          {{ business.location?.city }}, {{ business.location?.country }}
          · {{ formatType(business.business_type) }}
          <span v-if="business.category"> · {{ business.category.name }}</span>
        </p>
        <p v-if="business.description" class="mt-4 max-w-2xl text-slate-600">{{ business.description }}</p>
      </div>
    </div>

    <!-- Trust indicators -->
    <div v-if="business.score.trust_indicators.length" class="mt-6 flex flex-wrap gap-2">
      <span
        v-for="ind in business.score.trust_indicators"
        :key="ind"
        class="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600"
      >
        {{ formatIndicator(ind) }}
      </span>
    </div>

    <div class="mt-10 grid gap-8 lg:grid-cols-3">
      <div class="lg:col-span-2 space-y-8">
        <!-- Score breakdown -->
        <section class="card">
          <h2 class="text-lg font-semibold text-slate-900">What diners noticed</h2>
          <p class="mt-2 text-sm text-slate-500">Hygiene breakdown from recent reviews.</p>
          <div class="mt-6">
            <ScoreBreakdown :breakdown="business.score.breakdown" />
          </div>
        </section>

        <!-- Reviews -->
        <section class="card">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold text-slate-900">Recent reviews</h2>
            <NuxtLink
              v-if="auth.isLoggedIn"
              :to="`/submit-review/${business.id}`"
              class="btn-primary text-sm"
            >
              Write a review
            </NuxtLink>
          </div>
          <div v-if="!reviews?.length" class="mt-4 text-sm text-slate-500">No reviews yet — be the first to share your visit.</div>
          <div v-else class="mt-6 space-y-6">
            <div v-for="review in reviews" :key="review.id" class="border-t border-slate-100 pt-6 first:border-0 first:pt-0">
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-slate-700">{{ review.user_name }}</span>
                <span class="text-xs text-slate-400">{{ review.visit_date }} · {{ review.visit_type.replace('_', ' ') }}</span>
              </div>
              <p v-if="review.notes" class="mt-2 text-sm text-slate-600">{{ review.notes }}</p>
              <p v-if="review.business_response" class="mt-3 rounded-lg bg-trust-50 p-3 text-sm text-trust-800">
                <strong>Business response:</strong> {{ review.business_response }}
              </p>
            </div>
          </div>
        </section>
      </div>

      <div class="space-y-6">
        <section class="card">
          <h3 class="font-semibold text-slate-900">Share your visit</h3>
          <div class="mt-4 space-y-3">
            <NuxtLink
              v-if="ownsThisBusiness"
              to="/business-dashboard"
              class="btn-primary block w-full text-center"
            >
              Manage your business
            </NuxtLink>
            <NuxtLink
              v-if="auth.isLoggedIn && !ownsThisBusiness"
              :to="`/submit-review/${business.id}`"
              class="btn-primary block w-full text-center"
            >
              Write a review
            </NuxtLink>
            <button v-else class="btn-primary w-full" @click="openAuth('register')">Sign up to review</button>
            <button v-if="auth.isLoggedIn" class="btn-secondary w-full" @click="showFlag = true">Report a problem</button>
            <NuxtLink to="/moderation" class="block text-center text-xs text-slate-400 hover:text-slate-600">
              Owner? Request a correction
            </NuxtLink>
          </div>
        </section>

        <section class="card">
          <div class="flex items-center justify-between gap-2">
            <h3 class="font-semibold text-slate-900">Photos from diners</h3>
            <NuxtLink v-if="auth.isModerator" to="/admin" class="text-xs text-trust-600 hover:underline">
              Open moderation queue
            </NuxtLink>
          </div>
          <p v-if="!evidence?.length" class="mt-3 text-sm text-slate-500">
            No diner photos yet.
            <span v-if="auth.isModerator"> Submit a review with photos as a user, or check other businesses.</span>
          </p>
          <div v-else class="mt-4 grid grid-cols-2 gap-2">
            <div v-for="e in evidence" :key="e.id" class="relative">
              <img
                :src="e.file_url"
                class="h-24 w-full rounded-lg object-cover"
                alt="Community evidence"
              />
              <span
                v-if="e.verified"
                class="absolute bottom-1 left-1 rounded bg-trust-600/90 px-1.5 py-0.5 text-[10px] font-medium text-white"
              >
                Verified
              </span>
              <button
                v-else-if="auth.isModerator"
                type="button"
                class="absolute bottom-1 left-1 rounded bg-amber-500/90 px-1.5 py-0.5 text-[10px] font-medium text-white hover:bg-amber-600"
                :disabled="verifyingId === e.id"
                @click="verifyEvidence(e.id)"
              >
                {{ verifyingId === e.id ? '…' : 'Verify' }}
              </button>
            </div>
          </div>
          <p v-if="evidenceError" class="mt-2 text-xs text-red-600">{{ evidenceError }}</p>
        </section>
      </div>
    </div>

    <!-- Flag modal -->
    <div v-if="showFlag" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" @click.self="showFlag = false">
      <div class="card w-full max-w-md">
        <h3 class="font-semibold text-slate-900">Report a concern</h3>
        <p class="mt-2 text-sm text-slate-500">Use neutral language. Reports are reviewed by moderators.</p>
        <textarea v-model="flagReason" class="input mt-4" rows="4" placeholder="Describe your concern..." />
        <div class="mt-4 flex gap-3">
          <button class="btn-primary" @click="submitFlag">Submit</button>
          <button class="btn-secondary" @click="showFlag = false">Cancel</button>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="mx-auto max-w-7xl px-4 py-20 text-center text-slate-500">Business not found.</div>
</template>

<script setup lang="ts">
const route = useRoute()
const api = useApi()
const auth = useAuthStore()
const { open: openAuth } = useAuthModal()
const { claimedBusiness } = useBusinessAccount()
const showFlag = ref(false)
const flagReason = ref('')
const verifyingId = ref<number | null>(null)
const evidenceError = ref('')

const slug = route.params.slug as string

const { data: business } = await useAsyncData(`business-${slug}`, () => api.get(`/businesses/${slug}`))
const { data: reviews } = await useAsyncData(`reviews-${slug}`, () => api.get(`/businesses/${slug}/reviews`))
const { data: evidence, refresh: refreshEvidence } = await useAsyncData(`evidence-${slug}`, () =>
  api.get(`/businesses/${slug}/evidence`),
)

const verdict = computed(() =>
  business.value ? useTrustVerdict(business.value.score.overall_percent) : useTrustVerdict(0),
)

const ownsThisBusiness = computed(
  () => Boolean(business.value && claimedBusiness.value?.id === business.value.id),
)

useSeoMeta({
  title: () => business.value ? `${business.value.name} — BiteScore` : 'Business — BiteScore',
  description: () => business.value?.description || 'Check hygiene scores and diner reviews on BiteScore',
  ogTitle: () => business.value ? `${business.value.name} — BiteScore` : 'BiteScore',
})

function formatType(t: string) {
  return t.replace(/_/g, ' ')
}

function formatIndicator(ind: string) {
  return ind.replace(/_/g, ' ')
}

async function verifyEvidence(uploadId: number) {
  evidenceError.value = ''
  verifyingId.value = uploadId
  try {
    await api.patch(`/uploads/${uploadId}/verify`)
    await refreshEvidence()
  } catch (e: unknown) {
    evidenceError.value = e instanceof Error ? e.message : 'Could not verify photo'
  } finally {
    verifyingId.value = null
  }
}

async function submitFlag() {
  if (!business.value || flagReason.value.length < 10) return
  await api.post('/flags', {
    target_type: 'business',
    target_id: business.value.id,
    reason: flagReason.value,
  })
  showFlag.value = false
  flagReason.value = ''
  alert('Report submitted for moderation review.')
}
</script>
