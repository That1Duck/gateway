import { useAuth } from '@/lib/useAuth'

export default defineNuxtPlugin(async () => {
  const { fetchMe } = useAuth()
  await fetchMe()
})
