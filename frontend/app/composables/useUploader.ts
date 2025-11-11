// /composables/useUploader.ts
import { ref } from 'vue'

export type DocumentChunk = {
  id: number
  seq: number
  text: string
  page_from?: number | null
  page_to?: number | null
}

export type Document = {
  id: number
  user_id: number
  original_name: string
  stored_name: string
  mime: string
  size_bytes: number
  sha256: string
  path: string
  status: 'queued' | 'processing' | 'ready' | 'failed'
  error?: string | null
  page_count?: number | null
  title?: string | null
  author?: string | null
  language?: string | null
  chunks?: DocumentChunk[]
}

export function useUploader() {
  const progress = ref<number>(0)
  const isUploading = ref<boolean>(false)
  const error = ref<string | null>(null)

  const runtime = useRuntimeConfig()
  const apiBase = runtime.public.apiBase || ''

  function uploadFile(file: File, userId: number): Promise<Document> {
    return new Promise((resolve, reject) => {
      error.value = null
      progress.value = 0
      isUploading.value = true

      const form = new FormData()
      form.append('f', file)
      form.append('user_id', String(userId))

      const xhr = new XMLHttpRequest()
      xhr.open('POST', `${apiBase}/files/upload`)

      // Если нужны куки/авторизация:
      // xhr.withCredentials = true

      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
          progress.value = Math.round((e.loaded / e.total) * 100)
        }
      }

      xhr.onreadystatechange = () => {
        if (xhr.readyState === XMLHttpRequest.DONE) {
          isUploading.value = false
          try {
            if (xhr.status >= 200 && xhr.status < 300) {
              const json = JSON.parse(xhr.responseText) as Document
              resolve(json)
            } else {
              error.value = `Upload failed: ${xhr.status} ${xhr.statusText}`
              reject(new Error(error.value))
            }
          } catch (err: any) {
            error.value = err?.message || 'Unexpected error'
            reject(err)
          }
        }
      }

      xhr.onerror = () => {
        isUploading.value = false
        error.value = 'Network error during upload'
        reject(new Error(error.value))
      }

      xhr.send(form)
    })
  }

  async function fetchDocument(docId: number): Promise<Document> {
    const res = await $fetch<Document>(`${apiBase}/files/${docId}`)
    return res
  }

  /** Опрос статуса документа до перехода в ready/failed */
  function pollStatus(docId: number, { intervalMs = 1500, timeoutMs = 120000 } = {}): Promise<Document> {
    return new Promise((resolve, reject) => {
      const start = Date.now()
      const timer = setInterval(async () => {
        try {
          const doc = await fetchDocument(docId)
          if (doc.status === 'ready' || doc.status === 'failed') {
            clearInterval(timer)
            resolve(doc)
          } else if (Date.now() - start > timeoutMs) {
            clearInterval(timer)
            reject(new Error('Polling timeout'))
          }
        } catch (e) {
          clearInterval(timer)
          reject(e)
        }
      }, intervalMs)
    })
  }

  return { progress, isUploading, error, uploadFile, fetchDocument, pollStatus }
}



