<template>
  <div class="mx-auto max-w-6xl px-4 py-10 sm:px-6">
    <h1 class="text-2xl font-bold text-slate-900">Admin & moderation</h1>
    <p class="mt-2 text-slate-500">Review queue, flag handling, claim approvals, evidence verification, and badge assignment.</p>

    <div v-if="pending" class="mt-8 text-slate-500">Loading...</div>
    <div v-else class="mt-8 grid gap-6 lg:grid-cols-3">
      <div class="card">
        <h3 class="font-semibold text-slate-900">Pending reviews</h3>
        <p class="mt-2 text-3xl font-bold text-trust-600">{{ queue?.pending_reviews || 0 }}</p>
        <ul class="mt-4 space-y-2 text-sm text-slate-600">
          <li v-for="r in queue?.reviews" :key="r.id" class="rounded-lg border border-slate-100 p-3">
            <div class="flex items-start justify-between gap-2">
              <div>
                <span class="font-medium text-slate-900">Review #{{ r.id }}</span>
                <span class="ml-2 text-xs text-slate-400">Business #{{ r.business_id }}</span>
                <p v-if="r.notes" class="mt-1 text-slate-600">{{ r.notes }}</p>
              </div>
              <button class="shrink-0 text-trust-600 hover:underline" @click="moderate('review', r.id, 'approve')">
                Approve
              </button>
            </div>
          </li>
        </ul>
      </div>

      <div class="card">
        <h3 class="font-semibold text-slate-900">Open flags</h3>
        <ul class="mt-4 space-y-3 text-sm">
          <li v-for="f in queue?.open_flags" :key="f.id" class="border-b border-slate-100 pb-2">
            <p class="text-slate-700">{{ f.reason }}</p>
            <div class="mt-1 flex gap-2">
              <button class="text-trust-600 hover:underline" @click="moderate('flag', f.id, 'resolve')">Resolve</button>
              <button class="text-slate-500 hover:underline" @click="moderate('flag', f.id, 'dismiss')">Dismiss</button>
            </div>
          </li>
        </ul>
      </div>

      <div class="card">
        <h3 class="font-semibold text-slate-900">Pending claims</h3>
        <ul class="mt-4 space-y-3 text-sm">
          <li v-for="c in queue?.pending_claims" :key="c.id" class="flex justify-between">
            <span>Business #{{ c.business_id }}</span>
            <div class="flex gap-2">
              <button class="text-trust-600 hover:underline" @click="moderate('claim', c.id, 'approve')">Approve</button>
              <button class="text-slate-500 hover:underline" @click="moderate('claim', c.id, 'reject')">Reject</button>
            </div>
          </li>
        </ul>
      </div>
    </div>

    <div v-if="!pending" class="mt-8 card">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <h3 class="font-semibold text-slate-900">Photo evidence to verify</h3>
        <p class="text-sm text-slate-500">{{ queue?.pending_evidence || 0 }} pending</p>
      </div>
      <p v-if="evidenceError" class="mt-3 text-sm text-red-600">{{ evidenceError }}</p>
      <p v-if="!queue?.evidence?.length" class="mt-4 text-sm text-slate-500">
        No unverified photo evidence right now.
      </p>
      <div v-else class="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="item in queue.evidence"
          :key="item.id"
          class="overflow-hidden rounded-xl border border-slate-200"
        >
          <img
            :src="item.file_url"
            class="h-44 w-full object-cover"
            :alt="`Evidence for ${item.business_name || 'business'}`"
          />
          <div class="space-y-2 p-3">
            <p class="text-sm font-medium text-slate-900">
              <NuxtLink
                v-if="item.business_slug"
                :to="`/business/${item.business_slug}`"
                class="text-trust-600 hover:underline"
              >
                {{ item.business_name }}
              </NuxtLink>
              <span v-else>Business #{{ item.business_id }}</span>
            </p>
            <p v-if="item.review_id" class="text-xs text-slate-500">Review #{{ item.review_id }}</p>
            <button
              class="btn-primary w-full"
              type="button"
              :disabled="verifyingId === item.id"
              @click="verifyEvidence(item.id)"
            >
              {{ verifyingId === item.id ? 'Verifying…' : 'Verify photo' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-8 card">
      <h3 class="font-semibold text-slate-900">Assign badge</h3>
      <form class="mt-4 flex flex-wrap gap-4" @submit.prevent="assignBadge">
        <input v-model="badgeForm.business_id" class="input w-32" type="number" placeholder="Business ID" />
        <select v-model="badgeForm.badge_type" class="input w-48">
          <option value="verified">Verified</option>
          <option value="high_confidence">High confidence</option>
          <option value="under_review">Under review</option>
        </select>
        <button class="btn-primary" type="submit">Assign</button>
      </form>
    </div>

    <div class="mt-8 card">
      <h3 class="font-semibold text-slate-900">AI moderation stub</h3>
      <p class="mt-2 text-sm text-slate-500">Placeholder for future AI-assisted risk scoring.</p>
      <button class="btn-secondary mt-4" @click="runAiStub">Run risk scan (stub)</button>
      <p v-if="aiResult" class="mt-3 text-sm text-slate-600">{{ aiResult }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'admin' })
useSeoMeta({ title: 'Admin — BiteScore' })

interface EvidenceModerationItem {
  id: number
  file_url: string
  mime_type: string
  verified: boolean
  review_id: number | null
  business_id: number | null
  business_name: string | null
  business_slug: string | null
  created_at: string
}

interface ModerationQueue {
  pending_reviews: number
  pending_evidence: number
  reviews: { id: number; business_id: number; notes: string | null }[]
  open_flags: { id: number; target_type: string; reason: string }[]
  pending_claims: { id: number; business_id: number }[]
  evidence: EvidenceModerationItem[]
}

const api = useApi()
const aiResult = ref('')
const evidenceError = ref('')
const verifyingId = ref<number | null>(null)
const badgeForm = reactive({ business_id: '', badge_type: 'verified' })

const { data: queue, pending, refresh } = await useAsyncData<ModerationQueue>(
  'mod-queue',
  () => api.get('/admin/moderation-queue'),
)

async function moderate(target_type: string, target_id: number, action: string) {
  await api.post('/admin/moderate', { action, target_type, target_id })
  refresh()
}

async function verifyEvidence(uploadId: number) {
  evidenceError.value = ''
  verifyingId.value = uploadId
  try {
    await api.patch(`/uploads/${uploadId}/verify`)
    await refresh()
  } catch (e: unknown) {
    evidenceError.value = e instanceof Error ? e.message : 'Could not verify photo'
  } finally {
    verifyingId.value = null
  }
}

async function assignBadge() {
  await api.post('/admin/badges', {
    business_id: Number(badgeForm.business_id),
    badge_type: badgeForm.badge_type,
  })
  alert('Badge assigned.')
}

function runAiStub() {
  aiResult.value = 'Risk scan complete. 2 items flagged for manual review (stub — no AI connected in MVP).'
}
</script>
