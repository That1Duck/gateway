<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { Card } from '@/components/ui/card'
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar'
import { Separator } from '@/components/ui/separator'
import { Loader2 } from 'lucide-vue-next'
import { useChat } from '@/lib/useChat'

const { messages, loading } = useChat()

// scrolling viewport
const viewport = ref<HTMLDivElement | null>(null)
const stickToBottom = ref(true)

function atBottom(el: HTMLElement, thresh = 24) {
  return el.scrollHeight - el.scrollTop - el.clientHeight <= thresh
}
function scrollToBottom(smooth = true) {
  const el = viewport.value
  if (!el) return
  el.scrollTo({ top: el.scrollHeight, behavior: smooth ? 'smooth' : 'auto' })
}

watch(
  () => messages.value.length,
  () => { if (stickToBottom.value) scrollToBottom(true) }
)

onMounted(() => { scrollToBottom(false) })

function onScroll() {
  const el = viewport.value
  if (!el) return
  stickToBottom.value = atBottom(el)
}
</script>

<template>
  <!-- owns the scroll; fills remaining height -->
  <div class="relative flex-1 overflow-hidden bg-background">
    <div
      ref="viewport"
      class="h-full overflow-y-auto px-4 pt-4 pb-20"
      @scroll="onScroll"
    >
      <div class="w-full space-y-4">
        <template v-for="m in messages" :key="m.id">
          <div
            class="flex gap-3 items-start"
            :class="m.role === 'user' ? 'justify-end text-right' : 'justify-start text-left'"
          >
            <Avatar v-if="m.role === 'assistant'">
              <AvatarImage src="https://api.dicebear.com/7.x/bottts/svg?seed=bot" />
              <AvatarFallback>AI</AvatarFallback>
            </Avatar>

            <Card class="px-3 py-2 max-w-[80%] text-left">
              <!-- ВАЖНО: content, не text; + переносы строк -->
              <p class="whitespace-pre-wrap break-words">{{ m.content }}</p>
            </Card>

            <Avatar v-if="m.role === 'user'">
              <AvatarImage src="https://api.dicebear.com/7.x/thumbs/svg?seed=user" />
              <AvatarFallback>U</AvatarFallback>
            </Avatar>
          </div>

          <Separator class="opacity-10" />
        </template>

        <div v-if="loading" class="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 class="h-4 w-4 animate-spin" />
          Assistant is typing…
        </div>
      </div>
    </div>

    <!-- floating "jump to bottom" button -->
    <button
      v-if="!stickToBottom"
      class="absolute bottom-24 right-6 rounded-full border px-3 py-1 text-sm bg-background shadow"
      @click="scrollToBottom(true)"
    >
      ↓ New messages
    </button>
  </div>
</template>
