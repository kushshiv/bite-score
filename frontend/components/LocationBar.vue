<template>
  <div class="sticky top-[57px] z-40 border-b border-slate-200 bg-white shadow-sm">
    <div class="mx-auto max-w-7xl px-4 py-3 sm:px-6">
      <!-- Location row -->
      <div class="flex items-center gap-2">
        <button
          class="flex min-w-0 flex-1 items-center gap-2 rounded-xl border border-slate-200 px-3 py-2.5 text-left transition hover:border-trust-500 hover:bg-trust-50/50"
          @click="showPicker = true"
        >
          <span class="text-lg" aria-hidden="true">📍</span>
          <span class="min-w-0">
            <span class="block text-xs text-slate-500">Eating in</span>
            <span class="block truncate text-sm font-semibold text-slate-900">{{ location.label }}</span>
          </span>
          <span class="ml-auto text-slate-400">▾</span>
        </button>
        <button
          class="shrink-0 rounded-xl border border-slate-200 px-3 py-2.5 text-sm font-medium text-slate-700 transition hover:border-trust-500 hover:bg-trust-50"
          :disabled="detecting"
          @click="detectLocation"
        >
          {{ detecting ? '...' : 'Near me' }}
        </button>
      </div>
      <p v-if="detectError" class="mt-2 text-xs text-amber-700">{{ detectError }}</p>

      <!-- Search row -->
      <form class="mt-3 flex gap-2" @submit.prevent="submitSearch">
        <div class="relative flex-1">
          <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">🔍</span>
          <input
            v-model="query"
            class="input w-full py-2.5 pl-9"
            placeholder="Search restaurant or vendor..."
            type="search"
          />
        </div>
        <button class="btn-primary shrink-0 px-5" type="submit">Search</button>
      </form>
    </div>

    <!-- Location picker modal -->
    <div
      v-if="showPicker"
      class="fixed inset-0 z-50 flex items-end justify-center bg-black/40 p-4 sm:items-center"
      @click.self="showPicker = false"
    >
      <div class="w-full max-w-md rounded-2xl bg-white p-5 shadow-xl">
        <h3 class="text-lg font-semibold text-slate-900">Where are you eating?</h3>
        <p class="mt-1 text-sm text-slate-500">We'll show restaurants and vendors near you.</p>
        <ul class="mt-4 space-y-2">
          <li v-for="city in cities" :key="city.city">
            <button
              class="flex w-full items-center gap-3 rounded-xl border px-4 py-3 text-left transition hover:border-trust-500 hover:bg-trust-50"
              :class="location.city === city.city ? 'border-trust-500 bg-trust-50' : 'border-slate-200'"
              @click="pickCity(city.city)"
            >
              <span class="text-xl">📍</span>
              <span class="font-medium text-slate-900">{{ city.label }}</span>
            </button>
          </li>
        </ul>
        <button class="btn-secondary mt-4 w-full" @click="showPicker = false">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const { location, detecting, detectError, setCity, detectLocation, cities } = useUserLocation()
const route = useRoute()

const showPicker = ref(false)
const query = ref((route.query.q as string) || '')

watch(() => route.query.q, (q) => {
  query.value = (q as string) || ''
})

function pickCity(city: string) {
  setCity(city)
  showPicker.value = false
}

function submitSearch() {
  navigateTo({ path: '/search', query: { q: query.value || undefined } })
}
</script>
