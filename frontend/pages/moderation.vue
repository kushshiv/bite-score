<template>
  <LegalPage title="Content Moderation Policy" :sections="sections" />
</template>

<script setup lang="ts">
useSeoMeta({ title: 'Moderation Policy — BiteScore' })

const sections = [
  {
    heading: 'Community guidelines',
    body: 'BiteScore encourages structured, evidence-based observations. Prohibited content includes harassment, hate speech, false accusations, spam, and content unrelated to food trust.',
  },
  {
    heading: 'Neutral language',
    body: 'Use phrasing like "reported concern," "community observation," and "under review" rather than direct accusations. Our templates guide users toward factual reporting.',
  },
  {
    heading: 'Moderation process',
    body: 'Reviews may be pending, approved, hidden, or flagged. Moderators review reported content and can take action including hiding abusive submissions.',
  },
  {
    heading: 'Business correction and appeals',
    body: 'Business owners may respond to observations on claimed profiles. If you believe content is inaccurate, submit a correction request through the business dispute flow. Moderators will review appeals.',
  },
  {
    heading: 'Flag handling',
    body: 'Users can flag reviews, businesses, or evidence. Flags are reviewed by moderators and resolved or dismissed with actions logged in the admin audit trail.',
  },
]
</script>
