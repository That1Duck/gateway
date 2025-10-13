import { ref } from 'vue'
import {
  listMessages, addUserMessage, completeOnce,
  type Message
} from '@/lib/chatApi'

type Store = {
  messages: typeof messages
  loading: typeof loading
  activeChatId: typeof activeChatId
  setActiveChat: (id: number) => void
  loadHistoryFor: (id: number) => Promise<void>
  sendUser: (text: string) => Promise<Message | void>
  replyWith: () => Promise<Message | void>
}

const messages = ref<Message[]>([])
const loading  = ref(false)
const activeChatId = ref<number | null>(null)

function setActiveChat(id: number) {
  console.log('[useChat] setActiveChat', id)
  activeChatId.value = id
  messages.value = []
}

async function loadHistoryFor(id: number) {
  console.log('[useChat] loadHistoryFor', id)
  activeChatId.value = id
  loading.value = true
  try {
    const data = await listMessages(id)
    console.log('[useChat] history:', data)
    messages.value = data
  } catch (e) {
    console.error('[useChat] history error', e)
    throw e
  } finally {
    loading.value = false
  }
}

async function sendUser(text: string) {
  if (!activeChatId.value) {
    console.warn('[useChat] sendUser called without activeChatId')
    return
  }
  const tid = activeChatId.value
  console.log('[useChat] sendUser → POST /messages', { chatId: tid, text })
  try {
    const saved = await addUserMessage(tid, text)
    console.log('[useChat] saved user message:', saved)
    // защита от гонки: пока мы ждали ответ, пользователь мог перейти в другой чат
    if (activeChatId.value === tid) messages.value.push(saved)
    return saved
  } catch (e) {
    console.error('[useChat] sendUser error', e)
    throw e
  }
}

async function replyWith() {
  if (!activeChatId.value) {
    console.warn('[useChat] replyWith called without activeChatId')
    return
  }
  const tid = activeChatId.value
  loading.value = true
  try {
    const body = messages.value.map(m => ({ role: m.role, content: m.content }))
    console.log('[useChat] replyWith → POST /completion', { chatId: tid, body })
    const { message } = await completeOnce(tid, body)
    console.log('[useChat] assistant message:', message)
    if (activeChatId.value === tid) messages.value.push(message)
    return message
  } catch (e) {
    console.error('[useChat] replyWith error', e)
    throw e
  } finally {
    loading.value = false
  }
}

let store: Store | null = null
export function useChat(): Store {
  if (!store) {
    store = {
      messages,
      loading,
      activeChatId,
      setActiveChat,
      loadHistoryFor,
      sendUser,
      replyWith,
    }
  }
  return store
}
