<template>
  <LegalPage title="Terms of Service" :sections="sections" />
</template>

<script setup lang="ts">
useSeoMeta({ title: 'Terms of Service — BiteScore' })

const sections = [
  {
    heading: 'Acceptance',
    body: 'By using BiteScore, you agree to these Terms of Service. BiteScore is a community platform for structured food trust observations.',
  },
  {
    heading: 'User content',
    body: 'You are responsible for content you submit. Observations must be honest, based on personal experience, and use neutral language. Do not make defamatory or unsubstantiated accusations.',
  },
  {
    heading: 'Scoring disclaimer',
    body: 'BiteScore scores are platform-derived community signals. They do not represent government inspections, official certifications, or legal guarantees of food safety.',
  },
  {
    heading: 'Business accounts',
    body: 'Business owners may claim profiles subject to verification. Claimed businesses may respond to community observations through the platform.',
  },
  {
    heading: 'Limitation of liability',
    body: 'BiteScore is provided as-is. We do not guarantee accuracy of user-submitted content. Use scores as one input among many when making dining decisions.',
  },
]
</script>
