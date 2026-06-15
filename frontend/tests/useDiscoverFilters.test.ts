import { describe, expect, it } from 'vitest'
import {
  buildFacetParams,
  categoryFacetCount,
  filterSafeResults,
  filtersFromRoute,
  filtersToQuery,
  type BusinessFacets,
} from '../composables/useDiscoverFilters'
import { LOCATION_CITIES } from '../composables/useUserLocation'

describe('filtersFromRoute', () => {
  it('parses all discover query params', () => {
    expect(
      filtersFromRoute({
        q: 'pizza',
        category: 'italian',
        high_trust: 'true',
        verified_only: 'true',
        safe_only: 'true',
        sort: 'score',
      }),
    ).toEqual({
      q: 'pizza',
      category: 'italian',
      high_trust: true,
      verified_only: true,
      safe_only: true,
      sort: 'score',
    })
  })

  it('defaults to nearby browse state', () => {
    expect(filtersFromRoute({})).toEqual({
      q: '',
      category: '',
      high_trust: false,
      verified_only: false,
      safe_only: false,
      sort: 'nearby',
    })
  })
})

describe('filtersToQuery', () => {
  it('serializes only active filters', () => {
    expect(
      filtersToQuery({
        q: 'sushi',
        category: 'asian-fusion',
        high_trust: true,
        verified_only: false,
        safe_only: true,
        sort: 'score',
      }),
    ).toEqual({
      q: 'sushi',
      category: 'asian-fusion',
      high_trust: 'true',
      safe_only: 'true',
      sort: 'score',
    })
  })

  it('round-trips through filtersFromRoute', () => {
    const original = {
      q: 'tacos',
      category: 'mexican',
      high_trust: true,
      verified_only: true,
      safe_only: false,
      sort: 'score' as const,
    }
    const query = filtersToQuery(original)
    expect(filtersFromRoute(query)).toEqual(original)
  })
})

describe('buildFacetParams', () => {
  it('builds geo params for manual city selection', () => {
    const params = new URLSearchParams(buildFacetParams(LOCATION_CITIES[0], 'ramen'))
    expect(params.get('city')).toBe('Berlin')
    expect(params.get('near_lat')).toBe('52.52')
    expect(params.get('near_lng')).toBe('13.405')
    expect(params.get('q')).toBe('ramen')
  })

  it('omits empty search text', () => {
    const params = new URLSearchParams(buildFacetParams(LOCATION_CITIES[1], ''))
    expect(params.get('q')).toBeNull()
    expect(params.get('city')).toBe('Mumbai')
  })
})

describe('filterSafeResults', () => {
  const items = [
    { slug: 'a', overall_percent: 90 },
    { slug: 'b', overall_percent: 70 },
    { slug: 'c', overall_percent: 85 },
  ]

  it('returns all results when safe filter is off', () => {
    expect(filterSafeResults(items, false)).toEqual(items)
  })

  it('keeps only 80+ scores when safe filter is on', () => {
    expect(filterSafeResults(items, true)).toEqual([
      { slug: 'a', overall_percent: 90 },
      { slug: 'c', overall_percent: 85 },
    ])
  })
})

describe('categoryFacetCount', () => {
  const facets: BusinessFacets = {
    total: 5,
    high_trust: 2,
    verified: 1,
    safe_to_eat: 2,
    categories: [
      { slug: 'indian', name: 'Indian', count: 3 },
      { slug: 'cafe', name: 'Cafés', count: 2 },
    ],
  }

  it('returns count for known cuisine', () => {
    expect(categoryFacetCount(facets, 'indian')).toBe(3)
    expect(categoryFacetCount(facets, 'cafe')).toBe(2)
  })

  it('returns zero for missing cuisine or facets', () => {
    expect(categoryFacetCount(facets, 'mexican')).toBe(0)
    expect(categoryFacetCount(null, 'indian')).toBe(0)
  })
})
