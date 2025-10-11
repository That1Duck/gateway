import { useAuth } from '@/lib/useAuth'

const PUBLIC_ROUTES = ['/login', '/register']

export default defineNuxtRouteMiddleware((to) => {
  if (import.meta.server) return

  const { isAuthenticated } = useAuth()

  // если уже залогинен — не даём попасть на /login и /register
  if (isAuthenticated.value && PUBLIC_ROUTES.includes(to.path)) {
    return navigateTo('/')
  }

  // если не залогинен — защищаем все, кроме публичных
  if (!isAuthenticated.value && !PUBLIC_ROUTES.includes(to.path)) {
    return navigateTo('/login')
  }
})
