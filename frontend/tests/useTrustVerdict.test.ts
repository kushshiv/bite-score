import { describe, expect, it } from 'vitest'
import { useTrustVerdict } from '../composables/useTrustVerdict'

describe('useTrustVerdict', () => {
  it('marks 80+ as safe to eat', () => {
    expect(useTrustVerdict(80).label).toBe('Safe to eat')
    expect(useTrustVerdict(100).shortLabel).toBe('Safe')
  })

  it('marks 60-79 as caution', () => {
    expect(useTrustVerdict(60).label).toBe('Use caution')
    expect(useTrustVerdict(79).shortLabel).toBe('Caution')
  })

  it('marks 1-59 as low confidence', () => {
    expect(useTrustVerdict(1).label).toBe('Low confidence')
    expect(useTrustVerdict(59).shortLabel).toBe('Low')
  })

  it('marks zero score as not enough reviews', () => {
    expect(useTrustVerdict(0).label).toBe('Not enough reviews')
    expect(useTrustVerdict(0).shortLabel).toBe('New')
  })
})
