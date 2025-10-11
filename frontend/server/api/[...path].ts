import { defineEventHandler, proxyRequest } from 'h3'

export default defineEventHandler((event) => {
  const path = event.context.params?.path
  const suffix = Array.isArray(path) ? path.join('/') : (path || '')
  const target = `http://localhost:8000/${suffix}`  // <= адрес бэка
  return proxyRequest(event, target)
})
