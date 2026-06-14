export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: ['@nuxtjs/tailwindcss', '@pinia/nuxt', '@nuxtjs/sitemap'],
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
    },
  },
  app: {
    head: {
      title: 'BiteScore — Food Trust Platform',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content: 'Discover food businesses you can trust with structured hygiene observations and transparent scoring.',
        },
        { property: 'og:title', content: 'BiteScore — Food Trust Platform' },
        {
          property: 'og:description',
          content: 'Structured hygiene observations, evidence-backed reviews, and transparent food trust scores.',
        },
        { property: 'og:type', content: 'website' },
      ],
      link: [{ rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }],
    },
  },
  sitemap: {
    sources: ['/api/__sitemap__/urls'],
  },
  compatibilityDate: '2024-11-01',
})
