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

export function useCategoryMeta(slug?: string | null) {
  const meta = CATEGORIES.find((c) => c.slug === slug)
  return meta ?? { slug: 'default', label: 'Restaurant', emoji: '🍽️', gradient: 'from-slate-100 to-slate-50' }
}
