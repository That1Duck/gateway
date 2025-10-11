<script setup lang="ts">
import { ref } from 'vue'
import { useAuth } from '@/lib/useAuth'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import {
  Card, CardHeader, CardTitle, CardDescription,
  CardContent, CardFooter
} from '@/components/ui/card'

definePageMeta({ layout: 'auth', title: 'Sign in' })

const { login } = useAuth()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref<string | null>(null)

async function onSubmit() {
  error.value = null
  if (!email.value || !password.value) {
    error.value = 'Enter email and password'
    return
  }
  loading.value = true
  try {
    await login(email.value, password.value)
    navigateTo('/') // успех → на главную
  } catch (e: any) {
    // покажем деталь от бэка, если есть
    error.value =
      e?.data?.detail ||
      e?.message ||
      'Login failed. Check email/password.'
    console.error('Login failed:', e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <!-- Центрированная карточка формы -->
  <Card class="w-full max-w-sm">
    <CardHeader>
      <CardTitle>Sign in</CardTitle>
      <CardDescription>Use your account credentials</CardDescription>
    </CardHeader>

    <!-- Форма: submit по Enter -->
    <form @submit.prevent="onSubmit">
      <CardContent class="space-y-3">
        <div class="space-y-1">
          <label class="text-sm">Email</label>
          <Input
            v-model="email"
            type="email"
            autocomplete="username"
            placeholder="you@example.com"
            required
          />
        </div>

        <div class="space-y-1">
          <label class="text-sm">Password</label>
          <Input
            v-model="password"
            type="password"
            autocomplete="current-password"
            placeholder="••••••••"
            required
          />
        </div>

        <!-- Текст ошибки -->
        <p v-if="error" class="text-sm text-red-500">
          {{ error }}
        </p>
      </CardContent>

      <CardFooter class="flex items-center justify-between">
        <Button type="submit" :disabled="loading">
          {{ loading ? 'Signing in…' : 'Sign in' }}
        </Button>
        <NuxtLink to="/register" class="text-sm underline">
          Create account
        </NuxtLink>
      </CardFooter>
    </form>
  </Card>
</template>
