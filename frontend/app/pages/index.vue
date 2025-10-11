<!-- app/pages/index.vue -->
<script setup lang="ts">
import AppChat from '@/components/AppChat.vue'
import AppComposer from '@/components/AppComposer.vue'
</script>

<template>
  <div class="flex-1 flex flex-col overflow-hidden">
    <AppChat class="flex-1 overflow-hidden" />
    <AppComposer class="shrink-0" />
  </div>
</template>
