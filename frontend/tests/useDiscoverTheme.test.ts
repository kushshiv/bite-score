import { describe, expect, it } from 'vitest'
import {
  DISCOVER_THEME_STORAGE_KEY,
  nextDiscoverTheme,
  parseStoredDiscoverTheme,
} from '../composables/useDiscoverTheme'

describe('nextDiscoverTheme', () => {
  it('switches dark to light', () => {
    expect(nextDiscoverTheme('dark')).toBe('light')
  })

  it('switches light to dark', () => {
    expect(nextDiscoverTheme('light')).toBe('dark')
  })

  it('toggles back and forth', () => {
    expect(nextDiscoverTheme(nextDiscoverTheme('dark'))).toBe('dark')
  })
})

describe('parseStoredDiscoverTheme', () => {
  it('accepts saved dark and light values', () => {
    expect(parseStoredDiscoverTheme('dark')).toBe('dark')
    expect(parseStoredDiscoverTheme('light')).toBe('light')
  })

  it('rejects missing or invalid stored values', () => {
    expect(parseStoredDiscoverTheme(null)).toBeNull()
    expect(parseStoredDiscoverTheme('')).toBeNull()
    expect(parseStoredDiscoverTheme('system')).toBeNull()
  })
})

describe('DISCOVER_THEME_STORAGE_KEY', () => {
  it('uses a stable localStorage key', () => {
    expect(DISCOVER_THEME_STORAGE_KEY).toBe('bitescore-discover-theme')
  })
})
