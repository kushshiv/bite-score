<template>
  <header class="sticky top-0 z-50 border-b border-slate-200 bg-white/90 backdrop-blur">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6">
      <NuxtLink to="/" class="flex items-center gap-2">
        <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-trust-600 text-sm font-bold text-white">BS</div>
        <span class="text-lg font-semibold text-slate-900">BiteScore</span>
      </NuxtLink>

      <nav class="hidden items-center gap-6 md:flex">
        <NuxtLink to="/search" class="text-sm text-slate-600 hover:text-slate-900">Search</NuxtLink>
        <NuxtLink to="/how-it-works" class="text-sm text-slate-600 hover:text-slate-900">How it works</NuxtLink>
        <NuxtLink to="/about" class="text-sm text-slate-600 hover:text-slate-900">About</NuxtLink>
      </nav>

      <div class="flex items-center gap-3">
        <template v-if="auth.isLoggedIn">
          <NuxtLink to="/dashboard" class="text-sm text-slate-600 hover:text-slate-900">Dashboard</NuxtLink>
          <NuxtLink v-if="auth.isBusinessOwner" to="/business-dashboard" class="text-sm text-slate-600 hover:text-slate-900">Business</NuxtLink>
          <NuxtLink v-if="auth.isModerator" to="/admin" class="text-sm text-slate-600 hover:text-slate-900">Admin</NuxtLink>
          <button class="text-sm text-slate-500 hover:text-slate-700" @click="auth.logout()">Logout</button>
        </template>
        <template v-else>
          <button class="btn-secondary" @click="openAuth('login')">Sign in</button>
          <button class="btn-primary" @click="openAuth('register')">Get started</button>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
const auth = useAuthStore()
const { open: openAuth } = useAuthModal()
</script>
