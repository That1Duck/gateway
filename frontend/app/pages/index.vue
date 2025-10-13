<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { listProjects, listChats, listChatsInProject } from '@/lib/chatApi'

const loading = ref(true)
const empty = ref(false)

onMounted(async () => {
  try {
    // 1) сначала чаты без проекта
    const unassigned = await listChats({ unassigned: true })
    if (unassigned.length) {
      navigateTo(`/p/0/c/${unassigned[0].id}`)
      return
    }

    // 2) затем проекты и их чаты
    const projects = await listProjects()
    if (projects.length) {
      for (const p of projects) {
        const chats = await listChatsInProject(p.id)
        if (chats.length) {
          navigateTo(`/p/${p.id}/c/${chats[0].id}`)
          return
        }
      }
    }

    // если вообще ничего нет — показываем empty state
    empty.value = true
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="flex-1 grid place-items-center p-6">
    <div v-if="loading" class="text-muted-foreground">Loading…</div>
    <div v-else class="text-center text-muted-foreground space-y-2">
      <p class="text-lg">No chats yet.</p>
      <p>Create one with “+ New Chat” in the sidebar.</p>
    </div>
  </div>
</template>
