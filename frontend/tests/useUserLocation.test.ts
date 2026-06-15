import { describe, expect, it } from 'vitest'
import { buildBusinessParams, LOCATION_CITIES } from '../composables/useUserLocation'

describe('buildBusinessParams', () => {
  it('includes city for manual location picks', () => {
    expect(buildBusinessParams(LOCATION_CITIES[0], { sort: 'nearby', limit: 40 })).toEqual({
      near_lat: '52.52',
      near_lng: '13.405',
      city: 'Berlin',
      sort: 'nearby',
      limit: '40',
    })
  })

  it('omits city for gps-based near me', () => {
    const params = buildBusinessParams({
      ...LOCATION_CITIES[0],
      lat: 52.531,
      lng: 13.412,
      label: 'Near you',
      source: 'gps',
    })
    expect(params.city).toBeUndefined()
    expect(params.near_lat).toBe('52.531')
    expect(params.near_lng).toBe('13.412')
  })

  it('passes discover list filters to the API', () => {
    const params = buildBusinessParams(LOCATION_CITIES[2], {
      q: 'bbq',
      category: 'fast-casual',
      high_trust: true,
      verified_only: true,
      sort: 'score',
      limit: 40,
    })
    expect(params).toEqual({
      near_lat: '30.2672',
      near_lng: '-97.7431',
      city: 'Austin',
      q: 'bbq',
      category: 'fast-casual',
      high_trust: 'true',
      verified_only: 'true',
      sort: 'score',
      limit: '40',
    })
  })

  it('skips empty and false values', () => {
    const params = buildBusinessParams(LOCATION_CITIES[1], {
      q: '',
      high_trust: false,
      verified_only: true,
    })
    expect(params.city).toBe('Mumbai')
    expect(params).not.toHaveProperty('q')
    expect(params).not.toHaveProperty('high_trust')
    expect(params.verified_only).toBe('true')
  })
})

describe('LOCATION_CITIES', () => {
  it('includes supported discovery cities with coordinates', () => {
    expect(LOCATION_CITIES).toEqual([
      expect.objectContaining({ city: 'Berlin', country: 'Germany', lat: 52.52, lng: 13.405 }),
      expect.objectContaining({ city: 'Mumbai', country: 'India', lat: 19.076, lng: 72.8777 }),
      expect.objectContaining({ city: 'Austin', country: 'USA', lat: 30.2672, lng: -97.7431 }),
    ])
  })
})
