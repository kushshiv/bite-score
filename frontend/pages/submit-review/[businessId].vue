<template>
  <div class="mx-auto max-w-2xl px-4 py-10 sm:px-6">
    <h1 class="text-2xl font-bold text-slate-900">Submit a structured observation</h1>
    <p class="mt-2 text-sm text-slate-500">
      Focus on hygiene, food handling, and safety — not taste opinions. Use neutral, factual language.
    </p>

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

      <div class="card space-y-3">
        <label class="flex items-start gap-2 text-sm">
          <input v-model="form.consent_given" type="checkbox" class="mt-1 accent-trust-600" required />
          <span>
            I confirm this observation is based on my personal experience and reported honestly. I understand BiteScore is a community platform, not a government certification body.
          </span>
        </label>
        <p class="text-xs text-slate-400">
          Photo upload consent: By uploading images, you grant BiteScore permission to display them for moderation and trust verification purposes.
        </p>
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

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const api = useApi()
const businessId = Number(route.params.businessId)
const loading = ref(false)
const error = ref('')

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

async function submit() {
  error.value = ''
  const parsed = reviewSchema.safeParse(form)
  if (!parsed.success) {
    error.value = parsed.error.errors[0]?.message || 'Validation failed'
    return
  }

  loading.value = true
  try {
    await api.post('/reviews', {
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
    navigateTo('/dashboard')
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Submission failed'
  } finally {
    loading.value = false
  }
}
</script>
