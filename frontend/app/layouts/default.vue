<script setup lang="ts">
import AppSidebar from '@/components/AppSidebar.vue'
import { SidebarProvider, SidebarTrigger, SidebarInset } from '@/components/ui/sidebar'
</script>

<template>
  <!-- закрыт по умолчанию; сайдбар не забирает ширину -->
  <SidebarProvider :defaultOpen="false">
    <AppSidebar />

    <!-- ВАЖНО: весь основной контент внутри SidebarInset -->
    <SidebarInset>
      <div class="h-screen flex flex-col overflow-hidden">
        <header class="shrink-0 sticky top-0 border-b bg-background/70 backdrop-blur p-2 flex items-center gap-2 z-10">
          <SidebarTrigger />
          <h1 class="font-medium">PyFastRun</h1>
        </header>

        <main class="flex-1 flex flex-col overflow-hidden">
          <NuxtPage />
        </main>
      </div>
    </SidebarInset>
  </SidebarProvider>
</template>
