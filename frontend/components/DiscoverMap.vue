<template>
  <ClientOnly>
    <div ref="mapEl" class="h-[min(70vh,600px)] w-full overflow-hidden rounded-2xl border border-surface-border" />
    <template #fallback>
      <div class="flex h-64 items-center justify-center rounded-2xl border border-surface-border bg-surface-raised text-gray-500">
        Loading map...
      </div>
    </template>
  </ClientOnly>
</template>

<script setup lang="ts">
const props = defineProps<{
  businesses: Array<{
    slug: string
    name: string
    overall_percent: number
    location?: { latitude?: number | null; longitude?: number | null } | null
  }>
  center: { lat: number; lng: number }
  selectedSlug?: string | null
}>()

const emit = defineEmits<{ select: [slug: string] }>()

const mapEl = ref<HTMLElement | null>(null)
let mapInstance: import('leaflet').Map | null = null
let markersLayer: import('leaflet').LayerGroup | null = null

function scoreColor(score: number) {
  if (score >= 80) return '#16a34a'
  if (score >= 60) return '#f59e0b'
  return '#6b7280'
}

async function initMap() {
  if (!mapEl.value || !import.meta.client) return
  const L = await import('leaflet')
  await import('leaflet/dist/leaflet.css')

  if (mapInstance) {
    mapInstance.remove()
    mapInstance = null
  }

  mapInstance = L.map(mapEl.value, { zoomControl: true }).setView([props.center.lat, props.center.lng], 13)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap',
    maxZoom: 19,
  }).addTo(mapInstance)

  markersLayer = L.layerGroup().addTo(mapInstance)
  updateMarkers(L)
}

function updateMarkers(L: typeof import('leaflet')) {
  if (!mapInstance || !markersLayer) return
  markersLayer.clearLayers()

  const points: [number, number][] = []
  for (const b of props.businesses) {
    const lat = b.location?.latitude
    const lng = b.location?.longitude
    if (lat == null || lng == null) continue
    points.push([lat, lng])

    const isSelected = props.selectedSlug === b.slug
    const icon = L.divIcon({
      className: '',
      html: `<div style="background:${scoreColor(b.overall_percent)};color:white;font-weight:700;font-size:11px;width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;border:2px solid ${isSelected ? '#fff' : 'transparent'};box-shadow:0 2px 8px rgba(0,0,0,.4)">${Math.round(b.overall_percent)}</div>`,
      iconSize: [32, 32],
      iconAnchor: [16, 16],
    })
    const marker = L.marker([lat, lng], { icon })
    marker.bindPopup(`<strong>${b.name}</strong><br>Score: ${Math.round(b.overall_percent)}`)
    marker.on('click', () => emit('select', b.slug))
    marker.addTo(markersLayer)
  }

  if (points.length > 1) {
    mapInstance.fitBounds(points, { padding: [40, 40], maxZoom: 14 })
  } else if (points.length === 1) {
    mapInstance.setView(points[0], 14)
  }
}

watch(
  () => [props.businesses, props.selectedSlug, props.center],
  async () => {
    if (!mapInstance) {
      await initMap()
    } else {
      const L = await import('leaflet')
      updateMarkers(L)
    }
  },
  { deep: true },
)

onMounted(initMap)
onUnmounted(() => {
  mapInstance?.remove()
  mapInstance = null
})
</script>
