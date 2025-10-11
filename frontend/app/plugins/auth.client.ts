import { useAuth } from '@/lib/useAuth'

export default defineNuxtPlugin(async () => {
  const { fetchMe } = useAuth()
  try {
    await fetchMe()
  } catch {
    /* пользователь может быть не залогинен — ок */
  }
})
