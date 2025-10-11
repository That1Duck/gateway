<script setup lang="ts">
import { useAuth } from '@/lib/useAuth'
definePageMeta({ title: 'Profile' })
const { user, logout } = useAuth()
</script>

<template>
  <div class="p-6 space-y-4">
    <h1 class="text-xl font-semibold">Profile</h1>
    <pre class="p-3 bg-muted rounded-md text-sm">{{ user }}</pre>
    <div class="flex gap-2">
      <NuxtLink to="/">← Back</NuxtLink>
      <Button variant="outline" @click="logout">Logout</Button>
    </div>
  </div>
</template>
