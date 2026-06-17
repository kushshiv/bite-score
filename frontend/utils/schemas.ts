import { z } from 'zod'

export const loginSchema = z.object({
  email: z.string().email('Valid email required'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

export const registerSchema = loginSchema.extend({
  full_name: z.string().min(2, 'Name required').optional(),
})

export const reviewSchema = z.object({
  visit_type: z.enum(['dine_in', 'takeaway', 'delivery']),
  visit_date: z.string().min(1, 'Visit date required'),
  notes: z.string().max(1000).optional(),
  consent_given: z.literal(true, { errorMap: () => ({ message: 'You must confirm your observation is honest' }) }),
  cleanliness: z.number().min(1).max(5),
  staff_hygiene: z.number().min(1).max(5),
  food_handling: z.number().min(1).max(5),
  packaging: z.number().min(1).max(5),
  water_confidence: z.number().min(1).max(5),
  oil_freshness_concern: z.boolean(),
  taste_optional: z.number().min(1).max(5).optional(),
})

export const flagSchema = z.object({
  reason: z.string().min(10, 'Please provide at least 10 characters'),
})

export const addPlaceSchema = z.object({
  name: z.string().min(2, 'Name is required').max(255),
  address: z.string().max(500).optional(),
  city: z.string().min(2, 'City is required').max(100),
  country: z.string().min(2, 'Country is required').max(100),
  category: z.string().min(2, 'Category is required'),
  business_type: z.enum([
    'restaurant',
    'street_vendor',
    'cafe',
    'food_court',
    'bakery',
    'cloud_kitchen',
    'other',
  ]),
  description: z.string().max(2000).optional(),
})
