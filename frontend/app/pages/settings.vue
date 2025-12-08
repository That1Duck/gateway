<script setup lang="ts">
import { ref, watch } from 'vue'
import { useFetch } from '#app'

type LlmSettingsOut = {
  default_provider: string
  default_model: string
  temperature: number
  max_tokens: number | null
  use_streaming: boolean
  use_rag_by_default: boolean
  log_prompts: boolean
  timeout_seconds: number
  has_openai_key: boolean
  has_gemini_key: boolean
  has_grok_key: boolean
}

type LlmSettingsUpdate = {
  default_provider?: string | null
  default_model?: string | null
  temperature?: number | null
  max_tokens?: number | null
  use_streaming?: boolean | null
  use_rag_by_default?: boolean | null
  log_prompts?: boolean | null
  timeout_seconds?: number | null
}

type LlmCredentialsUpdate = {
  openai_api_key?: string | null
  gemini_api_key?: string | null
  grok_api_key?: string | null
}

// --- грузим настройки с бэка ---
const { data, pending, error, refresh } = await useFetch<LlmSettingsOut>(
  '/api/api/v1/settings/llm',
  {
    method: 'GET',
    credentials: 'include',   // на всякий случай явно
  }
)

// локальная форма с настройками
const form = ref<LlmSettingsUpdate>({
  default_provider: 'openai',
  default_model: '',
  temperature: 0.7,
  max_tokens: null,
  use_streaming: true,
  use_rag_by_default: false,
  log_prompts: false,
  timeout_seconds: 30,
})

// когда данные приехали — синхронизируем форму
watch(
  data,
  (val) => {
    if (!val) return
    form.value = {
      default_provider: val.default_provider,
      default_model: val.default_model,
      temperature: val.temperature,
      max_tokens: val.max_tokens,
      use_streaming: val.use_streaming,
      use_rag_by_default: val.use_rag_by_default,
      log_prompts: val.log_prompts,
      timeout_seconds: val.timeout_seconds,
    }
  },
  { immediate: true }
)

// инпуты для API-ключей (их никогда не показываем обратно)
const openaiKey = ref('')
const geminiKey = ref('')
const grokKey = ref('')

const savingSettings = ref(false)
const savingKeys = ref(false)
const message = ref<string | null>(null)

// --- сохранить общие настройки ---
async function saveSettings() {
  try {
    savingSettings.value = true
    message.value = null

    await $fetch('/api/api/v1/settings/llm', {
      method: 'PUT',
      body: form.value,
      credentials: 'include',
    })

    await refresh()
    message.value = 'Settings saved successfully.'
  } catch (e) {
    console.error(e)
    message.value = 'Failed to save settings.'
  } finally {
    savingSettings.value = false
  }
}

// --- сохранить API-ключи ---
async function saveKeys() {
  try {
    savingKeys.value = true
    message.value = null

    const payload: LlmCredentialsUpdate = {}
    if (openaiKey.value) payload.openai_api_key = openaiKey.value
    if (geminiKey.value) payload.gemini_api_key = geminiKey.value
    if (grokKey.value) payload.grok_api_key = grokKey.value

    if (Object.keys(payload).length === 0) {
      message.value = 'Nothing to update.'
      return
    }

    await $fetch('/api/api/v1/settings/llm/credentials', {
      method: 'PUT',
      body: payload,
      credentials: 'include',
    })

    // ключи не возвращаем — просто очищаем поля
    openaiKey.value = ''
    geminiKey.value = ''
    grokKey.value = ''

    await refresh()
    message.value = 'API keys updated successfully.'
  } catch (e) {
    console.error(e)
    message.value = 'Failed to update API keys.'
  } finally {
    savingKeys.value = false
  }
}
</script>

