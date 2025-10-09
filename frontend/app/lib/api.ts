// app/lib/api.ts
import { ofetch } from 'ofetch'
import { useRuntimeConfig, useRequestHeaders } from '#app'

let isRefreshing = false
let pending: Array<() => void> = []

export function createApi() {
  const config = useRuntimeConfig()

  // На клиенте используем прокси '/api'
  const clientBase = config.public.apiBase || '/api'

  // На сервере БЕЗ прокси идём прямо на FastAPI
  // Можно вынести в ENV: NUXT_PRIVATE_API_ORIGIN=http://127.0.0.1:8000
  const serverBase =
    (config as any).private?.apiOrigin ||
    process.env.NUXT_PRIVATE_API_ORIGIN ||
    'http://127.0.0.1:8000'

  const baseURL = import.meta.server ? serverBase : clientBase

  const common: any = {
    baseURL,
    credentials: 'include',
  }

  // На сервере пробрасываем Cookie пользователя к бэку
  if (import.meta.server) {
    common.headers = {
      ...useRequestHeaders(['cookie']),
    }
  }

  const api = ofetch.create(common)

  // Глобальный авто-refresh по 401
  api.onResponseError(async (error) => {
    const { response, request } = error
    if (response?.status !== 401) throw error

    if (!isRefreshing) {
      isRefreshing = true
      try {
        await api('/auth/refresh', { method: 'POST' })
        pending.forEach((resume) => resume())
        pending = []
      } catch (e) {
        pending = []
        throw e
      } finally {
        isRefreshing = false
      }
    }

    await new Promise<void>((resolve) => pending.push(resolve))
    return api(request)
  })

  return api
}
