<template>
  <div class="discover-theme min-h-screen bg-surface" :data-theme="theme">
    <slot />
    <AuthModal />
  </div>
</template>

<script setup lang="ts">
const { theme, init } = useDiscoverTheme()

onMounted(() => {
  document.body.classList.add('discover-theme')
  init()
})

onUnmounted(() => {
  document.body.classList.remove('discover-theme')
  document.body.removeAttribute('data-theme')
})
</script>
