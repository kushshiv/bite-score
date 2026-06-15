export interface CategoryMeta {
  slug: string
  label: string
  emoji: string
  gradient: string
}

export const CATEGORIES: CategoryMeta[] = [
  { slug: 'indian', label: 'Indian', emoji: '🍛', gradient: 'from-orange-100 to-amber-50' },
  { slug: 'italian', label: 'Italian', emoji: '🍝', gradient: 'from-red-100 to-rose-50' },
  { slug: 'street-food', label: 'Street food', emoji: '🌮', gradient: 'from-yellow-100 to-amber-50' },
  { slug: 'healthy', label: 'Healthy', emoji: '🥗', gradient: 'from-green-100 to-emerald-50' },
  { slug: 'cafe', label: 'Cafés', emoji: '☕', gradient: 'from-amber-100 to-orange-50' },
  { slug: 'bakery', label: 'Bakery', emoji: '🥐', gradient: 'from-yellow-50 to-orange-100' },
  { slug: 'asian-fusion', label: 'Asian', emoji: '🍜', gradient: 'from-pink-100 to-red-50' },
  { slug: 'mexican', label: 'Mexican', emoji: '🌯', gradient: 'from-lime-100 to-green-50' },
  { slug: 'mediterranean', label: 'Mediterranean', emoji: '🫒', gradient: 'from-teal-100 to-cyan-50' },
  { slug: 'fast-casual', label: 'Fast casual', emoji: '🍔', gradient: 'from-orange-50 to-yellow-100' },
]

export const CATEGORY_COVER_IMAGES: Record<string, string> = {
  indian: 'https://images.unsplash.com/photo-1585937421612-70a008296f36?w=800&h=500&fit=crop',
  italian: 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800&h=500&fit=crop',
  'street-food': 'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7440?w=800&h=500&fit=crop',
  healthy: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&h=500&fit=crop',
  cafe: 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&h=500&fit=crop',
  bakery: 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800&h=500&fit=crop',
  'asian-fusion': 'https://images.unsplash.com/photo-1569718211065-1ea9108a2bda?w=800&h=500&fit=crop',
  mexican: 'https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=800&h=500&fit=crop',
  mediterranean: 'https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=800&h=500&fit=crop',
  'fast-casual': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800&h=500&fit=crop',
}

export const DEFAULT_COVER_IMAGE = 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&h=500&fit=crop'

export function useCategoryMeta(slug?: string | null) {
  const meta = CATEGORIES.find((c) => c.slug === slug)
  return meta ?? { slug: 'default', label: 'Restaurant', emoji: '🍽️', gradient: 'from-slate-100 to-slate-50' }
}
