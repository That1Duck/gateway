<script setup lang="ts">
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
} from '@/components/ui/sidebar'
import { Button } from '@/components/ui/button'
import { Home, Settings, LogOut, LogIn, FileText } from 'lucide-vue-next'
import { useAuth } from '@/lib/useAuth'
import AppProjectTree from '@/components/AppProjectTree.vue'

const { user, isAuthenticated, logout } = useAuth()

const items = [
  { title: 'Home', url: '/', icon: Home },
  { title: 'Documents', url: '/documents', icon: FileText},
  { title: 'Settings', url: '/settings', icon: Settings }, // временно
]

async function onLogout() {
  try {
    await logout()
  } finally {
    navigateTo('/login')
  }
}
</script>

<template>
  <!-- offcanvas: выезжает поверх, не занимает ширину -->
  <Sidebar collapsible="offcanvas" class="border-r">
    <SidebarContent class="flex flex-col justify-between h-full">

      <!-- верх: базовое меню + дерево проектов/чатов -->
      <div class="space-y-2">
        <SidebarGroup>
          <SidebarGroupLabel>General</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem v-for="item in items" :key="item.title">
                <SidebarMenuButton asChild>
                  <NuxtLink :to="item.url">
                    <component :is="item.icon" class="h-4 w-4" />
                    <span>{{ item.title }}</span>
                  </NuxtLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <!-- дерево: Unassigned / Projects / Trash -->
        <AppProjectTree />
      </div>

      <!-- низ: auth-блок -->
      <div class="p-2 border-t">
        <ClientOnly>
          <template #default>
            <template v-if="isAuthenticated">
              <p class="text-sm truncate mb-2">
                👋 {{ user?.full_name || user?.email }}
              </p>
              <Button variant="outline" class="w-full justify-start" @click="onLogout">
                <LogOut class="h-4 w-4 mr-2" /> Logout
              </Button>
            </template>

            <template v-else>
              <NuxtLink to="/login">
                <Button variant="default" class="w-full justify-start">
                  <LogIn class="h-4 w-4 mr-2" /> Sign in
                </Button>
              </NuxtLink>
            </template>
          </template>

          <template #fallback>
            <div class="h-9 w-full animate-pulse rounded-md bg-muted" />
          </template>
        </ClientOnly>
      </div>

    </SidebarContent>
  </Sidebar>
</template>
