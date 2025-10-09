<script setup lang="ts">
import { ref } from 'vue'
import { useAuth } from '@/lib/useAuth'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import {
  Card, CardHeader, CardTitle, CardDescription,
  CardContent, CardFooter
} from '@/components/ui/card'

definePageMeta({ layout: 'auth', title: 'Create account' })

const { register } = useAuth()
const full_name = ref('')
const email = ref('')
const password = ref('')
const loading = ref(false)

async function onSubmit() {
  loading.value = true
  try {
    await register({ full_name: full_name.value, email: email.value, password: password.value })
    navigateTo('/') // после регистрации — на главную (чат)
  } catch (e) {
    alert('Register failed')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Card class="w-full max-w-sm">
    <CardHeader>
      <CardTitle>Create account</CardTitle>
      <CardDescription>It’s quick and easy</CardDescription>
    </CardHeader>

    <CardContent class="space-y-3">
      <div class="space-y-1">
        <label class="text-sm">Full name</label>
        <Input v-model="full_name" type="text" />
      </div>
      <div class="space-y-1">
        <label class="text-sm">Email</label>
        <Input v-model="email" type="email" autocomplete="username" />
      </div>
      <div class="space-y-1">
        <label class="text-sm">Password</label>
        <Input v-model="password" type="password" autocomplete="new-password" />
      </div>
    </CardContent>

    <CardFooter class="flex items-center justify-between">
      <Button :disabled="loading" @click="onSubmit">Create</Button>
      <NuxtLink to="/login" class="text-sm underline">Sign in</NuxtLink>
    </CardFooter>
  </Card>
</template>
