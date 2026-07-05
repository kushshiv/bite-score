export const CERTIFICATION_MAX_BYTES = 10 * 1024 * 1024
export const CERTIFICATION_ALLOWED_TYPES = [
  'image/jpeg',
  'image/png',
  'image/webp',
  'application/pdf',
] as const

export function validateCertificationFile(file: File): string | null {
  if (!CERTIFICATION_ALLOWED_TYPES.includes(file.type as (typeof CERTIFICATION_ALLOWED_TYPES)[number])) {
    return 'Only JPEG, PNG, WebP images and PDF documents are allowed'
  }
  if (file.size > CERTIFICATION_MAX_BYTES) {
    return 'File must be 10 MB or smaller'
  }
  return null
}
