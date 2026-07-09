<template>
  <div class="mx-auto max-w-xl px-4 py-8 lg:px-6">
    <NuxtLink to="/" class="text-sm text-discover-muted transition hover:text-discover-fg">← Back to discover</NuxtLink>

    <h1 class="mt-4 text-2xl font-bold text-discover-fg">Add a missing place</h1>
    <p class="mt-2 text-sm text-discover-muted">
      Can't find a restaurant or vendor? Add it so you and others can leave hygiene observations.
      New listings are reviewed by a moderator before they appear publicly.
    </p>

    <form
      class="card-dark mt-8 space-y-5 p-6"
      @submit.prevent="submit"
    >
      <div>
        <label class="label-discover">Place name</label>
        <input v-model="form.name" class="input-dark" placeholder="e.g. Joe's Taco Stand" required />
      </div>

      <div>
        <label class="label-discover">Address (optional)</label>
        <input v-model="form.address" class="input-dark" placeholder="Street address or landmark" />
        <p class="mt-1 text-xs text-discover-muted">We'll look up the exact location from the address when possible.</p>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <div>
          <label class="label-discover">City</label>
          <input v-model="form.city" class="input-dark" required />
        </div>
        <div>
          <label class="label-discover">Country</label>
          <input v-model="form.country" class="input-dark" required />
        </div>
      </div>

      <div class="rounded-xl border border-surface-border bg-surface p-4">
        <p class="text-sm text-discover-secondary">At the place right now?</p>
        <button
          type="button"
          class="btn-discover-ghost mt-2"
          :disabled="detecting"
          @click="useCurrentLocation"
        >
          {{ detecting ? 'Getting location…' : gpsCoords ? '✓ Using your current location' : 'Use my current location' }}
        </button>
        <p v-if="locationError" class="mt-2 text-xs text-red-400">{{ locationError }}</p>
        <p v-else-if="gpsCoords" class="mt-2 text-xs text-discover-muted">
          GPS pin saved as fallback if address lookup fails.
        </p>
      </div>

      <div>
        <label class="label-discover">Cuisine / category</label>
        <select v-model="form.category" class="input-dark" required>
          <option v-for="cat in CATEGORIES" :key="cat.slug" :value="cat.slug">
            {{ cat.emoji }} {{ cat.label }}
          </option>
        </select>
      </div>

      <div>
        <label class="label-discover">Type of place</label>
        <select v-model="form.business_type" class="input-dark" required>
          <option value="restaurant">Restaurant</option>
          <option value="street_vendor">Street vendor</option>
          <option value="cafe">Café</option>
          <option value="food_court">Food court stall</option>
          <option value="bakery">Bakery</option>
          <option value="cloud_kitchen">Cloud kitchen</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div>
        <label class="label-discover">Notes (optional)</label>
        <textarea
          v-model="form.description"
          class="input-dark"
          rows="2"
          placeholder="Anything helpful for others finding this place"
        />
      </div>

      <div v-if="duplicateConflict" class="rounded-xl border border-amber-500/40 bg-amber-500/10 p-4">
        <p class="text-sm text-amber-200">{{ duplicateConflict.message }}</p>
        <ul class="mt-3 space-y-2">
          <li v-for="match in duplicateConflict.matches" :key="match.id">
            <NuxtLink
              :to="`/business/${match.slug}`"
              class="text-sm text-discover-fg underline decoration-discover-muted underline-offset-2 hover:decoration-discover-fg"
            >
              {{ match.name }}
            </NuxtLink>
            <span class="ml-2 text-xs text-discover-muted">
              {{ Math.round(match.similarity * 100) }}% similar
            </span>
          </li>
        </ul>
        <label v-if="duplicateConflict.allow_confirm" class="mt-4 flex items-start gap-2 text-sm text-discover-secondary">
          <input v-model="confirmSimilar" type="checkbox" class="mt-1" />
          <span>This is a different place — add it for review even though the name is similar.</span>
        </label>
      </div>

      <p v-if="error" class="text-sm text-red-500">{{ error }}</p>

      <button type="submit" class="btn-primary w-full" :disabled="loading">
        {{
          loading
            ? 'Adding place…'
            : duplicateConflict?.allow_confirm && confirmSimilar
              ? 'Add anyway for review'
              : 'Add place for review'
        }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ApiError, useApi } from '~/composables/useApi'
