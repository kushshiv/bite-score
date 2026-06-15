<template>
  <div class="discover-theme min-h-screen bg-surface">
    <slot />
    <AuthModal />
  </div>
</template>

<script setup lang="ts">
onMounted(() => document.body.classList.add('discover-theme'))
onUnmounted(() => document.body.classList.remove('discover-theme'))
</script>
