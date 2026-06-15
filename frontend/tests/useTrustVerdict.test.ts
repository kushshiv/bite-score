import { describe, expect, it } from 'vitest'
import { useTrustVerdict } from '../composables/useTrustVerdict'

describe('useTrustVerdict', () => {
  it('returns safe verdict for high scores', () => {
    const verdict = useTrustVerdict(85)
    expect(verdict.label).toBe('Safe to eat')
    expect(verdict.shortLabel).toBe('Safe')
  })

  it('returns caution verdict for mid scores', () => {
    const verdict = useTrustVerdict(70)
    expect(verdict.label).toBe('Use caution')
    expect(verdict.shortLabel).toBe('Caution')
  })

  it('returns low confidence for poor scores', () => {
    const verdict = useTrustVerdict(40)
    expect(verdict.label).toBe('Low confidence')
    expect(verdict.shortLabel).toBe('Low')
  })

  it('returns new verdict when there are no reviews', () => {
    const verdict = useTrustVerdict(0)
    expect(verdict.label).toBe('Not enough reviews')
    expect(verdict.shortLabel).toBe('New')
  })
})
