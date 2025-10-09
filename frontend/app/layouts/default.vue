<script setup lang="ts">
import AppSidebar from '@/components/AppSidebar.vue'
import { SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
</script>

<template>
  <SidebarProvider>
    <AppSidebar />

    <!-- Full viewport app -->
    <div class="h-screen flex flex-col overflow-hidden">
      <!-- Sticky header (optional) -->
      <header class="shrink-0 sticky top-0 border-b bg-background/70 backdrop-blur p-2 flex items-center gap-2 z-10">
        <SidebarTrigger />
        <h1 class="font-medium">UI</h1>
      </header>

      <!-- Chat column: scroll lives INSIDE AppChat only -->
      <main class="flex-1 flex flex-col overflow-hidden">
        <AppChat class="flex-1 overflow-hidden" />
      </main>

      <!-- Fixed composer at the bottom -->
      <AppComposer class="shrink-0" />
    </div>
  </SidebarProvider>
</template>
