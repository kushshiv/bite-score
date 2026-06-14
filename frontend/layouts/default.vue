<template>
  <div class="min-h-screen flex flex-col">
    <AppHeader />
    <main class="flex-1">
      <slot />
    </main>
    <AppFooter />
    <AuthModal />
  </div>
</template>

<script setup lang="ts">
const auth = useAuthStore()
onMounted(() => auth.init())
</script>
