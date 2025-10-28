<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { listMessages, addUserMessage, completeOnce, type Message } from '@/lib/chatApi'
import ChatImageGrid from '@/components/ChatImageGrid.vue'
import ChatDataTable from '@/components/ChatDataTable.vue'
import AppComposer from '@/components/AppComposer.vue'

const route = useRoute()
const pid = computed(() => Number(route.params.pid))
const cid = computed(() => Number(route.params.cid))

const messages = ref<Message[]>([])
const sending = ref(false)
const assistantBusy = ref(false)
const input = ref('')

// scrolling
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
function onScroll() {
  const el = viewport.value
  if (!el) return
  stickToBottom.value = atBottom(el)
}

// race guard
const loadingFor = ref<number | null>(null)

async function loadMessagesSafe(chatId: number) {
  loadingFor.value = chatId
  try {
    const data = await listMessages(chatId)
    if (loadingFor.value !== chatId) return
    messages.value = data
    await nextTick()
    if (stickToBottom.value) scrollToBottom(false)
  } catch (e) {
    console.error('[chat] loadMessages error', e)
    messages.value = []
  }
}

async function send() {
  const text = input.value.trim()
  if (!text || sending.value || !cid.value) return
  sending.value = true
  assistantBusy.value = true
  const chatId = cid.value
  try {
    const userMsg = await addUserMessage(chatId, text)
    messages.value.push(userMsg)
    input.value = ''
    await nextTick()
    if (stickToBottom.value) scrollToBottom(true)

    const { message: aiMsg } = await completeOnce(chatId, [{ role: 'user', content: text }])
    if (cid.value !== chatId) return
    messages.value.push(aiMsg)
    await nextTick()
    if (stickToBottom.value) scrollToBottom(true)
  } catch (e) {
    console.error('[chat] send error', e)
  } finally {
    assistantBusy.value = false
    sending.value = false
  }
}

// react to cid change
watch(
  cid,
  async (newCid) => {
    if (!newCid || Number.isNaN(newCid)) return
    messages.value = []
    await nextTick()
    await loadMessagesSafe(newCid)
  },
  { immediate: true }
)

onMounted(() => nextTick(() => scrollToBottom(false)))

/** ===== Demo-insert handlers from composer buttons ===== **/

// Generates a demo image message (no backend)
function pushDemoImages(n = 6, query = 'demo cats') {
  if (!cid.value) return
  const items = Array.from({ length: n }).map((_, i) => {
    const w = 800, h = 600, seed = Math.floor(Math.random() * 1e9) + i
    const url = `https://picsum.photos/seed/${seed}/${w}/${h}`
    return {
      id: `picsum_${seed}`,
      thumb: url,
      url,
      width: w,
      height: h,
      source: 'picsum',
      attribution: 'Picsum demo image'
    }
  })

  const msg: Message = {
    id: Date.now(),
    chat_id: cid.value,
    role: 'assistant',
    content: `Found ${items.length} images for "${query}"`,
    meta_json: { type: 'images', items },
    created_at: new Date().toISOString()
  }
  messages.value.push(msg)
  nextTick(() => { if (stickToBottom.value) scrollToBottom(true) })
}

// Generates a demo table message (no backend)
function pushDemoTable(kind: 'sales'|'users'|'generic' = 'sales') {
  if (!cid.value) return
  const presets: Record<string, any> = {
    sales: {
      title: 'Sales (Q3)',
      headers: ['Product', 'Units', 'Revenue'],
      rows: [['Alpha', 120, 2400], ['Beta', 90, 1620], ['Gamma', 45, 900]],
      note: 'Demo data'
    },
    users: {
      title: 'Users',
      headers: ['Name', 'Email', 'Role'],
      rows: [['Jane', 'jane@example.com', 'admin'], ['Max', 'max@example.com', 'user']]
    },
    generic: {
      title: 'Sample table',
      headers: ['Col 1', 'Col 2', 'Col 3'],
      rows: [['A', 1, true], ['B', 2, false]]
    }
  }
  const data = presets[kind] || presets.generic

  const msg: Message = {
    id: Date.now(),
    chat_id: cid.value,
    role: 'assistant',
    content: data.title,
    meta_json: { type: 'table', headers: data.headers, rows: data.rows, note: data.note },
    created_at: new Date().toISOString()
  }
  messages.value.push(msg)
  nextTick(() => { if (stickToBottom.value) scrollToBottom(true) })
}
</script>

<template>
  <div class="flex flex-col h-full">
    <header class="shrink-0 border-b px-4 py-2 text-sm text-muted-foreground">
      Chat #{{ cid }} <span v-if="pid">in Project #{{ pid }}</span>
    </header>

    <div class="flex-1 relative overflow-hidden bg-background">
      <div ref="viewport" class="h-full overflow-y-auto px-4 pt-4 pb-24" @scroll="onScroll">
        <div class="space-y-3">
          <div
            v-for="m in messages"
            :key="m.id"
            class="flex"
            :class="m.role === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div
              class="max-w-[80%] rounded-md border px-3 py-2 text-sm bg-card"
              :class="m.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-card'"
            >
              <div v-if="m.content" class="whitespace-pre-wrap">{{ m.content }}</div>

              <!-- images block -->
              <ChatImageGrid
                v-if="m.meta_json && m.meta_json.type === 'images'"
                class="mt-2"
                :items="m.meta_json.items || []"
              />

              <!-- table block -->
              <ChatDataTable
                v-else-if="m.meta_json && m.meta_json.type === 'table'"
                class="mt-2"
                :headers="m.meta_json.headers || []"
                :rows="m.meta_json.rows || []"
                :note="m.meta_json.note"
                :title="m.meta_json.title"
              />
            </div>
          </div>

          <!-- Assistant status -->
          <div v-if="assistantBusy" class="flex items-center gap-2 text-xs text-muted-foreground px-3">
            <svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor"
                      d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
            </svg>
            Assistant is searching...
          </div>
        </div>
      </div>

      <button
        v-if="!stickToBottom"
        class="absolute bottom-24 right-4 rounded-full border bg-background px-3 py-1 text-xs shadow"
        @click="scrollToBottom(true)"
      >
        ↓ New messages
      </button>
    </div>

    <!-- Composer with demo buttons -->
    <div class="shrink-0 border-t bg-background p-3">
      <div class="mx-auto max-w-4xl w-full">
        <div class="flex items-center gap-2 mb-2">
          <button class="border rounded px-2 py-1 text-xs" @click="pushDemoImages()">
            + Images demo
          </button>
          <button class="border rounded px-2 py-1 text-xs" @click="pushDemoTable()">
            + Table demo
          </button>
        </div>

        <div class="flex items-end gap-2">
          <textarea
            v-model="input"
            class="flex-1 min-h-10 max-h-40 h-10 resize-y border rounded-md px-3 py-2 text-sm"
            placeholder="Write a message…"
            @keydown.enter.exact.prevent="send"
          />
          <button class="border rounded-md px-3 py-2 text-sm" :disabled="sending || !input.trim()" @click="send">
            Send
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
