<script setup lang="ts">
type ImageItem = {
  id: string
  thumb?: string
  url: string
  width?: number
  height?: number
  source?: string
  author_name?: string
  author_url?: string
  attribution?: string
  blurhash?: string
  meta?: any
}

defineProps<{
  items: ImageItem[]
  caption?: string
}>()
</script>

<template>
  <div class="space-y-2">
    <p v-if="caption" class="text-sm text-muted-foreground">{{ caption }}</p>

    <div
      class="grid gap-2"
      :class="{
        'grid-cols-1 sm:grid-cols-2': items.length <= 4,
        'grid-cols-2 sm:grid-cols-3 lg:grid-cols-4': items.length > 4
      }"
    >
      <a
        v-for="img in items"
        :key="img.id"
        :href="img.url"
        target="_blank"
        rel="noopener noreferrer"
        class="block overflow-hidden rounded-md border bg-card"
        title="Open full size"
      >
        <div class="aspect-[4/3] w-full">
          <img
            :src="img.thumb || img.url"
            :alt="img.attribution || img.author_name || img.source || 'image'"
            loading="lazy"
            decoding="async"
            class="h-full w-full object-cover"
          />
        </div>
        <div
          v-if="img.attribution || img.author_name"
          class="px-2 py-1 text-[10px] text-muted-foreground truncate"
        >
          {{ img.attribution || img.author_name }}
        </div>
      </a>
    </div>
  </div>
</template>
