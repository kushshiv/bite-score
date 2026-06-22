export type DiscoverTheme = 'dark' | 'light'

const STORAGE_KEY = 'bitescore-discover-theme'

export function useDiscoverTheme() {
  const theme = useState<DiscoverTheme>('discover-theme', () => 'dark')

  function apply(next: DiscoverTheme) {
    theme.value = next
    if (!import.meta.client) return
    localStorage.setItem(STORAGE_KEY, next)
    document.body.setAttribute('data-theme', next)
  }

  function toggle() {
    apply(theme.value === 'dark' ? 'light' : 'dark')
  }

  function init() {
    if (!import.meta.client) return
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved === 'light' || saved === 'dark') {
      apply(saved)
      return
    }
    apply('dark')
  }

  const isDark = computed(() => theme.value === 'dark')

  return { theme, isDark, toggle, init, apply }
}
