import { CATEGORY_COVER_IMAGES, DEFAULT_COVER_IMAGE } from './useCategoryMeta'

export function businessCoverUrl(business: {
  cover_image_url?: string | null
  category?: { slug?: string } | null
}): string {
  if (business.cover_image_url) return business.cover_image_url
  const slug = business.category?.slug
  if (slug && slug in CATEGORY_COVER_IMAGES) return CATEGORY_COVER_IMAGES[slug]
  return DEFAULT_COVER_IMAGE
}
