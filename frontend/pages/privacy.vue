<template>
  <LegalPage title="Privacy Policy" :sections="sections" />
</template>

<script setup lang="ts">
useSeoMeta({ title: 'Privacy Policy — BiteScore' })

const sections = [
  {
    heading: 'Data we collect',
    body: 'We collect account information (email, name), review content, optional photos, and usage data necessary to operate the platform.',
  },
  {
    heading: 'Lawful basis (GDPR)',
    body: 'For users in the EU, we process data based on consent (review submissions), contract (account services), and legitimate interest (platform safety and moderation).',
  },
  {
    heading: 'Your rights',
    body: 'You may request access, correction, or deletion of your personal data. Contact us to exercise GDPR rights including data portability and objection to processing.',
  },
  {
    heading: 'Photo uploads',
    body: 'Uploaded photos may be displayed for trust verification and moderation. By uploading, you consent to this use as described at submission time.',
  },
  {
    heading: 'Data retention',
    body: 'We retain account and review data while your account is active. Deleted accounts are purged within 30 days except where retention is required by law.',
  },
]
</script>
