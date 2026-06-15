import { describe, expect, it } from 'vitest'
import {
  CATEGORIES,
  CATEGORY_COVER_IMAGES,
  DEFAULT_COVER_IMAGE,
  useCategoryMeta,
} from '../composables/useCategoryMeta'

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

  it('includes all discovery cuisines used in the UI', () => {
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

  it('maps every cuisine to a stock cover photo', () => {
    for (const category of CATEGORIES) {
      expect(CATEGORY_COVER_IMAGES[category.slug]).toMatch(/^https:\/\//)
    }
    expect(DEFAULT_COVER_IMAGE).toMatch(/^https:\/\//)
  })
})
