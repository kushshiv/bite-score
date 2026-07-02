export interface ClaimedBusinessSummary {
  id: number
  name: string
  slug: string
}

export interface ClaimSummary {
  id: number
  business_id: number
  business_name: string | null
  business_slug: string | null
  status: string
  notes: string | null
  created_at: string
}

export interface BusinessAccount {
  claimed_business: ClaimedBusinessSummary | null
  claims: ClaimSummary[]
}

export function useBusinessAccount() {
  const auth = useAuthStore()
  const api = useApi()

  const { data: account, pending, refresh } = useAsyncData(
    'business-account',
    () => {
      if (!auth.isLoggedIn) return Promise.resolve(null as BusinessAccount | null)
      return api.get<BusinessAccount>('/business-dashboard/account')
    },
    { watch: [() => auth.isLoggedIn] },
  )

  const hasClaimedBusiness = computed(() => Boolean(account.value?.claimed_business))
  const pendingClaims = computed(
    () => account.value?.claims.filter((claim) => claim.status === 'pending') ?? [],
  )
  const showClaimProfileLink = computed(
    () => auth.isLoggedIn && !hasClaimedBusiness.value && pendingClaims.value.length === 0,
  )
  const showBusinessDashboardLink = computed(
    () => auth.isLoggedIn && (hasClaimedBusiness.value || pendingClaims.value.length > 0 || auth.isBusinessOwner),
  )

  return {
    account,
    pending,
    refresh,
    hasClaimedBusiness,
    pendingClaims,
    showClaimProfileLink,
    showBusinessDashboardLink,
    claimedBusiness: computed(() => account.value?.claimed_business ?? null),
  }
}
