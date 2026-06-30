export class ApiError extends Error {
  status: number
  detail: unknown

  constructor(message: string, detail: unknown, status: number) {
    super(message)
    this.name = 'ApiError'
    this.detail = detail
    this.status = status
  }
}

export function useApi() {
  const config = useRuntimeConfig()
  const auth = useAuthStore()

  async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string>),
    }
    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json'
    }
    if (auth.token) {
      headers.Authorization = `Bearer ${auth.token}`
    }

    const res = await fetch(`${config.public.apiBase}${path}`, {
      ...options,
      headers,
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }))
      const detail = err.detail
      const message =
        typeof detail === 'string'
          ? detail
          : typeof detail === 'object' && detail !== null && 'message' in detail
            ? String((detail as { message: string }).message)
            : 'Request failed'
      throw new ApiError(message, detail, res.status)
    }
    return res.json()
  }

  return {
    get: <T>(path: string) => request<T>(path),
    post: <T>(path: string, body?: unknown) =>
      request<T>(path, { method: 'POST', body: body instanceof FormData ? body : JSON.stringify(body) }),
    patch: <T>(path: string, body?: unknown) =>
      request<T>(path, { method: 'PATCH', body: JSON.stringify(body) }),
  }
}
