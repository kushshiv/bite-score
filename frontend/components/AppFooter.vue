<template>
  <footer class="border-t border-slate-200 bg-white">
    <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6">
      <div class="grid gap-8 md:grid-cols-4">
        <div>
          <div class="flex items-center gap-2">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-trust-600 text-sm font-bold text-white">BS</div>
            <span class="font-semibold text-slate-900">BiteScore</span>
          </div>
          <p class="mt-3 text-sm text-slate-500">
            Know before you eat — find safe restaurants and street food near you.
          </p>
        </div>
        <div>
          <h4 class="text-sm font-semibold text-slate-900">Explore</h4>
          <ul class="mt-3 space-y-2 text-sm text-slate-500">
            <li><NuxtLink to="/search">Search places</NuxtLink></li>
            <li><NuxtLink to="/how-it-works">How scoring works</NuxtLink></li>
            <li><NuxtLink to="/about">About</NuxtLink></li>
          </ul>
        </div>
        <div>
          <h4 class="text-sm font-semibold text-slate-900">Legal</h4>
          <ul class="mt-3 space-y-2 text-sm text-slate-500">
            <li><NuxtLink to="/terms">Terms of Service</NuxtLink></li>
            <li><NuxtLink to="/privacy">Privacy Policy</NuxtLink></li>
            <li><NuxtLink to="/moderation">Moderation Policy</NuxtLink></li>
          </ul>
        </div>
        <div>
          <h4 class="text-sm font-semibold text-slate-900">Restaurant owners</h4>
          <p class="mt-3 text-sm text-slate-500">
            <NuxtLink to="/account" class="text-trust-600 hover:text-trust-700">Business owners</NuxtLink>
            can claim a profile and respond to reviews.
          </p>
        </div>
      </div>
      <p class="mt-8 border-t border-slate-100 pt-8 text-center text-xs text-slate-400">
        Scores are based on diner reviews, not government inspections.
      </p>
    </div>
  </footer>
</template>
