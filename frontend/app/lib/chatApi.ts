// app/lib/chatApi.ts
import { createApi } from '@/lib/api'
const api = () => createApi()

export type Project = { id: number; name: string; created_at: string }
export type Chat = {
  id: number; project_id: number | null; title: string;
  provider: string; model: string; settings_json?: any;
  created_at: string; deleted_at?: string | null;
}
export type Message = {
  id: number; chat_id: number; role: 'user'|'assistant'|'system';
  content: string; meta_json?: any; created_at: string;
}

/** Projects */
export const listProjects = () => api()<Project[]>('/projects', { method: 'GET' })
export const createProject = (name: string) =>
  api()<Project>('/projects', { method: 'POST', body: { name } })
export const listChatsInProject = (pid: number) =>
  api()<Chat[]>(`/projects/${pid}/chats`, { method: 'GET' })
export const createChatInProject = (pid: number, title: string) =>
  api()<Chat>(`/projects/${pid}/chats`, { method: 'POST', body: { title } })
export const deleteProject = (pid: number, mode: 'hard'|'trash' = 'hard') =>
  api().raw(`/projects/${pid}`, { method: 'DELETE', query: { mode } }).then(() => {})

export const deleteProjectHard = (pid: number) =>
  api().raw(`/projects/${pid}/hard`, { method: 'DELETE' }).then(() => {})

/** Chats (global) */
export const listChats = (params?: { project_id?: number; unassigned?: boolean; include_deleted?: boolean }) =>
  api()<Chat[]>('/chats', { method: 'GET', query: params as any })

export const createUnassignedChat = (title: string) =>
  api()<Chat>('/chats', { method: 'POST', body: { title } })

export const updateChat = (chatId: number, patch: { title?: string; project_id?: number | null; settings?: any }) =>
  api()<Chat>(`/chats/${chatId}`, { method: 'PATCH', body: patch })

export const deleteChat = (chatId: number) =>
  api().raw(`/chats/${chatId}`, { method: 'DELETE' }).then(() => {})

export const deleteChatPermanent = (chatId: number) =>
  api().raw(`/chats/${chatId}/hard`, { method: 'DELETE' }).then(() => {})

export const listTrash = () => api()<Chat[]>('/chats/trash', { method: 'GET' })
export const restoreChat = (chatId: number) =>
  api()<Chat>(`/chats/${chatId}/restore`, { method: 'POST' })

export const emptyTrash = () =>
  api().raw('/chats/trash', { method: 'POST' }).then(() => {})

/** Messages & Completion */
export const listMessages = (chatId: number) =>
  api()<Message[]>(`/chats/${chatId}/messages`, { method: 'GET' })

export const addUserMessage = (chatId: number, content: string) =>
  api()<Message>(`/chats/${chatId}/messages`, { method: 'POST', body: { role: 'user', content } })

export const completeOnce = (
  chatId: number,
  messages: { role: string; content: string }[],
  model?: string,
  settings?: any
) => api()<{ message: Message }>(`/chats/${chatId}/completion`, {
  method: 'POST',
  body: { messages, model, settings }
})
