<template>
  <div class="mx-auto max-w-2xl px-4 py-10 sm:px-6">
    <h1 class="text-2xl font-bold text-slate-900">Submit a structured observation</h1>
    <p class="mt-2 text-sm text-slate-500">
      Focus on hygiene, food handling, and safety — not taste opinions. Use neutral, factual language.
    </p>

    <div
      v-if="route.query.place_pending === '1'"
      class="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      Thanks for adding this place. A moderator will review it before it appears on discover.
      You can still submit your observation now — it will be published after the place is approved.
    </div>

    <form class="mt-8 space-y-6" @submit.prevent="submit">
      <div class="card space-y-4">
        <div>
          <label class="label">Visit type</label>
          <select v-model="form.visit_type" class="input">
            <option value="dine_in">Dine in</option>
            <option value="takeaway">Takeaway</option>
            <option value="delivery">Delivery</option>
          </select>
        </div>
        <div>
          <label class="label">Date of visit</label>
          <input v-model="form.visit_date" class="input" type="date" required />
        </div>
        <div>
          <label class="label">Notes (optional)</label>
          <textarea v-model="form.notes" class="input" rows="3" placeholder="Community observation in neutral language..." />
        </div>
      </div>

      <div class="card space-y-5">
        <h2 class="font-semibold text-slate-900">Structured scores (1–5)</h2>
        <ScoreSlider v-model="form.cleanliness" label="Cleanliness" />
        <ScoreSlider v-model="form.staff_hygiene" label="Staff hygiene" />
        <ScoreSlider v-model="form.food_handling" label="Food handling" />
        <ScoreSlider v-model="form.packaging" label="Packaging safety" />
        <ScoreSlider v-model="form.water_confidence" label="Water safety confidence" />
        <label class="flex items-center gap-2 text-sm">
          <input v-model="form.oil_freshness_concern" type="checkbox" class="accent-caution-500" />
          Reported concern about oil reuse / freshness
        </label>
        <ScoreSlider v-model="form.taste_optional" label="Taste (optional, secondary)" />
      </div>

      <div class="card space-y-4">
        <h2 class="font-semibold text-slate-900">Photo evidence (optional)</h2>
        <p class="text-sm text-slate-500">
          Photos of cleanliness, packaging, or food handling can strengthen your observation. Up to {{ EVIDENCE_MAX_FILES }} images, 5 MB each.
        </p>

        <div v-if="photos.length" class="grid grid-cols-2 gap-3 sm:grid-cols-3">
          <div v-for="photo in photos" :key="photo.id" class="relative">
            <img
              :src="photo.previewUrl"
              class="h-28 w-full rounded-lg border border-slate-200 object-cover"
              alt="Selected evidence preview"
            />
            <button
              type="button"
              class="absolute right-1 top-1 rounded-full bg-slate-900/70 px-2 py-0.5 text-xs text-white hover:bg-slate-900"
              @click="removePhoto(photo.id)"
            >
              Remove
            </button>
          </div>
        </div>

        <input
          ref="fileInput"
          type="file"
          accept="image/jpeg,image/png,image/webp"
          multiple
          class="hidden"
          @change="onFilesSelected"
        />
        <button
          type="button"
          class="btn-secondary w-full sm:w-auto"
          :disabled="photos.length >= EVIDENCE_MAX_FILES"
          @click="fileInput?.click()"
        >
          {{ photos.length ? 'Add more photos' : 'Add photos' }}
        </button>
        <p v-if="photoError" class="text-sm text-red-600">{{ photoError }}</p>

        <label v-if="photos.length" class="flex items-start gap-2 text-sm text-slate-600">
          <input v-model="photoConsent" type="checkbox" class="mt-1 accent-trust-600" />
          <span>
            I consent to BiteScore displaying these photos for moderation and trust verification purposes.
          </span>
        </label>
      </div>

      <div class="card space-y-3">
        <label class="flex items-start gap-2 text-sm">
          <input v-model="form.consent_given" type="checkbox" class="mt-1 accent-trust-600" required />
          <span>
            I confirm this observation is based on my personal experience and reported honestly. I understand BiteScore is a community platform, not a government certification body.
          </span>
        </label>
      </div>

      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
      <button class="btn-primary w-full" type="submit" :disabled="loading">
        {{ loading ? 'Submitting...' : 'Submit observation' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { reviewSchema } from '~/utils/schemas'
import {
  EVIDENCE_MAX_FILES,
  remainingEvidenceSlots,
  validateEvidenceFile,
} from '~/composables/useReviewEvidence'

definePageMeta({ middleware: 'auth' })

interface ReviewResponse {
  id: number
}

interface SelectedPhoto {
  id: string
  file: File
  previewUrl: string
}

const route = useRoute()
const api = useApi()
const businessId = Number(route.params.businessId)
const loading = ref(false)
const error = ref('')
const photoError = ref('')
const photoConsent = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const photos = ref<SelectedPhoto[]>([])

const form = reactive({
  visit_type: 'dine_in' as 'dine_in' | 'takeaway' | 'delivery',
  visit_date: new Date().toISOString().split('T')[0],
  notes: '',
  consent_given: false,
  cleanliness: 4,
  staff_hygiene: 4,
  food_handling: 4,
  packaging: 4,
  water_confidence: 4,
  oil_freshness_concern: false,
  taste_optional: 4,
})

useSeoMeta({ title: 'Submit Review — BiteScore' })

onBeforeUnmount(() => {
  for (const photo of photos.value) {
    URL.revokeObjectURL(photo.previewUrl)
  }
})

function onFilesSelected(event: Event) {
  photoError.value = ''
  const input = event.target as HTMLInputElement
  const files = Array.from(input.files ?? [])
  input.value = ''

  if (!files.length) return

  const slots = remainingEvidenceSlots(photos.value.length)
  if (slots === 0) {
    photoError.value = `You can attach up to ${EVIDENCE_MAX_FILES} photos`
    return
  }

  const accepted: SelectedPhoto[] = []
  for (const file of files.slice(0, slots)) {
    const validationError = validateEvidenceFile(file)
    if (validationError) {
      photoError.value = validationError
      continue
    }
    accepted.push({
      id: crypto.randomUUID(),
      file,
      previewUrl: URL.createObjectURL(file),
    })
  }

  if (!accepted.length && !photoError.value) {
    photoError.value = 'No valid images were selected'
    return
  }

  photos.value.push(...accepted)
}

function removePhoto(id: string) {
  const index = photos.value.findIndex((photo) => photo.id === id)
  if (index === -1) return
  URL.revokeObjectURL(photos.value[index].previewUrl)
  photos.value.splice(index, 1)
  photoError.value = ''
}

async function uploadReviewEvidence(reviewId: number) {
  const results = await Promise.allSettled(
    photos.value.map(async (photo) => {
      const formData = new FormData()
      formData.append('file', photo.file)
      formData.append('review_id', String(reviewId))
      formData.append('business_id', String(businessId))
      await api.post('/uploads', formData)
    }),
  )

  const failed = results.filter((result) => result.status === 'rejected').length
  if (failed > 0) {
    throw new Error(
      failed === photos.value.length
        ? 'Review saved, but photos could not be uploaded. Try again from your dashboard.'
        : `Review saved, but ${failed} of ${photos.value.length} photos failed to upload.`,
    )
  }
}

async function submit() {
  error.value = ''
  photoError.value = ''

  if (photos.value.length && !photoConsent.value) {
    photoError.value = 'Please confirm photo upload consent before submitting'
    return
  }

  const parsed = reviewSchema.safeParse(form)
  if (!parsed.success) {
    error.value = parsed.error.errors[0]?.message || 'Validation failed'
    return
  }

  loading.value = true
  try {
    const review = await api.post<ReviewResponse>('/reviews', {
      business_id: businessId,
      visit_type: form.visit_type,
      visit_date: form.visit_date,
      notes: form.notes || null,
      consent_given: true,
      structured_score: {
        cleanliness: form.cleanliness,
        staff_hygiene: form.staff_hygiene,
        food_handling: form.food_handling,
        packaging: form.packaging,
        water_confidence: form.water_confidence,
        oil_freshness_concern: form.oil_freshness_concern,
        taste_optional: form.taste_optional,
      },
    })

    if (photos.value.length) {
      await uploadReviewEvidence(review.id)
    }

    await navigateTo('/dashboard?submitted=1')
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Submission failed'
  } finally {
    loading.value = false
  }
}
</script>
