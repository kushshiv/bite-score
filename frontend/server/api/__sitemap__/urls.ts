export default defineEventHandler(async () => {
  const config = useRuntimeConfig()
  const staticPages = ['/', '/search', '/about', '/how-it-works', '/terms', '/privacy', '/moderation']

  let businessUrls: { loc: string }[] = []
  try {
    const businesses = await $fetch(`${config.public.apiBase}/businesses?limit=100`)
    businessUrls = (businesses as { slug: string }[]).map((b) => ({
      loc: `/business/${b.slug}`,
    }))
  } catch {
    // API may be unavailable during build
  }

  return [...staticPages.map((loc) => ({ loc })), ...businessUrls]
})
