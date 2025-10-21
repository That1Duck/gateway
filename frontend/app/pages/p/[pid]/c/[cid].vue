<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { listMessages, addUserMessage, completeOnce, type Message } from '@/lib/chatApi'

// ---- Параметры из маршрута ----
const route = useRoute()
const pid = computed(() => Number(route.params.pid))
const cid = computed(() => Number(route.params.cid))

// ---- Состояния чата ----
const messages = ref<Message[]>([])
const sending = ref(false)
const input = ref('')

// защита от гонок загрузки (когда запрашивали один чат, а пользователь уже переключился на другой)
const loadingFor = ref<number | null>(null)

// ---- Вьюпорт для скролла ----
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

// ---- Загрузка сообщений ----
async function loadMessagesSafe(chatId: number) {
  loadingFor.value = chatId
  try {
    const data = await listMessages(chatId)
    // если пока грузили пользователь уже ушёл в другой чат — игнорируем ответ
    if (loadingFor.value !== chatId) return
    messages.value = data
    await nextTick()
    if (stickToBottom.value) scrollToBottom(false)
  } catch (e) {
    // не валим страницу, просто логируем
    console.error('[chat] loadMessages error', e)
    messages.value = []
  }
}

// ---- Отправка реплики ----
async function send() {
  const text = input.value.trim()
  if (!text || sending.value || !cid.value) return
  sending.value = true

  const chatId = cid.value

  try {
    // 1) добавляем юзерское сообщение (сразу появляется в истории)
    const userMsg = await addUserMessage(chatId, text)
    messages.value.push(userMsg)
    input.value = ''

    await nextTick()
    if (stickToBottom.value) scrollToBottom(true)

    // 2) запрашиваем ответ ассистента (одноразовая completion, без стриминга)
    const { message: aiMsg } = await completeOnce(chatId, [
      { role: 'user', content: text }
    ])
    // защита: чат мог смениться пока ждали ответ
    if (cid.value !== chatId) return

    messages.value.push(aiMsg)
    await nextTick()
    if (stickToBottom.value) scrollToBottom(true)
  } catch (e) {
    console.error('[chat] send error', e)
    // Можно отобразить тост/ошибку по вкусу
  } finally {
    sending.value = false
  }
}

// ---- Реакция на смену cid: сброс + перезагрузка с защитой от гонок ----
watch(
  cid,
  async (newCid) => {
    if (!newCid || Number.isNaN(newCid)) return
    // сбрасываем старую историю до загрузки новой
    messages.value = []
    await nextTick()
    await loadMessagesSafe(newCid)
  },
  { immediate: true }
)

// первоначальный автоскролл
onMounted(() => {
  nextTick(() => scrollToBottom(false))
})
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Заголовок (опционально можно вывести pid/cid) -->
    <header class="shrink-0 border-b px-4 py-2 text-sm text-muted-foreground">
      Chat #{{ cid }} <span v-if="pid">in Project #{{ pid }}</span>
    </header>

    <!-- Вьюпорт сообщений (владеет скроллом) -->
    <div class="flex-1 relative overflow-hidden bg-background">
      <div
        ref="viewport"
        class="h-full overflow-y-auto px-4 pt-4 pb-24"
        @scroll="onScroll"
      >
        <div class="space-y-3">
          <div
            v-for="m in messages"
            :key="m.id"
            class="flex"
            :class="m.role === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div
              class="max-w-[80%] rounded-md border px-3 py-2 text-sm"
              :class="m.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-card'"
            >
              {{ m.content }}
            </div>
          </div>

          <div v-if="sending" class="text-xs text-muted-foreground">
            Assistant is typing…
          </div>
        </div>
      </div>

      <!-- Плавающая кнопка «вниз», если ушли от низа -->
      <button
        v-if="!stickToBottom"
        class="absolute bottom-24 right-4 rounded-full border bg-background px-3 py-1 text-xs shadow"
        @click="scrollToBottom(true)"
      >
        ↓ New messages
      </button>
    </div>

    <!-- Композер -->
    <div class="shrink-0 border-t bg-background p-3">
      <div class="mx-auto max-w-4xl flex items-end gap-2">
        <textarea
          v-model="input"
          class="flex-1 min-h-10 max-h-40 h-10 resize-y border rounded-md px-3 py-2 text-sm"
          placeholder="Write a message…"
          @keydown.enter.exact.prevent="send"
        />
        <button
          class="border rounded-md px-3 py-2 text-sm"
          :disabled="sending || !input.trim()"
          @click="send"
        >
          Send
        </button>
      </div>
    </div>
  </div>
</template>
