export type DiscoverTheme = 'dark' | 'light'

export const DISCOVER_THEME_STORAGE_KEY = 'bitescore-discover-theme'

export function nextDiscoverTheme(current: DiscoverTheme): DiscoverTheme {
  return current === 'dark' ? 'light' : 'dark'
}

export function parseStoredDiscoverTheme(saved: string | null): DiscoverTheme | null {
  if (saved === 'light' || saved === 'dark') return saved
  return null
}

export function useDiscoverTheme() {
  const theme = useState<DiscoverTheme>('discover-theme', () => 'dark')

  function apply(next: DiscoverTheme) {
    theme.value = next
    if (!import.meta.client) return
    localStorage.setItem(DISCOVER_THEME_STORAGE_KEY, next)
    document.body.setAttribute('data-theme', next)
  }

  function toggle() {
    apply(nextDiscoverTheme(theme.value))
  }

  function init() {
    if (!import.meta.client) return
    const saved = parseStoredDiscoverTheme(localStorage.getItem(DISCOVER_THEME_STORAGE_KEY))
    apply(saved ?? 'dark')
  }

  const isDark = computed(() => theme.value === 'dark')

  return { theme, isDark, toggle, init, apply }
}
