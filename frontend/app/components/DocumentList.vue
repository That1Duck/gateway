<!-- /components/DocumentList.vue -->
<script setup lang="ts">
import type { Document } from '@/composables/useUploader'

defineProps<{ items: Document[] }>()

function badgeClass(status: Document['status']) {
  const base = 'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium'
  switch (status) {
    case 'queued': return `${base} bg-yellow-100 text-yellow-800`
    case 'processing': return `${base} bg-blue-100 text-blue-800`
    case 'ready': return `${base} bg-green-100 text-green-800`
    case 'failed': return `${base} bg-red-100 text-red-800`
  }
}
</script>


<template>
  <div class="mt-6">
    <table class="w-full text-sm">
      <thead class="text-left border-b">
        <tr>
          <th class="py-2 pr-3">Файл</th>
          <th class="py-2 pr-3">Статус</th>
          <th class="py-2 pr-3">Страниц</th>
          <th class="py-2 pr-3">Автор</th>
          <th class="py-2 pr-3 w-0"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="doc in items" :key="doc.id" class="border-b hover:bg-gray-50/60">
          <td class="py-2 pr-3">
            <div class="font-medium">{{ doc.original_name }}</div>
            <div class="text-xs opacity-60">{{ doc.mime }} · {{ (doc.size_bytes/1024).toFixed(1) }} KB</div>
          </td>
          <td class="py-2 pr-3">
            <span :class="badgeClass(doc.status)">{{ doc.status }}</span>
            <div v-if="doc.status==='failed' && doc.error" class="text-xs text-red-600 mt-1">{{ doc.error }}</div>
          </td>
          <td class="py-2 pr-3">{{ doc.page_count ?? '—' }}</td>
          <td class="py-2 pr-3">{{ doc.author || '—' }}</td>
          <td class="py-2">
            <button class="px-3 py-1 rounded-lg border" @click="$emit('refresh', doc.id)">Обновить</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>