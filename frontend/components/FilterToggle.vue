<template>
  <button type="button" class="flex w-full items-center justify-between gap-3" @click="emit('toggle')">
    <span class="text-sm text-discover-secondary">{{ label }}</span>
    <span class="toggle-pill" :class="{ active }" role="switch" :aria-checked="active">
      <span class="toggle-pill-knob" />
    </span>
  </button>
</template>

<script setup lang="ts">
defineProps<{ label: string; active: boolean }>()
const emit = defineEmits<{ toggle: [] }>()
</script>
