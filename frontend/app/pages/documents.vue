<!-- /pages/documents.vue -->
<script setup lang="ts">
import { ref } from 'vue'
import UploadDropzone from '@/components/UploadDropzone.vue'
import DocumentList from '@/components/DocumentList.vue'
import { useUploader, type Document } from '@/composables/useUploader'

const docs = ref<Document[]>([])
const { pollStatus, fetchDocument } = useUploader()

function upsert(doc: Document) {
    const i = docs.value.findIndex(d => d.id === doc.id)
    if (i === -1) docs.value.unshift(doc)
    else docs.value[i] = doc
}

async function onUploaded(doc: Document) {
    upsert(doc)
    // сразу же начинаем опрос статуса, чтобы поймать ready/failed
    try {
        const finalDoc = await pollStatus(doc.id, { intervalMs: 1200, timeoutMs: 5 * 60 * 1000 })
        upsert(finalDoc)
    } catch (e) {
        // таймаут или ошибка опроса — оставим как есть
    }
}

async function refresh(id: number) {
    const fresh = await fetchDocument(id)
    upsert(fresh)
}
</script>

<template>
    <div class="max-w-4xl mx-auto p-6">
        <h1 class="text-2xl font-semibold">Документы</h1>
        <p class="text-sm opacity-70">Загружай PDF/DOC/DOCX — мы распарсим и сохраним содержимое.</p>

        <UploadDropzone @uploaded="onUploaded" />

        <DocumentList :items="docs" @refresh="refresh" />
    </div>
</template>
