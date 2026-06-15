export function useTrustVerdict(score: number) {
  if (score >= 80) {
    return {
      label: 'Safe to eat',
      shortLabel: 'Safe',
      description: 'Strong hygiene signals from recent diner reviews.',
      badgeClass: 'bg-trust-100 text-trust-700',
      bannerClass: 'border-trust-200 bg-trust-50',
    }
  }
  if (score >= 60) {
    return {
      label: 'Use caution',
      shortLabel: 'Caution',
      description: 'Mixed signals — read recent reviews before you order.',
      badgeClass: 'bg-caution-100 text-amber-800',
      bannerClass: 'border-caution-500/30 bg-caution-100/60',
    }
  }
  if (score > 0) {
    return {
      label: 'Low confidence',
      shortLabel: 'Low',
      description: 'Weak hygiene signals — consider other options.',
      badgeClass: 'bg-red-100 text-red-800',
      bannerClass: 'border-red-200 bg-red-50',
    }
  }
  return {
    label: 'Not enough reviews',
    shortLabel: 'New',
    description: 'No reviews yet — be the first to share your visit.',
    badgeClass: 'bg-slate-100 text-slate-600',
    bannerClass: 'border-slate-200 bg-slate-50',
  }
}
