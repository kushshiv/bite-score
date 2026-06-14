<template>
  <div>
    <label class="label">{{ label }}</label>
    <div class="flex items-center gap-3">
      <input
        type="range"
        min="1"
        max="5"
        step="0.5"
        :value="modelValue"
        class="flex-1 accent-trust-600"
        @input="$emit('update:modelValue', Number(($event.target as HTMLInputElement).value))"
      />
      <span class="w-8 text-center text-sm font-semibold text-trust-700">{{ modelValue }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ label: string; modelValue: number }>()
defineEmits<{ 'update:modelValue': [value: number] }>()
</script>
