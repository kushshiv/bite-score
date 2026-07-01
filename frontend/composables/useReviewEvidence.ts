export const EVIDENCE_MAX_BYTES = 5 * 1024 * 1024
export const EVIDENCE_MAX_FILES = 5
export const EVIDENCE_ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'] as const

export function validateEvidenceFile(file: File): string | null {
  if (!EVIDENCE_ALLOWED_TYPES.includes(file.type as (typeof EVIDENCE_ALLOWED_TYPES)[number])) {
    return 'Only JPEG, PNG, and WebP images are allowed'
  }
  if (file.size > EVIDENCE_MAX_BYTES) {
    return 'Each image must be 5 MB or smaller'
  }
  return null
}

export function remainingEvidenceSlots(currentCount: number, maxFiles = EVIDENCE_MAX_FILES): number {
  return Math.max(0, maxFiles - currentCount)
}
