<script setup lang="ts">
import { onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import AppChat from '@/components/AppChat.vue'
import AppComposer from '@/components/AppComposer.vue'
import { useChat } from '@/lib/useChat'

definePageMeta({ title: 'Chat' })

const route = useRoute()
const pid = computed(() => String(route.params.pid ?? '0'))
const cid = computed(() => Number(route.params.cid))

const { loadHistoryFor, setActiveChat } = useChat()

async function boot() {
  if (!cid.value || Number.isNaN(cid.value)) {
    console.warn('[ChatPage] invalid cid', route.params)
    return
  }
  console.log('[ChatPage] open chat', { pid: pid.value, cid: cid.value })
  setActiveChat(cid.value)
  await loadHistoryFor(cid.value)
}

onMounted(boot)
watch(() => route.fullPath, boot)
</script>

<template>
  <div class="flex-1 flex flex-col overflow-hidden">
    <AppChat class="flex-1 overflow-hidden" />
    <AppComposer class="shrink-0" />
  </div>
</template>
