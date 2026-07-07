<template>
  <div class="mx-auto max-w-5xl px-4 py-10 sm:px-6">
    <h1 class="text-2xl font-bold text-slate-900">Business dashboard</h1>
    <p class="mt-2 text-slate-500">Manage your claimed profile, respond to observations, and track your trust score.</p>

    <div v-if="accountPending || (hasClaimedBusiness && statsPending)" class="mt-8 text-slate-500">Loading...</div>

    <div v-else-if="hasClaimedBusiness && stats" class="mt-8 space-y-8">
      <div class="card">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 class="text-xl font-semibold text-slate-900">{{ stats.business.name }}</h2>
            <NuxtLink :to="`/business/${stats.business.slug}`" class="text-sm text-trust-600 hover:underline">
              View public profile
            </NuxtLink>
          </div>
          <ScoreBadge :score="stats.score.overall_percent" />
        </div>
        <p class="mt-4 text-sm text-slate-500">{{ stats.total_reviews }} total observations</p>
      </div>

      <div class="card">
        <h3 class="font-semibold text-slate-900">Score breakdown</h3>
        <div class="mt-4">
          <ScoreBreakdown :breakdown="stats.score.breakdown" />
        </div>
        <div v-if="stats.score.trust_indicators.length" class="mt-4 flex flex-wrap gap-2">
          <span v-for="ind in stats.score.trust_indicators" :key="ind" class="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
            {{ ind.replace(/_/g, ' ') }}
          </span>
        </div>
      </div>

      <div class="card">
        <h3 class="font-semibold text-slate-900">Respond to observations</h3>
        <p class="mt-1 text-sm text-slate-500">
          Reply to diner reviews on your public profile. Use neutral, factual language.
        </p>
        <p v-if="reviewError" class="mt-3 text-sm text-red-600">{{ reviewError }}</p>
        <div v-if="reviewsPending" class="mt-4 text-sm text-slate-500">Loading reviews...</div>
        <p v-else-if="!reviews?.length" class="mt-4 text-sm text-slate-500">No reviews yet.</p>
        <div v-else class="mt-4 space-y-6">
          <div
            v-for="review in reviews"
            :key="review.id"
            class="border-t border-slate-100 pt-6 first:border-0 first:pt-0"
          >
            <div class="flex flex-wrap items-center justify-between gap-2">
              <span class="text-sm font-medium text-slate-700">{{ review.user_name }}</span>
              <span class="text-xs text-slate-400">
                {{ review.visit_date }} · {{ review.visit_type.replace('_', ' ') }}
              </span>
            </div>
            <p v-if="review.notes" class="mt-2 text-sm text-slate-600">{{ review.notes }}</p>
            <form class="mt-4 space-y-3" @submit.prevent="submitResponse(review.id)">
              <div>
                <label class="label">Your response</label>
                <textarea
                  v-model="responseDrafts[review.id]"
                  class="input"
                  rows="3"
                  placeholder="Thank the diner or clarify your hygiene practices..."
                />
              </div>
              <button class="btn-primary" type="submit" :disabled="respondingId === review.id">
                {{
                  respondingId === review.id
                    ? 'Posting...'
                    : review.business_response
                      ? 'Update response'
                      : 'Post response'
                }}
              </button>
            </form>
          </div>
        </div>
      </div>

      <div class="card">
        <h3 class="font-semibold text-slate-900">Edit profile</h3>
        <form class="mt-4 space-y-4" @submit.prevent="updateProfile">
          <div>
            <label class="label">Description</label>
            <textarea v-model="description" class="input" rows="3" />
          </div>
          <button class="btn-primary" type="submit">Save</button>
        </form>
      </div>

      <div class="card">
        <h3 class="font-semibold text-slate-900">Trust verification</h3>
        <p class="mt-1 text-sm text-slate-500">
          Upload hygiene or food-safety certificates. A moderator reviews your documents and grants the
          Verified badge — no separate request needed.
        </p>
        <div
          v-if="certData?.has_verified_badge"
          class="mt-4 rounded-lg border border-trust-200 bg-trust-50 px-4 py-3 text-sm text-trust-800"
        >
          Your business displays the Verified badge on its public profile.
        </div>
        <div
          v-else-if="pendingCertificationCount"
          class="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
        >
          <p class="font-medium">
            {{ pendingCertificationCount === 1 ? '1 certificate' : `${pendingCertificationCount} certificates` }}
            submitted for review
          </p>
          <p class="mt-1 text-amber-800">
            A moderator will review your upload{{ pendingCertificationCount > 1 ? 's' : '' }} and grant the
            Verified badge if approved. Nothing else is required from you.
          </p>
        </div>
        <p v-if="certError" class="mt-3 text-sm text-red-600">{{ certError }}</p>
        <p v-if="certUploadSuccess" class="mt-3 text-sm text-trust-700">{{ certUploadSuccess }}</p>
        <form class="mt-4 space-y-4" @submit.prevent="submitCertification">
          <div>
            <label class="label">Certificate title</label>
            <input
              v-model="certTitle"
              class="input"
              type="text"
              placeholder="e.g. FSSAI license, health inspection report"
              required
            />
          </div>
          <div>
            <label class="label">Document (PDF or image, max 10 MB)</label>
            <input
              ref="certFileInput"
              class="input"
              type="file"
              accept="image/jpeg,image/png,image/webp,application/pdf"
              @change="onCertFileChange"
            />
          </div>
          <button class="btn-primary" type="submit" :disabled="certSubmitting || !certFile">
            {{ certSubmitting ? 'Uploading…' : 'Upload certification' }}
          </button>
        </form>
        <div v-if="certsPending" class="mt-6 text-sm text-slate-500">Loading certifications...</div>
        <p v-else-if="!certificationList.length" class="mt-6 text-sm text-slate-500">
          No certifications uploaded yet.
        </p>
        <ul v-else class="mt-6 space-y-4">
          <li
            v-for="cert in certificationList"
            :key="cert.id"
            class="flex flex-col gap-2 border-t border-slate-100 pt-4 first:border-0 first:pt-0 sm:flex-row sm:items-center sm:justify-between"
          >
            <div>
              <p class="font-medium text-slate-900">{{ cert.title }}</p>
              <p class="text-xs text-slate-400">{{ formatCertDate(cert.created_at) }}</p>
            </div>
            <div class="flex items-center gap-3">
              <span
                class="rounded-full px-3 py-1 text-xs font-medium capitalize"
                :class="certStatusClass(cert.status)"
              >
                {{ certStatusLabel(cert.status) }}
              </span>
              <a
                :href="cert.file_url"
                target="_blank"
                rel="noopener noreferrer"
                class="text-sm text-trust-600 hover:underline"
              >
                View
              </a>
            </div>
          </li>
        </ul>
      </div>

      <div class="card">
        <h3 class="font-semibold text-slate-900">Score trend</h3>
        <p class="mt-1 text-sm text-slate-500">
          Cumulative trust score by week, based on diner visit dates.
        </p>
        <div v-if="trendPending" class="mt-4 text-sm text-slate-500">Loading trend...</div>
        <p v-else-if="!scoreTrend?.points.length" class="mt-4 text-sm text-slate-500">
          Not enough review history yet. Trends appear after reviews accumulate over time.
        </p>
        <div v-else class="mt-4">
          <div class="flex h-36 items-end gap-1 sm:gap-2">
            <div
              v-for="point in scoreTrend.points"
              :key="point.period_end"
              class="flex min-w-0 flex-1 flex-col items-center gap-1"
            >
              <span class="text-[10px] font-medium text-slate-500">{{ point.overall_percent }}%</span>
              <div
                class="w-full rounded-t bg-trust-500 transition-all"
                :style="{ height: `${Math.max(8, point.overall_percent)}%` }"
                :title="`${point.label}: ${point.overall_percent}% (${point.review_count} reviews)`"
              />
              <span class="w-full truncate text-center text-[10px] text-slate-400">{{ point.label }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="mt-8 space-y-6">
      <div v-if="pendingClaims.length" class="card">
        <h3 class="font-semibold text-slate-900">Claim requests in review</h3>
        <p class="mt-2 text-sm text-slate-500">
          You already submitted a claim. A moderator will review it — no need to submit again.
        </p>
        <ul class="mt-4 space-y-3">
          <li
            v-for="claim in pendingClaims"
            :key="claim.id"
            class="rounded-lg border border-slate-200 p-4"
          >
            <p class="font-medium text-slate-900">
              <NuxtLink
                v-if="claim.business_slug"
                :to="`/business/${claim.business_slug}`"
                class="text-trust-600 hover:underline"
              >
                {{ claim.business_name || `Business #${claim.business_id}` }}
              </NuxtLink>
              <span v-else>Business #{{ claim.business_id }}</span>
            </p>
            <p class="mt-1 text-xs uppercase tracking-wide text-amber-600">{{ claim.status }}</p>
            <p v-if="claim.notes" class="mt-2 text-sm text-slate-600">{{ claim.notes }}</p>
          </li>
        </ul>
      </div>

      <div v-if="pastClaims.length" class="card">
        <h3 class="font-semibold text-slate-900">Previous claim requests</h3>
        <ul class="mt-4 space-y-2 text-sm text-slate-600">
          <li v-for="claim in pastClaims" :key="claim.id">
            {{ claim.business_name || `Business #${claim.business_id}` }} — {{ claim.status }}
          </li>
        </ul>
      </div>

      <div v-if="!pendingClaims.length && canClaimBusiness" id="claim" class="card">
        <h3 class="font-semibold text-slate-900">Claim a business profile</h3>
        <p class="mt-2 text-sm text-slate-500">
          Search by business name, select your listing, then submit a claim for moderator review.
        </p>
        <p v-if="claimError" class="mt-3 text-sm text-red-600">{{ claimError }}</p>
        <form class="mt-4 space-y-4" @submit.prevent="submitClaim">
          <div>
            <label class="label">Business name</label>
            <input
              v-model="claimSearchQuery"
              class="input"
              type="search"
              placeholder="e.g. Green Leaf Kitchen"
              autocomplete="off"
            />
          </div>
          <div>
            <label class="label">City (optional)</label>
            <input
              v-model="claimSearchCity"
              class="input"
              type="text"
              placeholder="e.g. Berlin"
              autocomplete="off"
            />
          </div>
          <p v-if="claimSearchError" class="text-sm text-red-600">{{ claimSearchError }}</p>
          <p v-if="claimSearchPending" class="text-sm text-slate-500">Searching...</p>
          <p
            v-else-if="claimSearchQuery.trim().length >= 2 && !claimSearchResults.length"
            class="text-sm text-slate-500"
          >
            No businesses found. Try a different name or city.
          </p>
          <ul v-else-if="claimSearchResults.length" class="space-y-2">
            <li v-for="business in claimSearchResults" :key="business.id">
              <button
                type="button"
                class="w-full rounded-lg border p-3 text-left transition"
                :class="
                  selectedClaimBusiness?.id === business.id
                    ? 'border-trust-500 bg-trust-50'
                    : 'border-slate-200 hover:border-slate-300'
                "
                :disabled="business.is_claimed"
                @click="selectClaimBusiness(business)"
              >
                <div class="flex items-start justify-between gap-3">
                  <div>
                    <p class="font-medium text-slate-900">{{ business.name }}</p>
                    <p class="mt-1 text-xs text-slate-500">
                      <span v-if="business.city">{{ business.city }}</span>
                      <span v-if="business.city && business.category_name"> · </span>
                      <span v-if="business.category_name">{{ business.category_name }}</span>
                    </p>
                  </div>
                  <span
                    v-if="business.is_claimed"
                    class="shrink-0 rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600"
                  >
                    Already claimed
                  </span>
                </div>
              </button>
            </li>
          </ul>
          <div
            v-if="selectedClaimBusiness"
            class="rounded-lg border border-trust-200 bg-trust-50 px-4 py-3 text-sm text-trust-900"
          >
            Selected:
            <NuxtLink
              :to="`/business/${selectedClaimBusiness.slug}`"
              class="font-medium text-trust-700 hover:underline"
              target="_blank"
            >
              {{ selectedClaimBusiness.name }}
            </NuxtLink>
          </div>
          <div>
            <label class="label">Notes for moderators</label>
            <textarea
              v-model="claimNotes"
              class="input"
              rows="2"
              placeholder="How can we verify you own or manage this place?"
            />
          </div>
          <button
            class="btn-primary"
            type="submit"
            :disabled="claimSubmitting || !selectedClaimBusiness || selectedClaimBusiness.is_claimed"
          >
            {{ claimSubmitting ? 'Submitting…' : 'Submit claim request' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reviewResponseSchema } from '~/utils/schemas'

definePageMeta({ middleware: 'auth' })
useSeoMeta({ title: 'Business Dashboard — BiteScore' })

interface BusinessStats {
  business: { id: number; name: string; slug: string }
  score: { overall_percent: number; breakdown: Record<string, number>; trust_indicators: string[] }
  total_reviews: number
}

interface ScoreTrendPoint {
  period_end: string
  label: string
  overall: number
  overall_percent: number
  review_count: number
}

interface ScoreTrend {
  points: ScoreTrendPoint[]
  weeks: number
}

interface BusinessReview {
  id: number
  user_name: string | null
  visit_date: string
  visit_type: string
  notes: string | null
  business_response: string | null
}

interface Certification {
  id: number
  title: string
  file_url: string
  mime_type: string
  status: 'pending' | 'verified' | 'rejected'
  created_at: string
}

interface CertificationData {
  has_verified_badge: boolean
  certifications: Certification[]
}

interface ClaimSearchResult {
  id: number
  name: string
  slug: string
  city: string | null
  category_name: string | null
  is_claimed: boolean
}

const api = useApi()
const certTitle = ref('')
const certFile = ref<File | null>(null)
const certFileInput = ref<HTMLInputElement | null>(null)
const certError = ref('')
const certUploadSuccess = ref('')
const certSubmitting = ref(false)
const claimNotes = ref('')
const claimError = ref('')
const claimSubmitting = ref(false)
const selectedClaimBusiness = ref<ClaimSearchResult | null>(null)
const description = ref('')
const reviewError = ref('')
const respondingId = ref<number | null>(null)
const responseDrafts = reactive<Record<number, string>>({})

const { account, pending: accountPending, refresh: refreshAccount, hasClaimedBusiness, pendingClaims, canClaimBusiness } =
  useBusinessAccount()

const {
  query: claimSearchQuery,
  city: claimSearchCity,
  results: claimSearchResults,
  searching: claimSearchPending,
  searchError: claimSearchError,
} = useBusinessClaimSearch()

const pastClaims = computed(
  () => account.value?.claims.filter((claim) => claim.status !== 'pending') ?? [],
)

const { data: stats, pending: statsPending } = await useAsyncData<BusinessStats | null>(
  'biz-stats',
  () => {
    if (!hasClaimedBusiness.value) return Promise.resolve(null)
    return api.get('/business-dashboard/stats')
  },
  { watch: [hasClaimedBusiness] },
)

const { data: scoreTrend, pending: trendPending } = await useAsyncData<ScoreTrend | null>(
  'biz-score-trend',
  () => {
    if (!hasClaimedBusiness.value) return Promise.resolve(null)
    return api.get('/business-dashboard/score-trend')
  },
  { watch: [hasClaimedBusiness] },
)

const reviewsSlug = computed(() => stats.value?.business.slug ?? null)

const { data: reviews, pending: reviewsPending, refresh: refreshReviews } = await useAsyncData(
  'biz-reviews',
  () => {
    if (!reviewsSlug.value) return Promise.resolve([] as BusinessReview[])
    return api.get<BusinessReview[]>(`/businesses/${reviewsSlug.value}/reviews`)
  },
  { watch: [reviewsSlug] },
)

const { data: certData, pending: certsPending, refresh: refreshCertifications } =
  await useAsyncData(
    'biz-certifications',
    () => {
      if (!hasClaimedBusiness.value) return Promise.resolve(null)
      return api.get<CertificationData>('/business-dashboard/certifications')
    },
    { watch: [hasClaimedBusiness] },
  )

const certificationList = computed(() => certData.value?.certifications ?? [])

const pendingCertificationCount = computed(
  () => certificationList.value.filter((cert) => cert.status === 'pending').length,
)

watch(
  reviews,
  (items) => {
    for (const review of items ?? []) {
      if (!(review.id in responseDrafts)) {
        responseDrafts[review.id] = review.business_response ?? ''
      }
    }
  },
  { immediate: true },
)

async function submitClaim() {
  if (!selectedClaimBusiness.value || selectedClaimBusiness.value.is_claimed) {
    claimError.value = 'Please select an unclaimed business'
    return
  }

  claimError.value = ''
  claimSubmitting.value = true
  try {
    await api.post('/claims', {
      business_id: selectedClaimBusiness.value.id,
      notes: claimNotes.value,
    })
    selectedClaimBusiness.value = null
    claimSearchQuery.value = ''
    claimNotes.value = ''
    await refreshAccount()
  } catch (e: unknown) {
    claimError.value = e instanceof Error ? e.message : 'Could not submit claim'
  } finally {
    claimSubmitting.value = false
  }
}

function selectClaimBusiness(business: ClaimSearchResult) {
  if (business.is_claimed) return
  selectedClaimBusiness.value = business
  claimError.value = ''
}

async function updateProfile() {
  await api.patch('/business-dashboard/profile', { description: description.value })
  alert('Profile updated.')
}

function onCertFileChange(event: Event) {
  certError.value = ''
  const input = event.target as HTMLInputElement
  const file = input.files?.[0] ?? null
  if (!file) {
    certFile.value = null
    return
  }
  const validationError = validateCertificationFile(file)
  if (validationError) {
    certError.value = validationError
    certFile.value = null
    input.value = ''
    return
  }
  certFile.value = file
}

function certStatusClass(status: Certification['status']) {
  if (status === 'verified') return 'bg-green-100 text-green-700'
  if (status === 'rejected') return 'bg-red-100 text-red-700'
  return 'bg-amber-100 text-amber-700'
}

function certStatusLabel(status: Certification['status']) {
  if (status === 'pending') return 'Awaiting review'
  if (status === 'verified') return 'Approved'
  return 'Rejected'
}

function formatCertDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

async function submitCertification() {
  certError.value = ''
  certUploadSuccess.value = ''
  const trimmed = certTitle.value.trim()
  if (trimmed.length < 3) {
    certError.value = 'Title must be at least 3 characters'
    return
  }
  if (!certFile.value) {
    certError.value = 'Please choose a file to upload'
    return
  }

  certSubmitting.value = true
  try {
    const form = new FormData()
    form.append('title', trimmed)
    form.append('file', certFile.value)
    await api.post('/business-dashboard/certifications', form)
    certTitle.value = ''
    certFile.value = null
    if (certFileInput.value) certFileInput.value.value = ''
    certUploadSuccess.value =
      'Certificate uploaded. A moderator will review it and grant your Verified badge if approved.'
    await refreshCertifications()
  } catch (e: unknown) {
    certError.value = e instanceof Error ? e.message : 'Could not upload certification'
  } finally {
    certSubmitting.value = false
  }
}

async function submitResponse(reviewId: number) {
  reviewError.value = ''
  const parsed = reviewResponseSchema.safeParse({ response: responseDrafts[reviewId] ?? '' })
  if (!parsed.success) {
    reviewError.value = parsed.error.errors[0]?.message || 'Please check your response'
    return
  }

  respondingId.value = reviewId
  try {
    await api.patch(`/business-dashboard/reviews/${reviewId}/respond`, parsed.data)
    await refreshReviews()
  } catch (e: unknown) {
    reviewError.value = e instanceof Error ? e.message : 'Could not post response'
  } finally {
    respondingId.value = null
  }
}
</script>
