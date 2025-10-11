// app/lib/api.ts
import { ofetch } from 'ofetch'
import { useRuntimeConfig, useRequestHeaders } from '#app'

let isRefreshing = false
let waiters: Array<() => void> = []

export function createApi() {
  const config = useRuntimeConfig()

  // КЛИЕНТ → через Nuxt-прокси (мы настроили /api/api/v1 в nuxt.config.ts)
  const clientBase = config.public.apiBase || '/api/api/v1'

  // СЕРВЕР (SSR) → прямой адрес бэка с префиксом /api/v1
  const origin =
    (config as any).apiOrigin ||
    process.env.NUXT_PRIVATE_API_ORIGIN ||
    'http://localhost:8000'
  const serverBase = `${origin}/api/v1`

  const baseURL = import.meta.server ? serverBase : clientBase

  const api = ofetch.create({
    baseURL,
    credentials: 'include',

    // На сервере пробрасываем куки клиента к бэку
    headers: import.meta.server ? { ...useRequestHeaders(['cookie']) } : undefined,

    // ↓↓↓ ХУКИ передаются здесь, а не через api.onRequest(...)
    onRequest({ request, options }) {
      // Удобный лог для диагностики — можно убрать после проверки
      // console.log('[API]', options.method || 'GET', String(baseURL) + String(request))
    },

    async onResponseError({ response, request, options }) {
      if (response?.status !== 401) return

      // один общий refresh для параллельных запросов
      if (!isRefreshing) {
        isRefreshing = true
        try {
          await ofetch('/auth/refresh', {
            baseURL,
            method: 'POST',
            credentials: 'include',
            headers: import.meta.server ? { ...useRequestHeaders(['cookie']) } : undefined,
          })
          waiters.forEach((r) => r())
          waiters = []
        } catch (e) {
          waiters = []
          throw e
        } finally {
          isRefreshing = false
        }
      }

      await new Promise<void>((resolve) => waiters.push(resolve))
      // повторяем исходный запрос
      return ofetch(request as string, { ...options, baseURL })
    },
  })

  return api
}
