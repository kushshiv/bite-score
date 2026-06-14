import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'
import { useAuthStore } from '../stores/auth'

describe('useAuthStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('starts logged out', () => {
    const auth = useAuthStore()
    expect(auth.isLoggedIn).toBe(false)
    expect(auth.isAdmin).toBe(false)
    expect(auth.isModerator).toBe(false)
    expect(auth.isBusinessOwner).toBe(false)
  })

  it('setAuth marks user as logged in', () => {
    const auth = useAuthStore()
    auth.setAuth('fake-token', {
      id: 1,
      email: 'user@bitescore.demo',
      full_name: 'Demo User',
      role: 'user',
    })
    expect(auth.isLoggedIn).toBe(true)
    expect(auth.user?.email).toBe('user@bitescore.demo')
  })

  it('detects admin role', () => {
    const auth = useAuthStore()
    auth.setAuth('token', {
      id: 1,
      email: 'admin@bitescore.demo',
      full_name: 'Admin',
      role: 'admin',
    })
    expect(auth.isAdmin).toBe(true)
    expect(auth.isModerator).toBe(true)
  })

  it('detects business owner role', () => {
    const auth = useAuthStore()
    auth.setAuth('token', {
      id: 2,
      email: 'owner@bitescore.demo',
      full_name: 'Owner',
      role: 'business_owner',
    })
    expect(auth.isBusinessOwner).toBe(true)
    expect(auth.isAdmin).toBe(false)
  })

  it('logout clears session', () => {
    const auth = useAuthStore()
    auth.setAuth('token', {
      id: 1,
      email: 'user@bitescore.demo',
      full_name: 'User',
      role: 'user',
    })
    auth.logout()
    expect(auth.isLoggedIn).toBe(false)
    expect(auth.token).toBeNull()
    expect(auth.user).toBeNull()
  })
})
