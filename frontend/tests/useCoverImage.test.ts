import { describe, expect, it } from 'vitest'
import { businessCoverUrl } from '../composables/useCoverImage'
import { CATEGORY_COVER_IMAGES, DEFAULT_COVER_IMAGE } from '../composables/useCategoryMeta'

describe('businessCoverUrl', () => {
  it('prefers explicit business cover image', () => {
    const url = 'https://cdn.example.com/kitchen.jpg'
    expect(businessCoverUrl({ cover_image_url: url })).toBe(url)
  })

  it('falls back to category stock photo', () => {
    expect(businessCoverUrl({ category: { slug: 'indian' } })).toBe(CATEGORY_COVER_IMAGES.indian)
    expect(businessCoverUrl({ category: { slug: 'street-food' } })).toBe(CATEGORY_COVER_IMAGES['street-food'])
  })

  it('uses default image when no cover or category match', () => {
    expect(businessCoverUrl({})).toBe(DEFAULT_COVER_IMAGE)
    expect(businessCoverUrl({ category: { slug: 'unknown' } })).toBe(DEFAULT_COVER_IMAGE)
  })
})
