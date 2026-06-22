<template>
  <button
    type="button"
    class="flex h-9 w-9 items-center justify-center rounded-full border border-surface-border text-base transition hover:bg-surface-hover"
    :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
    :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
    @click="toggle"
  >
    <span aria-hidden="true">{{ isDark ? '☀️' : '🌙' }}</span>
  </button>
</template>

<script setup lang="ts">
const { isDark, toggle } = useDiscoverTheme()
</script>
