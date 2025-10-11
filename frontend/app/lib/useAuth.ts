// app/lib/useAuth.ts
import { ref, computed, shallowRef } from 'vue'
import { createApi } from './api'

export type Me = { id: number; email: string; full_name?: string } // подгони под свой бек

const user = ref<Me | null>(null)
const loading = ref(false)
const _api = shallowRef<ReturnType<typeof createApi> | null>(null)

function api() {
  if (!_api.value) _api.value = createApi()
  return _api.value
}

export function useAuth() {
  async function fetchMe() {
    try {
      loading.value = true
      const me = await api()<Me>('/auth/me', { method: 'GET' })
      user.value = me
      return true
    } catch {
      user.value = null
      return false
    } finally {
      loading.value = false
    }
  }

  async function login(email: string, password: string) {
    try {
      await api()('/auth/login', { method: 'POST', body: { email, password } })
      const ok = await fetchMe()
      if (!ok) throw new Error('Login: /auth/me failed after login')
    } catch (e: any) {
      console.error('Login error:', e?.data || e?.message || e)
      throw e
    }
  }

  async function register(values: { email: string; password: string; full_name?: string }) {
    await api()('/auth/register', { method: 'POST', body: values })
    await login(values.email, values.password)
  }

  async function logout() {
    try {
      await api()('/auth/logout', { method: 'POST' })
    } finally {
      user.value = null
    }
  }

  const isAuthenticated = computed(() => !!user.value)
  return { user, loading, isAuthenticated, fetchMe, login, register, logout }
}
