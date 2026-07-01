import { describe, expect, it } from 'vitest'
import {
  EVIDENCE_MAX_BYTES,
  EVIDENCE_MAX_FILES,
  remainingEvidenceSlots,
  validateEvidenceFile,
} from '../composables/useReviewEvidence'

function makeFile(type: string, size: number): File {
  return new File([new Uint8Array(size)], 'photo.jpg', { type })
}

describe('validateEvidenceFile', () => {
  it('accepts allowed image types under size limit', () => {
    expect(validateEvidenceFile(makeFile('image/jpeg', 1024))).toBeNull()
    expect(validateEvidenceFile(makeFile('image/png', 1024))).toBeNull()
    expect(validateEvidenceFile(makeFile('image/webp', 1024))).toBeNull()
  })

  it('rejects unsupported types', () => {
    expect(validateEvidenceFile(makeFile('image/gif', 1024))).toMatch(/allowed/i)
  })

  it('rejects files over 5 MB', () => {
    expect(validateEvidenceFile(makeFile('image/jpeg', EVIDENCE_MAX_BYTES + 1))).toMatch(/5 MB/i)
  })
})

describe('remainingEvidenceSlots', () => {
  it('returns remaining slots up to the max', () => {
    expect(remainingEvidenceSlots(0, EVIDENCE_MAX_FILES)).toBe(5)
    expect(remainingEvidenceSlots(3, EVIDENCE_MAX_FILES)).toBe(2)
    expect(remainingEvidenceSlots(5, EVIDENCE_MAX_FILES)).toBe(0)
    expect(remainingEvidenceSlots(8, EVIDENCE_MAX_FILES)).toBe(0)
  })
})
