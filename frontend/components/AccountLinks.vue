<template>
  <template v-if="auth.isLoggedIn">
    <NuxtLink
      v-if="auth.isModerator"
      to="/admin"
      :class="linkClass"
    >
      Moderation
    </NuxtLink>
    <NuxtLink to="/account" :class="linkClass">Account</NuxtLink>
    <NuxtLink
      v-if="showBusinessDashboardLink"
      to="/business-dashboard"
      :class="linkClass"
    >
      {{ hasClaimedBusiness ? 'My business' : 'Business' }}
    </NuxtLink>
    <NuxtLink
      v-else-if="showClaimProfileLink"
      to="/business-dashboard#claim"
      :class="linkClass"
    >
      Claim a profile
    </NuxtLink>
  </template>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    linkClass?: string
  }>(),
  {
    linkClass: 'hidden text-sm text-slate-600 hover:text-slate-900 sm:block',
  },
)

const auth = useAuthStore()
const { hasClaimedBusiness, showBusinessDashboardLink, showClaimProfileLink } = useBusinessAccount()
</script>
