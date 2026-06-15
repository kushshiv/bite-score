export interface UserLocation {
  city: string
  country: string
  lat: number
  lng: number
  label: string
  source: 'manual' | 'gps'
}

export const LOCATION_CITIES: UserLocation[] = [
  { city: 'Berlin', country: 'Germany', lat: 52.52, lng: 13.405, label: 'Berlin, Germany', source: 'manual' },
  { city: 'Mumbai', country: 'India', lat: 19.076, lng: 72.8777, label: 'Mumbai, India', source: 'manual' },
  { city: 'Austin', country: 'USA', lat: 30.2672, lng: -97.7431, label: 'Austin, USA', source: 'manual' },
]

const STORAGE_KEY = 'bitescore-location'

export function buildBusinessParams(
  location: UserLocation,
  extra: Record<string, string | number | boolean | undefined> = {},
) {
  const params: Record<string, string> = {
    near_lat: String(location.lat),
    near_lng: String(location.lng),
  }
  if (location.source === 'manual') {
    params.city = location.city
  }
  for (const [key, value] of Object.entries(extra)) {
    if (value !== undefined && value !== false && value !== '') {
      params[key] = String(value)
    }
  }
  return params
}

export function useUserLocation() {
  const location = useState<UserLocation>('user-location', () => ({ ...LOCATION_CITIES[0] }))
  const detecting = ref(false)
  const detectError = ref<string | null>(null)

  function persist(next: UserLocation) {
    location.value = next
    if (import.meta.client) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
    }
  }

  function setCity(cityName: string) {
    const match = LOCATION_CITIES.find((c) => c.city === cityName)
    if (match) persist({ ...match, source: 'manual' })
  }

  function detectLocation() {
    if (!import.meta.client || !navigator.geolocation) {
      detectError.value = 'Location is not available in this browser.'
      return
    }
    detecting.value = true
    detectError.value = null
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords
        const nearest = LOCATION_CITIES.reduce((best, city) => {
          const d = Math.hypot(city.lat - latitude, city.lng - longitude)
          return d < best.dist ? { city, dist: d } : best
        }, { city: LOCATION_CITIES[0], dist: Infinity }).city
        persist({
          city: nearest.city,
          country: nearest.country,
          lat: latitude,
          lng: longitude,
          label: 'Near you',
          source: 'gps',
        })
        detecting.value = false
      },
      () => {
        detectError.value = 'Could not get your location. Pick a city instead.'
        detecting.value = false
      },
      { enableHighAccuracy: false, timeout: 10000 },
    )
  }

  function businessParams(extra: Record<string, string | number | boolean | undefined> = {}) {
    return buildBusinessParams(location.value, extra)
  }

  onMounted(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      try {
        location.value = JSON.parse(saved)
      } catch {
        /* ignore */
      }
    }
  })

  return { location, detecting, detectError, setCity, detectLocation, businessParams, cities: LOCATION_CITIES }
}
