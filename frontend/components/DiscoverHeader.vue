<template>
  <header class="sticky top-0 z-50 border-b border-surface-border bg-surface">
    <div class="mx-auto flex max-w-[1400px] items-center gap-3 px-4 py-3 lg:px-6">
      <NuxtLink to="/" class="flex shrink-0 items-center gap-2">
        <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-trust-600 text-sm font-bold text-white">BS</div>
        <span class="hidden text-lg font-bold text-discover-fg sm:block">BiteScore</span>
      </NuxtLink>

      <button
        class="mx-auto flex max-w-md flex-1 items-center gap-2 rounded-full border border-surface-border bg-surface-raised px-4 py-2.5 text-left transition hover:border-discover-muted"
        @click="showPicker = true"
      >
        <span class="text-trust-400">📍</span>
        <span class="min-w-0 truncate text-sm text-discover-fg">{{ location.label }}</span>
        <span class="ml-auto text-discover-muted">▾</span>
      </button>

      <div class="flex shrink-0 items-center gap-2">
        <ThemeToggle />
        <button
          class="hidden rounded-full border border-surface-border px-3 py-2 text-xs font-medium text-discover-secondary transition hover:bg-surface-hover sm:block"
          :disabled="detecting"
          @click="detectLocation"
        >
          {{ detecting ? 'Locating…' : 'Near me' }}
        </button>
        <template v-if="auth.isLoggedIn">
          <NuxtLink to="/add-place" class="btn-discover-ghost hidden sm:inline-flex">Add a place</NuxtLink>
          <NuxtLink to="/dashboard" class="btn-discover-ghost hidden sm:inline-flex">My reviews</NuxtLink>
          <button class="btn-discover-ghost text-xs" @click="auth.logout()">Logout</button>
        </template>
        <template v-else>
          <button class="btn-discover-ghost text-xs" @click="openAuth('login')">Sign in</button>
        </template>
      </div>
    </div>

    <!-- Location modal -->
    <div
      v-if="showPicker"
      class="fixed inset-0 z-[60] flex items-end justify-center bg-black/60 p-4 sm:items-center"
      @click.self="showPicker = false"
    >
      <div class="w-full max-w-md rounded-2xl border border-surface-border bg-surface-raised p-5 shadow-2xl">
        <h3 class="text-lg font-semibold text-discover-fg">Where are you eating?</h3>
        <p class="mt-1 text-sm text-discover-muted">We'll show restaurants and vendors near you.</p>
        <ul class="mt-4 space-y-2">
          <li v-for="city in cities" :key="city.city">
            <button
              class="flex w-full items-center gap-3 rounded-xl border px-4 py-3 text-left transition"
              :class="location.city === city.city ? 'border-trust-500 bg-trust-600/10 text-discover-fg' : 'border-surface-border text-discover-secondary hover:border-discover-muted'"
              @click="pickCity(city.city)"
            >
              <span>📍</span>
              <span class="font-medium">{{ city.label }}</span>
            </button>
          </li>
        </ul>
        <button class="mt-4 w-full rounded-full border border-surface-border py-2.5 text-sm text-discover-muted transition hover:text-discover-fg" @click="showPicker = false">
          Cancel
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
const auth = useAuthStore()
const { open: openAuth } = useAuthModal()
const { location, detecting, setCity, detectLocation, cities } = useUserLocation()
const showPicker = ref(false)

function pickCity(city: string) {
  setCity(city)
  showPicker.value = false
}
</script>
