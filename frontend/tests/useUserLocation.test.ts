import { describe, expect, it } from 'vitest'
import { buildBusinessParams, LOCATION_CITIES } from '../composables/useUserLocation'

describe('buildBusinessParams', () => {
  it('includes city when location was picked manually', () => {
    const params = buildBusinessParams(LOCATION_CITIES[0], { sort: 'nearby', limit: 8 })
    expect(params).toEqual({
      near_lat: '52.52',
      near_lng: '13.405',
      city: 'Berlin',
      sort: 'nearby',
      limit: '8',
    })
  })

  it('omits city when location comes from gps', () => {
    const params = buildBusinessParams({
      ...LOCATION_CITIES[0],
      lat: 52.53,
      lng: 13.41,
      label: 'Near you',
      source: 'gps',
    })
    expect(params.city).toBeUndefined()
    expect(params.near_lat).toBe('52.53')
    expect(params.near_lng).toBe('13.41')
  })

  it('skips empty and false filter values', () => {
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
  it('includes supported discovery cities', () => {
    expect(LOCATION_CITIES.map((c) => c.city)).toEqual(['Berlin', 'Mumbai', 'Austin'])
  })
})
