<script setup lang="ts">
const props = defineProps<{
  headers: (string | number)[]
  rows: any[][]
  note?: string
  title?: string
}>()

function formatCell(v: any) {
  if (v == null) return ''
  if (typeof v === 'number') return v.toLocaleString()
  if (typeof v === 'object') return JSON.stringify(v)
  return String(v)
}
</script>

<template>
  <div class="space-y-2">
    <p v-if="title" class="text-sm text-muted-foreground">{{ title }}</p>

    <div class="overflow-x-auto rounded-md border">
      <table class="w-full text-sm">
        <thead class="bg-muted/50">
          <tr>
            <th
              v-for="h in headers"
              :key="String(h)"
              class="text-left px-3 py-2 border-b font-medium"
            >
              {{ h }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, i) in rows"
            :key="i"
            class="hover:bg-muted/30"
          >
            <td
              v-for="(cell, j) in row"
              :key="j"
              class="px-3 py-2 border-b align-top"
            >
              {{ formatCell(cell) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-if="note" class="text-xs text-muted-foreground">{{ note }}</p>
  </div>
</template>
