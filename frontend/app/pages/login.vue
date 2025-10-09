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

async function onSubmit() {
  loading.value = true
  try {
    await login(email.value, password.value)
    navigateTo('/') // после входа — на главную (чат)
  } catch (e) {
    alert('Login failed')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Card class="w-full max-w-sm">
    <CardHeader>
      <CardTitle>Sign in</CardTitle>
      <CardDescription>Use your account credentials</CardDescription>
    </CardHeader>

    <CardContent class="space-y-3">
      <div class="space-y-1">
        <label class="text-sm">Email</label>
        <Input v-model="email" type="email" autocomplete="username" />
      </div>
      <div class="space-y-1">
        <label class="text-sm">Password</label>
        <Input v-model="password" type="password" autocomplete="current-password" />
      </div>
    </CardContent>

    <CardFooter class="flex items-center justify-between">
      <Button :disabled="loading" @click="onSubmit">Sign in</Button>
      <NuxtLink to="/register" class="text-sm underline">Create account</NuxtLink>
    </CardFooter>
  </Card>
</template>
