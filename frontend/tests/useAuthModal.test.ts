import { beforeEach, describe, expect, it } from 'vitest'

// Minimal reimplementation for unit testing shared modal state pattern
function createAuthModalState() {
  const visible = { value: false }
  const mode = { value: 'login' as 'login' | 'register' }

  function open(m: 'login' | 'register') {
    mode.value = m
    visible.value = true
  }

  function close() {
    visible.value = false
  }

  return { visible, mode, open, close }
}

describe('auth modal state', () => {
  let modal: ReturnType<typeof createAuthModalState>

  beforeEach(() => {
    modal = createAuthModalState()
  })

  it('starts closed', () => {
    expect(modal.visible.value).toBe(false)
    expect(modal.mode.value).toBe('login')
  })

  it('opens in login mode', () => {
    modal.open('login')
    expect(modal.visible.value).toBe(true)
    expect(modal.mode.value).toBe('login')
  })

  it('opens in register mode', () => {
    modal.open('register')
    expect(modal.visible.value).toBe(true)
    expect(modal.mode.value).toBe('register')
  })

  it('closes the modal', () => {
    modal.open('login')
    modal.close()
    expect(modal.visible.value).toBe(false)
  })
})
