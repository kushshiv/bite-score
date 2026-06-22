<template>
  <div class="flex flex-col gap-4 sm:flex-row sm:items-center">
    <form class="relative flex-1" @submit.prevent="submit">
      <span class="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-discover-muted">🔍</span>
      <input
        v-model="query"
        class="input-dark w-full py-3 pl-11 pr-4"
        placeholder="Search restaurant or vendor..."
        type="search"
      />
    </form>

    <div class="flex shrink-0 items-center gap-2">
      <div class="relative">
        <select
          :value="sort"
          class="appearance-none rounded-full border border-surface-border bg-surface-raised py-3 pl-4 pr-10 text-sm text-discover-fg focus:border-trust-500 focus:outline-none"
          @change="onSort(($event.target as HTMLSelectElement).value)"
        >
          <option value="nearby">Sort: Best match</option>
          <option value="score">Sort: Top rated</option>
        </select>
        <span class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-discover-muted">▾</span>
      </div>
      <button
        type="button"
        class="flex h-11 w-11 items-center justify-center rounded-full border text-lg transition"
        :class="viewMode === 'map' ? 'border-trust-500 bg-trust-600/20 text-trust-400' : 'border-surface-border bg-surface-raised text-discover-muted hover:border-discover-muted hover:text-discover-fg'"
        title="Toggle map view"
        @click="toggleView"
      >
        🗺️
      </button>
      <button
        type="button"
        class="flex h-11 w-11 items-center justify-center rounded-full border text-lg transition"
        :class="viewMode === 'list' ? 'border-trust-500 bg-trust-600/20 text-trust-400' : 'border-surface-border bg-surface-raised text-discover-muted hover:border-discover-muted hover:text-discover-fg'"
        title="List view"
        @click="emit('update:viewMode', 'list')"
      >
        ☰
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ modelValue: string; sort: string; viewMode: 'list' | 'map' }>()
const emit = defineEmits<{
  'update:modelValue': [value: string]
  search: []
  'update:sort': [value: string]
  'update:viewMode': [value: 'list' | 'map']
}>()

const query = ref(props.modelValue)

watch(() => props.modelValue, (v) => { query.value = v })

function submit() {
  emit('update:modelValue', query.value)
  emit('search')
}

function onSort(value: string) {
  emit('update:sort', value)
}

function toggleView() {
  emit('update:viewMode', props.viewMode === 'map' ? 'list' : 'map')
}
</script>
