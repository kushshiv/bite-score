<template>
  <div v-if="visible" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 p-4" @click.self="close">
    <div class="card w-full max-w-md">
      <h2 class="text-xl font-semibold text-slate-900">{{ mode === 'login' ? 'Sign in' : 'Create account' }}</h2>
      <p class="mt-1 text-sm text-slate-500">Access structured food trust reviews and dashboards.</p>

      <form class="mt-6 space-y-4" @submit.prevent="submit">
        <div v-if="mode === 'register'">
          <label class="label">Full name</label>
          <input v-model="form.full_name" class="input" type="text" />
        </div>
        <div>
          <label class="label">Email</label>
          <input v-model="form.email" class="input" type="email" required />
        </div>
        <div>
          <label class="label">Password</label>
          <input v-model="form.password" class="input" type="password" required minlength="8" />
        </div>
        <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
        <button class="btn-primary w-full" type="submit" :disabled="loading">
          {{ loading ? 'Please wait...' : mode === 'login' ? 'Sign in' : 'Register' }}
        </button>
      </form>

      <button class="mt-4 w-full text-sm text-slate-500 hover:text-slate-700" @click="toggleMode">
        {{ mode === 'login' ? 'Need an account? Register' : 'Already have an account? Sign in' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
const auth = useAuthStore()
const api = useApi()
const { visible, mode, close } = useAuthModal()
const loading = ref(false)
const error = ref('')
const form = reactive({ email: '', password: '', full_name: '' })

watch(visible, (v) => {
  if (v) error.value = ''
})

async function submit() {
  loading.value = true
  error.value = ''
  try {
    const endpoint = mode.value === 'login' ? '/auth/login' : '/auth/register'
    const body = mode.value === 'login'
      ? { email: form.email, password: form.password }
      : { email: form.email, password: form.password, full_name: form.full_name || undefined }
    const { access_token } = await api.post<{ access_token: string }>(endpoint, body)
    auth.setAuth(access_token, { id: 0, email: form.email, full_name: form.full_name, role: 'user' })
    await auth.fetchMe()
    close()
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Authentication failed'
  } finally {
    loading.value = false
  }
}

function toggleMode() {
  mode.value = mode.value === 'login' ? 'register' : 'login'
  error.value = ''
}
</script>
