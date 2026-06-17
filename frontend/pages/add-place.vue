<template>
  <div class="mx-auto max-w-xl px-4 py-8 lg:px-6">
    <NuxtLink to="/" class="text-sm text-gray-400 transition hover:text-white">← Back to discover</NuxtLink>

    <h1 class="mt-4 text-2xl font-bold text-white">Add a missing place</h1>
    <p class="mt-2 text-sm text-gray-400">
      Can't find a restaurant or vendor? Add it so you and others can leave hygiene observations.
    </p>

    <form
      class="mt-8 space-y-5 rounded-2xl border border-surface-border bg-surface-raised p-6 text-slate-900"
      @submit.prevent="submit"
    >
      <div>
        <label class="label">Place name</label>
        <input v-model="form.name" class="input" placeholder="e.g. Joe's Taco Stand" required />
      </div>

      <div>
        <label class="label">Address (optional)</label>
        <input v-model="form.address" class="input" placeholder="Street address or landmark" />
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <div>
          <label class="label">City</label>
          <input v-model="form.city" class="input" required />
        </div>
        <div>
          <label class="label">Country</label>
          <input v-model="form.country" class="input" required />
        </div>
      </div>

      <div>
        <label class="label">Cuisine / category</label>
        <select v-model="form.category" class="input" required>
          <option v-for="cat in CATEGORIES" :key="cat.slug" :value="cat.slug">
            {{ cat.emoji }} {{ cat.label }}
          </option>
        </select>
      </div>

      <div>
        <label class="label">Type of place</label>
        <select v-model="form.business_type" class="input" required>
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
        <label class="label">Notes (optional)</label>
        <textarea
          v-model="form.description"
          class="input"
          rows="2"
          placeholder="Anything helpful for others finding this place"
        />
      </div>

      <p v-if="error" class="text-sm text-red-500">{{ error }}</p>

      <button type="submit" class="btn-primary w-full" :disabled="loading">
        {{ loading ? 'Adding place…' : 'Add place & write a review' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { addPlaceSchema } from '~/utils/schemas'
import { CATEGORIES } from '~/composables/useCategoryMeta'

definePageMeta({ layout: 'discover', middleware: 'auth' })

const api = useApi()
const { location } = useUserLocation()
const loading = ref(false)
const error = ref('')

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

async function submit() {
  error.value = ''
  const parsed = addPlaceSchema.safeParse(form)
  if (!parsed.success) {
    error.value = parsed.error.errors[0]?.message || 'Please check the form'
    return
  }

  loading.value = true
  try {
    const business = await api.post<{ id: number; slug: string }>('/businesses', {
      name: parsed.data.name,
      address: parsed.data.address || null,
      city: parsed.data.city,
      country: parsed.data.country,
      category: parsed.data.category,
      business_type: parsed.data.business_type,
      description: parsed.data.description || null,
      latitude: location.value.lat,
      longitude: location.value.lng,
    })
    await navigateTo(`/submit-review/${business.id}`)
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Could not add this place'
  } finally {
    loading.value = false
  }
}
</script>
