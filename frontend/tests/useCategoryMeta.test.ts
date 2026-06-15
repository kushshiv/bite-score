import { describe, expect, it } from 'vitest'
import { CATEGORIES, useCategoryMeta } from '../composables/useCategoryMeta'

describe('useCategoryMeta', () => {
  it('returns metadata for a known category slug', () => {
    const meta = useCategoryMeta('indian')
    expect(meta.label).toBe('Indian')
    expect(meta.emoji).toBe('🍛')
    expect(meta.gradient).toContain('orange')
  })

  it('returns defaults for unknown categories', () => {
    const meta = useCategoryMeta('unknown-category')
    expect(meta.label).toBe('Restaurant')
    expect(meta.emoji).toBe('🍽️')
    expect(meta.slug).toBe('default')
  })

  it('includes all discovery categories', () => {
    expect(CATEGORIES.map((c) => c.slug)).toEqual([
      'indian',
      'italian',
      'street-food',
      'healthy',
      'cafe',
      'bakery',
      'asian-fusion',
      'mexican',
      'mediterranean',
      'fast-casual',
    ])
  })
})
