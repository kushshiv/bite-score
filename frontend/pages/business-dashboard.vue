<template>
  <div class="mx-auto max-w-5xl px-4 py-10 sm:px-6">
    <h1 class="text-2xl font-bold text-slate-900">Business dashboard</h1>
    <p class="mt-2 text-slate-500">Manage your claimed profile, respond to observations, and track your trust score.</p>

    <div v-if="pending" class="mt-8 text-slate-500">Loading...</div>
    <div v-else-if="!stats" class="mt-8 card">
      <p class="text-slate-600">No claimed business found. Submit a claim to manage a profile.</p>
      <form class="mt-6 space-y-4" @submit.prevent="submitClaim">
        <div>
          <label class="label">Business ID to claim</label>
          <input v-model="claimBusinessId" class="input" type="number" placeholder="e.g. 3" />
        </div>
        <div>
          <label class="label">Notes</label>
          <textarea v-model="claimNotes" class="input" rows="2" placeholder="Verification details..." />
        </div>
        <button class="btn-primary" type="submit">Submit claim request</button>
      </form>
    </div>
    <div v-else class="mt-8 space-y-8">
      <div class="card">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 class="text-xl font-semibold text-slate-900">{{ stats.business.name }}</h2>
            <NuxtLink :to="`/business/${stats.business.slug}`" class="text-sm text-trust-600 hover:underline">View public profile</NuxtLink>
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
        <h3 class="font-semibold text-slate-900">Edit profile</h3>
        <form class="mt-4 space-y-4" @submit.prevent="updateProfile">
          <div>
            <label class="label">Description</label>
            <textarea v-model="description" class="input" rows="3" />
          </div>
          <button class="btn-primary" type="submit">Save</button>
        </form>
      </div>

      <!-- Simple trend chart -->
      <div class="card">
        <h3 class="font-semibold text-slate-900">Score trend (illustrative)</h3>
        <div class="mt-4 flex items-end gap-2 h-32">
          <div
            v-for="(bar, i) in trendBars"
            :key="i"
            class="flex-1 rounded-t bg-trust-500 transition-all"
            :style="{ height: `${bar}%` }"
            :title="`Week ${i + 1}`"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useSeoMeta({ title: 'Business Dashboard — BiteScore' })

const api = useApi()
const claimBusinessId = ref('')
const claimNotes = ref('')
const description = ref('')

const { data: stats, pending, refresh } = await useAsyncData('biz-stats', () =>
  api.get('/business-dashboard/stats').catch(() => null)
)

const trendBars = computed(() => {
  const base = stats.value?.score?.overall_percent || 50
  return Array.from({ length: 8 }, (_, i) => Math.min(100, base - 10 + i * 3 + Math.random() * 5))
})

async function submitClaim() {
  await api.post('/claims', { business_id: Number(claimBusinessId.value), notes: claimNotes.value })
  alert('Claim submitted for review.')
}

async function updateProfile() {
  await api.patch('/business-dashboard/profile', { description: description.value })
  alert('Profile updated.')
}
</script>
