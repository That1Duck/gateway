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
import { Home, Inbox, Settings, LogOut, LogIn } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/lib/useAuth'

const { user, isAuthenticated, logout } = useAuth()

const items = [
  { title: 'Home', url: '/', icon: Home },
  { title: 'Inbox', url: '/inbox', icon: Inbox },
  { title: 'Settings', url: '/settings', icon: Settings },
]
</script>

<template>
  <!-- collapsible sidebar -->
  <Sidebar collapsible="icon" class="border-r">
    <SidebarContent class="flex flex-col justify-between h-full">
      <!-- верхняя часть -->
      <div>
        <SidebarGroup>
          <SidebarGroupLabel>General</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem v-for="item in items" :key="item.title">
                <SidebarMenuButton asChild>
                  <NuxtLink :to="item.url">
                    <component :is="item.icon" />
                    <span>{{ item.title }}</span>
                  </NuxtLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </div>

      <!-- нижняя часть: логин / логаут -->
      <div class="p-2 border-t">
        <ClientOnly>
          <template #default>
            <template v-if="isAuthenticated">
              <p class="text-sm truncate mb-2">
                👋 {{ user?.full_name || user?.email }}
              </p>
              <Button
                variant="outline"
                class="w-full justify-start"
                @click="logout"
              >
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

          <!-- отображается на SSR, пока гидрируется -->
          <template #fallback>
            <div class="h-9 w-full animate-pulse rounded-md bg-muted" />
          </template>
        </ClientOnly>
      </div>
    </SidebarContent>
  </Sidebar>
</template>
