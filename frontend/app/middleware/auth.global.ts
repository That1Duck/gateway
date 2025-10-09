// app/middleware/auth.global.ts
import { useAuth } from '@/lib/useAuth'

export default defineNuxtRouteMiddleware((to) => {
  // Не выполняем редиректы на сервере — это часто даёт 500
  if (import.meta.server) return

  const { isAuthenticated } = useAuth()
  const publicRoutes = ['/login', '/register']

  if (!isAuthenticated.value && !publicRoutes.includes(to.path)) {
    return navigateTo('/login')
  }
})
