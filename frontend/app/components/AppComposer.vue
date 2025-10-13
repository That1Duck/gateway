<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Send, Sparkles } from 'lucide-vue-next'
import { useChat } from '@/lib/useChat'

const { sendUser, replyWith } = useChat()
const text = ref('')
const el = ref<HTMLTextAreaElement | null>(null)

async function onSend() {
  const t = text.value.trim()
  if (!t) return

  try {
    // 1️⃣ сохраняем сообщение пользователя
    await sendUser(t)

    // 2️⃣ очищаем поле и пытаемся вернуть фокус
    text.value = ''
    await nextTick()
    if (el.value && typeof (el.value as any).focus === 'function') {
      (el.value as any).focus()
    }

    // 3️⃣ просим ассистента ответить
    await replyWith()
  } catch (e: any) {
    console.error('[Composer] send error', e)
    alert('Failed to send message: ' + (e?.data?.detail || e?.message || 'unknown'))
  }
}

const suggestions = [
  'Summarize today’s tasks',
  'Generate a roadmap for the UI',
  'Explain Monte Carlo briefly'
]
function useSuggestion(s: string) {
  text.value = s
}
</script>

<template>
  <div class="border-t bg-background p-3">
    <div class="w-full flex items-end gap-2 px-4">
      <Popover>
        <PopoverTrigger as-child>
          <Button variant="outline" class="shrink-0" title="Prompt ideas">
            <Sparkles class="h-4 w-4" />
          </Button>
        </PopoverTrigger>
        <PopoverContent class="w-64">
          <div class="space-y-2">
            <p class="text-sm text-muted-foreground">Try one of these:</p>
            <ul class="space-y-1">
              <li v-for="s in suggestions" :key="s">
                <Button variant="ghost" class="w-full justify-start" @click="useSuggestion(s)">
                  {{ s }}
                </Button>
              </li>
            </ul>
          </div>
        </PopoverContent>
      </Popover>

      <!-- ref теперь точно висит на Textarea -->
      <Textarea
        ref="el"
        v-model="text"
        placeholder="Message your assistant…"
        class="min-h-12 h-12 max-h-40 resize-y flex-1"
        @keydown.enter.exact.prevent="onSend"
      />

      <Button class="shrink-0" @click="onSend" title="Send">
        <Send class="h-4 w-4 mr-1" /> Send
      </Button>
    </div>
  </div>
</template>
