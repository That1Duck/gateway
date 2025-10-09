import { ref } from 'vue'

export type Role = 'user' | 'assistant'
export interface Message { id: number; role: Role; text: string }

const messages = ref<Message[]>([
  { id: 1, role: 'assistant', text: 'Hey! How can I help you today?' }
])
const loading = ref(false)

let _id = 2
export function useChat() {
  function sendUser(text: string) {
    if (!text.trim()) return
    messages.value.push({ id: _id++, role: 'user', text: text.trim() })
  }
  // fake assistant reply (replace with your API call later)
  async function replyWith(delayMs = 600) {
    loading.value = true
    await new Promise(r => setTimeout(r, delayMs))
    messages.value.push({ id: _id++, role: 'assistant', text: 'Got it! (demo reply)' })
    loading.value = false
  }
  return { messages, loading, sendUser, replyWith }
}
