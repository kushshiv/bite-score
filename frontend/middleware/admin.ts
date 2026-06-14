export default defineNuxtRouteMiddleware(() => {
  const auth = useAuthStore()
  auth.init()
  if (!auth.isModerator) {
    return navigateTo('/')
  }
})
