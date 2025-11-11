<!-- /components/UploadDropzone.vue -->
<script setup lang="ts">
import { ref } from 'vue'
import { useUploader, type Document } from '@/composables/useUploader'

const emit = defineEmits<{ (e: 'uploaded', doc: Document): void }>()
const fileInput = ref<HTMLInputElement | null>(null)
const userId = 1 // подставь реального пользователя из своей auth-логики

const { progress, isUploading, error, uploadFile } = useUploader()

function openPicker() {
  fileInput.value?.click()
}

async function handleFiles(files: FileList | null) {
  if (!files || !files.length) return
  const file = files[0]
  try {
    const doc = await uploadFile(file, userId)
    emit('uploaded', doc)
  } catch (e) {
    // error уже проброшен из composable
  }
}

function onPick(e: Event) {
  const target = e.target as HTMLInputElement
  handleFiles(target.files)
  if (target) target.value = '' // сброс, чтобы можно было выбрать тот же файл снова
}

function onDrop(e: DragEvent) {
  handleFiles(e.dataTransfer?.files || null)
}
</script>

<template>
  <div
    class="border-2 border-dashed rounded-2xl p-6 text-center hover:bg-gray-50 dark:hover:bg-neutral-900 transition"
    @dragover.prevent
    @drop.prevent="onDrop"
  >
    <p class="font-medium">Перетащи сюда PDF/DOCX или нажми, чтобы выбрать</p>
    <input ref="fileInput" type="file" class="hidden" accept=".pdf,.doc,.docx" @change="onPick" />

    <div class="mt-4 flex items-center justify-center gap-3">
      <button class="px-4 py-2 rounded-xl shadow border" @click="openPicker">Выбрать файл</button>
      <span v-if="isUploading" class="text-sm opacity-70">Загрузка: {{ progress }}%</span>
    </div>

    <div v-if="error" class="mt-3 text-sm text-red-600">{{ error }}</div>
  </div>
</template>