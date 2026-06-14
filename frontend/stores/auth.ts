import { defineStore } from 'pinia'

interface User {
  id: number
  email: string
  full_name: string | null
  role: string
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: null as string | null,
    user: null as User | null,
  }),
  getters: {
    isLoggedIn: (s) => !!s.token,
    isAdmin: (s) => s.user?.role === 'admin',
    isModerator: (s) => s.user?.role === 'moderator' || s.user?.role === 'admin',
    isBusinessOwner: (s) => s.user?.role === 'business_owner',
  },
  actions: {
    init() {
      if (import.meta.client) {
        this.token = localStorage.getItem('bitescore_token')
        const user = localStorage.getItem('bitescore_user')
        if (user) this.user = JSON.parse(user)
      }
    },
    setAuth(token: string, user: User) {
      this.token = token
      this.user = user
      if (import.meta.client) {
        localStorage.setItem('bitescore_token', token)
        localStorage.setItem('bitescore_user', JSON.stringify(user))
      }
    },
    logout() {
      this.token = null
      this.user = null
      if (import.meta.client) {
        localStorage.removeItem('bitescore_token')
        localStorage.removeItem('bitescore_user')
      }
    },
    async fetchMe() {
      const api = useApi()
      try {
        const user = await api.get<User>('/auth/me')
        this.user = user
        if (import.meta.client) {
          localStorage.setItem('bitescore_user', JSON.stringify(user))
        }
      } catch {
        this.logout()
      }
    },
  },
})