<template>
  <div class="p-6 space-y-6">
    <h1 class="text-2xl font-semibold mb-4">LLM Settings</h1>

    <!-- состояние загрузки / ошибок -->
    <div v-if="pending">Loading...</div>
    <div v-else-if="error">Failed to load settings.</div>

    <div v-else>
      <!-- сообщение об успехе/ошибке -->
      <div v-if="message" class="border rounded p-2 text-sm mb-2">
        {{ message }}
      </div>

      <!-- Блок: General -->
      <section class="border rounded-lg p-4 space-y-4">
        <h2 class="text-lg font-medium">General</h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Default provider</label>
            <select
              v-model="form.default_provider"
              class="border rounded px-2 py-1 w-full"
            >
              <option value="openai">OpenAI</option>
              <option value="gemini">Gemini</option>
              <option value="grok">Grok</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Default model</label>
            <input
              v-model="form.default_model"
              type="text"
              class="border rounded px-2 py-1 w-full"
              placeholder="gpt-4o, gemini-2.5-pro, grok-2..."
            />
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Temperature</label>
            <input
              v-model.number="form.temperature"
              type="number"
              step="0.1"
              min="0"
              max="2"
              class="border rounded px-2 py-1 w-full"
            />
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Max tokens</label>
            <input
              v-model.number="form.max_tokens"
              type="number"
              min="0"
              class="border rounded px-2 py-1 w-full"
            />
          </div>

          <div class="flex items-center gap-2">
            <input
              id="use_streaming"
              v-model="form.use_streaming"
              type="checkbox"
            />
            <label for="use_streaming" class="text-sm">Use streaming</label>
          </div>

          <div class="flex items-center gap-2">
            <input
              id="use_rag_by_default"
              v-model="form.use_rag_by_default"
              type="checkbox"
            />
            <label for="use_rag_by_default" class="text-sm">
              Use RAG by default
            </label>
          </div>

          <div class="flex items-center gap-2">
            <input
              id="log_prompts"
              v-model="form.log_prompts"
              type="checkbox"
            />
            <label for="log_prompts" class="text-sm">
              Log prompts and responses
            </label>
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">
              Timeout (seconds)
            </label>
            <input
              v-model.number="form.timeout_seconds"
              type="number"
              min="0"
              class="border rounded px-2 py-1 w-full"
            />
          </div>
        </div>

        <button
          class="mt-2 px-4 py-2 border rounded text-sm"
          :disabled="savingSettings"
          @click="saveSettings"
        >
          {{ savingSettings ? 'Saving...' : 'Save settings' }}
        </button>
      </section>

      <!-- Блок: API Keys -->
      <section class="border rounded-lg p-4 space-y-4">
        <h2 class="text-lg font-medium">API keys</h2>

        <p class="text-xs text-gray-500">
          Keys are stored encrypted and are never shown back. Indicators show only
          whether a key is set.
        </p>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">
              OpenAI API key
              <span class="ml-2 text-xs">
                ({{ data?.has_openai_key ? 'set' : 'not set' }})
              </span>
            </label>
            <input
              v-model="openaiKey"
              type="password"
              class="border rounded px-2 py-1 w-full"
              placeholder="sk-..."
            />
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">
              Gemini API key
              <span class="ml-2 text-xs">
                ({{ data?.has_gemini_key ? 'set' : 'not set' }})
              </span>
            </label>
            <input
              v-model="geminiKey"
              type="password"
              class="border rounded px-2 py-1 w-full"
              placeholder="..."
            />
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">
              Grok API key
              <span class="ml-2 text-xs">
                ({{ data?.has_grok_key ? 'set' : 'not set' }})
              </span>
            </label>
            <input
              v-model="grokKey"
              type="password"
              class="border rounded px-2 py-1 w-full"
              placeholder="..."
            />
          </div>
        </div>

        <button
          class="mt-2 px-4 py-2 border rounded text-sm"
          :disabled="savingKeys"
          @click="saveKeys"
        >
          {{ savingKeys ? 'Saving...' : 'Save API keys' }}
        </button>
      </section>
    </div>
  </div>
</template>
