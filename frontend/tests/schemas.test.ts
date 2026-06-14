import { describe, expect, it } from 'vitest'
import { flagSchema, loginSchema, registerSchema, reviewSchema } from '../utils/schemas'

describe('loginSchema', () => {
  it('accepts valid credentials', () => {
    const result = loginSchema.safeParse({
      email: 'user@bitescore.demo',
      password: 'Demo1234!',
    })
    expect(result.success).toBe(true)
  })

  it('rejects invalid email', () => {
    const result = loginSchema.safeParse({
      email: 'not-an-email',
      password: 'Demo1234!',
    })
    expect(result.success).toBe(false)
  })

  it('rejects short password', () => {
    const result = loginSchema.safeParse({
      email: 'user@bitescore.demo',
      password: 'short',
    })
    expect(result.success).toBe(false)
  })
})

describe('registerSchema', () => {
  it('accepts optional full name', () => {
    const result = registerSchema.safeParse({
      email: 'new@bitescore.demo',
      password: 'Demo1234!',
      full_name: 'New User',
    })
    expect(result.success).toBe(true)
  })
})

describe('reviewSchema', () => {
  const validReview = {
    visit_type: 'dine_in' as const,
    visit_date: '2026-02-01',
    notes: 'Clean area observed.',
    consent_given: true,
    cleanliness: 4,
    staff_hygiene: 4,
    food_handling: 4,
    packaging: 4,
    water_confidence: 4,
    oil_freshness_concern: false,
  }

  it('accepts a valid structured review', () => {
    const result = reviewSchema.safeParse(validReview)
    expect(result.success).toBe(true)
  })

  it('requires consent', () => {
    const result = reviewSchema.safeParse({ ...validReview, consent_given: false })
    expect(result.success).toBe(false)
  })

  it('rejects scores outside 1-5 range', () => {
    const result = reviewSchema.safeParse({ ...validReview, cleanliness: 6 })
    expect(result.success).toBe(false)
  })

  it('accepts optional taste score', () => {
    const result = reviewSchema.safeParse({ ...validReview, taste_optional: 4 })
    expect(result.success).toBe(true)
  })
})

describe('flagSchema', () => {
  it('requires at least 10 characters', () => {
    expect(flagSchema.safeParse({ reason: 'too short' }).success).toBe(false)
    expect(flagSchema.safeParse({ reason: 'This is a valid reported concern.' }).success).toBe(true)
  })
})