import { addPlaceSchema } from '~/utils/schemas'
import { CATEGORIES } from '~/composables/useCategoryMeta'

definePageMeta({ layout: 'discover', middleware: 'auth' })

interface SimilarBusinessMatch {
  id: number
  name: string
  slug: string
  similarity: number
  match_type: string
}

interface DuplicateBusinessErrorDetail {
  message: string
  matches: SimilarBusinessMatch[]
  allow_confirm: boolean
}

const api = useApi()
const { location } = useUserLocation()
const loading = ref(false)
const error = ref('')
const detecting = ref(false)
const locationError = ref('')
const gpsCoords = ref<{ lat: number; lng: number } | null>(null)
const duplicateConflict = ref<DuplicateBusinessErrorDetail | null>(null)
const confirmSimilar = ref(false)

const form = reactive({
  name: '',
  address: '',
  city: location.value.city,
  country: location.value.country,
  category: CATEGORIES[0].slug,
  business_type: 'restaurant' as const,
  description: '',
})

useSeoMeta({
  title: 'Add a place — BiteScore',
  description: 'Add a missing restaurant or food vendor so the community can review hygiene and safety.',
})

function useCurrentLocation() {
  if (!import.meta.client || !navigator.geolocation) {
    locationError.value = 'Location is not available in this browser.'
    return
  }
  detecting.value = true
  locationError.value = ''
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      gpsCoords.value = {
        lat: pos.coords.latitude,
        lng: pos.coords.longitude,
      }
      detecting.value = false
    },
    () => {
      locationError.value = 'Could not get your location. Try adding an address instead.'
      detecting.value = false
    },
    { enableHighAccuracy: true, timeout: 10000 },
  )
}

async function submit() {
  error.value = ''
  duplicateConflict.value = null
  const parsed = addPlaceSchema.safeParse(form)
  if (!parsed.success) {
    error.value = parsed.error.errors[0]?.message || 'Please check the form'
    return
  }

  loading.value = true
  try {
    const payload: Record<string, unknown> = {
      name: parsed.data.name,
      address: parsed.data.address || null,
      city: parsed.data.city,
      country: parsed.data.country,
      category: parsed.data.category,
      business_type: parsed.data.business_type,
      description: parsed.data.description || null,
    }
    if (gpsCoords.value) {
      payload.latitude = gpsCoords.value.lat
      payload.longitude = gpsCoords.value.lng
    }
    if (confirmSimilar.value) {
      payload.acknowledge_similar = true
    }

    const business = await api.post<{ id: number; slug: string; status: string }>('/businesses', payload)
    await navigateTo(`/submit-review/${business.id}?place_pending=1`)
  } catch (e: unknown) {
    if (e instanceof ApiError && e.status === 409 && isDuplicateDetail(e.detail)) {
      duplicateConflict.value = e.detail
      if (!e.detail.allow_confirm) {
        error.value = e.message
      }
      return
    }
    error.value = e instanceof Error ? e.message : 'Could not add this place'
  } finally {
    loading.value = false
  }
}

function isDuplicateDetail(detail: unknown): detail is DuplicateBusinessErrorDetail {
  if (typeof detail !== 'object' || detail === null) return false
  const candidate = detail as DuplicateBusinessErrorDetail
  return (
    typeof candidate.message === 'string' &&
    Array.isArray(candidate.matches) &&
    typeof candidate.allow_confirm === 'boolean'
  )
}
</script>
