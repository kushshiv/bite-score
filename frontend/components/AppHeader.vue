<template>
  <header class="sticky top-0 z-50 border-b border-slate-200 bg-white">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
      <NuxtLink to="/" class="flex items-center gap-2">
        <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-trust-600 text-sm font-bold text-white">BS</div>
        <span class="text-lg font-bold text-slate-900">BiteScore</span>
      </NuxtLink>

      <div class="flex items-center gap-2 sm:gap-3">
        <template v-if="auth.isLoggedIn">
          <NuxtLink to="/dashboard" class="hidden text-sm text-slate-600 hover:text-slate-900 sm:block">My reviews</NuxtLink>
          <button class="text-sm text-slate-500 hover:text-slate-700" @click="auth.logout()">Logout</button>
        </template>
        <template v-else>
          <button class="hidden text-sm text-slate-600 hover:text-slate-900 sm:block" @click="openAuth('login')">Sign in</button>
        </template>
        <NuxtLink to="/search" class="btn-primary text-sm">Search</NuxtLink>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
const auth = useAuthStore()
const { open: openAuth } = useAuthModal()
</script>
